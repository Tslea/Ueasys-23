# 🧙‍♂️ Fantasy World RAG - Guida Completa all'Installazione

> **Questa guida ti aiuterà a far funzionare il sistema passo dopo passo, anche se non hai mai programmato prima!**

---

## 📋 Indice

1. [Cos'è questo progetto?](#-cosè-questo-progetto)
2. [Cosa ti serve prima di iniziare](#-cosa-ti-serve-prima-di-iniziare)
3. [Installazione passo-passo](#-installazione-passo-passo)
4. [Configurazione](#-configurazione)
5. [Avviare il sistema](#-avviare-il-sistema)
6. [Come usare il sistema](#-come-usare-il-sistema)
7. [Risoluzione problemi](#-risoluzione-problemi)
8. [FAQ - Domande Frequenti](#-faq---domande-frequenti)

---

## 🎮 Cos'è questo progetto?

Fantasy World RAG è un sistema che ti permette di creare **personaggi fantasy intelligenti** con cui puoi chattare! 

Immagina di poter parlare con Gandalf, un drago, o qualsiasi personaggio tu voglia creare. Il sistema usa l'intelligenza artificiale per far "vivere" questi personaggi, dando loro:

- 🧠 **Memoria** - Si ricordano le conversazioni passate
- 💭 **Personalità** - Ogni personaggio ha il suo carattere unico
- 📚 **Conoscenza** - Sanno cose sul loro mondo
- 😊 **Emozioni** - Reagiscono in modo realistico

---

## 🛠 Cosa ti serve prima di iniziare

### 1. Un Computer con:
- **Windows 10/11**, **Mac**, o **Linux**
- Almeno **8 GB di RAM** (meglio 16 GB)
- Almeno **10 GB di spazio libero** su disco

### 2. Software da installare (ti spiego come fare):

| Software | A cosa serve | Link |
|----------|--------------|------|
| **Python 3.11+** | Il linguaggio di programmazione | [python.org](https://www.python.org/downloads/) |
| **Node.js 18+** | Per il frontend | [nodejs.org](https://nodejs.org/) |
| **Docker Desktop** | Per i database | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Git** | Per scaricare il codice | [git-scm.com](https://git-scm.com/downloads) |
| **VS Code** | Editor di codice (opzionale ma consigliato) | [code.visualstudio.com](https://code.visualstudio.com/) |

### 3. Chiavi API (gratuite o a basso costo):

| Servizio | Costo | Per cosa si usa |
|----------|-------|-----------------|
| **Grok (xAI)** | ~$5/mese crediti | Chat con personaggi |
| **DeepSeek** | ~$2/mese | Analisi documenti |

---

## 📥 Installazione passo-passo

### PASSO 1: Installa Python 🐍

#### Su Windows:
1. Vai su [python.org/downloads](https://www.python.org/downloads/)
2. Clicca il bottone giallo **"Download Python 3.12.x"**
3. Apri il file scaricato
4. ⚠️ **IMPORTANTE**: Spunta la casella **"Add Python to PATH"** in basso!
5. Clicca **"Install Now"**
6. Aspetta che finisca e clicca **"Close"**

#### Verifica che funzioni:
Apri il **Prompt dei comandi** (cerca "cmd" nel menu Start) e scrivi:
```
python --version
```
Dovresti vedere qualcosa come: `Python 3.12.1`

---

### PASSO 2: Installa Node.js 📦

1. Vai su [nodejs.org](https://nodejs.org/)
2. Scarica la versione **LTS** (quella raccomandata)
3. Apri il file e clicca **"Next"** fino alla fine
4. Clicca **"Install"** e poi **"Finish"**

#### Verifica che funzioni:
Nel Prompt dei comandi scrivi:
```
node --version
npm --version
```
Dovresti vedere due numeri di versione.

---

### PASSO 3: Installa Docker Desktop 🐳

Docker serve per far girare i database senza doverli installare uno per uno.

1. Vai su [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Scarica la versione per il tuo sistema
3. Installa seguendo le istruzioni
4. **Riavvia il computer** quando richiesto
5. Dopo il riavvio, apri Docker Desktop
6. Accetta i termini di servizio
7. Aspetta che Docker si avvii (l'icona della balena diventa verde)

#### Verifica che funzioni:
Nel Prompt dei comandi scrivi:
```
docker --version
```

---

### PASSO 4: Installa Git 📂

1. Vai su [git-scm.com/downloads](https://git-scm.com/downloads)
2. Scarica per il tuo sistema
3. Installa con le impostazioni predefinite (clicca sempre "Next")

---

### PASSO 5: Scarica il Progetto 📁

1. Apri il **Prompt dei comandi**
2. Vai nella cartella dove vuoi mettere il progetto:
   ```
   cd C:\Users\TuoNome\Documents
   ```
3. Scarica il progetto:
   ```
   git clone https://github.com/tuouser/fantasy-world-rag.git
   ```
4. Entra nella cartella:
   ```
   cd fantasy-world-rag
   ```

---

### PASSO 6: Installa Poetry (gestore pacchetti Python) 📚

Poetry gestisce tutte le librerie Python necessarie.

#### Su Windows (PowerShell come Amministratore):
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### Aggiungi Poetry al PATH:
1. Cerca "Variabili d'ambiente" nel menu Start
2. Clicca "Modifica le variabili d'ambiente di sistema"
3. Clicca "Variabili d'ambiente..."
4. Nella sezione "Variabili utente", trova "Path" e clicca "Modifica"
5. Clicca "Nuovo" e aggiungi: `%APPDATA%\Python\Scripts`
6. Clicca "OK" su tutto e **riapri il Prompt dei comandi**

#### Verifica:
```
poetry --version
```

---

### PASSO 7: Installa le dipendenze Python 🔧

Nella cartella del progetto:
```
poetry install
```

Questo scaricherà tutte le librerie necessarie. Aspetta qualche minuto!

---

### PASSO 8: Installa le dipendenze Frontend 🎨

```
cd frontend
npm install
cd ..
```

---

## ⚙️ Configurazione

### PASSO 9: Crea il file di configurazione 📝

1. Nella cartella principale del progetto, trova il file `.env.example`
2. Copialo e rinominalo in `.env`:
   
   **Su Windows (Prompt dei comandi):**
   ```
   copy .env.example .env
   ```

3. Apri il file `.env` con un editor di testo (Blocco Note o VS Code)

---

### PASSO 10: Ottieni le chiavi API 🔑

#### A) Chiave Grok (xAI) - Per le chat

1. Vai su [console.x.ai](https://console.x.ai)
2. Crea un account o accedi con X (Twitter)
3. Vai su "API Keys"
4. Clicca "Create new API key"
5. Copia la chiave (inizia con `xai-`)

#### B) Chiave DeepSeek - Per l'analisi

1. Vai su [platform.deepseek.com](https://platform.deepseek.com)
2. Crea un account
3. Vai su "API Keys"
4. Crea una nuova chiave
5. Copia la chiave

---

### PASSO 11: Inserisci le chiavi nel file .env 📋

Apri il file `.env` e modifica queste righe:

```env
# Metti qui la tua chiave Grok
GROK_API_KEY=xai-la-tua-chiave-qui

# Metti qui la tua chiave DeepSeek
DEEPSEEK_API_KEY=la-tua-chiave-deepseek-qui
```

**⚠️ IMPORTANTE**: 
- NON mettere spazi intorno al `=`
- NON usare virgolette
- NON condividere mai queste chiavi con nessuno!

---

### PASSO 12: Configura il database 🗄️

Il file `.env` dovrebbe già avere queste impostazioni:

```env
# Database PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fantasy_world
POSTGRES_USER=fantasy_user
POSTGRES_PASSWORD=fantasy_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Qdrant (Vector Database)
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

Non devi cambiare nulla se usi Docker!

---

## 🚀 Avviare il sistema

### PASSO 13: Avvia i database con Docker 🐳

Assicurati che Docker Desktop sia aperto e funzionante (icona balena verde).

Nella cartella del progetto:
```
docker-compose up -d
```

Questo avvierà:
- ✅ PostgreSQL (database principale)
- ✅ Redis (cache)
- ✅ Qdrant (database vettoriale)

**Prima volta?** Aspetta 2-3 minuti che tutto si scarichi e si avvii.

#### Verifica che i database funzionino:
```
docker-compose ps
```
Dovresti vedere tutti i servizi con stato "Up".

---

### PASSO 14: Inizializza il database 🏗️

Solo la prima volta, devi creare le tabelle:

```
poetry run alembic upgrade head
```

---

### PASSO 15: Avvia il Backend 🖥️

Apri un **nuovo** terminale e scrivi:

```
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Dovresti vedere:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

**Lascia questo terminale aperto!**

---

### PASSO 16: Avvia il Frontend 🎨

Apri un **altro** terminale (lascia il backend aperto!) e scrivi:

```
cd frontend
npm run dev
```

Dovresti vedere:
```
  VITE v5.0.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

---

### PASSO 17: Apri l'applicazione! 🎉

Apri il tuo browser preferito e vai su:

👉 **http://localhost:5173**

Dovresti vedere la homepage di Fantasy World RAG!

---

## 🎮 Come usare il sistema

### Creare un Personaggio 👤

1. **Vai nel pannello Admin**
   - Clicca su "Admin" nel menu
   - Oppure vai su `http://localhost:5173/admin`

2. **Crea un nuovo personaggio**
   - Clicca "Nuovo Personaggio"
   - Compila i campi base:
     - **Nome**: es. "Gandalf"
     - **Descrizione**: chi è il personaggio
     - **Razza**: Umano, Elfo, Nano, ecc.
     - **Classe**: Mago, Guerriero, ecc.

3. **Aggiungi la Personalità**
   - **Tratti**: coraggioso, saggio, misterioso
   - **Valori**: amicizia, giustizia
   - **Paure**: fallimento, perdere gli amici
   - **Stile di parlare**: formale, arcaico, usa proverbi

4. **Aggiungi la Storia (Background)**
   - Da dove viene
   - Eventi importanti della sua vita
   - Relazioni con altri personaggi

5. **Salva il personaggio**
   - Clicca "Crea Personaggio"

### Creare un Personaggio da un Documento 📄

Hai un file con la descrizione di un personaggio? Puoi caricarlo!

1. Vai in "Crea Personaggio"
2. Clicca "Carica Documento"
3. Trascina un file (PDF, TXT, DOCX, YAML)
4. L'AI analizzerà il documento ed estrarrà le informazioni
5. Rivedi e modifica se necessario
6. Salva

### Chattare con un Personaggio 💬

1. Dalla homepage, clicca su un personaggio
2. Si aprirà la chat
3. Scrivi il tuo messaggio e premi Invio
4. Il personaggio risponderà in character!

**Suggerimenti per chat migliori:**
- Parla al personaggio come se fosse reale
- Fai riferimento alla sua storia
- Chiedi della sua vita, opinioni, ricordi
- Il personaggio si ricorderà delle conversazioni precedenti!

### Gestire i Personaggi ⚙️

Nel pannello Admin puoi:
- ✏️ **Modificare** un personaggio esistente
- 🗑️ **Eliminare** un personaggio
- 📊 **Vedere statistiche** delle conversazioni
- 💾 **Esportare** un personaggio in YAML

---

## 🔧 Risoluzione problemi

### ❌ "Python non è riconosciuto come comando"

**Problema**: Python non è nel PATH.

**Soluzione**:
1. Reinstalla Python
2. ⚠️ **Assicurati di spuntare "Add Python to PATH"**
3. Riavvia il computer

---

### ❌ "poetry non è riconosciuto"

**Problema**: Poetry non è nel PATH.

**Soluzione Windows**:
1. Apri PowerShell come Amministratore
2. Esegui:
```powershell
$env:Path += ";$env:APPDATA\Python\Scripts"
```
3. Oppure aggiungi manualmente al PATH (vedi Passo 6)

---

### ❌ Docker non si avvia

**Problema**: Può essere WSL2 su Windows.

**Soluzione Windows**:
1. Apri PowerShell come Amministratore
2. Esegui:
```powershell
wsl --install
```
3. Riavvia il computer
4. Riapri Docker Desktop

---

### ❌ "Connection refused" sul database

**Problema**: I container Docker non sono avviati.

**Soluzione**:
1. Verifica che Docker Desktop sia aperto
2. Esegui:
```
docker-compose down
docker-compose up -d
```
3. Aspetta 30 secondi
4. Riprova

---

### ❌ "API key invalid" o errori LLM

**Problema**: Chiave API non valida o non configurata.

**Soluzione**:
1. Controlla il file `.env`
2. Verifica che le chiavi siano corrette (senza spazi)
3. Controlla di avere credito sull'account Grok/DeepSeek
4. Riavvia il backend dopo aver modificato `.env`

---

### ❌ Il frontend non si carica

**Problema**: Errore durante `npm install` o `npm run dev`.

**Soluzione**:
1. Elimina la cartella `node_modules` in `frontend/`
2. Elimina il file `package-lock.json`
3. Riesegui:
```
cd frontend
npm install
npm run dev
```

---

### ❌ "Module not found" in Python

**Problema**: Dipendenze non installate.

**Soluzione**:
```
poetry install --no-cache
```

---

## ❓ FAQ - Domande Frequenti

### Quanto costa usare il sistema?

Con un uso normale (100-500 messaggi al giorno):
- **Grok**: ~$2-5/mese
- **DeepSeek**: ~$1-2/mese
- **Totale**: ~$3-7/mese

### Posso usarlo offline?

Non completamente. Hai bisogno di internet per:
- Le risposte AI (Grok/DeepSeek)

Puoi usare offline:
- Il database (PostgreSQL, Redis, Qdrant sono locali)
- Il frontend e backend

### Posso usare altri modelli AI?

Sì! Il sistema supporta:
- **Grok** (xAI) - Consigliato per chat
- **DeepSeek** - Consigliato per analisi
- **OpenAI** (GPT-4) - Alternativa
- **Anthropic** (Claude) - Alternativa

Modifica `DEFAULT_CHAT_PROVIDER` e `DEFAULT_ANALYSIS_PROVIDER` nel file `.env`.

### Come faccio il backup dei personaggi?

1. **Esporta in YAML**:
   - Vai nel pannello Admin
   - Clicca su un personaggio
   - Clicca "Esporta YAML"
   - Salva il file

2. **Backup database** (avanzato):
```
docker exec fantasy-world-rag-postgres-1 pg_dump -U fantasy_user fantasy_world > backup.sql
```

### Posso condividere i miei personaggi?

Sì! Esporta il personaggio in YAML e condividi il file. Altri utenti possono importarlo nel loro sistema.

### Il sistema è sicuro?

- Le chiavi API sono salvate solo localmente nel file `.env`
- Non condividere mai il file `.env`!
- Le conversazioni sono salvate nel tuo database locale
- Nessun dato viene inviato a server esterni tranne le chiamate AI

---

## 🎉 Ce l'hai fatta!

Se sei arrivato fin qui, complimenti! Hai un sistema Fantasy World RAG funzionante!

### Prossimi passi:
1. 🧙‍♂️ Crea il tuo primo personaggio
2. 💬 Fai una conversazione di prova
3. 📚 Esplora le impostazioni avanzate
4. 🎨 Personalizza l'interfaccia

### Hai bisogno di aiuto?

- 📖 Leggi la documentazione in `/docs`
- 🐛 Apri un issue su GitHub
- 💬 Unisciti alla community Discord

---

## 📝 Comandi Rapidi (Cheat Sheet)

```bash
# Avvia tutto (Docker + Backend + Frontend)
# Terminale 1:
docker-compose up -d

# Terminale 2:
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminale 3:
cd frontend && npm run dev

# Ferma tutto
docker-compose down
# Premi CTRL+C nei terminali del backend e frontend

# Vedi i log dei database
docker-compose logs -f

# Ricrea il database (ATTENZIONE: cancella tutti i dati!)
docker-compose down -v
docker-compose up -d
poetry run alembic upgrade head

# Aggiorna il progetto
git pull
poetry install
cd frontend && npm install
```

---

**Buon divertimento con i tuoi personaggi fantasy! 🐉✨**
