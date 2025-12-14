# 📖 Guida Utente - Fantasy World RAG

> Come usare il sistema per chattare con personaggi fantasy

---

## 📋 Indice

1. [Introduzione](#-introduzione)
2. [La Home Page](#-la-home-page)
3. [Esplorare i Personaggi](#-esplorare-i-personaggi)
4. [Chattare con un Personaggio](#-chattare-con-un-personaggio)
5. [Capire le Risposte](#-capire-le-risposte)
6. [Funzionalità Avanzate](#-funzionalità-avanzate)
7. [Consigli per Chat Migliori](#-consigli-per-chat-migliori)

---

## 🎮 Introduzione

Fantasy World RAG ti permette di **conversare con personaggi fantasy** come se fossero reali. Ogni personaggio ha:

- **Una personalità unica** - Modi di fare, valori, paure
- **Una storia** - Da dove viene, cosa ha vissuto
- **Conoscenze** - Cosa sa del suo mondo
- **Memoria** - Si ricorda delle vostre conversazioni passate!
- **Emozioni** - Reagisce in base a come gli parli

### Esempi di cosa puoi fare:

- 🧙‍♂️ Chiedere consiglio a un saggio mago
- 🐉 Parlare con un drago delle sue avventure
- ⚔️ Discutere strategie con un guerriero
- 🧝 Scoprire i segreti di un antico elfo

---

## 🏠 La Home Page

Quando apri l'applicazione (`http://localhost:5173`), vedi la **Home Page**:

```
┌─────────────────────────────────────────────────────┐
│  🏰 Fantasy World RAG                    [Admin]    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Benvenuto nel mondo dei personaggi viventi!        │
│                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │ Gandalf │  │ Smaug   │  │Galadriel│             │
│  │  🧙‍♂️     │  │  🐉     │  │  🧝‍♀️    │             │
│  │  Mago   │  │  Drago  │  │  Elfa   │             │
│  └─────────┘  └─────────┘  └─────────┘             │
│                                                     │
│  [Cerca personaggio...]                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Elementi della Home:

| Elemento | Descrizione |
|----------|-------------|
| **Logo** | Clicca per tornare sempre alla home |
| **Admin** | Accesso al pannello amministratore (se hai i permessi) |
| **Card Personaggi** | Ogni card mostra un personaggio disponibile |
| **Barra di ricerca** | Cerca personaggi per nome, razza o classe |

---

## 👥 Esplorare i Personaggi

### La Card del Personaggio

Ogni personaggio ha una **card** che mostra:

```
┌─────────────────────┐
│      [Avatar]       │
│                     │
│     GANDALF         │
│   "Il Grigio"       │
│                     │
│  Razza: Maia        │
│  Classe: Mago       │
│                     │
│  ⭐ Saggio          │
│  ⭐ Misterioso      │
│  ⭐ Protettivo      │
│                     │
│  [💬 Chatta]        │
└─────────────────────┘
```

### Informazioni visibili:

- **Avatar** - Immagine del personaggio
- **Nome e titolo** - Chi è il personaggio
- **Razza** - Umano, Elfo, Nano, Drago, ecc.
- **Classe** - Mago, Guerriero, Ladro, ecc.
- **Tratti principali** - 3 caratteristiche distintive

### Filtrare i personaggi:

Puoi cercare per:
- **Nome**: "Gandalf", "Smaug"
- **Razza**: "Elfo", "Nano", "Drago"
- **Classe**: "Mago", "Guerriero"
- **Tratti**: "saggio", "coraggioso"

---

## 💬 Chattare con un Personaggio

### Iniziare una conversazione

1. **Clicca sulla card** di un personaggio
2. Si apre la **finestra di chat**
3. Scrivi il tuo messaggio nella casella in basso
4. Premi **Invio** o clicca **Invia**

### L'interfaccia della chat:

```
┌─────────────────────────────────────────────────────┐
│  ← Gandalf il Grigio                    [⚙️] [X]   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🧙‍♂️ Gandalf:                                       │
│  "Benvenuto, viaggiatore. Sono Gandalf.            │
│   Come posso aiutarti oggi?"                        │
│                                                     │
│  👤 Tu:                                             │
│  "Ciao Gandalf! Puoi raccontarmi della             │
│   Terra di Mezzo?"                                  │
│                                                     │
│  🧙‍♂️ Gandalf:                                       │
│  "Ah, la Terra di Mezzo! Una terra vasta           │
│   e antica, piena di meraviglie e pericoli..."     │
│                                           😊 Felice │
│                                                     │
├─────────────────────────────────────────────────────┤
│  [Scrivi un messaggio...]              [📎] [Invia] │
└─────────────────────────────────────────────────────┘
```

### Elementi della chat:

| Elemento | Descrizione |
|----------|-------------|
| **←** | Torna alla lista personaggi |
| **⚙️** | Impostazioni chat |
| **Messaggi** | Storico della conversazione |
| **Stato emotivo** | Come si sente il personaggio (😊 😢 😠 ecc.) |
| **📎** | Allega file (se abilitato) |

---

## 🧠 Capire le Risposte

### Perché il personaggio risponde così?

Le risposte sono generate considerando:

1. **Personalità**
   - Un personaggio timido darà risposte più brevi
   - Un personaggio loquace parlerà a lungo
   - Un personaggio saggio userà metafore

2. **Conoscenze**
   - Il personaggio sa solo ciò che è nella sua "base di conoscenza"
   - Non sa cose del mondo reale moderno (a meno che non sia parte della sua storia)

3. **Storia passata**
   - Se gli hai già parlato di qualcosa, se lo ricorda
   - Può fare riferimento a conversazioni precedenti

4. **Stato emotivo**
   - Se l'hai offeso, potrebbe essere scontroso
   - Se l'hai aiutato, sarà più amichevole

### L'indicatore emotivo

Accanto ai messaggi potresti vedere un'emoji che indica lo stato emotivo:

| Emoji | Stato | Cosa significa |
|-------|-------|----------------|
| 😊 | Felice | Il personaggio è contento |
| 😐 | Neutro | Stato normale |
| 🤔 | Pensieroso | Sta riflettendo |
| 😢 | Triste | Qualcosa l'ha rattristato |
| 😠 | Arrabbiato | È irritato o offeso |
| 😨 | Spaventato | Ha paura di qualcosa |
| 😮 | Sorpreso | Qualcosa l'ha stupito |

---

## 🔧 Funzionalità Avanzate

### Cronologia conversazioni

Il sistema **salva automaticamente** tutte le conversazioni:

- Puoi riprendere da dove avevi lasciato
- Il personaggio si ricorda cosa avete discusso
- Puoi vedere lo storico nelle impostazioni

### Comandi speciali (opzionali)

Alcuni comandi speciali nella chat:

| Comando | Effetto |
|---------|---------|
| `/reset` | Azzera la memoria della conversazione |
| `/mood` | Mostra lo stato emotivo dettagliato |
| `/info` | Mostra info sul personaggio |

### Modalità streaming

Le risposte appaiono **parola per parola** in tempo reale, come se il personaggio stesse davvero scrivendo. Questo rende la conversazione più naturale.

---

## 💡 Consigli per Chat Migliori

### ✅ Cosa funziona bene:

1. **Parla in modo naturale**
   ```
   ❌ "output informazioni su draghi"
   ✅ "Gandalf, cosa sai dei draghi? Ne hai mai incontrato uno?"
   ```

2. **Fai riferimento alla storia del personaggio**
   ```
   ❌ "Parlami del tuo lavoro"
   ✅ "Gandalf, com'era viaggiare con Bilbo verso Erebor?"
   ```

3. **Mostra emozioni**
   ```
   ❌ "Dammi informazioni"
   ✅ "Sono preoccupato per un amico. Hai un consiglio?"
   ```

4. **Fai domande aperte**
   ```
   ❌ "I draghi sono pericolosi? Sì o no?"
   ✅ "Cosa pensi dei draghi?"
   ```

### ❌ Cosa evitare:

1. **Domande sul mondo reale moderno**
   - Il personaggio non sa cosa sia un computer o internet
   - A meno che non sia parte del suo mondo

2. **Rompere il personaggio**
   - Non dire "so che sei un'AI"
   - Il sistema è progettato per roleplay immersivo

3. **Richieste inappropriate**
   - Il sistema ha filtri di sicurezza
   - Contenuti violenti/adulti vengono bloccati

### 🎭 Esempi di buone conversazioni:

**Con un mago:**
```
Tu: "Maestro, sto cercando di imparare la magia. Da dove dovrei iniziare?"

Gandalf: "Ah, un aspirante mago! La magia non si impara dai libri 
soltanto, giovane amico. Inizia osservando il mondo intorno a te. 
Ogni foglia che cade, ogni fiamma che danza, nasconde segreti..."
```

**Con un guerriero:**
```
Tu: "Ho sentito che hai combattuto nella Battaglia delle Cinque Armate. 
Com'è stato?"

Thorin: "Una giornata che non dimenticherò mai. Il sangue, il ferro, 
i gridi... Ma anche il coraggio dei miei compagni. Abbiamo vinto, 
ma il prezzo fu alto..."
```

**Con un personaggio misterioso:**
```
Tu: "Chi sei veramente?"

Personaggio: "Chi sono? *ride sommessamente* Questa è una domanda 
che mi pongo anch'io, a volte. Sono ciò che il destino ha fatto di me, 
né più né meno..."
```

---

## ❓ Problemi Comuni

### "Il personaggio non risponde"

1. Aspetta qualche secondo (l'AI sta elaborando)
2. Controlla la connessione internet
3. Ricarica la pagina

### "La risposta non ha senso"

1. Riformula la domanda in modo più chiaro
2. Il personaggio potrebbe non conoscere l'argomento
3. Prova a dare più contesto

### "Il personaggio si è dimenticato qualcosa"

1. La memoria ha dei limiti
2. Conversazioni molto vecchie potrebbero essere "sbiadite"
3. Ricordagli brevemente l'argomento

---

## 🎉 Divertiti!

Il sistema è progettato per offrirti conversazioni **immersive e coinvolgenti**. Esplora, sperimenta, e lasciati trasportare nel mondo fantasy!

Se sei un **amministratore** e vuoi creare nuovi personaggi, leggi la [Guida Amministratore](GUIDA_ADMIN.md).

---

*Fantasy World RAG - Dove i personaggi prendono vita* 🏰✨
