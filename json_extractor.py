import json
import re
import demjson3
from typing import Union, Dict, List, Any, Optional, Tuple


def extract_valid_json(text: str, max_attempts: int = 5) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Estrae un JSON valido da una stringa che potrebbe contenere testo aggiuntivo.
    Implementa strategie multiple e avanzate per l'estrazione del JSON.

    Args:
        text (str): La stringa contenente il JSON da estrarre
        max_attempts (int): Numero massimo di tentativi di estrazione usando diverse strategie

    Returns:
        Union[Dict[str, Any], List[Any], None]: L'oggetto JSON estratto e parsato, o None se nessun JSON valido è trovato
    """
    # Rimuovi caratteri di formattazione comuni che potrebbero interferire
    cleaned_text = text.replace('\t', ' ').replace('\r', '')

    # Normalizza gli spazi in eccesso
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # Prova con il parsing diretto (potrebbe funzionare se il testo è già un JSON valido)
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass

    strategies = [
        _extract_with_regex,
        _extract_with_balanced_parser,
        _extract_with_markdown_code_blocks,
        _extract_with_line_based_approach,
        _extract_with_fuzzy_matching
    ]

    # Limita i tentativi al numero di strategie disponibili
    attempts = min(max_attempts, len(strategies))

    # Prova ogni strategia in sequenza
    for i in range(attempts):
        result = strategies[i](cleaned_text)
        if result is not None:
            return result

    return None


def _extract_with_regex(text: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """Estrae JSON usando pattern regex per oggetti e array."""
    # Pattern per oggetti JSON con gestione nidificata
    json_patterns = [
        # Oggetti JSON
        r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}',
        # Array JSON
        r'\[(?:[^\[\]]|(?:\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\]))*\]'
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, text)
        for potential_json in matches:
            try:
                return json.loads(potential_json)
            except json.JSONDecodeError:
                continue

    return None


def _extract_with_balanced_parser(text: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """Estrae JSON usando un parser che bilancia parentesi e gestisce le stringhe correttamente."""
    candidates = []

    # Cerca entrambi i tipi di aperture JSON
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start_index = text.find(start_char)
        if start_index == -1:
            continue

        stack = []
        in_string = False
        escape_next = False

        for i, char in enumerate(text[start_index:]):
            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if in_string:
                continue

            if char == start_char:
                stack.append(char)
            elif char == end_char:
                if stack and stack[-1] == start_char:
                    stack.pop()
                    if not stack:  # Abbiamo trovato una struttura JSON completa
                        potential_json = text[start_index:start_index + i + 1]
                        try:
                            parsed = json.loads(potential_json)
                            candidates.append((start_index, parsed))
                        except json.JSONDecodeError:
                            pass

    # Restituisci il JSON che inizia prima nel testo
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    return None


def _extract_with_markdown_code_blocks(text: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """Cerca JSON in blocchi di codice markdown."""
    # Cerca JSON in blocchi di codice markdown
    code_block_patterns = [
        r'```(?:json)?\s*([\s\S]*?)```',  # Markdown code blocks
        r'`([\s\S]*?)`'  # Inline code blocks
    ]

    for pattern in code_block_patterns:
        matches = re.findall(pattern, text)
        for code_content in matches:
            code_content = code_content.strip()
            try:
                if code_content.startswith('{') or code_content.startswith('['):
                    return json.loads(code_content)
            except json.JSONDecodeError:
                continue

    return None


def _extract_with_line_based_approach(text: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Cerca JSON analizzando il testo riga per riga,
    identificando dove può iniziare e finire un JSON.
    """
    lines = text.split('\n')

    for i in range(len(lines)):
        line = lines[i].strip()
        # Cerca linee che potrebbero iniziare un JSON
        if line.startswith('{') or line.startswith('['):
            for j in range(i, len(lines)):
                end_line = lines[j].strip()
                if (line.startswith('{') and end_line.endswith('}')) or \
                        (line.startswith('[') and end_line.endswith(']')):
                    # Potenziale blocco JSON trovato
                    potential_json = '\n'.join(lines[i:j + 1])
                    try:
                        return json.loads(potential_json)
                    except json.JSONDecodeError:
                        # Prova a rimuovere commenti o testo in eccesso
                        cleaned = re.sub(r'//.*$|/\*[\s\S]*?\*/', '', potential_json, flags=re.MULTILINE)
                        try:
                            return json.loads(cleaned)
                        except json.JSONDecodeError:
                            continue

    return None


def _extract_with_fuzzy_matching(text: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Approccio fuzzy per JSON malformati: cerca di correggere errori comuni
    come virgole finali, virgolette non corrispondenti, ecc.
    """
    # Cerca parti che sembrano JSON
    json_like_patterns = [
        r'(\{[\s\S]*?\})',
        r'(\[[\s\S]*?\])'
    ]

    for pattern in json_like_patterns:
        matches = re.findall(pattern, text)
        for potential_json in matches:
            try:
                return demjson3.decode(potential_json)
            except json.JSONDecodeError:
                continue

    return None


def extract_all_json_objects(text: str) -> List[Union[Dict[str, Any], List[Any]]]:
    """
    Estrae tutti i JSON validi presenti nella stringa invece di fermarsi al primo.

    Args:
        text (str): La stringa contenente potenziali JSON

    Returns:
        List[Union[Dict[str, Any], List[Any]]]: Lista di tutti gli oggetti JSON trovati
    """
    all_json_objects = []

    # Pattern per trovare potenziali JSON (oggetti e array)
    patterns = [
        r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}',
        r'\[(?:[^\[\]]|(?:\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\]))*\]'
    ]

    for pattern in patterns:
        matches = set(re.findall(pattern, text))
        for potential_json in matches:
            try:
                parsed = json.loads(potential_json)
                all_json_objects.append(parsed)
            except json.JSONDecodeError:
                continue

    return all_json_objects