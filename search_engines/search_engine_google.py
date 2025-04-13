from typing import List, Optional, ClassVar
from search_engines.search_engine_base import BaseSearchEngine, SearchEngResult
import uuid
import time
from googlesearch import search

import logging
logger = logging.getLogger(__name__)

class GoogleSearchEngine(BaseSearchEngine):
    _last_search_time: ClassVar[float] = 0.0
    _min_delay: ClassVar[float] = 1.0

    def __init__(self):
        super().__init__(name="Google")

    @classmethod
    def _ensure_delay(cls) -> None:
        """Metodo di classe per gestire il delay tra le ricerche"""
        current_time = time.time()
        elapsed = current_time - cls._last_search_time

        if elapsed < cls._min_delay:
            time.sleep(cls._min_delay - elapsed)

        cls._last_search_time = time.time()

    def search(self, query, max_results: Optional[int] = 10, site: str = None) -> List[SearchEngResult]:
        # Applica il rate limiting a livello di classe
        self._ensure_delay()

        if site:
            query = query + f" site:{site}"

        search_results = list(search(query,
                                     num_results=max_results,
                                     lang="it",
                                     sleep_interval=1,
                                     advanced=True, ))

        results: List[SearchEngResult] = []
        k = 0
        for res in search_results:
            url = res.url
            title = res.title if res.title else ''
            content = res.description if res.description else ''
            k += 1
            if not all([url, title, content]):
                logger.warning(f"Warning: Incomplete result from Google: {res}")
                continue
            results.append(
                SearchEngResult(id=str(uuid.uuid4()), query=query, title=title, snippet=content, url=url, position=k,
                                full_content=None, num_source=None, score=None, search_engine=self.name))

        return results

