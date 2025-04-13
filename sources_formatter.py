from typing import List
from search_engines.search_engine_base import SearchEngResult


class SourcesFormatter():
    def __init__(self):
        pass

    @staticmethod
    def format_riepilogo(sources: List[SearchEngResult], include_snippet: bool = False):
        formatted_text = ""
        for i, source in enumerate(sources, 1):
            if include_snippet:
                formatted_text += f"<a href='{source['url']}'>[{source['num_source']}]</a> {source['title']} - {source['snippet']}\n\n"
            else:
                formatted_text += f"<a href='{source['url']}'>[{source['num_source']}]</a> {source['title']}\n\n"
        return formatted_text.strip()

    @staticmethod
    def format_sources(sources: List[SearchEngResult], include_raw_content: bool,
                       max_tokens_per_source: int, numbering: bool = True):
        formatted_text = "Contenuto delle fonti:\n"
        for i, source in enumerate(sources, 1):
            formatted_text += f"{'=' * 80}\n"  # Clear section separator
            if numbering:
                formatted_text += f"[{[source['num_source']]}] Fonte: {source['title']}\n"
            else:
                formatted_text += f"Fonte: {source['title']}\n"
            formatted_text += f"{'-' * 80}\n"  # Subsection separator
            formatted_text += f"URL: {source['url']}\n===\n"
            formatted_text += f"Contenuti più pertinenti dalla fonte: {source['snippet']}\n===\n"
            if include_raw_content:
                # Using rough estimate of 4 characters per token
                char_limit = max_tokens_per_source * 4
                # Handle None raw_content
                raw_content = source.get('full_content', '')
                if raw_content is None:
                    raw_content = ''
                if len(raw_content) > char_limit:
                    raw_content = raw_content[:char_limit] + "... [truncated]"
                    formatted_text += f"Contenuto completo della fonte limitata a {max_tokens_per_source} tokens: {raw_content}\n\n"
                else:
                    formatted_text += f"Contenuto completo della fonte: {raw_content}\n\n"
            formatted_text += f"{'=' * 80}\n\n"  # End section separator

        return formatted_text.strip()
