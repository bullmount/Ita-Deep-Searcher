import os
from typing import Any, Optional, Literal, List
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    search_api: Literal["duckduckgo", "google", "tavily",] = Field(
        default="duckduckgo",
        title="Search API",
        description="Web search API to use"
    )
    sites_search_restriction: List[str] = Field(
        default=None,
        title="Search Restriction",
        description="Restriction of search to a single site (empty for any site)"
    )
    initial_num_queries_in_addition: int = Field(
        default=2,
        title="Number of queries in initial addition",
        description="Number of queries in initial addition"
    )
    max_filtered_results: int = Field(
        default=4,
        title="Max Filtered Results",
        description="Max number of filtered results"
    )
    max_results_per_query: int = Field(
        default=8,
        title="Max results per query",
        description="Maximum number of results for each query"
    )
    fetch_full_page: bool = Field(
        default=True,
        title="Fetch Full Page",
        description="Include the full page content in the search results"
    )
    max_tokens_per_source: int = Field(
        default=1000,
        title="Max Tokens per Source",
        description="Max number of tokens per source"
    )
    max_web_research_loops: int = Field(
        default=2,
        title="Research Depth",
        description="Number of research iterations to perform"
    )
    model_name: str = Field(
        default="google/gemma-3-27b-it:free",
        title="LLM Model Name",
        description="Name of the LLM model to use"
    )
    llm_provider: Literal["openrouter", "lmstudio", "my_provider",] = Field(
        default="openrouter",
        title="LLM Provider",
        description="Provider for the LLM (LMStudio or openrouter)"
    )
    strip_thinking_tokens: bool = Field(
        default=True,
        title="Strip Thinking Tokens",
        description="Whether to strip <think> tokens from model responses"
    )

    @classmethod
    def from_runnable_config(
            cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (config["configurable"] if config and "configurable" in config else {})

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
