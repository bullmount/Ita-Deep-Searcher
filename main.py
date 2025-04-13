from dotenv import load_dotenv

from deep_searcher_graph import DeepSearcherGraph
from logger_config import setup_logger
from langchain_core.runnables import RunnableConfig


load_dotenv()
setup_logger()

if __name__ == "__main__":
    config: RunnableConfig = RunnableConfig(
        configurable={
            "search_api": "google",
            # "site_search_restriction": "dominio",
            "fetch_full_page": True,

            "llm_provider": "openrouter",
            # # "model_name": "google/gemma-3-27b-it:free",
            "model_name": "mistralai/mistral-small-24b-instruct-2501:free",

            # sistema interno privato ----------
            # "llm_provider": "my_provider",
            # "model_name": "gpt-4o",
            # "model_name": "gpt-4o-mini",

        }
    )

    deep_searcher = DeepSearcherGraph(config)
    deep_searcher.graph_to_image("graph.png")
    r = deep_searcher.invoke("ultime normative europee su intelligenza artificiale")

    with open(f"sommario_finale.md", "w", encoding="utf-8") as file:
        file.write(r["running_summary"])

    print("\n\nSOMMARIO")
    print(r["running_summary"])

