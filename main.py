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
            # "site_search_restriction": "puntosicuro.it",
            "fetch_full_page": True,

            # "llm_provider": "openrouter",
            # # "model_name": "google/gemma-3-27b-it:free",
            # "model_name": "mistralai/mistral-small-24b-instruct-2501:free",

            "llm_provider": "my_provider",
            "model_name": "gpt-4o-mini",

        }
    )

    deep_searcher = DeepSearcherGraph(config)
    deep_searcher.graph_to_image("graph.png")
    r = deep_searcher.invoke("ultimi aggiornamenti del movarisch")
    # r = deep_searcher.invoke("incidenti sul lavoro per punture delle vespe")

    with open(f"sommario_finale.md", "w", encoding="utf-8") as file:
        file.write(r["running_summary"])

    for res in r["web_research_results"][-1]:
        print(res)
        print(res['score'], res['position'], res['num_source'])

    print("\n\nSOMMARIO")
    print(r["running_summary"])

