from search_system import SearchSystem


def test_google_search():
    search_system = SearchSystem("google")
    results = search_system.execute_search(["Finanziamenti per la sicurezza, apertura domande del bando ISI 2024"],
                                           max_filtered_results=6,
                                           max_results_per_query=8,
                                           include_raw_content=False, additional_params={})

    assert len(results) == 6, "Numero di risultati non corretto"

    for i in range(len(results) - 1):
        assert results[i]['score'] >= results[i + 1][
            'score'], f"Score non in ordine decrescente: {results[i]['score']} < {results[i + 1]['score']}"

    for result in results:
        assert result['full_content'] is None or result['full_content'] == "", "full_content non vuoto o None"


def test_google_search_include_raw_content():
    search_system = SearchSystem("google")
    results = search_system.execute_search(["Finanziamenti per la sicurezza, apertura domande del bando ISI 2024"],
                                           max_filtered_results=3,
                                           max_results_per_query=8,
                                           include_raw_content=True, additional_params={})

    assert len(results) == 3, "Numero di risultati non corretto"

    for i in range(len(results) - 1):
        assert results[i]['score'] >= results[i + 1][
            'score'], f"Score non in ordine decrescente: {results[i]['score']} < {results[i + 1]['score']}"

    for result in results:
        assert result['full_content'] is not None and len(
            result['full_content'].split()) > 20, "full_content vuoto o troppo corta"


def test_google_search_exclude_sources():
    search_system = SearchSystem("google")

    results_to_exclude = search_system.execute_search(
        ["Finanziamenti per la sicurezza, apertura domande del bando ISI 2024"],
        max_filtered_results=4,
        max_results_per_query=4,
        include_raw_content=False, additional_params={})

    results = search_system.execute_search(["Finanziamenti per la sicurezza, apertura domande del bando ISI 2024"],
                                           max_filtered_results=3,
                                           max_results_per_query=8,
                                           include_raw_content=False,
                                           exclude_sources=results_to_exclude,
                                           additional_params={})

    assert len(results) == 3, "Numero di risultati non corretto"

    excluded_urls = {r["url"] for r in results_to_exclude}
    for result in results:
        assert result["url"] not in excluded_urls, \
            f"URL {result['url']} trovato sia nei results che in results_to_exclude"


def test_google_search_site_restriction():
    search_system = SearchSystem("google")
    results = search_system.execute_search(["Finanziamenti per la difesa"],
                                           max_filtered_results=4,
                                           max_results_per_query=8,
                                           include_raw_content=False,
                                           additional_params={}, site="it.wikipedia.org")
    assert len(results) == 4, "Numero di risultati non corretto"

    for result in results:
        assert "it.wikipedia.org" in result["url"], \
            f"URL {result['url']} non è di Wikipedia Italia"


if __name__ == "__main__":
    import sys
    import pytest

    sys.exit(pytest.main([__file__]))
