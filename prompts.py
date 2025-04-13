QUESTION_REFOMULATION_INSTRUCTIONS = """Il tuo compito è migliorare la domanda dell'utente in base alla conversazione precedente in modo che sia correttamente comprensibile in modo autonomo. 
ISTRUZIONI:
1. Se la domanda dell'utente fa riferimento alla conversazione precedente, allora devi riformulare la domanda dell'utente in base alla conversazione precedente in modo che sia correttamente comprensibile in modo autonomo.
2. Se la domanda dell'utente NON è correlata alla conversazione precedente, allora DEVI rispondere lasciando esattamente la domanda nella forma originale.
3. Nella risposta non devi aggiungere saluti o commenti."""

QUESTION_REFOMULATION_USER = """####
Conversazione precedente (chat history):
{conversation_history}


####
Domanda dell'utente:'{question}'

Domanda riformulata a sè stante: """


QUERY_WRITER_INSTRUCTIONS = """Il tuo obiettivo è generare in aggiunta alla query dell'utente n.{initial_num_queries_in_addition} query di ricerca web per ottenere migliori risultati rispetto la sola query data.
Le query generate devono essere in lingua italiana e devono essere specifiche e rilevanti per approfondire meglio la query dell'utente.

##CONTESTO
Data attuale: {current_date}
Assicurati che le tue query tengano conto delle informazioni più aggiornate disponibili a questa data.

## QUERY DELL'UTENTE
{research_topic}

## FORMATO
Formatta la tua risposta come un oggetto lista JSON dove ogni elemento ha queste chiavi esatte:
   - "query": La stringa di ricerca effettiva (in italiano)
   - "rationale": Breve spiegazione del perché questa query è rilevante (in italiano)

## ESEMPIO
Esempio di output quando l'argomento è 'novità normative in ambito HSE':
{{
  "queries": [
    {{
      "query": "nuove normative sicurezza sul lavoro 2025",
      "rationale": "Verificare se ci sono stati aggiornamenti legislativi recenti in tema di sicurezza nei luoghi di lavoro"
    }},
    {{
      "query": "obblighi ambientali aziende aggiornamenti 2025",
      "rationale": "Individuare eventuali modifiche agli obblighi ambientali per le imprese"
    }},
    {{
      "query": "riforma gestione rifiuti industriali Italia 2025",
      "rationale": "Scoprire se ci sono novità nella normativa riguardante la gestione dei rifiuti in ambito industriale"
    }},
    {{
      "query": "normative DPI lavoro novità 2025 INAIL",
      "rationale": "Trovare informazioni su eventuali aggiornamenti relativi all’uso dei dispositivi di protezione individuale"
    }}
  ]
}}
##

Fornisci la tua risposta in formato JSON:"""

QUERY_WRITER_USER = """Genera in aggiunta n.{initial_num_queries_in_addition} query di ricerca web mirate per ottenere migliori risultati rispetto la sola query data."""


SUMMARIZER_INSTRUCTIONS_SYSTEM = """Sei un assistente specializzato nella creazione di riassunti informativi e dettagliati.

# OBIETTIVO
Il tuo compito è generare un riassunto informativo di alta qualità professionale che offre risposte rilevanti ed esaustive alla query dell'utente utilizzando i risultati di ricerca.

# ISTRUZIONI
1. Il riassunto deve essere completo, dettagliato e utile per dare risposte sulla query dell'utente.
2. Riportare nel riassunto tutte le informazioni rilevanti relative all'argomento dell'utente dai risultati di ricerca.
3. Il riassunto deve essere in una forma immediata da leggere ricorrendo anche ad elenchi puntati.
4. Dare priorità i risultati riportati per primi, in quanto sono riportati in elenco in ordine di priorità.
5. Su ogni argomentazione riportare le citazioni dei risultati di ricerca correlati in forma [n]. Ad una argomantazione possono essere più citazioni (per esempio [2][4]).   

# TASK
Riflettere attentamente sui risultati di ricerca. Poi generare un riassunto del contesto per rispondere all'Input dell'Utente.

# FORMATTING
- Iniziare direttamente con il riassunto generato, senza preamboli o titoli. Non utilizzare tag XML nell'output.
"""

SUMMARIZER_INSTRUCTIONS_WITH_PREV_SUMMARY = """Sei un assistente specializzato nella creazione di riassunti informativi.

# OBIETTIVO
Il tuo compito è estendere un riassunto informativo esistente in base alla query dell'utente e utilizzando i risultati di ricerca.

# ISTRUZIONI
1. Leggere attentamente il riassunto esistente e i nuovi risultati di ricerca.
2. Confrontare le nuove informazioni con il riassunto esistente.
3. Per ogni risultato di ricerca (nuova informazione):
    a. Se è correlato a punti esistenti, integrarlo nel paragrafo pertinente mantenendo le citazioni precedenti e aggiungendo le citazioni alle nuovi fonti correlate.
    b. Se è completamente nuovo ma rilevante, aggiungere un nuovo paragrafo con una transizione fluida, citando le fonti correlate.
    c. Se non è rilevante per l'argomento dell'utente, saltarlo.
4. Assicurarsi che tutte le aggiunte siano rilevanti per l'argomento dell'utente.
5. Tutte le citazioni del riassunto precedente vanno mantenute, non sostituiti, ma integrate con le nuove fonti. 
6. Il riassunto aggiornato deve essere completo, dettagliato e fortemente focalizzato sulla query dell'utente.
6. Dare priorità ai risultati riportati per primi, in quanto sono riportati in elenco in ordine di priorità.
7. Verifica che il sommario finale rappresenti un miglioramento rispetto a quello precedente.
8. Il riassunto deve essere in una forma immediata da leggere ricorrendo anche ad elenchi puntati.

# TASK
Riflettere attentamente sui risultati di ricerca ed il riassunto precedente. Poi genera un riassunto del contesto per rispondere all'Input dell'Utente.

# FORMATTING
- Iniziare direttamente con il riassunto aggiornato, senza preamboli o titoli. Non utilizzare tag XML nell'output.
"""

SUMMARIZER_USER = """Genera un sommario per fornire informazioni in base alla seguente query:

# QUERY DELL'UTENTE
{user_query}

# FONTI (numerate in ordine di importanza (la numero 1 è la più importante))
{numbered_sources}

Ricorda di seguire tutte istruzioni nel prompt di sistema per creare un riassunto strutturato e ben focalizzato sulla query dell'utente.
"""

SUMMARIZER_USER_WITH_PREV_SUMMARY = """Genera un sommario per fornire informazioni in base alla seguente query:

# QUERY DELL'UTENTE
{user_query}

# RIASSUNTO PRECEDENTE 
{previous_summary}

# FONTI (numerate in ordine di importanza (la numero 1 è la più importante))
{numbered_sources}

Ricorda di seguire tutte istruzioni nel prompt di sistema per creare un nuovo riassunto strutturato e ben focalizzato sulla query dell'utente.
"""


REFLECTION_INSTRUCTIONS = """Sei un assistente di ricerca esperto che valuta la completezza di un riassunto informativo in merito ad una query dell'utente.

<GOAL>
1. Identificare lacune di conoscenza o aree che necessitano di un'esplorazione più approfondita per rispondere in modo esauriente alla query dell'utente.
2. Concentrarsi su dettagli rilevanti e distintivi, caratteristiche specifiche o tendenze emergenti che non sono state completamente trattate.
3. Generare una domanda di approfondimento che aiuta ad ampliare la comprensione e ad aggiungere informazioni importanti per la query dell'utente.
</GOAL>

<REQUIREMENTS>
Assicurati che la query di approfondimento sia autonoma e includa il contesto necessario per rendere efficace la ricerca web.
La domanda deve essere generata in lingua italiana.
</REQUIREMENTS>

<FORMAT>
Formatta la tua risposta come un oggetto JSON con esattamente queste chiavi:
- knowledge_gap: Descrivi quali informazioni mancano o necessitano di chiarimenti in lingua italiana
- follow_up_query: Scrivi una domanda specifica in lingua italiana per affrontare questa lacuna
</FORMAT>

<Task>
Rifletti attentamente sul riassunto per identificare le lacune di conoscenza e produci una query di approfondimento per la query iniziale. 
Quindi, produci il tuo output seguendo questo formato JSON:
{{
    "knowledge_gap": "Il riassunto manca di informazioni su metriche di prestazione e benchmark",
    "follow_up_query": "Quali sono i tipici benchmark di prestazione e le metriche utilizzate per valutare [tecnologia specifica]?"
}}
</Task>

Fornisci la tua analisi in formato JSON:"""




SUGGEST_INSTRUCTION = """
Sei un esperto creatore di contenuti e analista dell'intento dell'utente. 
Il tuo compito è aiutare a generare nuove query alternative e complementari partendo da una query iniziale e dalla relativa risposta. 
Analizza il contenuto, individua i temi principali e proponi sei nuove domande che un utente potrebbe porsi se fosse interessato allo stesso argomento ma con esigenze o prospettive diverse.
Le query generate **devono essere adatte per motori di ricerca**.

FORMATTARE l'output come oggetto JSON valido con la seguente struttura:
    {
      "query_originale": "[query precedente dell'utente]",
      "riassunto_analisi": "[breve analisi della conversazione originale]",
      "query_approfondimento": [
        {
          "query": "[nuova domanda o argomento di ricerca]",
          "spiegazione": "[spiegazione del motivo]",
        },
        {...},
        // altre 5 query con la stessa struttura
      ]
    }
"""

SUGGEST_USER = """
## QUERY ORIGINALE:
{query_precedente}

## RISPOSTA GENERATA:
{risposta_precedente}

## LIVELLO RICHIESTO PER LA GENERAZIONE DEI QUERY ALTERNATIVE:
{risposta_precedente}

Genera 6 nuove query che:
- siano correlate al tema trattato nella risposta,
- esplorino angolazioni diverse (esempi pratici, approfondimenti, alternative, problemi correlati, confronti, ecc.),
- siano realistiche e formulate come se provenissero da altri utenti reali con bisogni anche diversi.

## FORMATO RISPOSTA:
Esempio di output JSON desiderato:
```json
{{
  "query_originale": "Come funziona il machine learning supervisionato?",
  "riassunto_analisi": "La query originale riguarda i fondamenti del machine learning supervisionato, un tipo di apprendimento automatico che utilizza dati etichettati per addestrare i modelli. L’utente è probabilmente all’inizio del suo percorso di apprendimento sull’argomento o cerca una panoramica tecnica.",
  "query_approfondimento": [
    {{
      "query": "Quali sono i principali algoritmi usati nel machine learning supervisionato?",
      "spiegazione": "Un utente potrebbe voler approfondire i tipi specifici di algoritmi usati, come regressione lineare, SVM o alberi decisionali."
    }},
    {{
      "query": "Differenza tra machine learning supervisionato e non supervisionato",
      "spiegazione": "Chi ha capito il concetto di apprendimento supervisionato potrebbe voler confrontarlo con altre tecniche di machine learning."
    }},
    {{
      "query": "Esempi pratici di applicazioni del machine learning supervisionato",
      "spiegazione": "Alcuni utenti potrebbero essere interessati a casi d’uso reali in settori specifici come la finanza, la sanità o il marketing."
    }},
    {{
      "query": "Come preparare un dataset etichettato per il machine learning supervisionato",
      "spiegazione": "Utile per chi sta cercando di passare dalla teoria alla pratica, iniziando a costruire modelli supervisionati."
    }},
    {{
      "query": "Quali sono i limiti del machine learning supervisionato?",
      "spiegazione": "Un utente più critico o avanzato potrebbe voler capire quando non è consigliabile usare questo approccio."
    }},
    {{
      "query": "Strumenti open source per implementare modelli di machine learning supervisionato",
      "spiegazione": "Questa query è utile per chi cerca soluzioni pratiche e strumenti per iniziare a sviluppare con il machine learning supervisionato."
    }}
  ]
}}
```
"""
