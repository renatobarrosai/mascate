# Arquitetura do Mascate

Visao geral da arquitetura tecnica do sistema.

---

## Indice

1. [Visao Geral](#1-visao-geral)
2. [Componentes Principais](#2-componentes-principais)
3. [Fluxo de Dados](#3-fluxo-de-dados)
4. [Modelos de IA](#4-modelos-de-ia)
5. [Seguranca](#5-seguranca)

---

## 1. Visao Geral

O Mascate segue uma arquitetura de pipeline com separacao clara de responsabilidades:

```
┌─────────────────────────────────────────────────────────────────┐
│                         MASCATE                                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│     AUDIO       │   INTELLIGENCE  │         EXECUTOR            │
│  (Ouvido/Voz)   │    (Cerebro)    │     (Guarda-Costas)         │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ - Captura       │ - LLM (Granite) │ - Parser de comandos        │
│ - VAD (Silero)  │ - RAG (BGE-M3)  │ - Validacao de seguranca    │
│ - STT (Whisper) │ - Prompts       │ - Handlers de acao          │
│ - TTS (Piper)   │ - GBNF Grammar  │ - Blacklist/Whitelist       │
│ - Hotkey        │                 │                             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Principios de Design

1. **Separacao de Responsabilidades**
   - Cada modulo tem uma funcao especifica
   - Nenhuma logica de LLM no modulo de audio
   - Nenhuma logica de I/O no modulo de inteligencia

2. **Seguranca por Design**
   - LLM nunca executa comandos diretamente
   - Executor valida tudo antes de executar
   - Multiplas camadas de protecao

3. **Performance**
   - GPU exclusiva para LLM
   - Audio e RAG rodam em CPU
   - Pipeline de streaming para baixa latencia

---

## 2. Componentes Principais

### 2.1 Modulo Audio (`src/mascate/audio/`)

Responsavel por toda interacao de audio.

```
audio/
├── capture.py      # Captura de microfone
├── hotkey.py       # Ativacao por teclado
├── pipeline.py     # Orquestracao de audio
├── vad/            # Deteccao de voz (Silero)
├── wake/           # Wake word detection
├── stt/            # Speech-to-Text (Whisper)
└── tts/            # Text-to-Speech (Piper)
```

**Fluxo:**

```
Microfone → Captura → VAD → STT → Texto
                             ↓
Alto-falante ← TTS ← Resposta
```

### 2.2 Modulo Intelligence (`src/mascate/intelligence/`)

Processamento de linguagem natural e memoria.

```
intelligence/
├── brain.py        # Orquestrador principal
├── llm/            # LLM (Granite via llama.cpp)
│   ├── granite.py  # Interface com modelo
│   ├── prompts.py  # Templates de prompt
│   └── grammars/   # Gramaticas GBNF
└── rag/            # Memoria de longo prazo
    ├── embeddings.py   # BGE-M3
    ├── vectordb.py     # Qdrant
    └── retriever.py    # Busca semantica
```

**Fluxo:**

```
Texto → RAG (contexto) → LLM → JSON estruturado
```

### 2.3 Modulo Executor (`src/mascate/executor/`)

Execucao segura de comandos.

```
executor/
├── executor.py     # Orquestrador
├── parser.py       # JSON → Command
├── security.py     # Validacao de seguranca
├── registry.py     # Registro de handlers
└── handlers/       # Executores por tipo
    ├── app.py      # Abrir aplicativos
    ├── browser.py  # Navegacao web
    ├── media.py    # Controle de midia
    ├── file.py     # Operacoes de arquivo
    └── system.py   # Acoes de sistema
```

**Fluxo:**

```
JSON → Parser → Security → Handler → Acao no Sistema
```

### 2.4 Modulo Core (`src/mascate/core/`)

Orquestracao e infraestrutura.

```
core/
├── config.py       # Carregamento de config
├── exceptions.py   # Excecoes customizadas
├── logging.py      # Sistema de logs
└── orchestrator.py # Maquina de estados principal
```

### 2.5 Modulo Interface (`src/mascate/interface/`)

Interface com usuario.

```
interface/
├── cli.py          # Comandos de terminal
└── hud.py          # Interface visual (Rich)
```

---

## 3. Fluxo de Dados

### 3.1 Pipeline Completo

```
┌──────────────────────────────────────────────────────────────────┐
│  1. ATIVACAO                                                      │
│     Hotkey (Ctrl+Shift+M) ou Wake Word                           │
│                          ↓                                        │
├──────────────────────────────────────────────────────────────────┤
│  2. CAPTURA                                                       │
│     Microfone → Buffer Circular → VAD                            │
│                          ↓                                        │
├──────────────────────────────────────────────────────────────────┤
│  3. TRANSCRICAO                                                   │
│     Audio → Whisper STT → Texto                                  │
│     "Abre o Firefox"                                             │
│                          ↓                                        │
├──────────────────────────────────────────────────────────────────┤
│  4. INTERPRETACAO                                                 │
│     Texto → RAG (contexto) → Granite LLM → JSON                  │
│     {"action": "open_app", "target": "firefox"}                  │
│                          ↓                                        │
├──────────────────────────────────────────────────────────────────┤
│  5. VALIDACAO                                                     │
│     JSON → Parser → SecurityGuard → Validado?                    │
│                          ↓                                        │
├──────────────────────────────────────────────────────────────────┤
│  6. EXECUCAO                                                      │
│     Command → Handler → subprocess → Sistema                     │
│                          ↓                                        │
├──────────────────────────────────────────────────────────────────┤
│  7. FEEDBACK                                                      │
│     Resultado → Template → Piper TTS → Audio                     │
│     "Pronto, Firefox aberto."                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Maquina de Estados

```
                    ┌──────────┐
                    │   IDLE   │
                    └────┬─────┘
                         │ hotkey/wake
                         ↓
                    ┌──────────┐
                    │ LISTENING│
                    └────┬─────┘
                         │ fim de fala (VAD)
                         ↓
                    ┌──────────┐
                    │PROCESSING│
                    └────┬─────┘
                         │ intent processado
                         ↓
                    ┌──────────┐
          ┌─────────│EXECUTING │─────────┐
          │ high    └────┬─────┘         │ low/medium
          │ risk         │               │ risk
          ↓              │               ↓
    ┌──────────┐         │         ┌──────────┐
    │CONFIRMING│         │         │ SPEAKING │
    └────┬─────┘         │         └────┬─────┘
         │               │              │
         └───────────────┴──────────────┘
                         │
                         ↓
                    ┌──────────┐
                    │   IDLE   │
                    └──────────┘
```

### 3.3 Latencia Estimada

| Etapa     | Tempo  | Acumulado  |
| --------- | ------ | ---------- |
| VAD       | ~50ms  | 50ms       |
| STT       | ~100ms | 150ms      |
| RAG       | ~30ms  | 180ms      |
| LLM       | ~150ms | 330ms      |
| Execucao  | ~50ms  | 380ms      |
| TTS       | ~100ms | 480ms      |
| **Total** |        | **<500ms** |

---

## 4. Modelos de IA

### 4.1 Alocacao de Recursos

```
┌─────────────────────────────────────┐
│              GPU (VRAM)             │
│  ┌───────────────────────────────┐  │
│  │   Granite LLM (1.3GB)         │  │
│  │   + KV Cache (0.3GB)          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│              CPU (RAM)              │
│  ┌──────────┐ ┌──────────┐          │
│  │ Whisper  │ │  Piper   │          │
│  │  (3GB)   │ │ (100MB)  │          │
│  └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐          │
│  │  BGE-M3  │ │  Silero  │          │
│  │  (2GB)   │ │  (2MB)   │          │
│  └──────────┘ └──────────┘          │
└─────────────────────────────────────┘
```

### 4.2 Especificacoes dos Modelos

| Modelo      | Tamanho | Backend     | Device | Funcao          |
| ----------- | ------- | ----------- | ------ | --------------- |
| Granite 4.0 | 1.3GB   | llama.cpp   | GPU    | Interpretacao   |
| Whisper v3  | 3GB     | whisper.cpp | CPU    | Fala → Texto    |
| Piper       | 100MB   | ONNX        | CPU    | Texto → Fala    |
| BGE-M3      | 2GB     | ONNX        | CPU    | Embeddings      |
| Silero VAD  | 2MB     | ONNX        | CPU    | Deteccao de voz |

---

## 5. Seguranca

### 5.1 Arquitetura "Cerebro vs Guarda-Costas"

```
┌─────────────────┐         ┌─────────────────┐
│    CEREBRO      │  JSON   │  GUARDA-COSTAS  │
│   (Granite)     │ ──────> │    (Python)     │
│                 │         │                 │
│ - Interpreta    │         │ - Valida        │
│ - Deduz intent  │         │ - Bloqueia      │
│ - Gera JSON     │         │ - Executa       │
│                 │         │                 │
│ NAO executa     │         │ NAO interpreta  │
│ comandos!       │         │ semantica!      │
└─────────────────┘         └─────────────────┘
```

**Cerebro (LLM):**

- Interpreta linguagem natural
- Consulta memoria (RAG)
- Gera JSON estruturado
- **Nunca executa comandos**

**Guarda-Costas (Executor):**

- Valida JSON contra regras
- Verifica blacklist
- Pede confirmacao se necessario
- Executa via subprocess
- **Nao julga semantica, julga risco**

### 5.2 Camadas de Protecao

```
┌─────────────────────────────────────────────┐
│  1. GBNF Grammar                            │
│     LLM so gera JSON no formato esperado    │
├─────────────────────────────────────────────┤
│  2. Schema Validation                       │
│     Parser valida estrutura do JSON         │
├─────────────────────────────────────────────┤
│  3. Blacklist Check                         │
│     Bloqueia padroes perigosos              │
├─────────────────────────────────────────────┤
│  4. Path Protection                         │
│     Protege diretorios do sistema           │
├─────────────────────────────────────────────┤
│  5. Shell Injection Detection               │
│     Detecta caracteres maliciosos           │
├─────────────────────────────────────────────┤
│  6. Risk Assessment                         │
│     Classifica nivel de risco               │
├─────────────────────────────────────────────┤
│  7. User Confirmation                       │
│     Pede confirmacao para acoes HIGH risk   │
└─────────────────────────────────────────────┘
```

---

## Documentacao Tecnica Adicional

Para detalhes mais profundos, consulte:

- [Especificacoes de Modelos](technical/01-models-spec.md)
- [Fluxo do Pipeline](technical/02-pipeline-flow.md)
- [Estrategia de Seguranca](technical/07-security.md)
- [Gramaticas GBNF](technical/06-gbnf-strategy.md)
- [Arquitetura RAG](technical/05-rag-memory.md)

---

[Voltar ao README](../README.md) | [Anterior: Configuracao](configuration.md) | [Proximo: Desenvolvimento](development.md)
