# LLM Configuration Guide

Questa guida spiega come configurare e utilizzare il sistema LLM centralizzato.

## 🎯 Configurazione Rapida

### Provider Raccomandati

| Task | Provider | Model | Perché |
|------|----------|-------|--------|
| Chat/Risposte | **Grok** | `grok-4-fast` | Veloce, economico, ottimo per conversazioni |
| Analisi/Estrazione | **DeepSeek** | `deepseek-chat` | V3.2 - Ragionamento profondo, basso costo |
| Agenti Complessi | **DeepSeek** | `deepseek-reasoner` | V3.2 - Chain-of-Thought reasoning |

### Setup Minimo

```bash
# Nel tuo .env
GROK_API_KEY=xai-your-key-here
DEEPSEEK_API_KEY=your-deepseek-key

# Questi sono i default, puoi cambiarli
DEFAULT_CHAT_PROVIDER=grok
DEFAULT_ANALYSIS_PROVIDER=deepseek
```

## 📖 Utilizzo

### Uso Semplice (Raccomandato)

```python
from src.llm import get_chat_llm, get_analysis_llm, get_agent_llm

# Per chat real-time (usa Grok)
chat_llm = get_chat_llm()
response = await chat_llm.generate("Dimmi chi sei")

# Per analisi/estrazione (usa DeepSeek)
analysis_llm = get_analysis_llm()
response = await analysis_llm.generate("Analizza questo testo...")

# Per agenti con reasoning complesso (DeepSeek Reasoner)
agent_llm = get_agent_llm()
response = await agent_llm.generate("Decidi cosa fare...")
```

### Uso con LLMManager

```python
from src.llm import LLMManager, ProviderType, LLMConfig

# Ottenere un provider specifico
grok = LLMManager.get_provider("grok")
deepseek = LLMManager.get_provider(ProviderType.DEEPSEEK)

# Con configurazione custom
custom_config = LLMConfig(
    model="grok-4",  # Modello più potente
    temperature=0.9,
    max_tokens=8192,
)
grok_creative = LLMManager.get_provider("grok", custom_config)

# Cambiare provider default a runtime
LLMManager.set_default_chat_provider("deepseek")
```

### Chat con History

```python
from src.llm import get_chat_llm, Message

llm = get_chat_llm()

messages = [
    Message(role="system", content="Sei Gandalf il Grigio"),
    Message(role="user", content="Chi sei?"),
]

response = await llm.generate_chat(messages)
print(response.content)
```

### Streaming

```python
from src.llm import get_chat_llm

llm = get_chat_llm()

async for chunk in llm.stream_generate("Raccontami una storia"):
    print(chunk, end="", flush=True)
```

## 💰 Costi Stimati

### Grok (xAI)
| Model | Input/1K | Output/1K | Speed |
|-------|----------|-----------|-------|
| grok-4-fast | $0.00005 | $0.00025 | ⚡ Fastest |
| grok-4 | $0.0003 | $0.0015 | 🎯 Most capable |
| grok-3-fast | $0.00003 | $0.00015 | ⚡⚡ Fastest |

### DeepSeek (V3.2)
| Model | Input/1K | Output/1K | Best For |
|-------|----------|-----------|----------|
| deepseek-chat | $0.00014 | $0.00028 | 📊 Analysis, Extraction |
| deepseek-reasoner | $0.00055 | $0.00219 | 🧠 Complex reasoning, Chain-of-Thought |

### Stima Mensile

Con 10,000 messaggi/mese (avg 500 tokens ciascuno):
- **Solo Grok Fast**: ~$2.50/mese
- **Solo DeepSeek Chat**: ~$2.10/mese
- **Mix (80% Grok, 20% DeepSeek)**: ~$2.40/mese

## 🔄 Switch Provider Facile

### A Runtime

```python
from src.llm import LLMManager

# Temporaneamente usa OpenAI per il chat
LLMManager.set_default_chat_provider("openai")

# Torna a Grok
LLMManager.set_default_chat_provider("grok")
```

### Via Environment

```bash
# .env
DEFAULT_CHAT_PROVIDER=openai
DEFAULT_ANALYSIS_PROVIDER=anthropic
```

## 🔧 Aggiungere Nuovi Provider

1. Crea `src/llm/nuovo_provider.py`:

```python
from src.llm.base_provider import BaseLLMProvider, LLMConfig

class NuovoProvider(BaseLLMProvider):
    def __init__(self, config: LLMConfig = None):
        if config is None:
            config = LLMConfig(model="default-model")
        super().__init__(config)
        # Setup...
    
    async def generate(self, prompt: str, **kwargs) -> str:
        # Implementazione...
        pass
```

2. Registra in `src/llm/llm_manager.py`:

```python
class ProviderType(str, Enum):
    NUOVO = "nuovo"  # Aggiungi

# Nel metodo _get_provider_class:
elif provider_type == ProviderType.NUOVO:
    from src.llm.nuovo_provider import NuovoProvider
    return NuovoProvider
```

3. Aggiungi settings in `src/config/settings.py`:

```python
nuovo_api_key: str = Field(default="", description="Nuovo API key")
nuovo_model: str = Field(default="default-model", description="Nuovo model")
```

## 📋 Best Practices

1. **Usa le funzioni helper** (`get_chat_llm()`, etc.) invece di istanziare provider direttamente
2. **Non hardcodare provider**: usa sempre le configurazioni
3. **Logga l'uso**: i provider loggano automaticamente le chiamate
4. **Gestisci errori**: i provider sollevano eccezioni chiare su errori API
5. **Cache**: i provider sono cached, non crearne multipli inutilmente

## 🐛 Troubleshooting

### "API key not set"
```bash
# Verifica che le chiavi siano nel .env
echo $GROK_API_KEY
echo $DEEPSEEK_API_KEY
```

### "Model not found"
Controlla la lista modelli supportati per ogni provider.

### Timeout
```python
config = LLMConfig(timeout=60)  # Aumenta timeout
llm = get_chat_llm(config)
```

### Rate Limiting
I provider gestiscono automaticamente retry con backoff esponenziale.
