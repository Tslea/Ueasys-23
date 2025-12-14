# 🔧 Guida Amministratore - Fantasy World RAG

> Come creare, gestire e configurare personaggi nel sistema

---

## 📋 Indice

1. [Accesso al Pannello Admin](#-accesso-al-pannello-admin)
2. [Creare un Personaggio](#-creare-un-personaggio)
3. [Importare da Documento](#-importare-da-documento)
4. [Struttura del Personaggio](#-struttura-del-personaggio)
5. [Gestire i Personaggi](#-gestire-i-personaggi)
6. [Import/Export YAML](#-importexport-yaml)
7. [Monitoraggio e Statistiche](#-monitoraggio-e-statistiche)
8. [Best Practices](#-best-practices)

---

## 🔐 Accesso al Pannello Admin

### Come accedere:

1. Dalla home page, clicca su **"Admin"** in alto a destra
2. Oppure vai direttamente a: `http://localhost:5173/admin`

### Interfaccia Admin:

```
┌─────────────────────────────────────────────────────┐
│  🔧 Pannello Amministrazione              [← Home]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [+ Nuovo Personaggio]  [📤 Importa YAML]           │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Personaggi (3)                              │   │
│  ├─────────────────────────────────────────────┤   │
│  │ 🧙‍♂️ Gandalf     Mago    [✏️] [📊] [🗑️]     │   │
│  │ 🐉 Smaug        Drago   [✏️] [📊] [🗑️]     │   │
│  │ 🧝 Galadriel    Elfa    [✏️] [📊] [🗑️]     │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Azioni disponibili:

| Icona | Azione |
|-------|--------|
| **+** | Crea nuovo personaggio |
| **📤** | Importa da file YAML |
| **✏️** | Modifica personaggio |
| **📊** | Vedi statistiche |
| **🗑️** | Elimina personaggio |

---

## ➕ Creare un Personaggio

### Metodo 1: Creazione Manuale

Clicca **"+ Nuovo Personaggio"** e compila il form:

#### Sezione 1: Informazioni Base

```
┌─────────────────────────────────────────────────────┐
│  INFORMAZIONI BASE                                  │
├─────────────────────────────────────────────────────┤
│  Nome*:        [Gandalf                    ]        │
│  Titolo:       [Il Grigio                  ]        │
│  Descrizione*: [Un potente mago, uno dei   ]        │
│                [Istari inviati nella Terra ]        │
│                [di Mezzo...                ]        │
│                                                     │
│  Razza*:       [Maia          ▼]                    │
│  Classe:       [Mago          ▼]                    │
│  Età:          [2000+         ] (opzionale)         │
│  Allineamento: [Legale Buono  ▼]                    │
│                                                     │
│  Avatar URL:   [https://...   ]                     │
└─────────────────────────────────────────────────────┘
```

**Campi obbligatori**: Nome, Descrizione, Razza

#### Sezione 2: Personalità

```
┌─────────────────────────────────────────────────────┐
│  PERSONALITÀ                                        │
├─────────────────────────────────────────────────────┤
│  Tratti (chi è):                                    │
│  [Saggio] [Misterioso] [Protettivo] [+ Aggiungi]   │
│                                                     │
│  Valori (cosa ritiene importante):                  │
│  [Amicizia] [Libertà] [Speranza] [+ Aggiungi]      │
│                                                     │
│  Paure (cosa teme):                                 │
│  [Fallimento] [Corruzione] [+ Aggiungi]            │
│                                                     │
│  Desideri (cosa vuole):                             │
│  [Sconfiggere il male] [Proteggere i deboli]       │
│                                                     │
│  Stile di parlare:                                  │
│  [Usa metafore, parla in modo solenne ma           ]│
│  [a volte con umorismo sottile. Ama i proverbi.    ]│
│                                                     │
│  Quirk/Abitudini:                                   │
│  [Fuma la pipa] [Arriva sempre al momento giusto]  │
└─────────────────────────────────────────────────────┘
```

#### Sezione 3: Background (Storia)

```
┌─────────────────────────────────────────────────────┐
│  BACKGROUND                                         │
├─────────────────────────────────────────────────────┤
│  Origine:                                           │
│  [Valinor, il Reame Beato oltre il mare            ]│
│                                                     │
│  Storia:                                            │
│  [Gandalf è uno degli Istari, spiriti Maiar        ]│
│  [inviati dai Valar nella Terra di Mezzo per       ]│
│  [contrastare Sauron. Ha viaggiato per secoli,     ]│
│  [aiutando i Popoli Liberi...                      ]│
│                                                     │
│  Eventi Chiave:                                     │
│  [Arrivo nella Terra di Mezzo] [+ Aggiungi]        │
│  [Viaggio con Bilbo a Erebor]                      │
│  [Caduta a Khazad-dûm]                             │
│  [Ritorno come Gandalf il Bianco]                  │
│                                                     │
│  Relazioni:                                         │
│  Frodo:    [Protettore e guida           ]         │
│  Saruman:  [Ex-alleato, ora nemico       ]         │
│  Bilbo:    [Vecchio amico                ]         │
│  [+ Aggiungi relazione]                             │
└─────────────────────────────────────────────────────┘
```

#### Sezione 4: Conoscenze

```
┌─────────────────────────────────────────────────────┐
│  CONOSCENZE                                         │
├─────────────────────────────────────────────────────┤
│  Aree di expertise:                                 │
│  [Magia del fuoco] [Storia della Terra di Mezzo]   │
│  [Lingue antiche] [Anelli del Potere]              │
│                                                     │
│  Segreti che conosce:                               │
│  [La vera natura dell'Anello]                      │
│  [I passaggi segreti di Moria]                     │
│                                                     │
│  Credenze:                                          │
│  [Anche i più piccoli possono cambiare il destino] │
│  [La pietà è una virtù]                            │
│                                                     │
│  Opinioni:                                          │
│  Su Sauron:    [Il male assoluto, va distrutto]    │
│  Sugli Hobbit: [Creature sorprendenti e resilienti]│
└─────────────────────────────────────────────────────┘
```

#### Sezione 5: Comportamento

```
┌─────────────────────────────────────────────────────┐
│  COMPORTAMENTO                                      │
├─────────────────────────────────────────────────────┤
│  Obiettivi:                                         │
│  [Distruggere l'Anello] [Proteggere la Terra di Mezzo]│
│                                                     │
│  Motivazioni:                                       │
│  [Senso del dovere] [Amore per i Popoli Liberi]    │
│                                                     │
│  Reazioni tipiche:                                  │
│  Alla minaccia:  [Affronta con coraggio           ]│
│  All'ingiustizia:[Si arrabbia, agisce             ]│
│  Alla tristezza: [Offre saggezza e conforto       ]│
│                                                     │
│  Pattern decisionali:                               │
│  [Valuta prima, agisce poi]                        │
│  [Preferisce guidare piuttosto che comandare]      │
└─────────────────────────────────────────────────────┘
```

---

## 📄 Importare da Documento

### Funzionalità AI-Assisted

Puoi caricare un documento (PDF, TXT, DOCX, MD) e l'AI estrarrà automaticamente le informazioni del personaggio!

### Come funziona:

1. Clicca **"Carica Documento"** o trascina il file
2. Il sistema usa **DeepSeek** per analizzare il testo
3. Estrae automaticamente:
   - Nome e descrizione
   - Tratti della personalità
   - Storia e background
   - Relazioni
   - Conoscenze

### Esempio:

**Input** (testo da un libro):
```
Gandalf il Grigio era un vecchio dall'aspetto canuto, con un lungo 
cappello a punta blu, un mantello grigio e un bastone nodoso. 
I suoi occhi brillavano di una luce particolare, come se 
nascondessero segreti di ere passate. Era noto per i suoi 
fuochi d'artificio e per arrivare sempre "precisamente quando 
intendeva arrivare"...
```

**Output** (estratto dall'AI):
```json
{
  "name": "Gandalf",
  "description": "Un vecchio mago dall'aspetto canuto...",
  "personality": {
    "traits": ["misterioso", "saggio", "puntuale a modo suo"],
    "quirks": ["crea fuochi d'artificio", "arriva quando vuole"]
  }
}
```

### Dopo l'estrazione:

1. **Rivedi** i dati estratti
2. **Modifica** se necessario (l'AI non è perfetta!)
3. **Completa** i campi mancanti
4. **Salva** il personaggio

---

## 📊 Struttura del Personaggio

### Schema completo (YAML):

```yaml
# Identificazione
id: "gandalf-001"
name: "Gandalf"
title: "Il Grigio"
description: "Un potente Istar, mago e consigliere..."

# Caratteristiche base
race: "Maia"
class_type: "Mago"
age: 2000
alignment: "Legale Buono"
avatar_url: "https://example.com/gandalf.jpg"

# Personalità
personality:
  traits:
    - "saggio"
    - "misterioso"
    - "protettivo"
    - "paziente"
  values:
    - "amicizia"
    - "libertà"
    - "speranza"
  fears:
    - "fallimento della missione"
    - "corruzione del potere"
  desires:
    - "sconfiggere Sauron"
    - "proteggere i Popoli Liberi"
  speaking_style: |
    Parla in modo solenne ma con occasionale umorismo.
    Usa metafore e proverbi. A volte è criptico.
  quirks:
    - "fuma la pipa"
    - "arriva sempre al momento giusto"
    - "ama i fuochi d'artificio"

# Background
background:
  origin: "Valinor, il Reame Beato"
  history: |
    Gandalf è uno degli Istari, spiriti Maiar inviati 
    dai Valar nella Terra di Mezzo nel Terzo Era per
    contrastare la minaccia di Sauron...
  key_events:
    - "Arrivo nella Terra di Mezzo (circa 1000 T.E.)"
    - "Viaggio a Erebor con Thorin e Bilbo"
    - "Scoperta della vera natura dell'Anello"
    - "Caduta nel Khazad-dûm"
    - "Ritorno come Gandalf il Bianco"
  relationships:
    Frodo: "Portatore dell'Anello, lo guida e protegge"
    Bilbo: "Vecchio amico, lo scelse per l'avventura"
    Saruman: "Capo dell'ordine, traditore"
    Aragorn: "Alleato fidato, futuro Re"
    Galadriel: "Amica e alleata tra gli Elfi"

# Conoscenze
knowledge:
  expertise:
    - "Magia del fuoco"
    - "Storia della Terra di Mezzo"
    - "Lingue antiche (Quenya, Sindarin, Linguaggio Nero)"
    - "Anelli del Potere"
  secrets:
    - "La vera natura dell'Unico Anello"
    - "L'ubicazione dell'ingresso segreto di Erebor"
    - "Possiede Narya, l'Anello del Fuoco"
  beliefs:
    - "Anche il più piccolo può cambiare il corso del futuro"
    - "La pietà di Bilbo governa il destino di molti"
    - "Il male non può creare, solo corrompere"
  opinions:
    Sauron: "Il nemico da sconfiggere, il male incarnato"
    Hobbit: "Creature sorprendenti, più forti di quanto sembrano"
    Uomini: "Fragili ma capaci di grande nobiltà"
    Anello: "Deve essere distrutto, non può essere usato per il bene"

# Comportamento
behavior:
  goals:
    - "Distruggere l'Unico Anello"
    - "Sconfiggere Sauron"
    - "Proteggere i Popoli Liberi"
  motivations:
    - "Senso del dovere verso i Valar"
    - "Amore per la Terra di Mezzo"
    - "Speranza in un futuro migliore"
  reactions:
    minaccia: "Affronta con coraggio, usa la magia se necessario"
    tristezza: "Offre parole di saggezza e conforto"
    ingiustizia: "Si arrabbia, la voce diventa tuono"
    stupidità: "Paziente ma può perdere la calma"
  decision_patterns:
    - "Valuta tutte le opzioni prima di agire"
    - "Preferisce guidare piuttosto che comandare"
    - "Crede nel libero arbitrio"
    - "Interviene solo quando necessario"

# Metadati (automatici)
metadata:
  created_at: "2024-12-13T10:00:00Z"
  updated_at: "2024-12-13T10:00:00Z"
  created_by: "admin"
  version: 1
  status: "active"
```

---

## 🔄 Import/Export YAML

### Esportare un personaggio:

1. Nel pannello Admin, trova il personaggio
2. Clicca **"⋮"** (menu) → **"Esporta YAML"**
3. Salva il file `.yaml`

### Importare un personaggio:

1. Clicca **"📤 Importa YAML"**
2. Seleziona il file `.yaml`
3. Rivedi e conferma
4. Il personaggio viene creato

### Utilità:

- **Backup**: Esporta tutti i personaggi
- **Condivisione**: Condividi personaggi con altri
- **Versionamento**: Tieni traccia delle modifiche
- **Migrazione**: Sposta personaggi tra sistemi

---

## 📈 Monitoraggio e Statistiche

### Dashboard statistiche:

```
┌─────────────────────────────────────────────────────┐
│  📊 Statistiche: Gandalf                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Conversazioni totali:     147                      │
│  Messaggi scambiati:       2,341                    │
│  Utenti unici:             23                       │
│  Tempo medio risposta:     1.2s                     │
│                                                     │
│  Stato emotivo medio:      😊 Positivo (72%)        │
│                                                     │
│  Argomenti più discussi:                            │
│  ████████████ Anello (34%)                         │
│  ████████   Hobbits (24%)                          │
│  ██████    Magia (18%)                             │
│  ████      Sauron (12%)                            │
│                                                     │
│  Andamento conversazioni:                           │
│       ╭─────────────────────╮                      │
│  50   │          ╱╲        │                      │
│  25   │    ╱╲  ╱  ╲  ╱    │                      │
│   0   │╲╱╱    ╲╱    ╲╱     │                      │
│       ╰─────────────────────╯                      │
│        Lun Mar Mer Gio Ven Sab Dom                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Metriche disponibili:

| Metrica | Descrizione |
|---------|-------------|
| **Conversazioni** | Numero totale di chat |
| **Messaggi** | Messaggi totali scambiati |
| **Utenti** | Utenti unici che hanno chattato |
| **Tempo risposta** | Velocità media di risposta |
| **Stato emotivo** | Distribuzione emozioni |
| **Argomenti** | Topic più frequenti |
| **Soddisfazione** | Rating utenti (se abilitato) |

---

## ✨ Best Practices

### Creare personaggi efficaci:

#### 1. **Personalità coerente**
```
✅ Buono:
traits: ["coraggioso", "impulsivo", "leale"]
# Coerente: un guerriero impulsivo ma leale

❌ Evita:
traits: ["codardo", "coraggioso", "cauto", "impulsivo"]
# Contraddittorio: non può essere codardo E coraggioso
```

#### 2. **Background dettagliato**
```
✅ Buono:
history: |
  Nato nel villaggio di Millbrook, figlio di un fabbro.
  A 15 anni vide il villaggio bruciato dai briganti.
  Giurò vendetta e si unì all'esercito del Re.
  Dopo 10 anni di servizio, divenne capitano...

❌ Evita:
history: "È un guerriero."
# Troppo generico, l'AI non ha contesto
```

#### 3. **Stile di parlare specifico**
```
✅ Buono:
speaking_style: |
  Parla in modo formale con i nobili, più rilassato con i compagni.
  Usa espressioni militari ("tenere la posizione", "all'attacco").
  Quando è arrabbiato, la voce diventa un ringhio basso.
  Ha un accento del Nord, dice "aye" invece di "sì".

❌ Evita:
speaking_style: "Parla normalmente"
# Non dà indicazioni all'AI
```

#### 4. **Relazioni con contesto**
```
✅ Buono:
relationships:
  Re Aldric: |
    Il suo signore. Lo rispetta ma non sempre è d'accordo
    con le sue decisioni. Gli salvò la vita una volta.
  Mara: |
    La sua ex-moglie. Il matrimonio finì male, ma
    mantengono rispetto reciproco. Lei ora è una guaritrice.

❌ Evita:
relationships:
  Re: "il re"
  Donna: "una donna"
# Troppo vago
```

#### 5. **Conoscenze appropriate**
```
✅ Buono:
expertise:
  - "Tattica militare"
  - "Manutenzione delle armi"
  - "Sopravvivenza in battaglia"
  - "Storia delle guerre del Regno"

# Un guerriero sa queste cose

❌ Evita:
expertise:
  - "Tutto sulla magia"
  - "Programmazione Python"
  - "Storia moderna"

# Un guerriero medievale NON sa queste cose
```

### Errori comuni da evitare:

| Errore | Problema | Soluzione |
|--------|----------|-----------|
| **Troppo generico** | Risposte banali | Aggiungi dettagli specifici |
| **Contraddizioni** | Comportamento incoerente | Rivedi la coerenza |
| **Meta-conoscenza** | Sa cose che non dovrebbe | Limita le expertise |
| **Nessuna debolezza** | Personaggio piatto | Aggiungi paure e difetti |
| **Troppe info** | Confonde l'AI | Sii conciso ma specifico |

---

## 🔒 Sicurezza e Moderazione

### Contenuti filtrati:

Il sistema blocca automaticamente:
- Contenuti violenti espliciti
- Contenuti sessualmente espliciti
- Discorsi d'odio
- Informazioni personali reali

### Log delle conversazioni:

Come admin puoi:
- Vedere i log delle chat
- Identificare abusi
- Bannare utenti problematici
- Esportare report

---

## 📝 Checklist nuovo personaggio

Prima di pubblicare un personaggio, verifica:

- [ ] Nome e descrizione compilati
- [ ] Almeno 3 tratti della personalità
- [ ] Background con storia significativa
- [ ] Almeno 3 relazioni definite
- [ ] Stile di parlare descritto
- [ ] Expertise coerenti con il personaggio
- [ ] Nessuna contraddizione evidente
- [ ] Avatar caricato (opzionale ma consigliato)
- [ ] Test conversazione effettuato

---

*Per informazioni tecniche dettagliate, vedi [Documentazione Tecnica](ARCHITETTURA_SISTEMA.md)*
