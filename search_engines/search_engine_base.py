from abc import ABC, abstractmethod
from typing import List, Optional
from typing_extensions import TypedDict


class SearchEngResult(TypedDict):
    id: str
    url: str
    title: str
    snippet: str
    full_content: Optional[str]
    query: str
    num_source: Optional[int]
    position: Optional[int]
    search_engine: Optional[str]
    score: Optional[float]


class BaseSearchEngine(ABC):
    def __init__(self, name: str, **kwargs):
        self.name = name

    @abstractmethod
    def search(self, query: str, max_results: Optional[int] = 10, sites: List[str] = None) -> List[SearchEngResult]:
        pass
