# Mascate - Plano de Implementação Detalhado

**Versão:** 2.0  
**Última Atualização:** 2024-12-27  
**Status:** Em Execução

Este documento define o plano de trabalho completo para o desenvolvimento da PoC do Mascate.
Estruturado em **Fases > Etapas > Atividades** para máxima clareza da equipe.

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Regras de Desenvolvimento](#2-regras-de-desenvolvimento)
3. [FASE 0: Fundação](#fase-0-fundação)
4. [FASE 1: Pipeline de Áudio](#fase-1-pipeline-de-áudio)
5. [FASE 2: Cérebro e Memória](#fase-2-cérebro-e-memória)
6. [FASE 3: Executor e Segurança](#fase-3-executor-e-segurança)
7. [FASE 4: Feedback e Interface](#fase-4-feedback-e-interface)
8. [FASE 5: Validação Final](#fase-5-validação-final)
9. [Cronograma Estimado](#cronograma-estimado)

---

## 1. Visão Geral

### 1.1. Estrutura do Plano

```
FASE (objetivo macro)
└── ETAPA (módulo/componente)
    └── ATIVIDADE (tarefa específica)
        ├── Descrição: O que fazer
        ├── Arquivo(s): Onde fazer
        ├── Dependências: Pré-requisitos
        ├── Critério de Aceite: Como validar
        └── Estimativa: Tempo esperado
```

### 1.2. Stack Tecnológica Consolidada

| Componente  | Tecnologia            | Versão | Execução |
| ----------- | --------------------- | ------ | -------- |
| Runtime     | Python                | 3.12+  | -        |
| Pkg Manager | uv                    | latest | -        |
| LLM         | Granite 4.0 Hybrid 1B | Q8_0   | GPU      |
| LLM Backend | llama-cpp-python      | 0.2+   | GPU      |
| STT         | Whisper Large v3      | Q5_K_M | CPU      |
| STT Backend | whisper.cpp           | latest | CPU      |
| TTS         | Piper                 | latest | CPU      |
| VAD         | Silero VAD            | v5     | CPU      |
| Wake Word   | openWakeWord          | latest | CPU      |
| Embeddings  | BGE-M3                | latest | CPU      |
| Vector DB   | Qdrant                | latest | CPU      |
| Audio I/O   | sounddevice           | 0.4+   | CPU      |
| CLI         | Click                 | 8.0+   | -        |
| TUI         | Rich + Textual        | latest | -        |

---

## 2. Regras de Desenvolvimento

### 2.1. Regra de Ouro: Testes Antes de Avançar

```
┌─────────────────────────────────────────────────────────────┐
│  NUNCA avançar para próxima Etapa/Fase sem:                 │
│  1. Todos os testes unitários passando                      │
│  2. Teste de integração da etapa passando                   │
│  3. Code review (se em equipe)                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2. Níveis de Teste

| Nível          | Quando         | Onde                 | Objetivo                |
| -------------- | -------------- | -------------------- | ----------------------- |
| **Unitário**   | Cada Atividade | `tests/unit/`        | Validar função isolada  |
| **Integração** | Final de Etapa | `tests/integration/` | Validar módulo completo |
| **E2E**        | Final de Fase  | `tests/e2e/`         | Validar fluxo completo  |

### 2.3. Comandos Padrão

```bash
# Rodar todos os testes
uv run pytest

# Rodar teste específico
uv run pytest tests/unit/test_config.py::test_load_config

# Rodar com cobertura
uv run pytest --cov=src

# Lint e format
uv run ruff format src tests scripts
uv run ruff check src tests scripts --fix
```

---

## FASE 0: Fundação

**Objetivo:** Preparar infraestrutura base do projeto  
**Duração Estimada:** 1-2 dias  
**Status:** ✅ CONCLUÍDA

### Etapa 0.1: Estrutura do Projeto

**Objetivo:** Criar estrutura de diretórios e arquivos base

| ID    | Atividade                     | Arquivo(s)                   | Status |
| ----- | ----------------------------- | ---------------------------- | ------ |
| 0.1.1 | Criar estrutura de diretórios | `src/mascate/**/__init__.py` | ✅     |
| 0.1.2 | Configurar pyproject.toml     | `pyproject.toml`             | ✅     |
| 0.1.3 | Configurar .gitignore         | `.gitignore`                 | ✅     |
| 0.1.4 | Criar config.toml exemplo     | `config.toml.example`        | ✅     |
| 0.1.5 | Criar README.md               | `README.md`                  | ✅     |
| 0.1.6 | Criar AGENTS.md               | `AGENTS.md`                  | ✅     |

**Teste de Integração 0.1:**

- [x] `uv sync` executa sem erros
- [x] Imports funcionam: `from mascate.core import config`

---

### Etapa 0.2: Sistema de Configuração

**Objetivo:** Carregar e validar configurações TOML

| ID    | Atividade                      | Arquivo(s)                       | Dependências | Status      |
| ----- | ------------------------------ | -------------------------------- | ------------ | ----------- |
| 0.2.1 | Criar dataclasses de config    | `src/mascate/core/config.py`     | -            | ✅          |
| 0.2.2 | Implementar Config.load()      | `src/mascate/core/config.py`     | 0.2.1        | ⏳ Parcial  |
| 0.2.3 | Implementar validação de paths | `src/mascate/core/config.py`     | 0.2.2        | ⏳ Pendente |
| 0.2.4 | Criar exceções customizadas    | `src/mascate/core/exceptions.py` | -            | ✅          |
| 0.2.5 | Criar sistema de logging       | `src/mascate/core/logging.py`    | -            | ✅          |

**Critérios de Aceite:**

```python
# Deve funcionar:
config = Config.load()
assert config.audio.sample_rate == 16000
assert config.models_dir.exists()
```

**Teste de Integração 0.2:**

- [x] Config carrega valores default
- [ ] Config carrega de arquivo TOML
- [ ] Config valida paths inválidos

---

### Etapa 0.3: Gestão de Dependências de Sistema

**Objetivo:** Detectar distro e instalar pacotes do SO

| ID    | Atividade                                | Arquivo(s)                | Dependências | Status |
| ----- | ---------------------------------------- | ------------------------- | ------------ | ------ |
| 0.3.1 | Implementar detect_distro()              | `scripts/install_deps.py` | -            | ✅     |
| 0.3.2 | Mapear pacotes por distro                | `scripts/install_deps.py` | 0.3.1        | ✅     |
| 0.3.3 | Implementar install_packages()           | `scripts/install_deps.py` | 0.3.2        | ✅     |
| 0.3.4 | Implementar verificação de já instalados | `scripts/install_deps.py` | 0.3.3        | ✅     |

**Critérios de Aceite:**

```bash
# Deve funcionar em Ubuntu:
uv run python scripts/install_deps.py
# Output: "Distribuicao detectada: Ubuntu/Debian"
```

**Teste de Integração 0.3:**

- [x] Detecta Ubuntu/Debian corretamente
- [x] Detecta Arch corretamente
- [ ] Instala pacotes sem erro (requer sudo)

---

### Etapa 0.4: Download de Modelos

**Objetivo:** Baixar modelos do Hugging Face Hub com verificação

| ID    | Atividade                       | Arquivo(s)                   | Dependências | Status      |
| ----- | ------------------------------- | ---------------------------- | ------------ | ----------- |
| 0.4.1 | Criar ModelSpec dataclass       | `scripts/download_models.py` | -            | ✅          |
| 0.4.2 | Definir lista de modelos        | `scripts/download_models.py` | 0.4.1        | ✅          |
| 0.4.3 | Implementar download via HF Hub | `scripts/download_models.py` | 0.4.2        | ✅          |
| 0.4.4 | Implementar verificação SHA256  | `scripts/download_models.py` | 0.4.3        | ✅          |
| 0.4.5 | Adicionar progress bar (Rich)   | `scripts/download_models.py` | 0.4.4        | ⏳ Pendente |

**Critérios de Aceite:**

```bash
uv run python scripts/download_models.py
# Deve baixar modelos para ~/.local/share/mascate/models/
# Deve verificar hash se disponível
```

---

### Etapa 0.5: CLI Base

**Objetivo:** Entry point da aplicação via linha de comando

| ID    | Atividade                               | Arquivo(s)                     | Dependências | Status |
| ----- | --------------------------------------- | ------------------------------ | ------------ | ------ |
| 0.5.1 | Criar grupo de comandos Click           | `src/mascate/interface/cli.py` | -            | ✅     |
| 0.5.2 | Implementar comando `version`           | `src/mascate/interface/cli.py` | 0.5.1        | ✅     |
| 0.5.3 | Implementar comando `check`             | `src/mascate/interface/cli.py` | 0.5.1        | ✅     |
| 0.5.4 | Implementar comando `run` (placeholder) | `src/mascate/interface/cli.py` | 0.5.1        | ✅     |

**Critérios de Aceite:**

```bash
uv run mascate version  # Mostra versão
uv run mascate check    # Mostra status de deps
uv run mascate run      # Inicia (placeholder)
```

---

### ✅ Teste E2E Fase 0

- [x] Clone repo limpo + `uv sync` funciona
- [x] `uv run mascate version` mostra versão
- [x] `uv run mascate check` mostra dependências
- [ ] `python scripts/install_deps.py` instala deps (requer sudo)
- [ ] `python scripts/download_models.py` baixa modelos
- [ ] Config carrega de arquivo TOML

---

## FASE 1: Pipeline de Áudio

**Objetivo:** Captura de áudio, wake word, VAD e STT  
**Duração Estimada:** 3-5 dias  
**Status:** ⏳ NÃO INICIADA

**Critério de Sucesso:** Falar "Ei Mascate, abre o Firefox" e obter texto transcrito

---

### Etapa 1.1: Captura de Áudio

**Objetivo:** Capturar áudio do microfone em tempo real

| ID    | Atividade                         | Arquivo(s)                         | Dependências | Estimativa |
| ----- | --------------------------------- | ---------------------------------- | ------------ | ---------- |
| 1.1.1 | Criar classe AudioCapture         | `src/mascate/audio/capture.py`     | sounddevice  | 2h         |
| 1.1.2 | Implementar lista de dispositivos | `src/mascate/audio/capture.py`     | 1.1.1        | 1h         |
| 1.1.3 | Implementar callback de captura   | `src/mascate/audio/capture.py`     | 1.1.1        | 2h         |
| 1.1.4 | Implementar buffer circular       | `src/mascate/audio/capture.py`     | 1.1.3        | 2h         |
| 1.1.5 | Criar testes unitários            | `tests/unit/audio/test_capture.py` | 1.1.4        | 2h         |

**Especificações Técnicas:**

```python
# Parâmetros de captura
SAMPLE_RATE = 16000      # Hz
CHANNELS = 1             # Mono
DTYPE = "float32"        # Formato
CHUNK_SIZE = 1024        # Samples por chunk
BUFFER_SECONDS = 0.5     # Buffer circular
```

**Critérios de Aceite:**

```python
capture = AudioCapture()
capture.start()
audio_chunk = capture.get_chunk()  # numpy array
assert audio_chunk.shape == (1024,)
assert audio_chunk.dtype == np.float32
capture.stop()
```

**Teste de Integração 1.1:**

- [ ] Captura funciona com microfone real
- [ ] Buffer não causa overflow
- [ ] Latência < 50ms

---

### Etapa 1.2: Wake Word Detection

**Objetivo:** Detectar palavra de ativação "Mascate"

| ID    | Atividade                          | Arquivo(s)                           | Dependências | Estimativa |
| ----- | ---------------------------------- | ------------------------------------ | ------------ | ---------- |
| 1.2.1 | Criar classe WakeWordDetector      | `src/mascate/audio/wake/detector.py` | openWakeWord | 2h         |
| 1.2.2 | Carregar modelo de wake word       | `src/mascate/audio/wake/detector.py` | 1.2.1        | 1h         |
| 1.2.3 | Implementar processo de detecção   | `src/mascate/audio/wake/detector.py` | 1.2.2        | 2h         |
| 1.2.4 | Implementar threshold configurável | `src/mascate/audio/wake/detector.py` | 1.2.3        | 1h         |
| 1.2.5 | Implementar callback de ativação   | `src/mascate/audio/wake/detector.py` | 1.2.4        | 1h         |
| 1.2.6 | Criar testes unitários             | `tests/unit/audio/test_wake.py`      | 1.2.5        | 2h         |

**Especificações Técnicas:**

```python
# Configuração wake word
WAKE_WORD = "hey_mascate"  # ou modelo custom
THRESHOLD = 0.5            # Score mínimo para ativação
COOLDOWN_MS = 2000         # Tempo entre ativações
```

**Critérios de Aceite:**

```python
detector = WakeWordDetector(threshold=0.5)
detector.on_activation(callback_fn)
score = detector.process(audio_chunk)
# Se score >= 0.5, callback_fn é chamado
```

---

### Etapa 1.3: Voice Activity Detection (VAD)

**Objetivo:** Detectar quando o usuário começa/termina de falar

| ID    | Atividade                        | Arquivo(s)                           | Dependências | Estimativa |
| ----- | -------------------------------- | ------------------------------------ | ------------ | ---------- |
| 1.3.1 | Criar classe VADProcessor        | `src/mascate/audio/vad/processor.py` | Silero VAD   | 2h         |
| 1.3.2 | Carregar modelo Silero           | `src/mascate/audio/vad/processor.py` | 1.3.1        | 1h         |
| 1.3.3 | Implementar detecção de voz      | `src/mascate/audio/vad/processor.py` | 1.3.2        | 2h         |
| 1.3.4 | Implementar detecção de silêncio | `src/mascate/audio/vad/processor.py` | 1.3.3        | 2h         |
| 1.3.5 | Implementar máquina de estados   | `src/mascate/audio/vad/processor.py` | 1.3.4        | 2h         |
| 1.3.6 | Criar testes unitários           | `tests/unit/audio/test_vad.py`       | 1.3.5        | 2h         |

**Máquina de Estados VAD:**

```
IDLE ──[voz detectada]──> SPEAKING
SPEAKING ──[silêncio 300ms]──> END_OF_SPEECH
END_OF_SPEECH ──[reset]──> IDLE
```

**Especificações Técnicas:**

```python
# Configuração VAD
VAD_THRESHOLD = 0.5        # Probabilidade mínima
SILENCE_DURATION_MS = 300  # Silêncio para fim de fala
MIN_SPEECH_DURATION_MS = 200  # Fala mínima válida
```

---

### Etapa 1.4: Speech-to-Text (STT)

**Objetivo:** Transcrever áudio para texto usando Whisper

| ID    | Atividade                      | Arquivo(s)                         | Dependências | Estimativa |
| ----- | ------------------------------ | ---------------------------------- | ------------ | ---------- |
| 1.4.1 | Criar classe WhisperSTT        | `src/mascate/audio/stt/whisper.py` | whisper.cpp  | 3h         |
| 1.4.2 | Carregar modelo Whisper        | `src/mascate/audio/stt/whisper.py` | 1.4.1        | 2h         |
| 1.4.3 | Implementar transcrição batch  | `src/mascate/audio/stt/whisper.py` | 1.4.2        | 3h         |
| 1.4.4 | Implementar pós-processamento  | `src/mascate/audio/stt/whisper.py` | 1.4.3        | 2h         |
| 1.4.5 | Implementar detecção de idioma | `src/mascate/audio/stt/whisper.py` | 1.4.4        | 1h         |
| 1.4.6 | Criar testes unitários         | `tests/unit/audio/test_stt.py`     | 1.4.5        | 2h         |

**Especificações Técnicas:**

```python
# Configuração Whisper
MODEL_PATH = "~/.local/share/mascate/models/ggml-large-v3-q5_0.bin"
LANGUAGE = "pt"            # Português
BEAM_SIZE = 5              # Beam search
BEST_OF = 5                # Candidatos
```

**Critérios de Aceite:**

```python
stt = WhisperSTT(model_path)
text = stt.transcribe(audio_array)
assert isinstance(text, str)
assert len(text) > 0
# "abre o firefox" deve ser transcrito corretamente
```

---

### Etapa 1.5: Integração do Pipeline de Áudio

**Objetivo:** Conectar todos os componentes de áudio

| ID    | Atividade                     | Arquivo(s)                                 | Dependências | Estimativa |
| ----- | ----------------------------- | ------------------------------------------ | ------------ | ---------- |
| 1.5.1 | Criar classe AudioPipeline    | `src/mascate/audio/pipeline.py`            | 1.1-1.4      | 3h         |
| 1.5.2 | Implementar fluxo de dados    | `src/mascate/audio/pipeline.py`            | 1.5.1        | 2h         |
| 1.5.3 | Implementar eventos/callbacks | `src/mascate/audio/pipeline.py`            | 1.5.2        | 2h         |
| 1.5.4 | Criar testes de integração    | `tests/integration/test_audio_pipeline.py` | 1.5.3        | 3h         |

**Fluxo do Pipeline:**

```
Microfone → Captura → Wake Word → VAD → STT → Texto
              ↓           ↓         ↓
           Buffer     Ativação   Fim de
           Circular               Fala
```

---

### ⏳ Teste E2E Fase 1

- [ ] Dizer "Ei Mascate" ativa o sistema
- [ ] VAD detecta fim de fala corretamente
- [ ] Texto é transcrito com precisão > 90%
- [ ] Latência total < 200ms (Wake → Texto)

---

## FASE 2: Cérebro e Memória

**Objetivo:** RAG, LLM com GBNF, geração de JSON estruturado  
**Duração Estimada:** 4-6 dias  
**Status:** ⏳ NÃO INICIADA

**Critério de Sucesso:** Texto "abre o firefox" gera JSON `{"action": "open_app", "target": "firefox"}`

---

### Etapa 2.1: Base de Conhecimento (Ingestão)

**Objetivo:** Indexar documentos Markdown no Qdrant

| ID    | Atividade                      | Arquivo(s)                                   | Dependências | Estimativa |
| ----- | ------------------------------ | -------------------------------------------- | ------------ | ---------- |
| 2.1.1 | Criar classe KnowledgeBase     | `src/mascate/intelligence/rag/knowledge.py`  | -            | 2h         |
| 2.1.2 | Implementar parser de Markdown | `src/mascate/intelligence/rag/parser.py`     | 2.1.1        | 2h         |
| 2.1.3 | Implementar chunking de texto  | `src/mascate/intelligence/rag/parser.py`     | 2.1.2        | 2h         |
| 2.1.4 | Setup Qdrant local             | `src/mascate/intelligence/rag/vectordb.py`   | -            | 2h         |
| 2.1.5 | Integrar BGE-M3 embeddings     | `src/mascate/intelligence/rag/embeddings.py` | 2.1.4        | 3h         |
| 2.1.6 | Implementar ingestão de docs   | `src/mascate/intelligence/rag/knowledge.py`  | 2.1.5        | 3h         |
| 2.1.7 | Criar testes unitários         | `tests/unit/intelligence/test_rag.py`        | 2.1.6        | 2h         |

**Estrutura de Chunks:**

```python
@dataclass
class Chunk:
    id: str
    content: str
    metadata: dict  # source, section, etc
    embedding: list[float]
```

---

### Etapa 2.2: Busca RAG

**Objetivo:** Recuperar documentos relevantes para uma query

| ID    | Atividade                          | Arquivo(s)                                  | Dependências | Estimativa |
| ----- | ---------------------------------- | ------------------------------------------- | ------------ | ---------- |
| 2.2.1 | Criar classe RAGRetriever          | `src/mascate/intelligence/rag/retriever.py` | 2.1          | 2h         |
| 2.2.2 | Implementar busca densa            | `src/mascate/intelligence/rag/retriever.py` | 2.2.1        | 2h         |
| 2.2.3 | Implementar busca esparsa (BM25)   | `src/mascate/intelligence/rag/retriever.py` | 2.2.2        | 2h         |
| 2.2.4 | Implementar fusão híbrida          | `src/mascate/intelligence/rag/retriever.py` | 2.2.3        | 2h         |
| 2.2.5 | Implementar formatação de contexto | `src/mascate/intelligence/rag/retriever.py` | 2.2.4        | 1h         |
| 2.2.6 | Criar testes unitários             | `tests/unit/intelligence/test_retriever.py` | 2.2.5        | 2h         |

**Critérios de Aceite:**

```python
retriever = RAGRetriever(knowledge_base)
results = retriever.search("como abrir o firefox", top_k=3)
assert len(results) == 3
assert "firefox" in results[0].content.lower()
```

---

### Etapa 2.3: Gramáticas GBNF

**Objetivo:** Criar gramáticas para saída estruturada do LLM

| ID    | Atividade                        | Arquivo(s)                                           | Dependências | Estimativa |
| ----- | -------------------------------- | ---------------------------------------------------- | ------------ | ---------- |
| 2.3.1 | Criar gramática base JSON        | `src/mascate/intelligence/llm/grammars/base.gbnf`    | -            | 2h         |
| 2.3.2 | Criar gramática de comandos      | `src/mascate/intelligence/llm/grammars/command.gbnf` | 2.3.1        | 3h         |
| 2.3.3 | Criar gramática de confirmação   | `src/mascate/intelligence/llm/grammars/confirm.gbnf` | 2.3.1        | 1h         |
| 2.3.4 | Implementar loader de gramáticas | `src/mascate/intelligence/llm/grammar.py`            | 2.3.1-3      | 2h         |
| 2.3.5 | Criar testes de validação        | `tests/unit/intelligence/test_grammar.py`            | 2.3.4        | 2h         |

**Exemplo de Gramática de Comando:**

```gbnf
root ::= "{" ws "\"action\":" ws action "," ws "\"target\":" ws target params? "}" ws

action ::= "\"open_app\"" | "\"open_url\"" | "\"media_control\"" | "\"file_op\""
target ::= "\"" [a-zA-Z0-9_/.-]+ "\""
params ::= "," ws "\"params\":" ws "{" param-list "}"
```

---

### Etapa 2.4: Integração LLM

**Objetivo:** Inferência com Granite via llama.cpp

| ID    | Atividade                          | Arquivo(s)                                | Dependências | Estimativa |
| ----- | ---------------------------------- | ----------------------------------------- | ------------ | ---------- |
| 2.4.1 | Criar classe GraniteLLM            | `src/mascate/intelligence/llm/granite.py` | llama-cpp    | 3h         |
| 2.4.2 | Implementar carregamento de modelo | `src/mascate/intelligence/llm/granite.py` | 2.4.1        | 2h         |
| 2.4.3 | Implementar geração com GBNF       | `src/mascate/intelligence/llm/granite.py` | 2.4.2, 2.3   | 3h         |
| 2.4.4 | Implementar templates de prompt    | `src/mascate/intelligence/llm/prompts.py` | 2.4.3        | 2h         |
| 2.4.5 | Implementar streaming              | `src/mascate/intelligence/llm/granite.py` | 2.4.4        | 2h         |
| 2.4.6 | Criar testes unitários             | `tests/unit/intelligence/test_llm.py`     | 2.4.5        | 3h         |

**Template de Prompt:**

```
<|system|>
Você é o Mascate, um assistente de voz para Linux.
Analise o pedido do usuário e o contexto fornecido.
Responda APENAS com JSON no formato especificado.

Contexto:
{context}
<|user|>
{user_input}
<|assistant|>
```

---

### Etapa 2.5: Integração Cérebro

**Objetivo:** Conectar RAG + LLM em pipeline unificado

| ID    | Atividade                      | Arquivo(s)                          | Dependências | Estimativa |
| ----- | ------------------------------ | ----------------------------------- | ------------ | ---------- |
| 2.5.1 | Criar classe Brain             | `src/mascate/intelligence/brain.py` | 2.1-2.4      | 3h         |
| 2.5.2 | Implementar fluxo RAG → LLM    | `src/mascate/intelligence/brain.py` | 2.5.1        | 2h         |
| 2.5.3 | Implementar parser de resposta | `src/mascate/intelligence/brain.py` | 2.5.2        | 2h         |
| 2.5.4 | Criar testes de integração     | `tests/integration/test_brain.py`   | 2.5.3        | 3h         |

**Critérios de Aceite:**

```python
brain = Brain(llm, retriever)
result = brain.process("abre o firefox")
assert result.action == "open_app"
assert result.target == "firefox"
```

---

### ⏳ Teste E2E Fase 2

- [ ] Query "como abrir o youtube" retorna docs relevantes
- [ ] LLM gera JSON válido 100% das vezes
- [ ] GBNF previne alucinações de formato
- [ ] Latência RAG + LLM < 300ms

---

## FASE 3: Executor e Segurança

**Objetivo:** Executar comandos com validação de segurança  
**Duração Estimada:** 3-4 dias  
**Status:** ⏳ NÃO INICIADA

**Critério de Sucesso:** JSON de comando → ação no sistema com proteção

---

### Etapa 3.1: Parser de Comandos

**Objetivo:** Converter JSON do LLM em objetos Command

| ID    | Atividade                       | Arquivo(s)                           | Dependências | Estimativa |
| ----- | ------------------------------- | ------------------------------------ | ------------ | ---------- |
| 3.1.1 | Criar dataclass Command         | `src/mascate/executor/models.py`     | -            | 1h         |
| 3.1.2 | Criar enum de ActionType        | `src/mascate/executor/models.py`     | 3.1.1        | 1h         |
| 3.1.3 | Criar CommandParser             | `src/mascate/executor/parser.py`     | 3.1.2        | 2h         |
| 3.1.4 | Implementar validação de schema | `src/mascate/executor/parser.py`     | 3.1.3        | 2h         |
| 3.1.5 | Criar testes unitários          | `tests/unit/executor/test_parser.py` | 3.1.4        | 2h         |

**Modelo de Command:**

```python
@dataclass
class Command:
    action: ActionType
    target: str
    params: dict
    raw_json: str
    risk_level: RiskLevel  # LOW, MEDIUM, HIGH, CRITICAL
```

---

### Etapa 3.2: Camada de Segurança (Guarda-Costas)

**Objetivo:** Validar comandos antes da execução

| ID    | Atividade                          | Arquivo(s)                             | Dependências | Estimativa |
| ----- | ---------------------------------- | -------------------------------------- | ------------ | ---------- |
| 3.2.1 | Criar classe SecurityGuard         | `src/mascate/executor/security.py`     | 3.1          | 2h         |
| 3.2.2 | Implementar blacklist de comandos  | `src/mascate/executor/security.py`     | 3.2.1        | 2h         |
| 3.2.3 | Implementar whitelist de paths     | `src/mascate/executor/security.py`     | 3.2.2        | 1h         |
| 3.2.4 | Implementar detector de risk level | `src/mascate/executor/security.py`     | 3.2.3        | 2h         |
| 3.2.5 | Implementar fluxo de confirmação   | `src/mascate/executor/security.py`     | 3.2.4        | 2h         |
| 3.2.6 | Criar testes unitários             | `tests/unit/executor/test_security.py` | 3.2.5        | 3h         |

**Blacklist de Comandos:**

```python
BLACKLIST = [
    "rm -rf", "rm -r",        # Deleção recursiva
    "dd",                      # Acesso direto a disco
    "mkfs", "format",          # Formatação
    "> /dev/", "| /dev/",      # Redireção para devices
    "chmod 777",               # Permissões perigosas
    "curl | bash",             # Execução remota
]
```

**Níveis de Risco:**

```python
class RiskLevel(Enum):
    LOW = "low"           # Executar diretamente
    MEDIUM = "medium"     # Log + executar
    HIGH = "high"         # Pedir confirmação
    CRITICAL = "critical" # Bloquear sempre
```

---

### Etapa 3.3: Handlers de Comandos

**Objetivo:** Implementar executores para cada tipo de ação

| ID    | Atividade                   | Arquivo(s)                                 | Dependências | Estimativa |
| ----- | --------------------------- | ------------------------------------------ | ------------ | ---------- |
| 3.3.1 | Criar interface BaseHandler | `src/mascate/executor/handlers/base.py`    | 3.2          | 1h         |
| 3.3.2 | Implementar AppHandler      | `src/mascate/executor/handlers/app.py`     | 3.3.1        | 2h         |
| 3.3.3 | Implementar BrowserHandler  | `src/mascate/executor/handlers/browser.py` | 3.3.1        | 2h         |
| 3.3.4 | Implementar MediaHandler    | `src/mascate/executor/handlers/media.py`   | 3.3.1        | 2h         |
| 3.3.5 | Implementar FileHandler     | `src/mascate/executor/handlers/file.py`    | 3.3.1        | 2h         |
| 3.3.6 | Implementar SystemHandler   | `src/mascate/executor/handlers/system.py`  | 3.3.1        | 2h         |
| 3.3.7 | Criar registry de handlers  | `src/mascate/executor/registry.py`         | 3.3.2-6      | 1h         |
| 3.3.8 | Criar testes unitários      | `tests/unit/executor/test_handlers.py`     | 3.3.7        | 3h         |

**Mapeamento de Handlers:**

```python
HANDLERS = {
    ActionType.OPEN_APP: AppHandler,
    ActionType.OPEN_URL: BrowserHandler,
    ActionType.MEDIA_CONTROL: MediaHandler,
    ActionType.FILE_OP: FileHandler,
    ActionType.SYSTEM: SystemHandler,
}
```

---

### Etapa 3.4: Integração do Executor

**Objetivo:** Conectar parser + segurança + handlers

| ID    | Atividade                         | Arquivo(s)                           | Dependências | Estimativa |
| ----- | --------------------------------- | ------------------------------------ | ------------ | ---------- |
| 3.4.1 | Criar classe Executor             | `src/mascate/executor/executor.py`   | 3.1-3.3      | 2h         |
| 3.4.2 | Implementar fluxo de execução     | `src/mascate/executor/executor.py`   | 3.4.1        | 2h         |
| 3.4.3 | Implementar feedback de resultado | `src/mascate/executor/executor.py`   | 3.4.2        | 1h         |
| 3.4.4 | Criar testes de integração        | `tests/integration/test_executor.py` | 3.4.3        | 3h         |

---

### ⏳ Teste E2E Fase 3

- [ ] Comandos LOW risk executam diretamente
- [ ] Comandos HIGH risk pedem confirmação
- [ ] Comandos CRITICAL são bloqueados
- [ ] `rm -rf` é sempre bloqueado
- [ ] Firefox abre com `xdg-open`
- [ ] playerctl controla mídia

---

## FASE 4: Feedback e Interface

**Objetivo:** TTS e interface visual (TUI)  
**Duração Estimada:** 3-4 dias  
**Status:** ⏳ NÃO INICIADA

**Critério de Sucesso:** Sistema responde por voz e mostra status visual

---

### Etapa 4.1: Text-to-Speech (TTS)

**Objetivo:** Sintetizar voz a partir de texto

| ID    | Atividade                    | Arquivo(s)                           | Dependências | Estimativa |
| ----- | ---------------------------- | ------------------------------------ | ------------ | ---------- |
| 4.1.1 | Criar classe PiperTTS        | `src/mascate/audio/tts/piper.py`     | piper        | 2h         |
| 4.1.2 | Carregar modelo de voz pt-BR | `src/mascate/audio/tts/piper.py`     | 4.1.1        | 1h         |
| 4.1.3 | Implementar síntese de áudio | `src/mascate/audio/tts/piper.py`     | 4.1.2        | 2h         |
| 4.1.4 | Implementar playback         | `src/mascate/audio/tts/piper.py`     | 4.1.3        | 2h         |
| 4.1.5 | Implementar streaming        | `src/mascate/audio/tts/piper.py`     | 4.1.4        | 2h         |
| 4.1.6 | Criar templates de resposta  | `src/mascate/audio/tts/templates.py` | 4.1.5        | 2h         |
| 4.1.7 | Criar testes unitários       | `tests/unit/audio/test_tts.py`       | 4.1.6        | 2h         |

**Templates de Resposta:**

```python
TEMPLATES = {
    "success": "Pronto, {action} executado.",
    "confirm": "Você tem certeza que quer {action}?",
    "error": "Desculpe, não consegui {action}.",
    "not_found": "Não encontrei {target}.",
}
```

---

### Etapa 4.2: Interface TUI

**Objetivo:** Interface visual com Rich/Textual

| ID    | Atividade                          | Arquivo(s)                         | Dependências | Estimativa |
| ----- | ---------------------------------- | ---------------------------------- | ------------ | ---------- |
| 4.2.1 | Criar HUD básico com Rich          | `src/mascate/interface/hud.py`     | Rich         | 2h         |
| 4.2.2 | Implementar indicador de estado    | `src/mascate/interface/hud.py`     | 4.2.1        | 2h         |
| 4.2.3 | Implementar indicador de áudio     | `src/mascate/interface/hud.py`     | 4.2.2        | 2h         |
| 4.2.4 | Implementar log em tempo real      | `src/mascate/interface/hud.py`     | 4.2.3        | 2h         |
| 4.2.5 | Implementar diálogo de confirmação | `src/mascate/interface/hud.py`     | 4.2.4        | 2h         |
| 4.2.6 | Criar testes unitários             | `tests/unit/interface/test_hud.py` | 4.2.5        | 2h         |

**Estados do HUD:**

```
┌──────────────────────────────────────┐
│  MASCATE v0.1.0                      │
├──────────────────────────────────────┤
│  Estado: [●] LISTENING               │
│  Audio:  [████████░░░░░░░░] 53%      │
│                                      │
│  > "abre o firefox"                  │
│  < Abrindo Firefox...                │
├──────────────────────────────────────┤
│  [Ctrl+C] Sair  [?] Ajuda            │
└──────────────────────────────────────┘
```

---

### Etapa 4.3: Orquestrador Principal

**Objetivo:** Máquina de estados que conecta tudo

| ID    | Atividade                      | Arquivo(s)                               | Dependências | Estimativa |
| ----- | ------------------------------ | ---------------------------------------- | ------------ | ---------- |
| 4.3.1 | Criar enum de Estados          | `src/mascate/core/orchestrator.py`       | -            | 1h         |
| 4.3.2 | Criar classe Orchestrator      | `src/mascate/core/orchestrator.py`       | 4.3.1        | 2h         |
| 4.3.3 | Implementar máquina de estados | `src/mascate/core/orchestrator.py`       | 4.3.2        | 3h         |
| 4.3.4 | Implementar loop principal     | `src/mascate/core/orchestrator.py`       | 4.3.3        | 2h         |
| 4.3.5 | Implementar graceful shutdown  | `src/mascate/core/orchestrator.py`       | 4.3.4        | 1h         |
| 4.3.6 | Integrar com CLI               | `src/mascate/interface/cli.py`           | 4.3.5        | 1h         |
| 4.3.7 | Criar testes de integração     | `tests/integration/test_orchestrator.py` | 4.3.6        | 3h         |

**Máquina de Estados:**

```
INITIALIZING ──> IDLE ──[wake word]──> LISTENING
                  ↑                         │
                  │                    [fim de fala]
                  │                         ↓
                  │                    PROCESSING
                  │                         │
                  │                    [comando]
                  │                         ↓
                  └──[feedback]──── EXECUTING
```

---

### ⏳ Teste E2E Fase 4

- [ ] TTS fala respostas claramente
- [ ] HUD mostra estados corretamente
- [ ] Fluxo completo: Wake → Fala → Ação → Feedback
- [ ] Ctrl+C fecha graciosamente

---

## FASE 5: Validação Final

**Objetivo:** Testes de integração, performance e polish  
**Duração Estimada:** 2-3 dias  
**Status:** ⏳ NÃO INICIADA

---

### Etapa 5.1: Testes de Performance

| ID    | Atividade                   | Arquivo(s)                      | Critério |
| ----- | --------------------------- | ------------------------------- | -------- |
| 5.1.1 | Teste de latência Wake Word | `tests/e2e/test_performance.py` | < 50ms   |
| 5.1.2 | Teste de latência STT       | `tests/e2e/test_performance.py` | < 150ms  |
| 5.1.3 | Teste de latência LLM       | `tests/e2e/test_performance.py` | < 200ms  |
| 5.1.4 | Teste de latência total     | `tests/e2e/test_performance.py` | < 500ms  |
| 5.1.5 | Teste de uso de VRAM        | `tests/e2e/test_performance.py` | < 4GB    |

---

### Etapa 5.2: Testes de Estabilidade

| ID    | Atividade                      | Arquivo(s)                     | Critério         |
| ----- | ------------------------------ | ------------------------------ | ---------------- |
| 5.2.1 | Teste de 1h contínuo           | `tests/e2e/test_stability.py`  | Sem crash        |
| 5.2.2 | Teste de 100 comandos seguidos | `tests/e2e/test_stability.py`  | 100% sucesso     |
| 5.2.3 | Teste de edge cases            | `tests/e2e/test_edge_cases.py` | Handling correto |

---

### Etapa 5.3: Documentação e Demo

| ID    | Atividade                  | Arquivo(s)             |
| ----- | -------------------------- | ---------------------- |
| 5.3.1 | Documentação de instalação | `docs/installation.md` |
| 5.3.2 | Documentação de uso        | `docs/usage.md`        |
| 5.3.3 | Gravar vídeo demo          | `docs/demo.mp4`        |
| 5.3.4 | Preparar release notes     | `CHANGELOG.md`         |

---

### ✅ Teste E2E Fase 5 (Critérios de Aceite da PoC)

- [ ] Latência total < 500ms (Time-to-First-Audio)
- [ ] Precisão STT > 90%
- [ ] 0 crashes em 1h de uso
- [ ] Todos os 4 pilares funcionando (Browser, Media, Files, Apps)
- [ ] Documentação completa
- [ ] Demo gravado

---

## Cronograma Estimado

| Fase       | Duração        | Dependências | Marco                       |
| ---------- | -------------- | ------------ | --------------------------- |
| **Fase 0** | 1-2 dias       | -            | ✅ Estrutura pronta         |
| **Fase 1** | 3-5 dias       | Fase 0       | Pipeline de áudio funcional |
| **Fase 2** | 4-6 dias       | Fase 1       | LLM gerando JSON            |
| **Fase 3** | 3-4 dias       | Fase 2       | Comandos executando         |
| **Fase 4** | 3-4 dias       | Fase 3       | TTS e TUI funcionando       |
| **Fase 5** | 2-3 dias       | Fase 4       | PoC validada                |
| **Total**  | **16-24 dias** | -            | **PoC Completa**            |

---

## Referências

- [00-architecture-overview.md](./00-architecture-overview.md) - Arquitetura geral
- [01-models-spec.md](./01-models-spec.md) - Especificações de modelos
- [02-pipeline-flow.md](./02-pipeline-flow.md) - Fluxo do pipeline
- [07-security.md](./07-security.md) - Estratégia de segurança
- [08-commands-strategy.md](./08-commands-strategy.md) - Comandos agnósticos

---

_Última atualização: 2024-12-27_
