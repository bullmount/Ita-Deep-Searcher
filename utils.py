from datetime import datetime
from typing import List, Tuple
import re


def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


def strip_thinking_tokens(text: str) -> str:
    while "<think>" in text and "</think>" in text:
        start = text.find("<think>")
        end = text.find("</think>") + len("</think>")
        text = text[:start] + text[end:]
    return text


def linkify_sources(text: str, sources: List[dict]) -> Tuple[str, List[dict]]:
    referenced_nums = set(int(num) for num in re.findall(r'\[(\d+)\]', text))
    filtered_sources = [s for s in sources if s['num_source'] in referenced_nums]
    ref_mapping = {}
    new_sources = []
    new_num: int
    for new_num, s in enumerate(filtered_sources, start=1):
        ref_mapping[s['num_source']] = new_num
        new_entry = s.copy()
        new_entry['num_source'] = new_num
        new_sources.append(new_entry)

    source_map = {s['num_source']: s['url'] for s in new_sources}

    def replace_reference(match):
        old_num = int(match.group(1))
        if old_num in ref_mapping:
            new_num_val = ref_mapping[old_num]
            # return f"[\[{new_num_val}\]]({source_map[new_num_val]})"
            link = source_map[new_num_val]
            return f"<a href=\"{link}\">[{new_num_val}]</a>"
        return match.group(0)

    linked_text = re.sub(r'\[(\d+)\]', replace_reference, text)
    return linked_text, new_sources
