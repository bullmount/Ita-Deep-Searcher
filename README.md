# Ita-Deep-Searcher
Assistente di ricerca locale compatibile con qualsiasi LLM. 
Supporta memoria conversazionale, usa espansione di query multiple, nella risposta riporta citazioni e suggerimenti finali.

Ita Deep Searcher è un assistente di ricerca web specifico per la lingua italiana, utilizzabile con diversi LLM provider.
Genera e riformula query multiple per esplorare a fondo un argomento, gestisce una memoria per una chat 
conversazionale, nella risposta generata cita accuratamente le fonti consultate e offre suggerimenti per quaery di approfondimento.


Questa versione prende spunto da [local-deep-researcher di LangChain](https://github.com/langchain-ai/local-deep-researcher)
ed ha le seguenti estensioni:
1. Aggiunta della **Short-Term Memory** per una chat conversazionale
2. Tecnica **multi-query** applicata alla query iniziale per migliorare la ricerca
3. Ricerca web con **rerank dei risultati** basati anche sul contenuto della pagina
4. Generazione della risposta con **citazioni** numerate e **suggerimenti di query per approfondimento**
5. Opzione per circoscrivere la ricerca su un **singolo dominio** 

### Principali Caratteristiche
- LLM configurabile
- Motore di ricerca configurabile (per ora previsti: duckduck, google, tavily)
- Opzione per usare l'intero contenuto delle pagine o solo l'abstract

### Schema LangGraph
<p align="center">
<img src="graph.png" alt="Grafo" width="" title="Grafo">
</p>