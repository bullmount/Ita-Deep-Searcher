import os
from typing import Any, Dict, Iterator, List, Optional, ClassVar, Tuple
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel, LLM
from langchain_core.messages import AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult, LLMResult
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompt_values import PromptValue
from pydantic import Field
import time
import json
import requests

import logging

logger = logging.getLogger(__name__)

class MyChatModel(BaseChatModel):
    model_name: str = Field(alias='model')
    max_tokens: Optional[int] = 4 * 1024
    temperature: Optional[float] = 0.0
    top_p: Optional[float] = 1.0
    timeout_sec: Optional[int] = 30
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stop: Optional[List[str]] = None
    max_retries: Optional[int] = 4
    rate_limit_seconds: Optional[float] = 4
    last_call_time: ClassVar[float] = 0.0
    _model_version: ClassVar[dict] = {"gpt-4o": "2024-05-13", "gpt-4o-mini": "2024-07-18"}
    format: Optional[str] = Field(default=None, description="Format for the response (e.g., 'json')")

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "my-chat-model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters.

        This information is used by the LangChain callback system, which
        is used for tracing purposes make it possible to monitor LLMs.
        """
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "timeout_sec": self.timeout_sec,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": self.stop,
            "max_retries": self.max_retries
        }

    async def agenerate(self, messages_list: List[List[BaseMessage]], stop: Optional[List[str]] = None,
                        **kwargs) -> LLMResult:
        """
        Metodo asincrono per generare risposte multiple.
        """
        results = []
        for messages in messages_list:
            chat_result = self._generate(messages, stop, **kwargs)
            results.append(chat_result.generations)

        return LLMResult(generations=results)

    async def agenerate_prompt(self, prompts: List[PromptValue], stop: Optional[List[str]] = None,
                               **kwargs) -> LLMResult:
        """
        Metodo legacy per compatibilità con versioni più vecchie di LangChain.
        """
        messages_list = [prompt.to_messages() for prompt in prompts]
        return await self.agenerate(messages_list, stop, **kwargs)

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:

        current_time = time.time()
        elapsed_time = current_time - MyChatModel.last_call_time
        if elapsed_time < self.rate_limit_seconds:
            time_to_wait = self.rate_limit_seconds - elapsed_time
            # print(f"Attesa di {time_to_wait:.2f} secondi prima di eseguire di nuovo il metodo [_get_embedding]")
            time.sleep(time_to_wait)

        openai_messages = self.__convert_to_openai_messages(messages)
        # for x in openai_messages:
        #     print(x)
        for i in range(self.max_retries):
            try:
                MyChatModel.last_call_time = time.time()
                text, usage = self.__chat_competion(messages=openai_messages, stop=stop, **kwargs, )
                text = text if type(text) is str else "".join(text)
                if stop is not None:
                    text = self.__enforce_stop_tokens(text, stop)
                if text:
                    if self.format == "json":
                        text = self._extract_json(text)
                    llm_output = {
                        "token_usage": usage,
                        "model_name": self.model_name,
                    }
                    generation = ChatGeneration(message=AIMessage(content=text))
                    return ChatResult(generations=[generation], llm_output=llm_output)
                time.sleep(0.2)
                print(f"Empty response, trying {i + 1} of {self.max_retries}")
            except Exception as e:
                time.sleep(1)
                print(f"Error in MyChatModel._generate: {e}, trying {i + 1} of {self.max_retries}")
        raise None

    def _extract_json(self, text):
        try:
            # Get the raw text
            raw_text = text
            # logger.info(f"Raw model response: {raw_text}")

            # Try to find JSON in the response
            json_start = raw_text.find('{')
            json_end = raw_text.rfind('}') + 1

            if 0 <= json_start < json_end:
                json_text = raw_text[json_start:json_end]
                json.loads(json_text)
                return json_text
            else:
                logger.warning("Could not find JSON in response")
                pass
        except Exception as e:
            # logger.error(f"Error processing JSON response: {str(e)}")
            # If any error occurs during cleanup, just use the original response
            pass

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        current_time = time.time()
        elapsed_time = current_time - MyChatModel.last_call_time
        if elapsed_time < self.rate_limit_seconds:
            time_to_wait = self.rate_limit_seconds - elapsed_time
            time.sleep(time_to_wait)

        openai_messages = self.__convert_to_openai_messages(messages)
        for i in range(self.max_retries):
            try:
                MyChatModel.last_call_time = time.time()
                response = requests.post(
                    url= os.getenv("MY_API_URL"),
                    headers={
                        "Content-Type": "application/json",
                        "Cache-Control": "no-cache",
                        "Ocp-Apim-Subscription-Key": os.getenv("OCP_APIM_SUBSCRIPTION_KEY"),
                    },
                    data=json.dumps({
                        "user_id": os.getenv("MY_API_USER_ID"),
                        "chat_completions_config": {
                            "model_name": self.model_name,
                            "model_version": self._model_version[self.model_name],
                            "temperature": self.temperature,
                            "max_tokens": self.max_tokens,
                            "top_p": self.top_p,
                            "frequency_penalty": self.frequency_penalty,
                            "presence_penalty": self.presence_penalty,
                            "stop": stop,
                        },
                        "prompt": openai_messages,
                        "stream": True  # Aggiunta per abilitare lo streaming, se supportato dalla tua API
                    }),
                    stream=True  # Richiede uno streaming della risposta
                )

                if response.status_code != 200:
                    raise Exception(f"Errore nella richiesta: {response.status_code}")

                # Elaborazione della risposta in streaming
                for line in response.iter_lines():
                    if line:
                        chunk_data = json.loads(line.decode("utf-8"))
                        if "usage" in chunk_data:
                            usage = chunk_data["usage"]
                        if "openai_response" in chunk_data:
                            chunk = AIMessageChunk(content=chunk_data["openai_response"])
                            yield ChatGenerationChunk(message=chunk)

                return  # Terminazione del ciclo, risposte complete

            except Exception as e:
                time.sleep(1)
                print(f"Errore in MyChatModel._stream: {e}, tentativo {i + 1} di {self.max_retries}")

        raise Exception("Tentativi esauriti senza successo.")

    def __convert_to_openai_messages(self, messages: list[BaseMessage]) -> list[dict]:
        """
        Converte una lista di messaggi LangChain in formato compatibile con OpenAI.
        """
        openai_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            elif isinstance(message, SystemMessage):
                role = "system"
            else:
                raise ValueError(f"Messaggio non supportato: {type(message)}")

            openai_messages.append({"role": role, "content": message.content})
        return openai_messages

    def __chat_competion(self, messages, stop, **kwargs: Any) -> Tuple[str, dict]:

        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": os.getenv("OCP_APIM_SUBSCRIPTION_KEY")
        }
        config = {
            "model_name": self.model_name,
            "model_version": self._model_version[self.model_name],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": stop
        }
        data = json.dumps({
            "user_id": os.getenv("MY_API_USER_ID"),
            "chat_completions_config": config,
            "prompt": messages
        })
        url = os.getenv("MY_API_URL")
        response = requests.post(url, headers=headers, data=data)
        res = response.json()

        if "usage" not in res:
            print("Usage not obtained.")
            usage = res["usage"]
        else:
            usage = {}

        if "openai_response" in res:
            return (res["openai_response"], usage)

        raise Exception("Response not obtained.")




