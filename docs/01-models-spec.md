# Mascate - Especificacoes de Modelos

**Versao:** 1.0  
**Status:** Aprovado para Implementacao

Este documento define exatamente quais modelos usar, suas quantizacoes, backends e alocacao de hardware.

---

## 1. Tabela Mestra de Modelos

| Componente         | Modelo                    | Backend      | Quantizacao | Alocacao | Consumo      |
| :----------------- | :------------------------ | :----------- | :---------- | :------- | :----------- |
| **LLM**            | IBM Granite 4.0 Hybrid 1B | llama.cpp    | Q8_0        | 100% GPU | ~1.3 GB VRAM |
| **STT**            | Whisper Large v3          | whisper.cpp  | Q5_K_M      | 100% CPU | ~2.2 GB RAM  |
| **TTS**            | Piper (pt_BR Custom)      | piper-tts    | ONNX High   | CPU      | ~300 MB RAM  |
| **RAG Embeddings** | BAAI BGE-M3               | ONNX Runtime | FP16        | CPU      | ~1.5 GB RAM  |
| **Banco Vetorial** | Qdrant (Local Mode)       | Rust/Python  | N/A         | RAM/SSD  | Variavel     |
| **VAD**            | Silero VAD v5             | ONNX         | Padrao      | CPU      | ~50 MB RAM   |
| **Wake Word**      | openWakeWord              | ONNX/tflite  | INT8        | CPU      | ~150 MB RAM  |

---

## 2. LLM - IBM Granite 4.0 Hybrid 1B

### 2.1. Por que Granite?

- **Arquitetura Mamba-2:** Consumo de memoria **linear** (nao quadratico) para contexto
- **Foco em Tool Use:** Treinado para comandos tecnicos e enterprise/coding
- **Tamanho:** 1B parametros - cabe com folga em 4GB VRAM

### 2.2. Especificacoes

| Propriedade | Valor                                      |
| :---------- | :----------------------------------------- |
| Arquivo     | `granite-4.0-hybrid-1b-instruct.Q8_0.gguf` |
| Quantizacao | Q8_0 (quase sem perda de qualidade)        |
| Tamanho     | ~1.3 GB                                    |
| Contexto    | Janela deslizante de 2048 tokens           |
| Velocidade  | >80 tokens/s na GTX 1650                   |

### 2.3. Por que Q8_0?

Optamos por Q8 (alta precisao) em vez de Q4 porque:

- O modelo e pequeno (1B), entao temos VRAM de sobra
- Maximiza inteligencia e qualidade das respostas
- Nao ha necessidade de comprimir mais

### 2.4. Integracao

```python
# Backend: llama.cpp via llama-cpp-python
from llama_cpp import Llama

llm = Llama(
    model_path="models/granite-4.0-hybrid-1b-instruct.Q8_0.gguf",
    n_gpu_layers=-1,  # Todas as camadas na GPU
    n_ctx=2048,
    verbose=False
)
```

---

## 3. STT - Whisper Large v3

### 3.1. Por que Whisper Large?

- **Melhor compreensao** de PT-BR, sotaques e termos tecnicos
- **Code-switching:** Entende mistura portugues/ingles
- **Streaming:** Suporte a transcricao em tempo real

### 3.2. Especificacoes

| Propriedade | Valor                                             |
| :---------- | :------------------------------------------------ |
| Arquivo     | `ggml-large-v3.bin` ou `ggml-large-v3-q5_k_m.bin` |
| Quantizacao | Q5_K_M (equilibrio velocidade/qualidade)          |
| Tamanho     | ~2.2 GB                                           |
| Threads     | 4-6 threads CPU                                   |
| Modo        | Streaming real-time                               |

### 3.3. Por que Q5_K_M?

- Perda de precisao imperceptivel para audio
- Roda muito mais leve na CPU que FP16
- Libera GPU completamente para o LLM

### 3.4. Integracao

```python
# Backend: whisper.cpp via pywhispercpp ou binding C
# Configuracao para streaming
whisper_config = {
    "model": "models/ggml-large-v3-q5_k_m.bin",
    "language": "pt",
    "threads": 4,
    "translate": False,
    "no_timestamps": True
}
```

---

## 4. TTS - Piper (VITS)

### 4.1. Por que Piper?

- **Baixissima latencia:** First Audio Packet em <200ms
- **Fine-tuning:** Capacidade de treinar vozes customizadas
- **Qualidade:** Alta fidelidade de prosodia com datasets pequenos (~40 min)

### 4.2. Especificacoes

| Propriedade | Valor                                     |
| :---------- | :---------------------------------------- |
| Arquivo     | `pt_BR-custom-high.onnx` + `.json` config |
| Qualidade   | High (melhor prosodia)                    |
| Tamanho     | ~300 MB                                   |
| Threads     | 1 thread CPU                              |
| Sample Rate | 22050 Hz                                  |

### 4.3. Vozes Planejadas

| Nome   | Descricao                    | Status                 |
| :----- | :--------------------------- | :--------------------- |
| Padrao | Voz neutra pt_BR             | Usar modelo base Piper |
| Ariano | Sotaque nordestino inspirado | Fine-tuning planejado  |
| Painho | Voz calorosa regional        | Fine-tuning planejado  |

### 4.4. Integracao

```python
# Backend: piper-tts
import piper

voice = piper.PiperVoice.load("models/pt_BR-custom-high.onnx")
audio = voice.synthesize("Ola, como posso ajudar?")
```

---

## 5. RAG - BGE-M3 + Qdrant

### 5.1. Por que BGE-M3?

- **Busca Hibrida:** Combina semantica (densa) + keywords (esparsa)
- **Multilingual:** Estado da arte em portugues
- **Contexto:** Janelas de ate 8192 tokens

### 5.2. Especificacoes BGE-M3

| Propriedade | Valor                 |
| :---------- | :-------------------- |
| Modelo      | BAAI/bge-m3           |
| Formato     | ONNX ou PyTorch       |
| Precisao    | FP16                  |
| Dimensao    | 1024 (dense) + sparse |
| Tamanho     | ~1.5 GB               |

### 5.3. Por que Qdrant?

- **Busca Hibrida Nativa:** Suporta saida do BGE-M3 diretamente
- **Local Mode:** Roda sem Docker, apenas como biblioteca Python
- **Performance:** Rust backend, extremamente rapido

### 5.4. Especificacoes Qdrant

| Propriedade  | Valor                      |
| :----------- | :------------------------- |
| Modo         | Local (in-process)         |
| Persistencia | SSD (`~/.mascate/qdrant/`) |
| Indice       | HNSW + Sparse              |

### 5.5. Integracao

```python
from qdrant_client import QdrantClient
from FlagEmbedding import BGEM3FlagModel

# Embeddings
model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)

# Qdrant local
client = QdrantClient(path="~/.mascate/qdrant")
```

---

## 6. VAD - Silero VAD v5

### 6.1. Funcao

- Detecta inicio/fim de fala com precisao
- "Tesoura inteligente" que corta silencio
- Threshold: >300ms de silencio = fim de fala

### 6.2. Especificacoes

| Propriedade | Valor          |
| :---------- | :------------- |
| Modelo      | silero_vad v5  |
| Formato     | ONNX           |
| Tamanho     | ~50 MB         |
| Threshold   | 300ms silencio |

### 6.3. Integracao

```python
import torch

model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False
)
```

---

## 7. Wake Word - openWakeWord

### 7.1. Funcao

- Monitoramento passivo continuo (low CPU)
- Detecta palavra-chave para ativar o sistema
- Suporta treinamento customizado (few-shot)

### 7.2. Especificacoes

| Propriedade | Valor                      |
| :---------- | :------------------------- |
| Modelo      | openWakeWord               |
| Formato     | ONNX/tflite                |
| Tamanho     | ~150 MB                    |
| Wake Words  | "Ei Painho", customizaveis |

### 7.3. Integracao

```python
from openwakeword import Model

model = Model(
    wakeword_models=["models/ei_painho.onnx"],
    inference_framework="onnx"
)
```

---

## 8. Consumo Total de Recursos

### 8.1. VRAM (GPU)

```
Granite 4.0 Q8_0:     ~1300 MB
KV Cache:             ~ 300 MB
Buffers CUDA:         ~ 400 MB
--------------------------------
Total GPU:            ~2000 MB de 4096 MB (49%)
Margem livre:         ~2000 MB
```

### 8.2. RAM (CPU)

```
Whisper Q5_K_M:       ~2200 MB
BGE-M3:               ~1500 MB
Piper:                ~ 300 MB
Silero VAD:           ~  50 MB
openWakeWord:         ~ 150 MB
Qdrant Index:         ~ 500 MB (variavel)
--------------------------------
Total RAM:            ~4700 MB
```

### 8.3. Disco (SSD)

```
Modelos GGUF/ONNX:    ~5 GB
Qdrant Vectors:       ~500 MB (variavel)
Manuais (.md):        ~10 MB
Logs:                 ~100 MB
--------------------------------
Total Disco:          ~6 GB
```

---

## Referencias

- [00-architecture-overview.md](./00-architecture-overview.md) - Visao geral da arquitetura
- [04-model-management.md](./04-model-management.md) - Download e gestao de modelos
- [05-rag-memory.md](./05-rag-memory.md) - Arquitetura RAG detalhada
