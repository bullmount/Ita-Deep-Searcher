# Ita-Deep-Searcher  
**Ita Deep Searcher** è un assistente di ricerca web avanzato, progettato specificamente per la **lingua italiana** e 
ispirato all'esempio [local-deep-researcher di LangChain](https://github.com/langchain-ai/local-deep-researcher).
Utilizza **LangGraph** per orchestrare un sistema di **deep search iterativo**, in grado di esplorare a fondo un 
argomento e fornire risposte complete e contestualizzate.

### Come funziona
Dopo che l’utente inserisce una query o un argomento, il sistema esegue una serie di passaggi strutturati:
1. **Riformulazione** della query sulla base della cronologia della conversazione. 
2. **Espansione multi-query** per esplorare l’argomento da più angolazioni.
3. **Ricerca sul web** tramite un motore configurabile, con possibilità di estrarre il contenuto completo delle pagine.
4. **Riassunto** dei contenuti raccolti per rispondere alla query utente.
5. **Riflessione automatica** per individuare lacune informative.
6. **Generazione di nuove query** mirate a colmare le lacune.
7. **Ripetizione del ciclo** per un numero configurabile di iterazioni.

Al termine, restituisce un riepilogo in **formato markdown**, arricchito da **citazioni numerate** e 
un **elenco delle fonti consultate**, con in coda dei **suggerimenti di query per approfondimenti**.

### Differenze dalla versione LangChain 
Rispetto la versione in Langchain Ita Deep Searcher, oltre i prompt in lingua italiana, ha le seguenti <span style="color:#2582d9">differenze</span>: 
- 🧠 **Short-Term Memory**: gestione della conversazione contestuale, con riformulazione dinamica delle query in base al dialogo precedente.     
- 🔍 **Multi-query intelligente**: espansione automatica della query iniziale per esplorare diverse sfaccettature dell’argomento (opzione configurabile).    
- 📄 **Modalità full-content**: possibilità di leggere il contenuto completo delle pagine trovate, estratto con `readability-lxml` e convertito in Markdown tramite `markdownify`.    
- 📊 **Rerank dei risultati**: i risultati della ricerca vengono riordinati tenendo conto della pertinenza e del contenuto effettivo delle fonti.    
- 🌐 **Ricerca su dominio specifico**: possibilità di limitare le ricerche a un solo dominio web.    
- 📚 **Risposte con citazioni e fonti numerate**, in stile accademico.    
- 💡 **Suggerimenti finali di approfondimento**: proposte di nuove query per continuare l’esplorazione dell’argomento.

### Schema LangGraph
Il grafo implementato è il seguente:
<p align="center">    
<img src="graph.png" alt="Grafo" width="140" title="Grafo">    
</p>

### Caratteristiche principali
 - 🔁 Architettura basata su LangGraph
-   🧠 LLM configurabile 
-   🔍 Motore di ricerca selezionabile (supportati: Google, DuckDuckGo, Tavily)
-   ⚙️ Opzioni di configurazione, tra cui:
    -   Opzione per utilizzare il contenuto completo delle pagine (`full-content`), oltre il titolo e lo snippet
    -   Numero di fonti da usare per ogni ciclo di ricerca
    -   Numero massimo di cicli iterativi
    -   Limite di token per ogni fonte (in modalità `full-content`)

 **In sintesi**, Ita Deep Searcher è un ulteriore esempio di **ricerca web profonda**, automatica e trasparente, 
 pensata per ottenere una comprensione approfondita di un argomento **in italiano**, 
 mantenendo tracciabilità delle fonti e supporto al dialogo conversazionale.

