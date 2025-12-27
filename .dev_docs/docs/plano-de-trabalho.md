# Plano de Trabalho: Mascate PoC

**Versão:** 1.0
**Data:** 25/12/2024
**Status:** Aprovado para Execução

---

## Visão Geral

Este documento define o plano de trabalho para desenvolvimento da Prova de Conceito (PoC) do Mascate, um assistente de IA de borda (Edge AI) focado em performance local, privacidade e identidade regional brasileira.

### Filosofia de Desenvolvimento

- **Estrutura Simples**: Fluxo completo end-to-end primeiro, polish depois
- **Zero Dívida Técnica**: Testes obrigatórios para avançar
- **Abordagem Agnóstica**: Desenvolver em Arch, mas manter portabilidade
- **Pareto (80/20)**: Focar nos 20% de funcionalidades que entregam 80% do valor

### Estratégia de Testes

| Nível          | Momento             | Objetivo                |
| -------------- | ------------------- | ----------------------- |
| **Unitário**   | Cada atividade      | Validar função isolada  |
| **Integração** | Final de cada etapa | Validar módulo completo |
| **End-to-End** | Final de cada fase  | Validar fluxo completo  |

### Critério de Avanço

> **REGRA**: Só avançar para a próxima etapa/fase após todos os testes passarem com sucesso.

---

## Decisões Técnicas Consolidadas

| Aspecto                  | Decisão                                   |
| ------------------------ | ----------------------------------------- |
| **Linguagem**            | Python 3.12+                              |
| **Gerenciador de Deps**  | `uv` (Astral)                             |
| **Configuração**         | TOML                                      |
| **Wake Word**            | openWakeWord ("hey jarvis" temporário)    |
| **STT**                  | Whisper Large v3 (`whisper.cpp`, Q5_K_M)  |
| **LLM**                  | Granite 4.0 Hybrid 1B (`llama.cpp`, Q8_0) |
| **TTS**                  | Piper (voz padrão pt-BR)                  |
| **VAD**                  | Silero VAD v5                             |
| **RAG**                  | BGE-M3 + Qdrant                           |
| **Automação de Teclado** | ydotool                                   |
| **Confirmação Sensível** | Teclado                                   |
| **Confirmação Root**     | Senha no teclado                          |

---

## FASE 0: Fundação

**Objetivo:** Preparar infraestrutura base do projeto
**Critério de Sucesso (E2E):** Ambiente configurado, modelos baixados, estrutura pronta para desenvolvimento

---

### Etapa 0.1: Estrutura do Projeto

**Objetivo:** Criar estrutura de diretórios e arquivos base do monorepo

#### Atividade 0.1.1: Criar Estrutura de Diretórios

```
mascate/
├── src/
│   └── mascate/
│       ├── __init__.py
│       ├── audio/           # Captura, Wake Word, VAD, STT
│       │   └── __init__.py
│       ├── intelligence/    # RAG, LLM, GBNF
│       │   └── __init__.py
│       ├── executor/        # Parser, Comandos, Segurança
│       │   └── __init__.py
│       ├── interface/       # CLI, Rich, Logs
│       │   └── __init__.py
│       ├── config/          # Configurações
│       │   └── __init__.py
│       └── core/            # Orquestrador, Utils
│           └── __init__.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── knowledge_base/          # Documentos para RAG
│   ├── sistema/
│   └── comandos/
├── models/                  # Pesos dos modelos (gitignore)
│   ├── llm/
│   ├── stt/
│   ├── tts/
│   ├── vad/
│   ├── wake/
│   └── embeddings/
├── scripts/
│   ├── install_deps.py
│   └── download_models.py
├── logs/                    # Logs de execução (gitignore)
├── pyproject.toml
├── config.toml
├── .gitignore
└── README.md
```

**Teste Unitário:**

- [ ] Verificar que todos os diretórios existem
- [ ] Verificar que `__init__.py` estão presentes nos módulos

#### Atividade 0.1.2: Configurar pyproject.toml

Definir metadados do projeto e dependências iniciais.

**Dependências Core:**

- `llama-cpp-python` (com CUDA)
- `openai-whisper` ou `faster-whisper`
- `piper-tts`
- `qdrant-client`
- `sentence-transformers` (para BGE-M3)
- `openwakeword`
- `silero-vad` (via torch)
- `sounddevice` (captura de áudio)
- `rich` (interface)
- `tomli` / `tomllib` (config)

**Dependências Dev:**

- `pytest`
- `pytest-cov`
- `ruff` (linting)

**Teste Unitário:**

- [ ] `uv sync` executa sem erros
- [ ] Importar cada dependência sem erro

#### Atividade 0.1.3: Configurar .gitignore

Ignorar:

- `models/`
- `logs/`
- `.env`
- `__pycache__/`
- `.venv/`
- `*.gguf`
- `*.onnx`

**Teste Unitário:**

- [ ] Arquivo existe e contém padrões corretos

#### Atividade 0.1.4: Criar config.toml Base

```toml
[mascate]
version = "0.1.0"
environment = "development"

[audio]
sample_rate = 16000
chunk_size = 1024
silence_threshold_ms = 300
wake_word = "hey_jarvis"

[models]
llm_path = "models/llm/granite-4.0-hybrid-1b-q8_0.gguf"
stt_path = "models/stt/whisper-large-v3-q5_k_m.bin"
tts_path = "models/tts/pt_BR-faber-medium.onnx"
vad_path = "models/vad/silero_vad.onnx"
wake_path = "models/wake/hey_jarvis.onnx"
embeddings_path = "models/embeddings/bge-m3"

[llm]
n_ctx = 2048
n_gpu_layers = -1  # Todas as camadas na GPU
temperature = 0.1
max_tokens = 256

[rag]
qdrant_path = "data/qdrant"
collection_name = "knowledge_base"
top_k = 3

[security]
require_confirmation = ["rm", "sudo", "chmod", "chown", "mkfs", "dd", "format"]
blocked_commands = ["rm -rf /", ":(){ :|:& };:"]

[terminal]
default = "ghostty"
fallback = ["kitty", "alacritty", "gnome-terminal", "xterm"]

[logging]
level = "INFO"
file = "logs/mascate.log"
max_size_mb = 10
backup_count = 5
```

**Teste Unitário:**

- [ ] Arquivo TOML é válido (parseia sem erro)
- [ ] Todas as seções obrigatórias existem

**Teste de Integração (Etapa 0.1):**

- [ ] Estrutura completa criada
- [ ] `uv sync` funciona
- [ ] Config carrega corretamente

---

### Etapa 0.2: Gestão de Dependências de Sistema

**Objetivo:** Criar script para instalar dependências do sistema operacional

#### Atividade 0.2.1: Criar install_deps.py

Script que:

1. Detecta a distribuição (Arch/Ubuntu)
2. Instala pacotes via gerenciador correto
3. Verifica instalação

**Mapeamento de Pacotes:**

| Pacote      | Arch (pacman) | Ubuntu (apt)      |
| ----------- | ------------- | ----------------- |
| FFmpeg      | `ffmpeg`      | `ffmpeg`          |
| PlayerCtl   | `playerctl`   | `playerctl`       |
| ydotool     | `ydotool`     | `ydotool`         |
| XDG Utils   | `xdg-utils`   | `xdg-utils`       |
| PortAudio   | `portaudio`   | `libportaudio2`   |
| Build Tools | `base-devel`  | `build-essential` |

**Teste Unitário:**

- [ ] Detecta Arch Linux corretamente
- [ ] Detecta Ubuntu corretamente
- [ ] Lista de pacotes é gerada corretamente

#### Atividade 0.2.2: Verificar Dependências Instaladas

Criar função que verifica se cada dependência está disponível no PATH.

**Teste Unitário:**

- [ ] Retorna True para comandos instalados
- [ ] Retorna False para comandos ausentes
- [ ] Lista dependências faltantes

**Teste de Integração (Etapa 0.2):**

- [ ] Script executa em Arch sem erros
- [ ] Todas as dependências são encontradas após instalação

---

### Etapa 0.3: Download de Modelos

**Objetivo:** Automatizar download dos pesos dos modelos

#### Atividade 0.3.1: Criar download_models.py

Script que:

1. Define dicionário com modelos e URLs
2. Usa `huggingface_hub` para download
3. Verifica integridade (hash SHA256)
4. Organiza em diretórios corretos

**Modelos a Baixar:**

| Modelo           | Repositório HF          | Arquivo                    | Destino              |
| ---------------- | ----------------------- | -------------------------- | -------------------- |
| Granite 4.0      | TBD (comunidade)        | `*q8_0.gguf`               | `models/llm/`        |
| Whisper Large v3 | `ggerganov/whisper.cpp` | `ggml-large-v3-q5_k_m.bin` | `models/stt/`        |
| Piper pt-BR      | `rhasspy/piper-voices`  | `pt_BR-faber-medium.onnx`  | `models/tts/`        |
| Silero VAD       | `snakers4/silero-vad`   | `silero_vad.onnx`          | `models/vad/`        |
| openWakeWord     | `dscripka/openwakeword` | `hey_jarvis_v0.1.onnx`     | `models/wake/`       |
| BGE-M3           | `BAAI/bge-m3`           | (diretório completo)       | `models/embeddings/` |

**Teste Unitário:**

- [ ] Função de download funciona (mock)
- [ ] Verificação de hash funciona
- [ ] Estrutura de diretórios é criada

#### Atividade 0.3.2: Implementar Verificação de Hash

Calcular SHA256 do arquivo baixado e comparar com hash esperado.

**Teste Unitário:**

- [ ] Hash correto retorna True
- [ ] Hash incorreto retorna False e alerta

#### Atividade 0.3.3: Implementar Progress Bar

Usar Rich para mostrar progresso do download.

**Teste Unitário:**

- [ ] Progress bar é exibida durante download

**Teste de Integração (Etapa 0.3):**

- [ ] Todos os modelos são baixados
- [ ] Todos os hashes são verificados
- [ ] Arquivos estão nos diretórios corretos

---

### Etapa 0.4: Sistema de Configuração

**Objetivo:** Criar módulo de configuração centralizado

#### Atividade 0.4.1: Criar Módulo de Config

`src/mascate/config/settings.py`:

- Carregar `config.toml`
- Validar campos obrigatórios
- Prover acesso tipado às configurações

**Teste Unitário:**

- [ ] Carrega config válido
- [ ] Lança erro para config inválido
- [ ] Acesso a campos funciona

#### Atividade 0.4.2: Criar Validadores

Validar:

- Paths de modelos existem
- Valores numéricos estão em ranges válidos
- Enums são valores permitidos

**Teste Unitário:**

- [ ] Validação de path funciona
- [ ] Validação de range funciona
- [ ] Erro claro para valores inválidos

**Teste de Integração (Etapa 0.4):**

- [ ] Config carrega e valida completamente
- [ ] Erros são claros e acionáveis

---

### Teste End-to-End (Fase 0)

- [ ] Clonar repo limpo e executar setup completo
- [ ] `uv sync` instala todas as dependências Python
- [ ] `python scripts/install_deps.py` instala dependências de sistema
- [ ] `python scripts/download_models.py` baixa todos os modelos
- [ ] Config carrega sem erros
- [ ] Importar `mascate` funciona

---

## FASE 1: Pipeline de Áudio (Entrada)

**Objetivo:** Implementar captura de áudio, detecção de wake word, VAD e STT
**Critério de Sucesso (E2E):** Falar "Hey Jarvis, abre o Firefox" e obter texto transcrito

---

### Etapa 1.1: Captura de Áudio

**Objetivo:** Capturar áudio do microfone em tempo real

#### Atividade 1.1.1: Criar Módulo de Captura

`src/mascate/audio/capture.py`:

- Usar `sounddevice` para captura
- Buffer circular para armazenar últimos N segundos
- Callback para processar chunks

**Teste Unitário:**

- [ ] Inicializa stream de áudio
- [ ] Buffer circular funciona (FIFO)
- [ ] Callback é chamado com dados

#### Atividade 1.1.2: Configurar Parâmetros de Áudio

- Sample rate: 16000 Hz (padrão Whisper)
- Channels: 1 (mono)
- Chunk size: 1024 samples
- Dtype: float32

**Teste Unitário:**

- [ ] Parâmetros são lidos do config
- [ ] Stream usa parâmetros corretos

#### Atividade 1.1.3: Implementar Buffer Circular

Manter últimos 0.5s de áudio para capturar início da frase após wake word.

**Teste Unitário:**

- [ ] Buffer mantém tamanho fixo
- [ ] Dados mais antigos são descartados
- [ ] Snapshot do buffer retorna cópia

**Teste de Integração (Etapa 1.1):**

- [ ] Captura 5 segundos de áudio sem erro
- [ ] Áudio capturado é válido (não é silêncio/ruído)
- [ ] Buffer circular funciona em tempo real

---

### Etapa 1.2: Wake Word Detection

**Objetivo:** Detectar palavra de ativação "Hey Jarvis"

#### Atividade 1.2.1: Integrar openWakeWord

`src/mascate/audio/wake_word.py`:

- Carregar modelo ONNX
- Processar chunks de áudio
- Retornar probabilidade de detecção

**Teste Unitário:**

- [ ] Modelo carrega sem erro
- [ ] Processa chunk e retorna score
- [ ] Score está entre 0 e 1

#### Atividade 1.2.2: Implementar Threshold de Ativação

- Threshold configurável (default: 0.5)
- Debounce para evitar ativações repetidas

**Teste Unitário:**

- [ ] Ativação ocorre acima do threshold
- [ ] Não ativa abaixo do threshold
- [ ] Debounce previne ativações em sequência

#### Atividade 1.2.3: Implementar Callback de Ativação

Quando wake word detectada:

1. Travar buffer circular (snapshot)
2. Mudar estado para "listening"
3. Emitir evento

**Teste Unitário:**

- [ ] Callback é chamado na detecção
- [ ] Estado muda corretamente
- [ ] Buffer é preservado

**Teste de Integração (Etapa 1.2):**

- [ ] Dizer "Hey Jarvis" ativa o sistema
- [ ] Outras palavras não ativam
- [ ] Buffer contém áudio anterior à ativação

---

### Etapa 1.3: Voice Activity Detection (VAD)

**Objetivo:** Detectar fim da fala do usuário

#### Atividade 1.3.1: Integrar Silero VAD

`src/mascate/audio/vad.py`:

- Carregar modelo ONNX via PyTorch
- Processar chunks de áudio
- Retornar probabilidade de voz

**Teste Unitário:**

- [ ] Modelo carrega sem erro
- [ ] Detecta voz em áudio com fala
- [ ] Detecta silêncio em áudio mudo

#### Atividade 1.3.2: Implementar Detector de Fim de Fala

- Threshold de silêncio: 300ms (configurável)
- Contador de frames silenciosos
- Trigger quando threshold atingido

**Teste Unitário:**

- [ ] Detecta fim após N ms de silêncio
- [ ] Não dispara durante pausas curtas
- [ ] Threshold é configurável

#### Atividade 1.3.3: Implementar Timeout de Segurança

- Timeout máximo: 30 segundos
- Evita gravação infinita

**Teste Unitário:**

- [ ] Timeout dispara após limite
- [ ] Áudio é preservado até o timeout

**Teste de Integração (Etapa 1.3):**

- [ ] Falar e parar → detecta fim corretamente
- [ ] Pausas curtas não interrompem
- [ ] Timeout funciona

---

### Etapa 1.4: Speech-to-Text (STT)

**Objetivo:** Transcrever áudio para texto

#### Atividade 1.4.1: Integrar Whisper

`src/mascate/audio/stt.py`:

- Carregar modelo (whisper.cpp ou faster-whisper)
- Configurar para português
- Processar áudio e retornar texto

**Teste Unitário:**

- [ ] Modelo carrega sem erro
- [ ] Transcreve áudio de teste corretamente
- [ ] Retorna texto em português

#### Atividade 1.4.2: Implementar Streaming (Opcional para PoC)

Se possível, transcrever enquanto usuário fala.
Se não, processar batch após VAD.

**Teste Unitário:**

- [ ] Transcrição funciona (streaming ou batch)
- [ ] Latência é aceitável (<2s para batch)

#### Atividade 1.4.3: Implementar Normalização de Texto

- Remover pontuação desnecessária
- Normalizar caixa (lowercase)
- Remover filler words ("ahn", "tipo")

**Teste Unitário:**

- [ ] Texto é normalizado corretamente
- [ ] Comandos são preservados

**Teste de Integração (Etapa 1.4):**

- [ ] Áudio completo é transcrito
- [ ] Texto é limpo e utilizável
- [ ] Latência total do pipeline de áudio <3s

---

### Teste End-to-End (Fase 1)

- [ ] Dizer "Hey Jarvis" → sistema ativa
- [ ] Dizer "abre o Firefox" → texto transcrito corretamente
- [ ] Sistema detecta fim da fala e processa
- [ ] Latência total <3 segundos
- [ ] Log mostra todas as etapas

---

## FASE 2: Pipeline de Inteligência

**Objetivo:** Implementar RAG, LLM com GBNF, e geração de comandos estruturados
**Critério de Sucesso (E2E):** Texto "abre o firefox" gera JSON `{"action": "OPEN_URL", "target": "firefox"}`

---

### Etapa 2.1: Base de Conhecimento (RAG)

**Objetivo:** Indexar documentos e recuperar contexto relevante

#### Atividade 2.1.1: Criar Documentos Base

`knowledge_base/comandos/`:

**linux_basics.md:**

```markdown
# Comandos Linux Básicos

## Navegação

- `ls`: listar arquivos
- `cd`: mudar diretório
- `pwd`: diretório atual

## Manipulação de Arquivos

- `cp`: copiar
- `mv`: mover/renomear
- `rm`: remover (PERIGOSO)
- `mkdir`: criar diretório
- `touch`: criar arquivo vazio

## Visualização

- `cat`: mostrar conteúdo
- `less`: paginar conteúdo
- `head`: início do arquivo
- `tail`: fim do arquivo
```

**media_control.md:**

```markdown
# Controle de Mídia

## Comandos Universais (playerctl)

- Play/Pause: `playerctl play-pause`
- Próxima: `playerctl next`
- Anterior: `playerctl previous`
- Parar: `playerctl stop`

## Volume (pactl)

- Aumentar: `pactl set-sink-volume @DEFAULT_SINK@ +5%`
- Diminuir: `pactl set-sink-volume @DEFAULT_SINK@ -5%`
- Mudo: `pactl set-sink-mute @DEFAULT_SINK@ toggle`
```

**system_actions.md:**

```markdown
# Ações de Sistema

## Abrir Aplicativos

- Navegador: `xdg-open https://...` ou nome do app
- Arquivos: `xdg-open /caminho/`
- Qualquer app: nome do executável

## Atalhos de Teclado (ydotool)

- Simular tecla: `ydotool key <keycode>`
- Simular texto: `ydotool type "texto"`
```

**Teste Unitário:**

- [ ] Documentos são válidos Markdown
- [ ] Contêm informações necessárias

#### Atividade 2.1.2: Integrar BGE-M3

`src/mascate/intelligence/embeddings.py`:

- Carregar modelo BGE-M3
- Gerar embeddings para texto
- Suportar busca híbrida (dense + sparse)

**Teste Unitário:**

- [ ] Modelo carrega sem erro
- [ ] Gera embedding de dimensão correta
- [ ] Embeddings similares para textos similares

#### Atividade 2.1.3: Configurar Qdrant

`src/mascate/intelligence/vector_store.py`:

- Inicializar Qdrant em modo local
- Criar collection com configuração correta
- Implementar insert e search

**Teste Unitário:**

- [ ] Qdrant inicializa sem erro
- [ ] Insert funciona
- [ ] Search retorna resultados relevantes

#### Atividade 2.1.4: Implementar Indexação

`src/mascate/intelligence/indexer.py`:

- Ler arquivos Markdown
- Chunkar por seções
- Gerar embeddings
- Inserir no Qdrant

**Teste Unitário:**

- [ ] Lê arquivos Markdown
- [ ] Chunks têm tamanho adequado
- [ ] Indexação completa sem erro

#### Atividade 2.1.5: Implementar Recuperação

`src/mascate/intelligence/retriever.py`:

- Receber query do usuário
- Gerar embedding da query
- Buscar top-k documentos
- Retornar contexto formatado

**Teste Unitário:**

- [ ] Query "abrir navegador" retorna doc de sistema
- [ ] Query "aumentar volume" retorna doc de mídia
- [ ] Top-k é respeitado

**Teste de Integração (Etapa 2.1):**

- [ ] Indexação completa dos documentos
- [ ] Busca retorna resultados relevantes
- [ ] Latência <100ms

---

### Etapa 2.2: LLM (Raciocínio)

**Objetivo:** Processar texto + contexto e gerar intenção estruturada

#### Atividade 2.2.1: Integrar llama.cpp

`src/mascate/intelligence/llm.py`:

- Carregar Granite 4.0 via llama-cpp-python
- Configurar para GPU (n_gpu_layers=-1)
- Configurar contexto (n_ctx=2048)

**Teste Unitário:**

- [ ] Modelo carrega na GPU
- [ ] Gera texto sem erro
- [ ] Uso de VRAM dentro do esperado

#### Atividade 2.2.2: Criar Prompt Template

```
Você é um assistente de sistema Linux. Analise o pedido do usuário e o contexto fornecido.
Responda APENAS com um JSON válido no formato especificado.

## Contexto Recuperado:
{context}

## Pedido do Usuário:
{user_input}

## Formato de Resposta (JSON):
{
  "action": "ACAO",
  "target": "alvo",
  "args": "argumentos opcionais",
  "confidence": 0.0-1.0,
  "requires_confirmation": true/false
}

## Ações Disponíveis:
- OPEN_APP: Abrir aplicativo
- OPEN_URL: Abrir URL no navegador
- OPEN_FOLDER: Abrir pasta no gerenciador de arquivos
- RUN_COMMAND: Executar comando no terminal
- MEDIA_PLAY_PAUSE: Play/Pause mídia
- MEDIA_NEXT: Próxima faixa
- MEDIA_PREV: Faixa anterior
- VOLUME_UP: Aumentar volume
- VOLUME_DOWN: Diminuir volume
- VOLUME_MUTE: Mutar/desmutar
- KEY_PRESS: Simular tecla
- UNKNOWN: Não entendi o pedido

JSON:
```

**Teste Unitário:**

- [ ] Template formata corretamente
- [ ] Variáveis são substituídas

#### Atividade 2.2.3: Implementar Inferência

- Montar prompt com contexto do RAG
- Chamar LLM
- Extrair JSON da resposta

**Teste Unitário:**

- [ ] Inferência retorna texto
- [ ] JSON é extraído corretamente
- [ ] Latência <500ms

**Teste de Integração (Etapa 2.2):**

- [ ] "abre o firefox" → JSON com OPEN_APP
- [ ] "aumenta o volume" → JSON com VOLUME_UP
- [ ] Comandos desconhecidos → UNKNOWN

---

### Etapa 2.3: Validação de Output (GBNF)

**Objetivo:** Garantir que LLM sempre gere JSON válido

#### Atividade 2.3.1: Criar Gramática GBNF

`src/mascate/intelligence/grammar.gbnf`:

```gbnf
root ::= object
object ::= "{" ws members ws "}"
members ::= pair ("," ws pair)*
pair ::= string ":" ws value
string ::= "\"" [a-zA-Z_]+ "\""
value ::= string | number | "true" | "false" | "null"
number ::= [0-9]+ ("." [0-9]+)?
ws ::= [ \t\n]*
```

**Teste Unitário:**

- [ ] Gramática é válida
- [ ] Parseia JSONs de exemplo

#### Atividade 2.3.2: Integrar GBNF no LLM

Passar gramática como parâmetro na inferência.

**Teste Unitário:**

- [ ] LLM respeita gramática
- [ ] Output é sempre JSON válido
- [ ] Não há texto fora do JSON

#### Atividade 2.3.3: Implementar Validação de Schema

Validar que JSON contém campos obrigatórios:

- `action`: string (enum válido)
- `target`: string
- `confidence`: float

**Teste Unitário:**

- [ ] JSON válido passa
- [ ] JSON com campo faltando falha
- [ ] JSON com action inválida falha

**Teste de Integração (Etapa 2.3):**

- [ ] 100 inferências → 100% JSON válido
- [ ] Todos os JSONs passam validação de schema
- [ ] Nenhuma alucinação de texto

---

### Teste End-to-End (Fase 2)

- [ ] Texto "abre o firefox" → busca RAG → LLM → JSON válido
- [ ] Texto "toca a música" → JSON com MEDIA_PLAY_PAUSE
- [ ] Texto "lista os arquivos" → JSON com RUN_COMMAND + "ls"
- [ ] Latência total <1s
- [ ] Nenhum JSON inválido

---

## FASE 3: Pipeline de Execução

**Objetivo:** Executar comandos de forma segura e fornecer feedback
**Critério de Sucesso (E2E):** JSON de comando → ação executada → feedback por voz

---

### Etapa 3.1: Parser de Comandos

**Objetivo:** Interpretar JSON e preparar execução

#### Atividade 3.1.1: Criar Modelos de Dados

`src/mascate/executor/models.py`:

```python
from dataclasses import dataclass
from enum import Enum

class ActionType(Enum):
    OPEN_APP = "OPEN_APP"
    OPEN_URL = "OPEN_URL"
    OPEN_FOLDER = "OPEN_FOLDER"
    RUN_COMMAND = "RUN_COMMAND"
    MEDIA_PLAY_PAUSE = "MEDIA_PLAY_PAUSE"
    # ... etc

@dataclass
class Command:
    action: ActionType
    target: str
    args: str | None
    confidence: float
    requires_confirmation: bool
```

**Teste Unitário:**

- [ ] Enum contém todas as ações
- [ ] Dataclass serializa/deserializa

#### Atividade 3.1.2: Implementar Parser

`src/mascate/executor/parser.py`:

- Receber JSON string
- Validar estrutura
- Retornar objeto Command

**Teste Unitário:**

- [ ] JSON válido → Command
- [ ] JSON inválido → erro claro
- [ ] Campos opcionais têm defaults

**Teste de Integração (Etapa 3.1):**

- [ ] Parser integra com output do LLM
- [ ] Todos os tipos de ação são parseados

---

### Etapa 3.2: Executor Agnóstico

**Objetivo:** Traduzir ações para comandos de sistema

#### Atividade 3.2.1: Criar Executor Base

`src/mascate/executor/executor.py`:

- Interface abstrata para executores
- Método `execute(command: Command) -> Result`

**Teste Unitário:**

- [ ] Interface está definida
- [ ] Result contém success/error/output

#### Atividade 3.2.2: Implementar Executor de Apps

Traduzir OPEN_APP, OPEN_URL, OPEN_FOLDER:

- `xdg-open` para URLs e pastas
- Nome do executável para apps

**Teste Unitário:**

- [ ] OPEN_URL abre navegador (mock)
- [ ] OPEN_FOLDER abre gerenciador (mock)
- [ ] OPEN_APP executa aplicativo (mock)

#### Atividade 3.2.3: Implementar Executor de Mídia

Traduzir MEDIA*\* e VOLUME*\*:

- `playerctl` para controle de mídia
- `pactl` para volume

**Teste Unitário:**

- [ ] MEDIA_PLAY_PAUSE chama playerctl
- [ ] VOLUME_UP aumenta volume
- [ ] Comandos são construídos corretamente

#### Atividade 3.2.4: Implementar Executor de Terminal

Traduzir RUN_COMMAND:

- Abrir terminal com comando
- Usar terminal configurado (ghostty, etc.)

**Teste Unitário:**

- [ ] Comando é passado para terminal
- [ ] Terminal correto é usado

#### Atividade 3.2.5: Implementar Executor de Teclado

Traduzir KEY_PRESS:

- Usar ydotool para simular teclas

**Teste Unitário:**

- [ ] Tecla é simulada corretamente
- [ ] Combinações (Ctrl+C) funcionam

**Teste de Integração (Etapa 3.2):**

- [ ] Cada tipo de ação executa corretamente
- [ ] Erros são capturados e reportados
- [ ] Logs registram execução

---

### Etapa 3.3: Sistema de Segurança

**Objetivo:** Validar comandos antes de executar

#### Atividade 3.3.1: Implementar Blacklist

`src/mascate/executor/security.py`:

- Carregar lista de comandos bloqueados do config
- Verificar se comando contém padrão bloqueado

**Teste Unitário:**

- [ ] `rm -rf /` é bloqueado
- [ ] `rm arquivo.txt` é permitido
- [ ] Padrões parciais são detectados

#### Atividade 3.3.2: Implementar Lista de Confirmação

Comandos que requerem confirmação:

- `rm` (qualquer)
- `sudo`
- `chmod`, `chown`

**Teste Unitário:**

- [ ] `sudo apt update` requer confirmação
- [ ] `ls` não requer confirmação
- [ ] Lista é configurável

#### Atividade 3.3.3: Implementar Prompt de Confirmação

- Mostrar comando ao usuário
- Aguardar input do teclado (Y/N)
- Para sudo, solicitar senha

**Teste Unitário:**

- [ ] Confirmação Y executa
- [ ] Confirmação N cancela
- [ ] Timeout cancela

#### Atividade 3.3.4: Implementar Sandbox (Opcional)

Se possível, executar comandos em ambiente isolado.

**Teste Unitário:**

- [ ] Comando roda em sandbox
- [ ] Acesso a sistema é limitado

**Teste de Integração (Etapa 3.3):**

- [ ] Comando perigoso → prompt de confirmação
- [ ] Comando bloqueado → erro
- [ ] Comando normal → execução direta

---

### Etapa 3.4: Feedback (TTS)

**Objetivo:** Informar usuário sobre resultado da ação

#### Atividade 3.4.1: Integrar Piper TTS

`src/mascate/audio/tts.py`:

- Carregar modelo pt-BR
- Converter texto em áudio
- Reproduzir áudio

**Teste Unitário:**

- [ ] Modelo carrega sem erro
- [ ] Gera áudio para texto
- [ ] Áudio é reproduzível

#### Atividade 3.4.2: Criar Templates de Resposta

```python
RESPONSES = {
    "success": "Pronto, {action} executado.",
    "error": "Não consegui {action}. Erro: {error}",
    "confirmation": "Você quer {action}? Confirme no teclado.",
    "blocked": "Este comando não é permitido por segurança.",
    "unknown": "Não entendi o que você quer fazer.",
}
```

**Teste Unitário:**

- [ ] Templates formatam corretamente
- [ ] Variáveis são substituídas

#### Atividade 3.4.3: Implementar Fila de Áudio

Evitar sobreposição de falas:

- Queue de mensagens
- Reproduzir uma por vez

**Teste Unitário:**

- [ ] Mensagens entram na fila
- [ ] Reprodução é sequencial

**Teste de Integração (Etapa 3.4):**

- [ ] Ação bem-sucedida → feedback de sucesso
- [ ] Ação com erro → feedback de erro
- [ ] Latência TTS <200ms

---

### Teste End-to-End (Fase 3)

- [ ] JSON OPEN_URL → Firefox abre → "Pronto, navegador aberto"
- [ ] JSON VOLUME_UP → Volume aumenta → "Volume aumentado"
- [ ] JSON com `rm` → Confirmação pedida → Executa após Y
- [ ] JSON bloqueado → "Comando não permitido"
- [ ] Latência execução + feedback <500ms

---

## FASE 4: Integração e Polish

**Objetivo:** Unir todos os pipelines e adicionar interface/logs
**Critério de Sucesso (E2E):** Fluxo completo funciona com interface visual e métricas

---

### Etapa 4.1: Orquestrador Central

**Objetivo:** Coordenar todos os módulos

#### Atividade 4.1.1: Criar State Machine

`src/mascate/core/orchestrator.py`:

Estados:

- IDLE: Aguardando wake word
- LISTENING: Capturando áudio do usuário
- PROCESSING: STT + RAG + LLM
- EXECUTING: Executando comando
- SPEAKING: Reproduzindo feedback

**Teste Unitário:**

- [ ] Transições de estado são válidas
- [ ] Estados inválidos são rejeitados

#### Atividade 4.1.2: Implementar Event Loop

Loop principal:

1. Capturar áudio
2. Verificar wake word
3. Se ativo, processar pipeline
4. Voltar ao idle

**Teste Unitário:**

- [ ] Loop roda continuamente
- [ ] Eventos são processados
- [ ] Graceful shutdown funciona

#### Atividade 4.1.3: Implementar Error Handling

- Capturar exceções em cada estágio
- Log de erros
- Feedback ao usuário
- Recuperação para estado IDLE

**Teste Unitário:**

- [ ] Erro no STT → feedback + volta ao idle
- [ ] Erro no LLM → feedback + volta ao idle
- [ ] Sistema não crasha

**Teste de Integração (Etapa 4.1):**

- [ ] Fluxo completo funciona
- [ ] Erros são tratados gracefully
- [ ] Sistema é responsivo

---

### Etapa 4.2: Interface (CLI + Rich)

**Objetivo:** Fornecer feedback visual durante operação

#### Atividade 4.2.1: Criar HUD com Rich

`src/mascate/interface/hud.py`:

Componentes:

- Status atual (Ouvindo, Processando, etc.)
- Última transcrição
- Último comando
- Métricas básicas (latência, uso de memória)

**Teste Unitário:**

- [ ] HUD renderiza sem erro
- [ ] Atualizações são refletidas
- [ ] Cores são aplicadas

#### Atividade 4.2.2: Implementar Live Display

Usar `rich.live` para atualização em tempo real.

**Teste Unitário:**

- [ ] Display atualiza em tempo real
- [ ] Não bloqueia o loop principal

#### Atividade 4.2.3: Implementar CLI de Inicialização

`src/mascate/interface/cli.py`:

Comandos:

- `mascate run`: Iniciar assistente
- `mascate config`: Mostrar configuração
- `mascate test-audio`: Testar microfone
- `mascate test-tts`: Testar voz

**Teste Unitário:**

- [ ] Comandos são parseados
- [ ] Help é exibido
- [ ] Erros são claros

**Teste de Integração (Etapa 4.2):**

- [ ] Interface mostra estados corretamente
- [ ] Transições são visíveis
- [ ] UX é fluida

---

### Etapa 4.3: Logs e Métricas

**Objetivo:** Registrar operações e medir performance

#### Atividade 4.3.1: Configurar Sistema de Logs

`src/mascate/core/logging.py`:

Níveis:

- DEBUG: Detalhes internos
- INFO: Operações normais
- WARNING: Situações anormais
- ERROR: Falhas

Destinos:

- Console (Rich formatted)
- Arquivo (rotativo)

**Teste Unitário:**

- [ ] Logs são escritos em arquivo
- [ ] Rotação funciona
- [ ] Níveis são respeitados

#### Atividade 4.3.2: Implementar Métricas de Latência

Medir tempo de cada estágio:

- Wake word → STT
- STT → RAG
- RAG → LLM
- LLM → Executor
- Executor → TTS

**Teste Unitário:**

- [ ] Tempos são medidos
- [ ] Métricas são agregadas
- [ ] Relatório é gerado

#### Atividade 4.3.3: Implementar Métricas de Recursos

Medir:

- Uso de VRAM
- Uso de RAM
- Uso de CPU

**Teste Unitário:**

- [ ] Métricas são coletadas
- [ ] Alertas para uso alto

#### Atividade 4.3.4: Implementar Dashboard de Métricas

Mostrar no HUD:

- Latência média por estágio
- Taxa de sucesso
- Uso de recursos

**Teste Unitário:**

- [ ] Dashboard renderiza
- [ ] Dados são atualizados

**Teste de Integração (Etapa 4.3):**

- [ ] Logs capturam operações
- [ ] Métricas são precisas
- [ ] Dashboard é útil

---

### Etapa 4.4: Testes End-to-End Completos

**Objetivo:** Validar sistema integrado

#### Atividade 4.4.1: Criar Suite de Testes E2E

`tests/e2e/test_full_flow.py`:

Cenários:

1. Abrir navegador com URL
2. Controlar mídia
3. Executar comando de terminal
4. Comando que requer confirmação
5. Comando bloqueado
6. Comando não reconhecido

**Teste Unitário:**

- [ ] Cenários são executáveis
- [ ] Mocks funcionam para áudio

#### Atividade 4.4.2: Criar Fixtures de Áudio

Gravar áudios de teste:

- "Hey Jarvis, abre o Google"
- "Hey Jarvis, aumenta o volume"
- "Hey Jarvis, lista os arquivos"

**Teste Unitário:**

- [ ] Áudios são carregados
- [ ] Transcrição é correta

#### Atividade 4.4.3: Implementar Testes Automatizados

Rodar todos os cenários automaticamente.

**Teste Unitário:**

- [ ] Suite completa passa
- [ ] Relatório é gerado

**Teste de Integração (Etapa 4.4):**

- [ ] Todos os cenários passam
- [ ] Latência dentro do SLA (<500ms target, <3s acceptable)
- [ ] Nenhum erro não tratado

---

### Teste End-to-End (Fase 4)

- [ ] Sistema inicia e mostra HUD
- [ ] Wake word ativa corretamente
- [ ] Comandos são executados
- [ ] Feedback é fornecido
- [ ] Métricas são registradas
- [ ] Logs são gerados
- [ ] Sistema roda por 10 minutos sem crash

---

## FASE 5: Validação Final

**Objetivo:** Garantir robustez e documentar
**Critério de Sucesso (E2E):** Sistema pronto para demonstração

---

### Etapa 5.1: Testes de Stress

**Objetivo:** Validar comportamento sob carga

#### Atividade 5.1.1: Teste de Uso Prolongado

- Rodar sistema por 1 hora
- Verificar memory leaks
- Verificar degradação de performance

**Teste:**

- [ ] Memória estável
- [ ] Latência estável
- [ ] Sem crashes

#### Atividade 5.1.2: Teste de Comandos Rápidos

- Enviar múltiplos comandos em sequência
- Verificar fila de processamento
- Verificar que nada é perdido

**Teste:**

- [ ] Comandos são enfileirados
- [ ] Todos são processados
- [ ] Ordem é mantida

#### Atividade 5.1.3: Teste de Recuperação de Erros

- Simular falhas em cada componente
- Verificar recuperação
- Verificar logs

**Teste:**

- [ ] Sistema se recupera de erros
- [ ] Logs registram falhas
- [ ] UX não é degradada

**Teste de Integração (Etapa 5.1):**

- [ ] Sistema passa em todos os testes de stress
- [ ] Performance dentro do SLA

---

### Etapa 5.2: Testes de Portabilidade

**Objetivo:** Verificar funcionamento em Ubuntu

#### Atividade 5.2.1: Preparar Ambiente Ubuntu

- VM ou máquina com Ubuntu 22.04+
- Instalar dependências via script
- Baixar modelos

**Teste:**

- [ ] Script de instalação funciona
- [ ] Modelos são baixados

#### Atividade 5.2.2: Executar Suite de Testes

- Rodar todos os testes E2E
- Documentar diferenças

**Teste:**

- [ ] Testes passam em Ubuntu
- [ ] Diferenças são mínimas

#### Atividade 5.2.3: Documentar Ajustes Necessários

Se houver diferenças, documentar e implementar abstrações.

**Teste:**

- [ ] Documentação atualizada
- [ ] Abstrações implementadas

**Teste de Integração (Etapa 5.2):**

- [ ] Sistema funciona em Ubuntu
- [ ] Documentação cobre diferenças

---

### Etapa 5.3: Documentação

**Objetivo:** Documentar uso e arquitetura

#### Atividade 5.3.1: Criar README.md

Conteúdo:

- Visão geral do projeto
- Requisitos de hardware/software
- Instalação
- Uso básico
- Configuração
- Troubleshooting

**Teste:**

- [ ] README é completo
- [ ] Instruções funcionam

#### Atividade 5.3.2: Documentar Arquitetura

- Diagrama de componentes
- Fluxo de dados
- Decisões técnicas

**Teste:**

- [ ] Diagramas são claros
- [ ] Decisões estão justificadas

#### Atividade 5.3.3: Criar Guia de Contribuição

- Como adicionar novos comandos
- Como adicionar novos documentos ao RAG
- Como testar

**Teste:**

- [ ] Guia é seguível
- [ ] Exemplos funcionam

**Teste de Integração (Etapa 5.3):**

- [ ] Documentação é completa
- [ ] Novo desenvolvedor consegue configurar ambiente

---

### Teste End-to-End (Fase 5)

- [ ] Sistema roda 1 hora sem problemas
- [ ] Testes de stress passam
- [ ] Sistema funciona em Ubuntu
- [ ] Documentação permite setup do zero
- [ ] PoC está pronta para demonstração

---

## Resumo do Plano

| Fase  | Etapas | Objetivo                                       |
| ----- | ------ | ---------------------------------------------- |
| **0** | 4      | Fundação: estrutura, deps, modelos, config     |
| **1** | 4      | Áudio: captura, wake, VAD, STT                 |
| **2** | 3      | Inteligência: RAG, LLM, GBNF                   |
| **3** | 4      | Execução: parser, executor, segurança, TTS     |
| **4** | 4      | Integração: orquestrador, interface, logs, E2E |
| **5** | 3      | Validação: stress, portabilidade, docs         |

**Total:** 5 Fases, 22 Etapas, ~80 Atividades

---

## Critérios de Sucesso da PoC

1. **Funcional:** Fluxo completo voz → ação → feedback funciona
2. **Performance:** Latência <3s (target <500ms para TTS)
3. **Segurança:** Comandos perigosos são bloqueados/confirmados
4. **Robustez:** Sistema roda 1 hora sem crash
5. **Portabilidade:** Funciona em Arch e Ubuntu
6. **Documentação:** Setup do zero é possível

---

## Próximos Passos Pós-PoC

1. Fine-tuning de voz (Piper)
2. Wake word customizado (PT-BR)
3. TUI completa (Textual)
4. Identidade visual "Frevo"
5. Suporte a mais distros/SOs
6. Expansão de comandos

---

_Documento gerado em 25/12/2024_
_Versão 1.0 - Aprovado para execução_
