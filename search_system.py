import os
import tempfile

import cloudscraper
import requests
import math

import fitz
import pymupdf4llm

import io
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyPDF2 import PdfReader
from playwright.sync_api import sync_playwright
from readability import Document
from markdownify import markdownify
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from search_engines.search_engine_base import BaseSearchEngine, SearchEngResult
from search_engines.search_engine_ddg import DuckDuckGoSearchEngine
from search_engines.search_engine_google import GoogleSearchEngine
from search_engines.search_engine_tavily import TavilySearchEngine
import ssl
from requests.adapters import HTTPAdapter
import threading
import logging

logger = logging.getLogger(__name__)

lock = threading.Lock()


class SSLIgnoreAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False  # ❗️DISATTIVA PRIMA
        context.verify_mode = ssl.CERT_NONE  # ❗️POI IMPOSTA verify_mode
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


class SearchSystem:
    def __init__(self, search_api: str):
        self._search_api = search_api

    def execute_search(self, query_list: list[str],
                       max_filtered_results: int,
                       max_results_per_query: int,
                       include_raw_content: bool = False,
                       exclude_sources: Optional[List[SearchEngResult]] = None,
                       sites: Optional[List[str]] = None,
                       additional_params=None) -> List[SearchEngResult]:

        def process_result(result):
            result['full_content'] = self._fetch_raw_content(result['url'])
            return result

        search_engine: BaseSearchEngine = self._create_search_engine()

        all_results: List[SearchEngResult] = []
        exclude_sources = exclude_sources or []

        num_queries = len(query_list)
        num_exclusions = len(exclude_sources)
        if num_exclusions > 0:
            delta_per_query = math.ceil(num_exclusions / num_queries)
            max_results_per_query = max_results_per_query + delta_per_query

        for query in query_list:
            all_query_results: List[SearchEngResult] = search_engine.search(query,
                                                                            max_results=max_results_per_query,
                                                                            sites=sites)
            filtered_results = [r for r in all_query_results
                                if not any(exclude_result['url'] == r['url'] for exclude_result in exclude_sources)]

            for r in filtered_results:
                r['query'] = query
                r['search_engine'] = self._search_api
                r['full_content'] = ""

            if include_raw_content:
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(process_result, r) for r in filtered_results]
                processed_results = [future.result() for future in as_completed(futures)]
                processed_results = [r for r in processed_results
                                     if r['full_content'] is not None and len(r['full_content'].split()) > 30]
                all_results.extend(processed_results)
            else:
                all_results.extend(filtered_results)

        if len(all_results) <= 1:
            return all_results

        top_results = self._rank_search_results(all_results, max_filtered_results, include_raw_content)
        return top_results[:max_filtered_results]

    def _create_search_engine(self) -> BaseSearchEngine:
        if self._search_api == "google":
            return GoogleSearchEngine()
        elif self._search_api == "duckduckgo":
            return DuckDuckGoSearchEngine()
        elif self._search_api == "tavily":
            return TavilySearchEngine()
        else:
            raise ValueError("Invalid search engine name")

    @staticmethod
    def _fetch_pdf(url: str) -> bytes:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    temp_file_path = tmp_file.name

                with page.expect_download() as download_info:
                    page.goto(url)
                    download = download_info.value
                    download.save_as(temp_file_path)
                    with open(temp_file_path, 'rb') as f:
                        pdf_bytes = f.read()
                        return pdf_bytes
            finally:
                browser.close()
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)


    @staticmethod
    def _fetch_raw_content(url: str) -> Optional[str]:
        try:
            session = requests.Session()
            session.verify = False
            session.mount("https://", SSLIgnoreAdapter())
            try:
                head_resp = session.head(url, allow_redirects=True)
                content_type = head_resp.headers.get("Content-Type", "")
            except:
                content_type = ""

            if url.lower().endswith(".pdf") or "application/pdf" in content_type:
                try:
                    scraper = cloudscraper.create_scraper()  # crea un sessione che esegue JS-challenge
                    scraper.mount("https://", SSLIgnoreAdapter())
                    response = scraper.get(url, verify=False)
                    pdf_bytes = response.content
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                except Exception as e:
                    pdf_bytes = SearchSystem._fetch_pdf(url)
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

                with lock:
                    # da eseguire in mutua esclusione
                    testo = pymupdf4llm.to_markdown(doc)
                    return testo.strip() if testo else "[Nessun testo estraibile dal PDF]"

            # Create a client with reasonable timeout
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)  # headless=False per vedere il browser
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                    java_script_enabled=True,
                )
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=60 * 1000)  # 60 sec.
                # html = page.content()
                html = page.inner_html("body")
                doc = Document(html)
                contenuto_html = doc.summary()
                return markdownify(contenuto_html)
        except Exception as e:
            logger.warning(f"Warning: Failed to fetch full page content for {url}: {str(e)}")
            return None

    def _rank_search_results(self, results: List[SearchEngResult], top_n: int,
                             include_raw_content: bool) -> List[SearchEngResult]:
        df = pd.DataFrame(results)
        df['desc_length'] = df['snippet'].str.len()

        numeric_cols = ['position', 'desc_length']
        if include_raw_content:
            df['page_length'] = df['full_content'].str.len()
            numeric_cols.append('page_length')

        url_counts = Counter(df['url'])
        df['url_frequency'] = df['url'].map(url_counts)

        scaler = MinMaxScaler()
        df_scaled = df.copy()

        if not df[numeric_cols].empty:
            df_scaled[numeric_cols] = scaler.fit_transform(df[numeric_cols])

        max_freq = df['url_frequency'].max()
        df_scaled['url_frequency_norm'] = df['url_frequency'] / max_freq if max_freq > 0 else 0

        # 3.1 Inverti il valore della posizione (rank più basso è migliore)
        df_scaled['position_score'] = 1 - df_scaled['position']

        # 3.2 Calcola punteggio per lunghezza descrizione (preferibilmente non troppo corta né troppo lunga)
        # Questo crea una curva a campana con picco a 0.5
        df_scaled['desc_length_score'] = 1 - 2 * np.abs(df_scaled['desc_length'] - 0.5)

        if include_raw_content:
            # 3.3 Calcola punteggio per lunghezza pagina
            # Assumiamo che pagine più lunghe abbiano più contenuto, ma non troppo lunghe
            df_scaled['page_length_score'] = np.where(
                df_scaled['page_length'] <= 0.7,
                df_scaled['page_length'],
                0.7 - 0.3 * (df_scaled['page_length'] - 0.7) / 0.3
            )

            # 4. Calcolo dello score composito con pesi
            # Ora includiamo la frequenza dell'URL tra le query
            df_scaled['final_score'] = (
                    0.4 * df_scaled['position_score'] +  # La posizione originale è importante
                    0.2 * df_scaled['page_length_score'] +  # La lunghezza della pagina è abbastanza importante
                    0.15 * df_scaled['desc_length_score'] +  # La lunghezza della descrizione è meno importante
                    0.25 * df_scaled['url_frequency_norm']  # Premiamo i risultati che appaiono in più query
            )
        else:
            df_scaled['final_score'] = (
                    0.5 * df_scaled['position_score'] +  # La posizione originale diventa più importante
                    0.2 * df_scaled['desc_length_score'] +  # La lunghezza della descrizione resta importante
                    0.3 * df_scaled['url_frequency_norm']  # Premiamo di più i risultati che appaiono in più query
            )

        unique_urls = []
        final_indices = []

        for idx in df_scaled.sort_values('final_score', ascending=False).index:
            url = df_scaled.loc[idx, 'url']
            # Se l'URL non è già stato selezionato, lo aggiungiamo
            if url not in unique_urls:
                unique_urls.append(url)
                final_indices.append(idx)
                # Ci fermiamo quando raggiungiamo il numero desiderato di risultati
                if len(unique_urls) >= top_n:
                    break

        assert final_indices
        final_result_df = df.loc[final_indices].copy()
        final_result_df['score'] = df_scaled.loc[final_indices, 'final_score']
        final_result_df['frequency'] = df.loc[final_indices, 'url_frequency']

        search_results: List[SearchEngResult] = []
        for idx, row in final_result_df.iterrows():
            # Crea un dizionario con tutti i valori
            result_dict = {}

            # Itera su tutte le chiavi del DataFrame
            for key in SearchEngResult.__annotations__.keys():
                # Assegna il valore dalla riga corrente
                result_dict[key] = row[key]
            result_dict['score'] = row['score']

            # Crea l'oggetto SearchEngResult dal dizionario
            result = SearchEngResult(**result_dict)
            search_results.append(result)

        search_results.sort(key=lambda x: x['score'], reverse=True)

        return search_results
