import os
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from custom_llm.lmstudio import ChatLMStudio
from custom_llm.my_chat_model import MyChatModel


def llm_provide(model_name: str, model_provider: str,
                is_json_format: bool = False, max_tokens: int = 4000) -> BaseChatModel:
    if model_provider == "openrouter":
        openai_api_key = os.getenv("OPENROUTER_API_KEY")
        llm = ChatOpenAI(api_key=openai_api_key,
                         base_url="https://openrouter.ai/api/v1",
                         max_tokens=max_tokens,
                         model=model_name, temperature=0.0)
    elif model_provider == "lmstudio":
        llm = ChatLMStudio(
            base_url="http://localhost:1234/v1",
            model=model_name,
            temperature=0,
            format="json" if is_json_format else None
        )
    elif model_provider == "my_provider":   # ad uso privato con server interno
        llm = MyChatModel(
            model=model_name, temperature=0, max_tokens=max_tokens,
            format="json" if is_json_format else None
        )

    else:
        raise ValueError(f"Unknown model provider: {model_provider}")

    return llm
