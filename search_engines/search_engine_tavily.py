from typing import List, Optional
from search_engines.search_engine_base import BaseSearchEngine, SearchEngResult
import uuid
from tavily import TavilyClient
import os
import logging

logger = logging.getLogger(__name__)


class TavilySearchEngine(BaseSearchEngine):
    def __init__(self):
        super().__init__(name="Tavily")

    def search(self, query, max_results: Optional[int] = 10, site:str = None) -> List[SearchEngResult]:
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        search_results = tavily_client.search(query,
                                              include_domains=[] if site is None else [site],
                                              max_results=max_results,
                                              include_raw_content=False)

        results: List[SearchEngResult] = []
        k = 0
        for res in search_results['results']:
            url = res.get('url')
            title = res.get('title')
            content = res.get('content')
            k += 1
            if not all([url, title, content]):
                logger.warning(f"Incomplete result from Tavily: {res}")
                continue
            results.append(
                SearchEngResult(id=str(uuid.uuid4()), query=query, title=title, snippet=content, url=url,
                                position=k, full_content=None, num_source=None,
                                score=None, search_engine=self.name))

        return results


