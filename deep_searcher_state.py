from dataclasses import dataclass, field
from langchain_core.messages import AnyMessage
from typing_extensions import Annotated
import operator


@dataclass(kw_only=True)
class DeepSearcherGraphStateInput:
    query: str = field(default=None)  # Report topic
    chat_history: list[AnyMessage] = field(default_factory=list)


@dataclass(kw_only=True)
class DeepSearcherGraphStateOutput:
    running_summary: str = field(default=None)  # Final report
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    chat_history: list[AnyMessage] = field(default_factory=list)


@dataclass(kw_only=True)
class DeepSearcherGraphState:
    query: str = field(default=None)
    search_queries: list = field(default=None)  # Search query
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    research_loop_count: int = field(default=0)  # Research loop count
    chat_history: list[AnyMessage] = field(default_factory=list)
    running_summary: str = field(default=None)  # Final report
