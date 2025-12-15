# 🏗️ Architettura del Sistema - Fantasy World RAG

> Documentazione tecnica completa del sistema

---

## 📋 Indice

1. [Panoramica Architettura](#-panoramica-architettura)
2. [Stack Tecnologico](#-stack-tecnologico)
3. [Sistema RAG](#-sistema-rag-retrieval-augmented-generation)
4. [Sistema LLM](#-sistema-llm)
5. [Character Engine](#-character-engine)
6. [Database e Storage](#-database-e-storage)
7. [API e WebSocket](#-api-e-websocket)
8. [Frontend](#-frontend)
9. [Flusso di una Conversazione](#-flusso-di-una-conversazione)
10. [Configurazione Avanzata](#-configurazione-avanzata)

---

## 🏛️ Panoramica Architettura

### Schema generale:

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    React     │  │   Zustand    │  │   Tailwind   │          │
│  │  Components  │  │    Store     │  │     CSS      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                    HTTP/REST │ WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      FastAPI                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │   Routes   │  │ WebSocket  │  │Middlewares │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    SERVICES                               │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │   Chat     │  │ Character  │  │Conversation│         │  │
│  │  │  Service   │  │  Service   │  │  Service   │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌───────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │   RAG System  │  │ Character      │  │  LLM Manager   │    │
│  │   (LightRAG)  │  │ Engine         │  │ (Grok/DeepSeek)│    │
│  └───────────────┘  └────────────────┘  └────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│   PostgreSQL     │ │    Redis     │ │   Qdrant     │
│   (Dati)         │ │   (Cache)    │ │  (Vettori)   │
└──────────────────┘ └──────────────┘ └──────────────┘
```

### Componenti principali:

| Componente | Responsabilità |
|------------|----------------|
| **Frontend** | Interfaccia utente React |
| **FastAPI** | API REST e WebSocket |
| **Services** | Logica di business |
| **RAG System** | Recupero conoscenza |
| **Character Engine** | Personalità e memoria |
| **LLM Manager** | Gestione AI (Grok/DeepSeek) |
| **PostgreSQL** | Database relazionale |
| **Redis** | Cache e sessioni |
| **Qdrant** | Database vettoriale |

---

## 🛠️ Stack Tecnologico

### Backend (Python 3.11+)

| Libreria | Versione | Scopo |
|----------|----------|-------|
| **FastAPI** | 0.104+ | Framework web async |
| **SQLAlchemy** | 2.0+ | ORM database |
| **Pydantic** | 2.5+ | Validazione dati |
| **LightRAG** | latest | Sistema RAG |
| **httpx** | 0.25+ | Client HTTP async |
| **structlog** | 23.2+ | Logging strutturato |

### Frontend (Node.js 18+)

| Libreria | Versione | Scopo |
|----------|----------|-------|
| **React** | 18.2+ | UI Framework |
| **Vite** | 5.0+ | Build tool |
| **TypeScript** | 5.3+ | Type safety |
| **Tailwind CSS** | 3.4+ | Styling |
| **Zustand** | 4.4+ | State management |
| **Framer Motion** | 10+ | Animazioni |

### Database

| Database | Porta | Scopo |
|----------|-------|-------|
| **PostgreSQL** | 5432 | Dati strutturati |
| **Redis** | 6379 | Cache, sessioni, pub/sub |
| **Qdrant** | 6333 | Embedding vettoriali |

---

## 🔍 Sistema RAG (Retrieval-Augmented Generation)

### Cos'è il RAG?

RAG è una tecnica che **migliora le risposte dell'AI** fornendole contesto rilevante prima di rispondere:

```
Senza RAG:
  Utente: "Parlami dell'Anello"
  AI: [Risposta generica basata solo sui dati di training]

Con RAG:
  Utente: "Parlami dell'Anello"
  Sistema: 
    1. Cerca nella knowledge base del personaggio
    2. Trova: "L'Anello è un artefatto creato da Sauron..."
    3. Passa questo contesto all'AI
  AI: [Risposta specifica basata sulla conoscenza del personaggio]
```

### Come funziona nel sistema:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUSSO RAG                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. QUERY UTENTE                                                │
│     "Cosa sai dell'Anello?"                                     │
│              │                                                   │
│              ▼                                                   │
│  2. EMBEDDING                                                    │
│     Trasforma la query in vettore numerico                      │
│     [0.23, -0.45, 0.12, ...]  (1536 dimensioni)                │
│              │                                                   │
│              ▼                                                   │
│  3. RICERCA VETTORIALE (Qdrant)                                 │
│     Trova i chunk più simili alla query                         │
│     ┌────────────────────────────────────────┐                 │
│     │ Score: 0.92 - "L'Anello fu forgiato..."│                 │
│     │ Score: 0.87 - "Sauron creò l'Anello..."│                 │
│     │ Score: 0.81 - "Chi porta l'Anello..."  │                 │
│     └────────────────────────────────────────┘                 │
│              │                                                   │
│              ▼                                                   │
│  4. RERANKING                                                    │
│     Riordina per rilevanza effettiva                            │
│              │                                                   │
│              ▼                                                   │
│  5. CONTEXT INJECTION                                            │
│     Inietta il contesto nel prompt dell'AI                      │
│              │                                                   │
│              ▼                                                   │
│  6. RISPOSTA AI                                                  │
│     L'AI risponde usando il contesto fornito                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Configurazione Chunk

I **chunk** sono i "pezzi" in cui viene divisa la conoscenza del personaggio:

```python
# settings.py
rag_chunk_size: int = 512       # Caratteri per chunk
rag_chunk_overlap: int = 50     # Sovrapposizione tra chunk
rag_top_k: int = 5              # Chunk da recuperare
rag_rerank_top_k: int = 3       # Chunk dopo reranking
rag_min_relevance_score: float = 0.7  # Soglia minima
```

**Spiegazione:**

| Parametro | Valore | Significato |
|-----------|--------|-------------|
| **chunk_size** | 512 | Ogni pezzo di testo è lungo ~512 caratteri. Troppo piccolo = perde contesto. Troppo grande = impreciso. |
| **chunk_overlap** | 50 | 50 caratteri si sovrappongono tra chunk adiacenti, per non "tagliare" concetti a metà |
| **top_k** | 5 | Recupera i 5 chunk più rilevanti dalla ricerca vettoriale |
| **rerank_top_k** | 3 | Dopo il reranking, usa solo i migliori 3 |
| **min_relevance** | 0.7 | Ignora chunk con score sotto 0.7 (70% di somiglianza) |

### Knowledge Tiers (Livelli di Conoscenza)

Il sistema organizza la conoscenza in **livelli di priorità**:

```python
# Pesi per tier
tier_weights_essence: float = 0.30      # Chi è il personaggio
tier_weights_knowledge: float = 0.25    # Cosa sa
tier_weights_relationships: float = 0.20 # Chi conosce
tier_weights_style: float = 0.15        # Come parla
tier_weights_context: float = 0.10      # Contesto attuale
```

**Esempio pratico:**

Quando l'utente chiede "Chi sei?":
1. **Essence (30%)**: "Sono Gandalf, un Istar..."
2. **Knowledge (25%)**: "Conosco la magia, la storia..."
3. **Relationships (20%)**: "Sono amico di Frodo, Bilbo..."
4. **Style (15%)**: "Parlo in modo solenne..."
5. **Context (10%)**: "Ora sono nella Contea..."

---

## 🤖 Sistema LLM

### Provider disponibili:

```
┌─────────────────────────────────────────────────────────────────┐
│                     LLM MANAGER                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐     DEFAULT ROUTING:                           │
│  │   Grok      │ ◄── Chat/Risposte (veloce, economico)         │
│  │  (xAI)      │     Modello: grok-4-fast                       │
│  └─────────────┘                                                 │
│                                                                  │
│  ┌─────────────┐                                                 │
│  │  DeepSeek   │ ◄── Analisi/Estrazione (ragionamento)         │
│  │   (V3.2)    │     Modello: deepseek-chat                     │
│  └─────────────┘                                                 │
│                                                                  │
│  ┌─────────────┐                                                 │
│  │   OpenAI    │ ◄── Fallback                                   │
│  │  (GPT-4o)   │                                                │
│  └─────────────┘                                                 │
│                                                                  │
│  ┌─────────────┐                                                 │
│  │ Anthropic   │ ◄── Alternativa                                │
│  │  (Claude)   │                                                │
│  └─────────────┘                                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Uso nel codice:

```python
from src.llm import get_chat_llm, get_analysis_llm

# Per chat (usa Grok)
chat_llm = get_chat_llm()
response = await chat_llm.generate("Come ti chiami?")

# Per analisi (usa DeepSeek)
analysis_llm = get_analysis_llm()
extracted = await analysis_llm.generate("Analizza questo documento...")
```

### Costi stimati:

| Provider | Modello | Input/1K tok | Output/1K tok | Uso consigliato |
|----------|---------|--------------|---------------|-----------------|
| Grok | grok-4-fast | $0.00005 | $0.00025 | Chat real-time |
| DeepSeek | deepseek-chat | $0.00014 | $0.00028 | Analisi documenti |
| DeepSeek | deepseek-reasoner | $0.00055 | $0.00219 | Reasoning complesso |
| OpenAI | gpt-4o-mini | $0.00015 | $0.0006 | Fallback |

**Stima mensile** (10.000 messaggi, ~500 token ciascuno):
- Solo Grok: ~$2.50/mese
- Mix Grok + DeepSeek: ~$3.50/mese

---

## 🎭 Character Engine

### Componenti del motore:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHARACTER ENGINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  PERSONALITY CORE                          │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │  │
│  │  │ Traits  │ │ Values  │ │  Fears  │ │Desires  │        │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  MEMORY MANAGER                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │  Episodic   │  │  Semantic   │  │ Procedural  │      │  │
│  │  │  (Eventi)   │  │  (Fatti)    │  │ (Abilità)   │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  EMOTION SYSTEM                            │  │
│  │  Current: 😊 Happy (0.7)  │  Decay Rate: 0.05            │  │
│  │  History: 😐→😊→😢→😊    │  Influence: 0.3               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  DECISION ENGINE                           │  │
│  │  Goals → Motivations → Options → Selection                 │  │
│  │  Confidence Threshold: 0.7                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Personalità Core

Definisce l'identità fondamentale:

```python
class PersonalityCore:
    traits: List[str]       # ["saggio", "misterioso"]
    values: List[str]       # ["amicizia", "libertà"]
    fears: List[str]        # ["fallimento"]
    desires: List[str]      # ["proteggere i deboli"]
    speaking_style: str     # Come parla
    quirks: List[str]       # Abitudini particolari
```

### Sistema di Memoria

Tre tipi di memoria:

| Tipo | Descrizione | Esempio |
|------|-------------|---------|
| **Episodica** | Eventi specifici | "L'utente mi ha chiesto dell'Anello ieri" |
| **Semantica** | Fatti e conoscenze | "L'Anello è stato creato da Sauron" |
| **Procedurale** | Come fare le cose | "Quando saluto, uso questa formula" |

```python
# Configurazione memoria
memory_max_episodic_items: int = 1000   # Max eventi ricordati
memory_max_semantic_items: int = 5000   # Max fatti
memory_consolidation_threshold: int = 100  # Quando consolidare
memory_decay_rate: float = 0.1          # Tasso di "dimenticanza"
```

### Sistema Emotivo

Le emozioni influenzano le risposte:

```python
# Configurazione emozioni
emotion_update_interval: int = 60       # Aggiorna ogni 60 secondi
emotion_decay_rate: float = 0.05        # Le emozioni sfumano col tempo
emotion_influence_factor: float = 0.3   # Quanto influenzano le risposte
```

**Funzionamento:**
- Se l'utente è gentile → emozione positiva
- Se l'utente è aggressivo → emozione negativa
- Le emozioni "decadono" verso neutro col tempo

---

## 🗄️ Database e Storage

### PostgreSQL (Dati strutturati)

```sql
-- Tabelle principali
characters          -- Dati personaggi
conversations       -- Conversazioni
messages           -- Messaggi individuali
users              -- Utenti sistema
character_memories  -- Memorie persistenti
```

**Schema semplificato:**

```
characters
├── id (UUID)
├── name
├── description
├── personality (JSON)
├── background (JSON)
├── knowledge (JSON)
├── behavior (JSON)
└── created_at

conversations
├── id (UUID)
├── character_id (FK)
├── user_id
├── started_at
└── last_message_at

messages
├── id (UUID)
├── conversation_id (FK)
├── role (user/assistant)
├── content
├── emotional_state
└── created_at
```

### Redis (Cache e Sessioni)

```
Chiavi Redis:
├── session:{user_id}           # Sessione utente
├── character:{id}:state        # Stato emotivo corrente
├── conversation:{id}:context   # Contesto conversazione
├── cache:embedding:{hash}      # Embedding cached
└── rate_limit:{user_id}        # Rate limiting
```

**Configurazione:**
```python
cache_ttl: int = 3600        # Cache 1 ora
session_ttl: int = 86400     # Sessioni 24 ore
```

### Qdrant (Vector Database)

Memorizza gli **embedding** per la ricerca semantica:

```
Collection: fantasy_characters
├── Vectors: 1536 dimensioni (OpenAI embedding)
├── Payload:
│   ├── character_id
│   ├── content (testo originale)
│   ├── tier (essence/knowledge/etc)
│   └── metadata
└── Distance: Cosine similarity
```

**Configurazione:**
```python
vector_dimension: int = 1536    # Dimensione embedding
vector_distance: str = "Cosine" # Metrica distanza
```

---

## 🔌 API e WebSocket

### Endpoint REST principali:

| Method | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/v1/characters` | Lista personaggi |
| GET | `/api/v1/characters/{id}` | Dettaglio personaggio |
| POST | `/api/v1/characters` | Crea personaggio |
| PUT | `/api/v1/characters/{id}` | Aggiorna personaggio |
| DELETE | `/api/v1/characters/{id}` | Elimina personaggio |
| POST | `/api/v1/chat/{character_id}` | Invia messaggio |
| GET | `/api/v1/conversations/{id}` | Storico conversazione |
| POST | `/api/v1/extract-character` | Estrai da documento |

### WebSocket (Real-time chat):

```javascript
// Connessione
ws = new WebSocket("ws://localhost:8000/ws/chat/{character_id}")

// Inviare messaggio
ws.send(JSON.stringify({
  type: "message",
  content: "Ciao Gandalf!"
}))

// Ricevere risposta (streaming)
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === "chunk") {
    // Pezzo di risposta
    appendToChat(data.content)
  } else if (data.type === "complete") {
    // Risposta completa
    finalizeMessage(data)
  }
}
```

### Rate Limiting:

```python
rate_limit_requests: int = 100  # Max richieste
rate_limit_window: int = 60     # Per minuto
```

---

## 🎨 Frontend

### Struttura componenti:

```
frontend/src/
├── components/
│   ├── ui/              # Componenti base (Button, Card, Input)
│   ├── chat/            # Chat interface
│   │   ├── ChatWindow.tsx
│   │   ├── MessageBubble.tsx
│   │   └── InputBox.tsx
│   ├── character/       # Card personaggi
│   │   ├── CharacterCard.tsx
│   │   └── CharacterGrid.tsx
│   └── admin/           # Pannello admin
│       ├── CharacterForm.tsx
│       └── FileDropzone.tsx
├── stores/              # Zustand stores
│   ├── characterStore.ts
│   ├── chatStore.ts
│   └── authStore.ts
├── pages/               # Pagine
│   ├── Home.tsx
│   ├── Chat.tsx
│   └── Admin.tsx
└── lib/                 # Utilities
    ├── api.ts
    └── websocket.ts
```

### State Management (Zustand):

```typescript
// chatStore.ts
interface ChatStore {
  messages: Message[]
  isLoading: boolean
  emotionalState: string
  
  sendMessage: (content: string) => Promise<void>
  clearMessages: () => void
}
```

---

## 🔄 Flusso di una Conversazione

### Step by step:

```
1. UTENTE INVIA MESSAGGIO
   "Gandalf, parlami dell'Anello"
            │
            ▼
2. FRONTEND → BACKEND (WebSocket)
   { type: "message", content: "..." }
            │
            ▼
3. CHAT SERVICE riceve il messaggio
   - Valida input
   - Recupera contesto conversazione
   - Carica stato personaggio
            │
            ▼
4. RAG SYSTEM cerca contesto rilevante
   - Embedding della query
   - Ricerca in Qdrant
   - Recupera top-3 chunk
            │
            ▼
5. CHARACTER ENGINE processa
   - Applica personalità
   - Considera stato emotivo
   - Considera memoria
            │
            ▼
6. PROMPT BUILDER costruisce il prompt
   ┌────────────────────────────────────┐
   │ System: Sei Gandalf il Grigio...  │
   │ Context: [chunk RAG]              │
   │ History: [ultimi messaggi]        │
   │ User: Parlami dell'Anello         │
   └────────────────────────────────────┘
            │
            ▼
7. LLM MANAGER invia a Grok
   - Streaming response
            │
            ▼
8. RISPOSTA STREAMING → FRONTEND
   "L'Anello... è un artefatto... terribile..."
            │
            ▼
9. POST-PROCESSING
   - Aggiorna stato emotivo
   - Salva in memoria
   - Aggiorna conversazione DB
            │
            ▼
10. FRONTEND mostra risposta completa
    con indicatore emotivo
```

---

## ⚙️ Configurazione Avanzata

### File .env completo:

```env
# === APP ===
APP_NAME=fantasy-world-rag
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# === SERVER ===
HOST=0.0.0.0
PORT=8000
WORKERS=4

# === DATABASE ===
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fantasy_world
POSTGRES_USER=fantasy_user
POSTGRES_PASSWORD=your-secure-password

# === REDIS ===
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
CACHE_TTL=3600

# === QDRANT ===
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=fantasy_characters
VECTOR_DIMENSION=1536

# === LLM ===
DEFAULT_CHAT_PROVIDER=grok
DEFAULT_ANALYSIS_PROVIDER=deepseek
GROK_API_KEY=xai-your-key
DEEPSEEK_API_KEY=your-key
OPENAI_API_KEY=sk-your-key  # fallback

# === RAG ===
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
RAG_MIN_RELEVANCE=0.7

# === CHARACTER ===
MEMORY_MAX_EPISODIC=1000
MEMORY_DECAY_RATE=0.1
EMOTION_INFLUENCE=0.3

# === SECURITY ===
SECRET_KEY=your-256-bit-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# === CORS ===
CORS_ORIGINS=["http://localhost:5173"]
```

### Tuning per performance:

| Scenario | Modifica |
|----------|----------|
| **Più veloce** | `RAG_TOP_K=3`, usa solo `grok-4-fast` |
| **Più accurato** | `RAG_TOP_K=7`, `RAG_MIN_RELEVANCE=0.8` |
| **Meno memoria** | `MEMORY_MAX_EPISODIC=500` |
| **Più emotivo** | `EMOTION_INFLUENCE=0.5` |
| **Più economico** | `DEFAULT_CHAT_PROVIDER=deepseek` |

---

## 📚 Risorse aggiuntive

- [Guida Installazione](GUIDA_INSTALLAZIONE.md)
- [Guida Utente](GUIDA_UTENTE.md)
- [Guida Admin](GUIDA_ADMIN.md)
- [Configurazione LLM](LLM_CONFIGURATION.md)
- [API Reference](API_REFERENCE.md)

---

*Fantasy World RAG - Architettura v1.0*
