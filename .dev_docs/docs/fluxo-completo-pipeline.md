# Fluxo Completo do Pipeline: Da Ativação à Resposta

**Projeto:** Mascate - Edge AI Assistant
**Versão:** 1.0
**Data:** 25/12/2024

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Capacidades de Streaming](#2-capacidades-de-streaming)
3. [Estados do Sistema](#3-estados-do-sistema)
4. [Detalhamento de Cada Etapa](#4-detalhamento-de-cada-etapa)
5. [Timeline de Latência](#5-timeline-de-latência)
6. [Fluxos Alternativos](#6-fluxos-alternativos)
7. [Alocação de Hardware](#7-alocação-de-hardware)

---

## 1. Visão Geral

O Mascate processa comandos de voz através de um pipeline de 10 etapas, desde a detecção da palavra de ativação até o feedback por voz.

### Diagrama Simplificado

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FLUXO MASCATE                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

[Usuário]                                                              [Sistema]
    │                                                                      │
    │  "Hey Jarvis"                                                        │
    │ ─────────────────────────────────────────────────────────────────▶  │
    │                                                                      │
    │                         ┌──────────────────┐                         │
    │                         │  1. WAKE WORD    │                         │
    │                         │  (openWakeWord)  │                         │
    │                         └────────┬─────────┘                         │
    │                                  │ detectado!                        │
    │                                  ▼                                   │
    │                         ┌──────────────────┐                         │
    │  "abre o Firefox"       │  2. LISTENING    │                         │
    │ ─────────────────────▶  │  (Captura Áudio) │                         │
    │                         └────────┬─────────┘                         │
    │                                  │                                   │
    │  (silêncio 300ms)               ▼                                   │
    │                         ┌──────────────────┐                         │
    │                         │  3. VAD          │                         │
    │                         │  (Silero)        │                         │
    │                         └────────┬─────────┘                         │
    │                                  │ fim de fala!                      │
    │                                  ▼                                   │
    │                         ┌──────────────────┐                         │
    │                         │  4. STT          │                         │
    │                         │  (Whisper)       │                         │
    │                         └────────┬─────────┘                         │
    │                                  │ "abre o firefox"                  │
    │                                  ▼                                   │
    │                         ┌──────────────────┐                         │
    │                         │  5. RAG          │                         │
    │                         │  (BGE-M3+Qdrant) │                         │
    │                         └────────┬─────────┘                         │
    │                                  │ contexto recuperado               │
    │                                  ▼                                   │
    │                         ┌──────────────────┐                         │
    │                         │  6. LLM          │                         │
    │                         │  (Granite+GBNF)  │                         │
    │                         └────────┬─────────┘                         │
    │                                  │ {"action":"OPEN_APP"...}          │
    │                                  ▼                                   │
    │                         ┌──────────────────┐                         │
    │                         │  7. SEGURANÇA    │                         │
    │                         │  (Blacklist)     │                         │
    │                         └────────┬─────────┘                         │
    │                                  │ aprovado!                         │
    │                                  ▼                                   │
    │                         ┌──────────────────┐                         │
    │                         │  8. EXECUTOR     │                         │
    │                         │  (xdg-open)      │                         │
    │                         └────────┬─────────┘                         │
    │                                  │ Firefox abre                      │
    │                                  ▼                                   │
    │                         ┌──────────────────┐                         │
    │  "Pronto, Firefox       │  9. TTS          │                         │
    │   aberto"               │  (Piper)         │                         │
    │ ◀─────────────────────  └──────────────────┘                         │
    │                                                                      │
    │                         ┌──────────────────┐                         │
    │                         │  10. IDLE        │                         │
    │                         │  (Aguardando)    │                         │
    │                         └──────────────────┘                         │
```

---

## 2. Capacidades de Streaming

### 2.1. Whisper (STT) - Suporta Streaming Real-Time

**Confirmado**: O `whisper.cpp` suporta transcrição em tempo real através do executável `whisper-stream`.

**Características:**

- Processa áudio em chunks incrementais
- Suporta callbacks para novos segmentos transcritos
- Pode ser integrado com VAD para melhor performance
- Parâmetros configuráveis: `--step` (intervalo), `--length` (tamanho do chunk)

**Exemplo de uso (CLI):**

```bash
./build/bin/whisper-stream \
    -m models/ggml-large-v3-q5_k_m.bin \
    -t 8 \
    --step 500 \
    --length 5000 \
    -l pt \
    --vad \
    -vm models/silero_vad.bin
```

**Para a PoC:**

- **Opção 1 (Simples)**: Modo batch - aguarda VAD detectar fim da fala, depois transcreve tudo
- **Opção 2 (Avançado)**: Modo streaming - transcreve enquanto usuário fala

**Recomendação para PoC:** Começar com modo batch (mais simples), evoluir para streaming depois.

### 2.2. Piper (TTS) - Suporta Streaming

**Confirmado**: O Piper suporta síntese em streaming através do método `synthesize_stream_raw()`.

**Características:**

- Gera áudio em chunks incrementais
- Permite reprodução antes da síntese completa
- Output: 16-bit PCM, mono, 22050 Hz

**Exemplo de uso (Python):**

```python
from piper import PiperVoice

voice = PiperVoice.load("pt_BR-faber-medium.onnx")

# Streaming: reproduz enquanto gera
for audio_bytes in voice.synthesize_stream_raw(text, sentence_silence=0.0):
    # Enviar audio_bytes para o speaker imediatamente
    audio_output.write(audio_bytes)
```

**Para a PoC:**

- **Opção 1 (Simples)**: Gerar WAV completo, depois reproduzir
- **Opção 2 (Avançado)**: Streaming - reproduzir enquanto gera

**Recomendação para PoC:** Implementar streaming desde o início (reduz latência percebida significativamente).

### 2.3. Resumo de Streaming

| Componente        | Suporta Streaming | Recomendação PoC                 | Benefício                         |
| ----------------- | ----------------- | -------------------------------- | --------------------------------- |
| **Whisper (STT)** | Sim               | Batch primeiro, streaming depois | Simplifica implementação inicial  |
| **Piper (TTS)**   | Sim               | Streaming desde o início         | Reduz Time-to-First-Audio em ~50% |

---

## 3. Estados do Sistema

O sistema opera como uma máquina de estados finitos:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MÁQUINA DE ESTADOS                           │
└─────────────────────────────────────────────────────────────────┘

                         ┌──────────┐
                         │   IDLE   │◀─────────────────────────┐
                         └────┬─────┘                          │
                              │                                │
                    Wake Word detectado                        │
                              │                                │
                              ▼                                │
                         ┌──────────┐                          │
                         │LISTENING │                          │
                         └────┬─────┘                          │
                              │                                │
                    VAD detecta fim de fala                    │
                              │                                │
                              ▼                                │
                       ┌────────────┐                          │
                       │PROCESSING  │                          │
                       └────┬───────┘                          │
                            │                                  │
              ┌─────────────┼─────────────┐                    │
              ▼             ▼             ▼                    │
        ┌──────────┐  ┌──────────┐  ┌──────────┐              │
        │EXECUTING │  │CONFIRMING│  │ BLOCKED  │              │
        └────┬─────┘  └────┬─────┘  └────┬─────┘              │
             │             │             │                     │
             ▼             ▼             ▼                     │
        ┌──────────┐  ┌──────────┐  ┌──────────┐              │
        │ SPEAKING │  │ SPEAKING │  │ SPEAKING │              │
        └────┬─────┘  └────┬─────┘  └────┬─────┘              │
             │             │             │                     │
             └─────────────┴─────────────┴─────────────────────┘
```

### Descrição dos Estados

| Estado         | Descrição                                 | Próximo Estado                    |
| -------------- | ----------------------------------------- | --------------------------------- |
| **IDLE**       | Sistema em repouso, monitorando wake word | LISTENING                         |
| **LISTENING**  | Capturando áudio do usuário               | PROCESSING                        |
| **PROCESSING** | STT + RAG + LLM em execução               | EXECUTING, CONFIRMING, ou BLOCKED |
| **EXECUTING**  | Executando comando no sistema             | SPEAKING                          |
| **CONFIRMING** | Aguardando confirmação do usuário         | EXECUTING ou SPEAKING             |
| **BLOCKED**    | Comando bloqueado por segurança           | SPEAKING                          |
| **SPEAKING**   | Reproduzindo feedback por voz             | IDLE                              |

---

## 4. Detalhamento de Cada Etapa

### ESTADO INICIAL: IDLE (Repouso)

```
┌─────────────────────────────────────────────────────────────────┐
│  ESTADO: IDLE                                                   │
│                                                                 │
│  O que está acontecendo:                                        │
│  • Microfone capturando áudio continuamente                     │
│  • Buffer circular armazenando últimos 0.5s                     │
│  • openWakeWord analisando cada chunk de áudio                  │
│  • CPU: ~2-5% (wake word é muito leve)                          │
│  • GPU: Ociosa                                                  │
│                                                                 │
│  Pseudocódigo:                                                  │
│  while state == IDLE:                                           │
│      chunk = microphone.capture(1024 samples)                   │
│      circular_buffer.add(chunk)                                 │
│      score = wake_word.analyze(chunk)                           │
│      if score > 0.5:                                            │
│          state = LISTENING                                      │
│          snapshot = circular_buffer.copy()  # últimos 0.5s      │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 1: WAKE WORD - Detecção de "Hey Jarvis"

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 1: Detecção de Wake Word                                 │
│  Componente: openWakeWord                                       │
│  Hardware: CPU (baixa prioridade)                               │
│  Tempo: ~10-50ms                                                │
│                                                                 │
│  Entrada:                                                       │
│  • Chunk de áudio (1024 samples @ 16kHz = 64ms)                 │
│                                                                 │
│  Processamento:                                                 │
│  1. openWakeWord processa chunk com modelo ONNX                 │
│  2. Retorna probabilidade de detecção (0.0 a 1.0)               │
│  3. Se probabilidade > threshold (0.5): ATIVADO!                │
│                                                                 │
│  Saída:                                                         │
│  • Evento: "wake_word_detected"                                 │
│  • Snapshot do buffer circular (0.5s anteriores)                │
│  • Mudança de estado: IDLE → LISTENING                          │
│                                                                 │
│  Por que guardar o buffer anterior?                             │
│  O usuário pode começar a falar o comando antes do wake word    │
│  terminar: "Hey Jarvis abre o Firefox" - "abre" já começou!     │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 2: LISTENING - Captura do Comando

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 2: Captura de Áudio do Comando                           │
│  Componente: sounddevice + buffer                               │
│  Hardware: CPU                                                  │
│  Tempo: Variável (depende do usuário falar)                     │
│                                                                 │
│  Entrada:                                                       │
│  • Buffer inicial (0.5s do snapshot da wake word)               │
│  • Áudio contínuo do microfone                                  │
│                                                                 │
│  Processamento:                                                 │
│  1. Iniciar com snapshot do buffer circular                     │
│  2. Continuar capturando áudio do microfone                     │
│  3. Enviar chunks para VAD em paralelo                          │
│  4. Acumular em buffer de gravação                              │
│                                                                 │
│  Interface (Rich):                                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🎤 Ouvindo...                                               ││
│  │ ████████░░░░░░░░ (indicador de amplitude)                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Condições de saída:                                            │
│  • VAD detecta silêncio > 300ms → passa para STT                │
│  • Timeout de 30s → cancela e volta ao IDLE                     │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 3: VAD - Detecção de Fim de Fala

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 3: Voice Activity Detection                              │
│  Componente: Silero VAD v5                                      │
│  Hardware: CPU (ONNX)                                           │
│  Tempo: ~10-20ms por chunk                                      │
│                                                                 │
│  Entrada:                                                       │
│  • Chunks de áudio enquanto usuário fala                        │
│                                                                 │
│  Processamento:                                                 │
│  1. Silero VAD analisa cada chunk                               │
│  2. Retorna probabilidade de "voz presente" (0.0 a 1.0)         │
│  3. Mantém contador de frames silenciosos                       │
│                                                                 │
│  Lógica de detecção:                                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ if voice_probability < 0.3:                                 ││
│  │     silent_frames += 1                                      ││
│  │ else:                                                       ││
│  │     silent_frames = 0                                       ││
│  │                                                             ││
│  │ if silent_frames * frame_duration > 300ms:                  ││
│  │     → FIM DA FALA DETECTADO                                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Saída:                                                         │
│  • Evento: "speech_ended"                                       │
│  • Buffer de áudio completo (início ao fim da fala)             │
│  • Mudança de estado: LISTENING → PROCESSING                    │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 4: STT - Transcrição

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 4: Speech-to-Text                                        │
│  Componente: Whisper Large v3 (whisper.cpp)                     │
│  Hardware: CPU (4-6 threads)                                    │
│  Quantização: Q5_K_M                                            │
│  Tempo: ~200-500ms (batch mode)                                 │
│                                                                 │
│  Entrada:                                                       │
│  • Buffer de áudio completo (ex: 2.5 segundos)                  │
│  • Formato: float32, 16kHz, mono                                │
│                                                                 │
│  Processamento:                                                 │
│  1. Carregar modelo Whisper (se não carregado)                  │
│  2. Configurar idioma: português                                │
│  3. Executar transcrição (greedy ou beam search)                │
│  4. Normalizar texto de saída                                   │
│                                                                 │
│  Interface (Rich):                                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 💭 Processando...                                           ││
│  │ ⠋ Transcrevendo áudio                                       ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Pós-processamento:                                             │
│  • Normalizar caixa (lowercase)                                 │
│  • Remover pontuação excessiva                                  │
│  • Remover filler words ("ahn", "tipo", "né")                   │
│                                                                 │
│  Saída:                                                         │
│  • Texto transcrito: "abre o firefox"                           │
│  • Confiança: 0.95                                              │
│  • Idioma detectado: pt                                         │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 5: RAG - Recuperação de Contexto

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 5: Retrieval-Augmented Generation                        │
│  Componentes: BGE-M3 + Qdrant                                   │
│  Hardware: CPU + RAM                                            │
│  Tempo: ~30-100ms                                               │
│                                                                 │
│  Entrada:                                                       │
│  • Texto transcrito: "abre o firefox"                           │
│                                                                 │
│  Processamento:                                                 │
│  1. Gerar embedding da query com BGE-M3:                        │
│     • Embedding denso (semântico): vetor 1024 dims              │
│     • Embedding esparso (keywords): {"firefox": 0.9, ...}       │
│                                                                 │
│  2. Busca híbrida no Qdrant:                                    │
│     • Combina similaridade densa + match de keywords            │
│     • Retorna top-k documentos mais relevantes (k=3)            │
│                                                                 │
│  Resultado da busca:                                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Doc 1 (score: 0.92): system_actions.md                      ││
│  │ "Para abrir qualquer aplicativo, use o nome do executável   ││
│  │  ou xdg-open para URLs e arquivos..."                       ││
│  │                                                             ││
│  │ Doc 2 (score: 0.78): linux_basics.md                        ││
│  │ "Firefox é um navegador web. Executável: firefox"           ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Saída:                                                         │
│  • Contexto formatado para injeção no prompt do LLM             │
│  • Metadados dos documentos recuperados                         │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 6: LLM - Raciocínio

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 6: Inferência do LLM                                     │
│  Componente: Granite 4.0 Hybrid 1B (llama.cpp)                  │
│  Hardware: GPU (100% VRAM)                                      │
│  Quantização: Q8_0                                              │
│  Tempo: ~50-200ms                                               │
│                                                                 │
│  Entrada (Prompt Montado):                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Você é um assistente de sistema Linux.                      ││
│  │                                                             ││
│  │ ## Contexto Recuperado:                                     ││
│  │ Para abrir qualquer aplicativo, use o nome do executável    ││
│  │ ou xdg-open para URLs e arquivos. Firefox é um navegador    ││
│  │ web. Executável: firefox                                    ││
│  │                                                             ││
│  │ ## Pedido do Usuário:                                       ││
│  │ abre o firefox                                              ││
│  │                                                             ││
│  │ ## Responda com JSON:                                       ││
│  │ {"action": "...", "target": "...", ...}                     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Processamento:                                                 │
│  1. Prompt é tokenizado                                         │
│  2. GBNF grammar força output JSON válido                       │
│  3. Inferência com temperature=0.1 (determinístico)             │
│  4. Geração para quando JSON fecha                              │
│                                                                 │
│  Saída (JSON garantido pelo GBNF):                              │
│  {                                                              │
│    "action": "OPEN_APP",                                        │
│    "target": "firefox",                                         │
│    "args": null,                                                │
│    "confidence": 0.95,                                          │
│    "requires_confirmation": false                               │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 7: SEGURANÇA - Validação

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 7: Verificação de Segurança                              │
│  Componente: Python (Guarda-Costas)                             │
│  Hardware: CPU                                                  │
│  Tempo: <5ms                                                    │
│                                                                 │
│  Entrada:                                                       │
│  • Command object parseado do JSON                              │
│                                                                 │
│  Verificações:                                                  │
│  1. ✓ Ação está na lista de ações permitidas?                   │
│  2. ✓ Target está na blacklist?                                 │
│  3. ✓ Requer confirmação?                                       │
│  4. ✓ Requer sudo?                                              │
│                                                                 │
│  Cenários de resultado:                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ APPROVED:                                                   ││
│  │   Comando seguro → executa diretamente                      ││
│  │   Exemplo: OPEN_APP "firefox"                               ││
│  │                                                             ││
│  │ REQUIRES_CONFIRMATION:                                      ││
│  │   Comando sensível → pede confirmação no teclado            ││
│  │   Exemplo: RUN_COMMAND "rm arquivo.txt"                     ││
│  │   TTS: "Quer remover arquivo.txt? Confirme com Y."          ││
│  │                                                             ││
│  │ REQUIRES_PASSWORD:                                          ││
│  │   Comando precisa de sudo → pede senha no teclado           ││
│  │   Exemplo: RUN_COMMAND "sudo apt update"                    ││
│  │   TTS: "Este comando precisa de permissão. Digite a senha." ││
│  │                                                             ││
│  │ BLOCKED:                                                    ││
│  │   Comando na blacklist → rejeita                            ││
│  │   Exemplo: RUN_COMMAND "rm -rf /"                           ││
│  │   TTS: "Este comando não é permitido por segurança."        ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Saída (para OPEN_APP firefox):                                 │
│  • Status: APPROVED                                             │
│  • Pode executar: True                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 8: EXECUTOR - Ação no Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 8: Execução do Comando                                   │
│  Componente: subprocess + wrappers agnósticos                   │
│  Hardware: CPU                                                  │
│  Tempo: ~50-200ms                                               │
│                                                                 │
│  Entrada:                                                       │
│  • Command: OPEN_APP, target: "firefox"                         │
│                                                                 │
│  Tradução para Comando Agnóstico:                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Ação                → Comando de Sistema                    ││
│  │ ────────────────────────────────────────────────────────────││
│  │ OPEN_APP "firefox"  → subprocess.run(["firefox"])           ││
│  │ OPEN_URL "g1.com"   → xdg-open https://g1.com.br            ││
│  │ OPEN_FOLDER "~"     → xdg-open /home/user                   ││
│  │ VOLUME_UP           → pactl set-sink-volume +5%             ││
│  │ VOLUME_DOWN         → pactl set-sink-volume -5%             ││
│  │ VOLUME_MUTE         → pactl set-sink-mute toggle            ││
│  │ MEDIA_PLAY_PAUSE    → playerctl play-pause                  ││
│  │ MEDIA_NEXT          → playerctl next                        ││
│  │ MEDIA_PREV          → playerctl previous                    ││
│  │ RUN_COMMAND "ls"    → ghostty -e "ls; read"                 ││
│  │ KEY_PRESS "ctrl+c"  → ydotool key ctrl+c                    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Execução:                                                      │
│  • subprocess.Popen para não bloquear                           │
│  • Capturar exit code                                           │
│  • Timeout de 5 segundos para comandos que não retornam         │
│                                                                 │
│  Saída:                                                         │
│  • Result: SUCCESS                                              │
│  • Exit code: 0                                                 │
│  • Firefox inicia em background                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 9: TTS - Feedback por Voz

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 9: Text-to-Speech                                        │
│  Componente: Piper (VITS)                                       │
│  Hardware: CPU                                                  │
│  Voz: pt_BR-faber-medium (padrão)                               │
│  Tempo: ~100-200ms (geração) + reprodução                       │
│                                                                 │
│  Entrada:                                                       │
│  • Template: "Pronto, {action} executado."                      │
│  • Variáveis: action = "Firefox aberto"                         │
│  • Texto final: "Pronto, Firefox aberto."                       │
│                                                                 │
│  Processamento (Modo Streaming):                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ voice = PiperVoice.load("pt_BR-faber-medium.onnx")          ││
│  │                                                             ││
│  │ # Streaming: reproduz enquanto gera                         ││
│  │ for audio_bytes in voice.synthesize_stream_raw(text):       ││
│  │     audio_output.write(audio_bytes)                         ││
│  │     # Usuário já ouve enquanto resto é gerado               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Templates de resposta:                                         │
│  • Sucesso: "Pronto, {action} executado."                       │
│  • Erro: "Não consegui {action}. {error}"                       │
│  • Confirmação: "Quer {action}? Confirme no teclado."           │
│  • Bloqueado: "Este comando não é permitido por segurança."     │
│  • Desconhecido: "Não entendi o que você quer fazer."           │
│                                                                 │
│  Interface (Rich):                                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ✅ Comando executado                                        ││
│  │ 🔊 "Pronto, Firefox aberto."                                ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Saída:                                                         │
│  • Áudio reproduzido nos alto-falantes                          │
│  • Usuário ouve a confirmação                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Etapa 10: RETORNO AO IDLE

```
┌─────────────────────────────────────────────────────────────────┐
│  ESTADO: IDLE (Novamente)                                       │
│                                                                 │
│  Após o TTS terminar:                                           │
│  • Estado volta para IDLE                                       │
│  • Wake word listener reativado                                 │
│  • Buffer circular resetado                                     │
│  • Sistema aguarda próximo "Hey Jarvis"                         │
│                                                                 │
│  Log gerado:                                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ [10:30:45.000] INFO  Wake word detected                     ││
│  │ [10:30:45.050] INFO  State: IDLE → LISTENING                ││
│  │ [10:30:47.500] INFO  Speech ended (duration: 2.45s)         ││
│  │ [10:30:47.510] INFO  State: LISTENING → PROCESSING          ││
│  │ [10:30:47.860] INFO  STT result: "abre o firefox"           ││
│  │ [10:30:47.905] INFO  RAG: 2 documents retrieved             ││
│  │ [10:30:48.025] INFO  LLM: OPEN_APP target=firefox           ││
│  │ [10:30:48.030] INFO  Security: APPROVED                     ││
│  │ [10:30:48.115] INFO  Executor: firefox (exit_code=0)        ││
│  │ [10:30:48.120] INFO  State: PROCESSING → SPEAKING           ││
│  │ [10:30:49.620] INFO  TTS complete: "Pronto, Firefox aberto" ││
│  │ [10:30:49.625] INFO  State: SPEAKING → IDLE                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Métricas coletadas:                                            │
│  • Latência total (wake → idle): 4.625s                         │
│  • Tempo de fala do usuário: 2.45s                              │
│  • Processamento (STT→Executor): 0.61s                          │
│  • Reprodução TTS: 1.5s                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Timeline de Latência

### Cenário Típico: "Hey Jarvis, abre o Firefox"

```
Tempo (ms)    0    500   1000  1500  2000  2500  3000  3500  4000  4500  5000
              │     │     │     │     │     │     │     │     │     │     │
Wake Word     ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
              │ 50ms
              │
Usuário Fala  ░░░░██████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░
                        ~2450ms (variável)
                                              │
VAD (silêncio)                                ██████░░░░░░░░░░░░░░░░░░░░░░
                                              │ 300ms
                                                    │
STT                                                 ████████░░░░░░░░░░░░░░
                                                    │  350ms
                                                            │
RAG                                                         ██░░░░░░░░░░░░
                                                            │45ms
                                                              │
LLM                                                           ████░░░░░░░░
                                                              │ 120ms
                                                                  │
Segurança                                                         █░░░░░░░
                                                                  │5ms
                                                                   │
Executor                                                           ███░░░░
                                                                   │ 85ms
                                                                      │
TTS (streaming)                                                       █████
                                                                      1500ms
                                                                           │
                                                                           ▼
                                                              Usuário ouve resposta
```

### Breakdown de Latência

| Etapa               | Tempo   | Acumulado | Notas                  |
| ------------------- | ------- | --------- | ---------------------- |
| Wake Word           | 50ms    | 50ms      | Detecção instantânea   |
| Fala do Usuário     | ~2450ms | ~2500ms   | Variável               |
| VAD (silêncio)      | 300ms   | ~2800ms   | Configurável           |
| STT (Whisper)       | 350ms   | ~3150ms   | CPU, batch mode        |
| RAG (BGE-M3+Qdrant) | 45ms    | ~3195ms   | CPU+RAM                |
| LLM (Granite)       | 120ms   | ~3315ms   | GPU                    |
| Segurança           | 5ms     | ~3320ms   | CPU                    |
| Executor            | 85ms    | ~3405ms   | CPU                    |
| TTS (Piper)         | 1500ms  | ~4905ms   | CPU, inclui reprodução |

**Latência de Processamento (STT→Executor):** ~605ms
**Time-to-First-Audio (com streaming TTS):** ~3420ms + tempo de buffering inicial (~100ms)

---

## 6. Fluxos Alternativos

### 6.1. Comando com Confirmação

```
Usuário: "Hey Jarvis, apaga o arquivo teste.txt"

[Etapas 1-6 iguais ao fluxo normal]

Etapa 7 (Segurança):
├── Comando: RUN_COMMAND "rm teste.txt"
├── Detectado: "rm" na lista de confirmação
└── Status: REQUIRES_CONFIRMATION

Etapa 9a (TTS):
└── "Você quer remover teste.txt? Confirme com Y ou cancele com N."

Estado: CONFIRMING
├── Aguarda input do teclado...
│
├── [Y pressionado]
│   └── Etapa 8: Executa "rm teste.txt"
│   └── Etapa 9b: "Arquivo removido."
│   └── Estado → IDLE
│
├── [N pressionado]
│   └── Etapa 9b: "Comando cancelado."
│   └── Estado → IDLE
│
└── [Timeout 30s]
    └── Etapa 9b: "Tempo esgotado, cancelando."
    └── Estado → IDLE
```

### 6.2. Comando Bloqueado

```
Usuário: "Hey Jarvis, formata o disco"

[Etapas 1-6 iguais ao fluxo normal]

Etapa 7 (Segurança):
├── Comando: RUN_COMMAND contém padrão bloqueado
└── Status: BLOCKED

Etapa 9 (TTS):
└── "Este comando não é permitido por segurança."

Estado → IDLE
```

### 6.3. Comando Não Reconhecido

```
Usuário: "Hey Jarvis, faz um café"

[Etapas 1-5 iguais ao fluxo normal]

Etapa 6 (LLM):
└── {"action": "UNKNOWN", "confidence": 0.3}

Etapa 9 (TTS):
└── "Não entendi o que você quer fazer. Pode repetir?"

Estado → IDLE
```

### 6.4. Erro de Execução

```
Usuário: "Hey Jarvis, abre o programa_inexistente"

[Etapas 1-7 iguais ao fluxo normal]

Etapa 8 (Executor):
├── subprocess.run(["programa_inexistente"])
└── Exit code: 127 (comando não encontrado)

Etapa 9 (TTS):
└── "Não consegui abrir programa_inexistente. O programa não foi encontrado."

Estado → IDLE
```

---

## 7. Alocação de Hardware

### Distribuição de Recursos

```
┌─────────────────────────────────────────────────────────────────┐
│                    ALOCAÇÃO DE HARDWARE                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  GPU (GTX 1650 - 4GB VRAM)                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Granite 4.0 Hybrid 1B (Q8_0)                               ││
│  │  • Modelo: ~1.3 GB                                          ││
│  │  • KV Cache: ~300 MB (2048 tokens)                          ││
│  │  • Buffers CUDA: ~400 MB                                    ││
│  │  • Total: ~2.0 GB                                           ││
│  │  • Livre: ~1.4 GB (margem de segurança)                     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CPU (Ryzen 7 - 8c/16t)                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Thread Pool:                                               ││
│  │  • Whisper STT: 4-6 threads (alta prioridade)               ││
│  │  • BGE-M3: 2-4 threads (sob demanda)                        ││
│  │  • Piper TTS: 1-2 threads                                   ││
│  │  • Wake Word: 1 thread (baixa prioridade)                   ││
│  │  • VAD: compartilha com Wake Word                           ││
│  │  • Sistema: 2+ threads livres                               ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RAM (32 GB)                                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Alocação:                                                  ││
│  │  • Whisper Large v3: ~2.2 GB                                ││
│  │  • BGE-M3: ~2.5 GB                                          ││
│  │  • Qdrant (índice): ~500 MB                                 ││
│  │  • Piper: ~300 MB                                           ││
│  │  • Wake Word + VAD: ~200 MB                                 ││
│  │  • Python + buffers: ~1 GB                                  ││
│  │  • Total: ~6.7 GB                                           ││
│  │  • Livre: ~25 GB                                            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SSD                                                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Persistência:                                              ││
│  │  • Modelos: ~5 GB                                           ││
│  │  • Qdrant DB: variável                                      ││
│  │  • Logs: rotativo (max 50 MB)                               ││
│  │  • Knowledge Base: ~10 MB                                   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Tabela Resumo

| Componente       | Hardware | Memória      | Threads | Prioridade |
| ---------------- | -------- | ------------ | ------- | ---------- |
| Granite 4.0      | GPU      | ~2.0 GB VRAM | -       | Alta       |
| Whisper Large v3 | CPU      | ~2.2 GB RAM  | 4-6     | Alta       |
| BGE-M3           | CPU      | ~2.5 GB RAM  | 2-4     | Média      |
| Qdrant           | CPU      | ~500 MB RAM  | 1-2     | Média      |
| Piper TTS        | CPU      | ~300 MB RAM  | 1-2     | Média      |
| Silero VAD       | CPU      | ~100 MB RAM  | 1       | Baixa      |
| openWakeWord     | CPU      | ~100 MB RAM  | 1       | Baixa      |

---

## Conclusão

Este documento detalha o fluxo completo do pipeline do Mascate, desde a ativação por voz até o feedback sonoro. Os pontos-chave são:

1. **Whisper suporta streaming**, mas começaremos com batch mode para simplicidade
2. **Piper suporta streaming** e usaremos desde o início para reduzir latência
3. **Latência de processamento** (STT→Executor) é ~600ms
4. **Time-to-First-Audio** com streaming TTS é ~3.5s (incluindo fala do usuário)
5. **GPU é exclusiva** para o LLM (Granite)
6. **CPU gerencia** todo o resto (áudio, RAG, TTS)

---

_Documento gerado em 25/12/2024_
_Versão 1.0_
