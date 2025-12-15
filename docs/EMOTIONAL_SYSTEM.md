# Sistema Emotivo Avanzato

## Panoramica

Il sistema emotivo avanzato è basato su moderne teorie neuroscientifiche e psicologiche, implementando un modello multi-dimensionale delle emozioni.

## Fondamenti Teorici

### 1. Modello Dimensionale (Russell's Circumplex)

Le emozioni sono rappresentate su tre dimensioni continue:

| Dimensione | Range | Descrizione |
|------------|-------|-------------|
| **Valence** | -1 → +1 | Spiacevole ↔ Piacevole |
| **Arousal** | -1 → +1 | Disattivato ↔ Attivato |
| **Dominance** | -1 → +1 | Sottomesso ↔ Dominante |

### 2. Sistemi Affettivi di Panksepp

Basato sulle neuroscienze affettive di Jaak Panksepp, il sistema implementa 7 circuiti emotivi primari conservati evolutivamente:

| Sistema | Funzione | Trigger Esempi |
|---------|----------|----------------|
| **SEEKING** | Curiosità, esplorazione, desiderio | "cosa", "perché", "dimmi" |
| **RAGE** | Frustrazione, rabbia | "nemico", "ingiusto", "odio" |
| **FEAR** | Minaccia, ansia | "pericolo", "attacco", "morte" |
| **LUST** | Attrazione (contesti romantici) | - |
| **CARE** | Cura, attaccamento, empatia | "aiuto", "proteggere", "amico" |
| **PANIC/GRIEF** | Separazione, dolore, solitudine | "perso", "morto", "addio" |
| **PLAY** | Gioco, umorismo, legame sociale | "divertente", "gioco", "ridere" |

### 3. Teoria dell'Appraisal (Scherer)

L'analisi cognitiva degli stimoli determina la risposta emotiva:

```
Messaggio → Appraisal Cognitivo → Emozione

Dimensioni dell'Appraisal:
- Novità: Quanto è inaspettato?
- Piacevolezza: È intrinsecamente piacevole?
- Rilevanza per gli obiettivi: È importante?
- Conducibilità agli obiettivi: Aiuta o ostacola?
- Urgenza: Richiede risposta immediata?
- Controllo: Posso influenzare la situazione?
- Potere: Ho le risorse per affrontarla?
- Adattamento: Posso adattarmi al risultato?
```

### 4. Emozioni Costruite (Barrett)

Le etichette emotive sono costruzioni che il cervello crea da:
- Core affect (valence + arousal)
- Contesto situazionale
- Esperienze passate
- Predizioni

## Implementazione

### File Principali

```
src/core/character/
├── advanced_emotions.py    # Sistema emotivo avanzato
├── emotional_state.py      # Sistema emotivo classico (backup)
└── character_engine.py     # Integrazione nel motore personaggio
```

### Classi Chiave

#### `AffectiveDimensions`
Core affect dimensionale con operazioni di blend e decay.

```python
@dataclass
class AffectiveDimensions:
    valence: float = 0.0      # -1 to +1
    arousal: float = 0.0      # -1 to +1
    dominance: float = 0.0    # -1 to +1
```

#### `AdvancedEmotionalState`
Stato emotivo completo con appraisal e sistemi affettivi.

```python
class AdvancedEmotionalState:
    character_id: str
    current_affect: AffectiveDimensions
    baseline_affect: AffectiveDimensions
    system_activations: Dict[str, float]  # Panksepp systems
    emotional_inertia: float              # Resistenza al cambiamento
```

### Flusso di Elaborazione

```
1. Messaggio utente
       ↓
2. appraise_message()
   - Pattern matching per keyword
   - Calcolo dimensioni appraisal
   - Attivazione sistemi affettivi
       ↓
3. update_affect()
   - Integrazione appraisal + sistemi
   - Applicazione inerzia emotiva
       ↓
4. decay()
   - Ritorno graduale al baseline
   - Regolazione omeostatica
       ↓
5. get_emotion_label()
   - Costruzione etichetta emotiva
   - Calcolo confidenza
```

## Configurazione

### Flag di Attivazione

In `character_engine.py`:

```python
USE_ADVANCED_EMOTIONS = True  # Abilita sistema avanzato
```

### Personalizzazione Baseline

Il baseline emotivo è derivato dall'archetipo del personaggio:

| Archetipo | Valence | Arousal | Dominance |
|-----------|---------|---------|-----------|
| hero/warrior | 0.0 | +0.2 | +0.4 |
| sage/mentor | +0.2 | 0.0 | +0.3 |
| trickster | +0.3 | +0.3 | 0.0 |
| dragon/villain | -0.2 | 0.0 | +0.5 |

### Inerzia Emotiva

Controlla quanto rapidamente cambiano le emozioni:
- `0.0`: Nessuna resistenza (cambia immediatamente)
- `0.5`: Resistenza moderata
- `1.0`: Massima resistenza (quasi immutabile)

## API Frontend

### WebSocket Response

```json
{
  "type": "response",
  "emotional_state": "curiosity",
  "emotion_intensity": 0.65,
  "advanced_emotions": {
    "emotion": "curiosity",
    "emotion_confidence": 0.82,
    "valence": 0.35,
    "arousal": 0.48,
    "dominance": 0.22,
    "dominant_system": "seeking",
    "system_intensity": 0.6,
    "all_systems": {
      "seeking": 0.6,
      "care": 0.2,
      "play": 0.15
    }
  }
}
```

### Componente React

```tsx
import { AdvancedSoulState } from '@/components/chat/AdvancedSoulState'

<AdvancedSoulState
  emotionalState={{
    emotion: "curiosity",
    intensity: 0.65,
    advanced: advancedEmotionsData
  }}
  expanded={true}
/>
```

## Estensioni Future

1. **Analisi LLM-based**: Usare LLM per sentiment analysis più sofisticata
2. **Contagio Emotivo**: Propagazione emozioni tra personaggi
3. **Memoria Emotiva**: Ricordare pattern emotivi ricorrenti
4. **Regolazione Emotiva**: Strategie di coping attive
5. **Personalità-Emozione**: Interazione tratti personalità con emozioni

## Riferimenti Scientifici

- Panksepp, J. (2011). *Affective Neuroscience*
- Barrett, L.F. (2017). *How Emotions Are Made*
- Russell, J.A. (1980). A Circumplex Model of Affect
- Scherer, K.R. (2009). Component Process Model
- Lazarus, R.S. (1991). Emotion and Adaptation
