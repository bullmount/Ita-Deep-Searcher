import json
from typing_extensions import Literal

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph, START

from deep_searcher_state import DeepSearcherGraphState, DeepSearcherGraphStateInput, DeepSearcherGraphStateOutput
from configuration import Configuration
from json_extractor import extract_valid_json
from llm_provider import llm_provide
from prompts import (
    QUESTION_REFOMULATION_INSTRUCTIONS, QUESTION_REFOMULATION_USER,
    QUERY_WRITER_INSTRUCTIONS, QUERY_WRITER_USER,
    SUMMARIZER_USER_WITH_PREV_SUMMARY, SUMMARIZER_INSTRUCTIONS_WITH_PREV_SUMMARY,
    SUMMARIZER_USER, SUMMARIZER_INSTRUCTIONS_SYSTEM,
    REFLECTION_INSTRUCTIONS,
    SUGGEST_USER, SUGGEST_INSTRUCTION
)
from search_system import SearchSystem
from sources_formatter import SourcesFormatter
from utils import strip_thinking_tokens, get_current_date, linkify_sources

import logging

logger = logging.getLogger(__name__)


class DeepSearcherGraph():
    def __init__(self, config: RunnableConfig):
        self._config = config
        self._graph = self._build_graph()
        self._chat_history: list[AnyMessage] = []

    def graph_to_image(self, graph_image_path: str) -> None:
        self._graph.get_graph().draw_mermaid_png(output_file_path=graph_image_path)

    # region NODES and EDGES ************
    @staticmethod
    def _node_reformulate_question(state: DeepSearcherGraphState, config: RunnableConfig) -> dict:
        old_mssages = state.chat_history
        last_query = state.query
        if not old_mssages or len(old_mssages) == 0:
            old_mssages = [HumanMessage(last_query)]
        else:
            configurable = Configuration.from_runnable_config(config)
            llm = llm_provide(configurable.model_name, configurable.llm_provider, is_json_format=False)

            chat_history = "\n".join([f"{msg.type}: {msg.content}" for msg in old_mssages])

            re_write_prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(QUESTION_REFOMULATION_INSTRUCTIONS),
                    HumanMessagePromptTemplate.from_template(QUESTION_REFOMULATION_USER)
                ])

            question_rewriter = re_write_prompt | llm | StrOutputParser()
            res = question_rewriter.invoke({"question": state.query, "conversation_history": chat_history})
            if configurable.strip_thinking_tokens:
                res = strip_thinking_tokens(res)
            reformulated_query = res.split("human:")[0].strip()

            old_mssages.append(HumanMessage(reformulated_query))
            last_query = reformulated_query
        return {"chat_history": old_mssages, "query": last_query}

    @staticmethod
    def _node_generate_queries(state: DeepSearcherGraphState, config: RunnableConfig):
        configurable = Configuration.from_runnable_config(config)
        if configurable.initial_num_queries_in_addition == 0:
            return {"search_queries": [state.query]}

        current_date = get_current_date()
        formatted_prompt_sys = QUERY_WRITER_INSTRUCTIONS.format(
            initial_num_queries_in_addition=configurable.initial_num_queries_in_addition,
            current_date=current_date,
            research_topic=state.query
        )

        formatted_prompt_user = QUERY_WRITER_USER.format(
            initial_num_queries_in_addition=configurable.initial_num_queries_in_addition,
        )

        llm_json_mode = llm_provide(configurable.model_name, configurable.llm_provider, is_json_format=True)

        result = llm_json_mode.invoke(
            [
                SystemMessage(content=formatted_prompt_sys),
                HumanMessage(content=formatted_prompt_user)
            ]
        )
        content = result.content
        if configurable.strip_thinking_tokens:
            content = strip_thinking_tokens(content)

        try:
            queries = extract_valid_json(content)
            search_queries = queries['queries']
        except Exception as e:
            logging.error(f"json conversion error occurred: {e}", exc_info=True)
            raise e

        queries = {"search_queries": [state.query]}
        queries["search_queries"].extend([q["query"] for q in search_queries])
        return queries

    @staticmethod
    def _node_web_research(state: DeepSearcherGraphState, config: RunnableConfig):
        configurable = Configuration.from_runnable_config(config)

        prev_web_research_results = sum(state.web_research_results, [])
        last_num_source = len(prev_web_research_results)

        search_sys = SearchSystem(configurable.search_api)
        results = search_sys.execute_search(state.search_queries,
                                            configurable.max_filtered_results,
                                            configurable.max_results_per_query,
                                            include_raw_content=configurable.fetch_full_page,
                                            exclude_sources=prev_web_research_results,
                                            site=configurable.site_search_restriction)
        for res in results:
            last_num_source += 1
            res['num_source'] = last_num_source

        return {
            "research_loop_count": state.research_loop_count + 1,
            "web_research_results": [results]
        }

    @staticmethod
    def _node_summarize_sources(state: DeepSearcherGraphState, config: RunnableConfig) -> dict:
        existing_summary = state.running_summary
        most_recent_web_research = state.web_research_results[-1]

        if len(most_recent_web_research) == 0:
            return {"running_summary": existing_summary}

        configurable = Configuration.from_runnable_config(config)

        sources_formatter = SourcesFormatter()
        formatted_sources = sources_formatter.format_sources(most_recent_web_research,
                                                             configurable.fetch_full_page,
                                                             configurable.max_tokens_per_source,
                                                             numbering=True)

        llm = llm_provide(configurable.model_name, configurable.llm_provider, is_json_format=False)

        if existing_summary:  # aggiornamento sommario precedente
            formatted_prompt = SUMMARIZER_USER_WITH_PREV_SUMMARY.format(
                user_query=state.query,
                previous_summary=existing_summary,
                numbered_sources=formatted_sources
            )
            result = llm.invoke(
                [
                    SystemMessage(content=SUMMARIZER_INSTRUCTIONS_WITH_PREV_SUMMARY),
                    HumanMessage(content=formatted_prompt)
                ]
            )
        else:  # generazione primo sommario
            formatted_prompt = SUMMARIZER_USER.format(
                user_query=state.query,
                numbered_sources=formatted_sources
            )
            result = llm.invoke(
                [SystemMessage(content=SUMMARIZER_INSTRUCTIONS_SYSTEM), HumanMessage(content=formatted_prompt)]
            )
        if configurable.strip_thinking_tokens:
            result.content = strip_thinking_tokens(result.content)
        summary = result.content

        return {"running_summary": summary}

    @staticmethod
    def _node_reflect_on_summary(state: DeepSearcherGraphState, config: RunnableConfig):
        configurable = Configuration.from_runnable_config(config)
        llm_json_mode = llm_provide(configurable.model_name, configurable.llm_provider, is_json_format=True)

        old_queries = "\n".join([f"- {s}" for s in state.search_queries])
        human_msg = (f"Rifletti su questi dati attualmente conosciuti: "
                     f"\n === \n {state.running_summary},"
                     f"\n === \n"
                     f"\nOra identifica una lacuna di conoscenza e genera una query di ricerca web di follow-up tenendo conto che la query iniziale è:\n**{state.query}**.\n"
                     f"La nuova query non deve essere analoga a queste:\n{old_queries}\n\n")
        result = llm_json_mode.invoke(
            [
                SystemMessage(content=REFLECTION_INSTRUCTIONS.format(research_topic=state.query)),
                HumanMessage(content=human_msg)
            ]
        )
        if configurable.strip_thinking_tokens:
            result.content = strip_thinking_tokens(result.content)
        try:
            reflection_content = extract_valid_json(result.content)
            query = reflection_content.get('follow_up_query')
            if not query:
                return {"search_queries": [f"Dammi ulteriori approfondimenti su **{state.query}**"]}
            return {"search_queries": [query]}
        except (json.JSONDecodeError, KeyError, AttributeError):
            logging.error(f"json decode error occurred: {KeyError} - {AttributeError}", exc_info=True)
            return {"search_queries": [f"Dammi ulteriori approfondimenti su **{state.query}**"]}

    @staticmethod
    def _edge_route_research(state: DeepSearcherGraphState,
                             config: RunnableConfig) -> Literal["finalize_summary", "web_research"]:
        configurable = Configuration.from_runnable_config(config)
        if state.research_loop_count <= configurable.max_web_research_loops:
            return "web_research"
        else:
            return "finalize_summary"

    @staticmethod
    def _node_finalize_summary(state: DeepSearcherGraphState, config: RunnableConfig) -> dict:
        chat_history = state.chat_history
        answer = state.running_summary
        chat_history.append(AIMessage(answer))

        all_web_research_results = sum(state.web_research_results, [])
        answer_updated, used_sources = linkify_sources(answer, all_web_research_results)
        if len(used_sources) > 0:
            sources_formatter = SourcesFormatter()
            riepiloghi = sources_formatter.format_riepilogo(used_sources)
            answer = answer_updated + "\n\n## FONTI:\n" + riepiloghi

        return {"running_summary": answer, "chat_history": chat_history}

    @staticmethod
    def _node_generate_suggestions(state: DeepSearcherGraphState, config: RunnableConfig) -> dict:
        configurable = Configuration.from_runnable_config(config)
        llm = llm_provide(configurable.model_name, configurable.llm_provider, is_json_format=True)
        user_formatted_prompt = SUGGEST_USER.format(
            query_precedente=state.query,
            risposta_precedente=state.running_summary,
            livello_complessita="intermedio"
        )

        res = llm.invoke(
            [
                SystemMessage(content=SUGGEST_INSTRUCTION),
                HumanMessage(content=user_formatted_prompt)
            ])

        content = res.content
        if configurable.strip_thinking_tokens:
            content = strip_thinking_tokens(content)
        try:
            suggestions = extract_valid_json(content)

            summary = state.running_summary
            if len(suggestions["query_approfondimento"]) > 0:
                summary = summary + "\n\n## SUGGERIMENTI:\n" + "\n".join(
                    [f"{i}. {q['query']}" for i, q in enumerate(suggestions["query_approfondimento"], 1)])

            return {"suggestions": suggestions, "running_summary": summary}
        except Exception as e:
            logging.error(f"json conversion error occurred: {e}", exc_info=True)
            raise e

    # endregion NODES and EDGES ************

    def _build_graph(self):
        graph_builder = StateGraph(DeepSearcherGraphState,
                                   input=DeepSearcherGraphStateInput,
                                   output=DeepSearcherGraphStateOutput)
        graph_builder.add_node("reformulate_question", self._node_reformulate_question)
        graph_builder.add_node("generate_queries", self._node_generate_queries)
        graph_builder.add_node("web_research", self._node_web_research)
        graph_builder.add_node("summarize_sources", self._node_summarize_sources)
        graph_builder.add_node("reflect_on_summary", self._node_reflect_on_summary)
        graph_builder.add_node("finalize_summary", self._node_finalize_summary)
        graph_builder.add_node("generate_suggestions", self._node_generate_suggestions)

        graph_builder.add_edge(START, "reformulate_question")
        graph_builder.add_edge("reformulate_question", "generate_queries")
        graph_builder.add_edge("generate_queries", "web_research")
        graph_builder.add_edge("web_research", "summarize_sources")
        graph_builder.add_edge("summarize_sources", "reflect_on_summary")
        graph_builder.add_conditional_edges("reflect_on_summary", self._edge_route_research)
        graph_builder.add_edge("finalize_summary", "generate_suggestions")
        graph_builder.add_edge("generate_suggestions", END)

        graph = graph_builder.compile()

        return graph

    def invoke(self, query: str):
        initial_state = DeepSearcherGraphState(chat_history=self._chat_history, query=query)
        res = self._graph.invoke(initial_state, config=self._config)
        self._chat_history = res['chat_history']
        return res
