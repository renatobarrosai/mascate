# Mascate - Fluxo do Pipeline

**Versao:** 1.0  
**Status:** Aprovado para Implementacao

Este documento detalha o fluxo completo do pipeline, desde a ativacao por voz ate o feedback sonoro.

---

## 1. Visao Geral

O Mascate processa comandos de voz atraves de um pipeline de 10 etapas:

```
[Usuario]                                                    [Sistema]
    |                                                            |
    | "Ei Painho"                                                |
    | -------------------------------------------------------->  |
    |                       1. WAKE WORD (openWakeWord)          |
    |                                |                           |
    | "abre o Firefox"              v                           |
    | -----------------------> 2. LISTENING (Captura Audio)      |
    |                                |                           |
    | (silencio 300ms)              v                           |
    |                       3. VAD (Silero)                      |
    |                                |                           |
    |                               v                           |
    |                       4. STT (Whisper)                     |
    |                                |                           |
    |                               v                           |
    |                       5. RAG (BGE-M3 + Qdrant)             |
    |                                |                           |
    |                               v                           |
    |                       6. LLM (Granite + GBNF)              |
    |                                |                           |
    |                               v                           |
    |                       7. SEGURANCA (Blacklist)             |
    |                                |                           |
    |                               v                           |
    |                       8. EXECUTOR (xdg-open)               |
    |                                |                           |
    | "Pronto, Firefox aberto"      v                           |
    | <----------------------- 9. TTS (Piper)                    |
    |                                |                           |
    |                               v                           |
    |                       10. IDLE (Aguardando)                |
```

---

## 2. Maquina de Estados

```
                         +----------+
                         |   IDLE   |<-------------------------+
                         +----+-----+                          |
                              |                                |
                    Wake Word detectado                        |
                              |                                |
                              v                                |
                         +----------+                          |
                         |LISTENING |                          |
                         +----+-----+                          |
                              |                                |
                    VAD detecta fim de fala                    |
                              |                                |
                              v                                |
                       +------------+                          |
                       |PROCESSING  |                          |
                       +-----+------+                          |
                             |                                 |
              +--------------+--------------+                  |
              v              v              v                  |
        +----------+   +----------+   +----------+             |
        |EXECUTING |   |CONFIRMING|   | BLOCKED  |             |
        +----+-----+   +----+-----+   +----+-----+             |
             |              |              |                   |
             v              v              v                   |
        +----------+   +----------+   +----------+             |
        | SPEAKING |   | SPEAKING |   | SPEAKING |             |
        +----+-----+   +----+-----+   +----+-----+             |
             |              |              |                   |
             +--------------+--------------+-------------------+
```

### Descricao dos Estados

| Estado         | Descricao                                 | Proximo Estado                    |
| :------------- | :---------------------------------------- | :-------------------------------- |
| **IDLE**       | Sistema em repouso, monitorando wake word | LISTENING                         |
| **LISTENING**  | Capturando audio do usuario               | PROCESSING                        |
| **PROCESSING** | STT + RAG + LLM em execucao               | EXECUTING, CONFIRMING, ou BLOCKED |
| **EXECUTING**  | Executando comando no sistema             | SPEAKING                          |
| **CONFIRMING** | Aguardando confirmacao do usuario         | EXECUTING ou SPEAKING             |
| **BLOCKED**    | Comando bloqueado por seguranca           | SPEAKING                          |
| **SPEAKING**   | Reproduzindo feedback por voz             | IDLE                              |

---

## 3. Detalhamento das Etapas

### Etapa 1: WAKE WORD

| Propriedade | Valor                  |
| :---------- | :--------------------- |
| Componente  | openWakeWord           |
| Hardware    | CPU (baixa prioridade) |
| Tempo       | ~10-50ms               |

**Fluxo:**

1. openWakeWord processa chunks de audio com modelo ONNX
2. Retorna probabilidade de deteccao (0.0 a 1.0)
3. Se probabilidade > threshold (0.5): ATIVADO!

**Por que guardar o buffer anterior?**
O usuario pode comecar a falar o comando antes do wake word terminar:
"Ei Painho abre o Firefox" - "abre" ja comecou!

---

### Etapa 2: LISTENING

| Propriedade | Valor                         |
| :---------- | :---------------------------- |
| Componente  | sounddevice + buffer          |
| Hardware    | CPU                           |
| Tempo       | Variavel (depende do usuario) |

**Fluxo:**

1. Iniciar com snapshot do buffer circular (0.5s anteriores)
2. Continuar capturando audio do microfone
3. Enviar chunks para VAD em paralelo
4. Acumular em buffer de gravacao

**Condicoes de saida:**

- VAD detecta silencio > 300ms -> passa para STT
- Timeout de 30s -> cancela e volta ao IDLE

---

### Etapa 3: VAD (Voice Activity Detection)

| Propriedade | Valor              |
| :---------- | :----------------- |
| Componente  | Silero VAD v5      |
| Hardware    | CPU (ONNX)         |
| Tempo       | ~10-20ms por chunk |

**Logica de deteccao:**

```python
if voice_probability < 0.3:
    silent_frames += 1
else:
    silent_frames = 0

if silent_frames * frame_duration > 300ms:
    # FIM DA FALA DETECTADO
```

---

### Etapa 4: STT (Speech-to-Text)

| Propriedade | Valor                          |
| :---------- | :----------------------------- |
| Componente  | Whisper Large v3 (whisper.cpp) |
| Hardware    | CPU (4-6 threads)              |
| Quantizacao | Q5_K_M                         |
| Tempo       | ~200-500ms (batch mode)        |

**Pos-processamento:**

- Normalizar caixa (lowercase)
- Remover pontuacao excessiva
- Remover filler words ("ahn", "tipo", "ne")

**Modos de operacao:**

- **Batch (PoC):** Aguarda VAD, depois transcreve tudo
- **Streaming (futuro):** Transcreve enquanto usuario fala

---

### Etapa 5: RAG (Retrieval-Augmented Generation)

| Propriedade | Valor           |
| :---------- | :-------------- |
| Componentes | BGE-M3 + Qdrant |
| Hardware    | CPU + RAM       |
| Tempo       | ~30-100ms       |

**Fluxo:**

1. Gerar embedding da query com BGE-M3:
   - Embedding denso (semantico): vetor 1024 dims
   - Embedding esparso (keywords): {"firefox": 0.9, ...}

2. Busca hibrida no Qdrant:
   - Combina similaridade densa + match de keywords
   - Retorna top-k documentos mais relevantes (k=3)

---

### Etapa 6: LLM (Raciocinio)

| Propriedade | Valor                             |
| :---------- | :-------------------------------- |
| Componente  | Granite 4.0 Hybrid 1B (llama.cpp) |
| Hardware    | GPU (100% VRAM)                   |
| Quantizacao | Q8_0                              |
| Tempo       | ~50-200ms                         |

**Prompt montado:**

```
Voce e um assistente de sistema Linux.

## Contexto Recuperado:
[Documentos do RAG]

## Pedido do Usuario:
abre o firefox

## Responda com JSON:
{"action": "...", "target": "...", ...}
```

**Saida (JSON garantido pelo GBNF):**

```json
{
  "action": "OPEN_APP",
  "target": "firefox",
  "args": null,
  "confidence": 0.95,
  "requires_confirmation": false
}
```

---

### Etapa 7: SEGURANCA (Guarda-Costas)

| Propriedade | Valor              |
| :---------- | :----------------- |
| Componente  | Python (validacao) |
| Hardware    | CPU                |
| Tempo       | <5ms               |

**Verificacoes:**

1. Acao esta na lista de acoes permitidas?
2. Target esta na blacklist?
3. Requer confirmacao?
4. Requer sudo?

**Cenarios de resultado:**

| Status                | Descricao                           | Exemplo            |
| :-------------------- | :---------------------------------- | :----------------- |
| APPROVED              | Comando seguro, executa diretamente | OPEN_APP "firefox" |
| REQUIRES_CONFIRMATION | Comando sensivel, pede confirmacao  | rm arquivo.txt     |
| REQUIRES_PASSWORD     | Precisa de sudo                     | sudo apt update    |
| BLOCKED               | Comando na blacklist, rejeita       | rm -rf /           |

---

### Etapa 8: EXECUTOR

| Propriedade | Valor                            |
| :---------- | :------------------------------- |
| Componente  | subprocess + wrappers agnosticos |
| Hardware    | CPU                              |
| Tempo       | ~50-200ms                        |

**Traducao para comandos agnosticos:**

| Acao               | Comando de Sistema          |
| :----------------- | :-------------------------- |
| OPEN_APP "firefox" | subprocess.run(["firefox"]) |
| OPEN_URL "g1.com"  | xdg-open https://g1.com.br  |
| OPEN_FOLDER "~"    | xdg-open /home/user         |
| VOLUME_UP          | pactl set-sink-volume +5%   |
| VOLUME_DOWN        | pactl set-sink-volume -5%   |
| VOLUME_MUTE        | pactl set-sink-mute toggle  |
| MEDIA_PLAY_PAUSE   | playerctl play-pause        |
| MEDIA_NEXT         | playerctl next              |
| MEDIA_PREV         | playerctl previous          |
| KEY_PRESS "ctrl+c" | ydotool key ctrl+c          |

---

### Etapa 9: TTS (Text-to-Speech)

| Propriedade | Valor                |
| :---------- | :------------------- |
| Componente  | Piper (VITS)         |
| Hardware    | CPU                  |
| Voz         | pt_BR (customizavel) |
| Tempo       | ~100-200ms (geracao) |

**Templates de resposta:**

- Sucesso: "Pronto, {action} executado."
- Erro: "Nao consegui {action}. {error}"
- Confirmacao: "Quer {action}? Confirme no teclado."
- Bloqueado: "Este comando nao e permitido por seguranca."
- Desconhecido: "Nao entendi o que voce quer fazer."

**Modo Streaming (recomendado):**

```python
for audio_bytes in voice.synthesize_stream_raw(text):
    audio_output.write(audio_bytes)
    # Usuario ja ouve enquanto resto e gerado
```

---

### Etapa 10: RETORNO AO IDLE

Apos o TTS terminar:

- Estado volta para IDLE
- Wake word listener reativado
- Buffer circular resetado
- Sistema aguarda proximo wake word

---

## 4. Timeline de Latencia

### Cenario Tipico: "Ei Painho, abre o Firefox"

| Etapa               | Tempo   | Acumulado | Notas                |
| :------------------ | :------ | :-------- | :------------------- |
| Wake Word           | 50ms    | 50ms      | Deteccao instantanea |
| Fala do Usuario     | ~2450ms | ~2500ms   | Variavel             |
| VAD (silencio)      | 300ms   | ~2800ms   | Configuravel         |
| STT (Whisper)       | 350ms   | ~3150ms   | CPU, batch mode      |
| RAG (BGE-M3+Qdrant) | 45ms    | ~3195ms   | CPU+RAM              |
| LLM (Granite)       | 120ms   | ~3315ms   | GPU                  |
| Seguranca           | 5ms     | ~3320ms   | CPU                  |
| Executor            | 85ms    | ~3405ms   | CPU                  |
| TTS (Piper)         | 100ms+  | ~3505ms+  | First audio          |

**Latencia de Processamento (STT->Executor):** ~605ms
**Time-to-First-Audio:** ~530ms apos fim da fala

---

## 5. Fluxos Alternativos

### 5.1. Comando com Confirmacao

```
Usuario: "Ei Painho, apaga o arquivo teste.txt"

[Etapas 1-6 iguais]

Etapa 7 (Seguranca):
  - Comando: rm teste.txt
  - Detectado: "rm" na lista de confirmacao
  - Status: REQUIRES_CONFIRMATION

Etapa 9a (TTS):
  "Voce quer remover teste.txt? Confirme com Y ou cancele com N."

Estado: CONFIRMING
  - [Y pressionado] -> Executa -> "Arquivo removido."
  - [N pressionado] -> "Comando cancelado."
  - [Timeout 30s] -> "Tempo esgotado, cancelando."
```

### 5.2. Comando Bloqueado

```
Usuario: "Ei Painho, formata o disco"

Etapa 7 (Seguranca):
  - Status: BLOCKED

Etapa 9 (TTS):
  "Este comando nao e permitido por seguranca."
```

### 5.3. Comando Nao Reconhecido

```
Usuario: "Ei Painho, faz um cafe"

Etapa 6 (LLM):
  {"action": "UNKNOWN", "confidence": 0.3}

Etapa 9 (TTS):
  "Nao entendi o que voce quer fazer. Pode repetir?"
```

### 5.4. Erro de Execucao

```
Usuario: "Ei Painho, abre o programa_inexistente"

Etapa 8 (Executor):
  Exit code: 127 (comando nao encontrado)

Etapa 9 (TTS):
  "Nao consegui abrir programa_inexistente. O programa nao foi encontrado."
```

---

## 6. Capacidades de Streaming

### 6.1. Whisper (STT)

| Modo      | Descricao                    | Recomendacao PoC |
| :-------- | :--------------------------- | :--------------- |
| Batch     | Aguarda VAD, transcreve tudo | Comecar com este |
| Streaming | Transcreve enquanto fala     | Evoluir depois   |

### 6.2. Piper (TTS)

| Modo      | Descricao              | Recomendacao PoC      |
| :-------- | :--------------------- | :-------------------- |
| Batch     | Gera WAV completo      | Nao recomendado       |
| Streaming | Reproduz enquanto gera | **Usar desde inicio** |

---

## 7. Alocacao de Hardware

### 7.1. GPU (GTX 1650 - 4GB VRAM)

```
Granite 4.0 (Q8_0):    ~1300 MB
KV Cache:              ~ 300 MB
Buffers CUDA:          ~ 400 MB
--------------------------------
Total GPU:             ~2000 MB
Livre:                 ~2000 MB
```

### 7.2. CPU (Ryzen 7 - 8c/16t)

| Componente  | Threads | Prioridade |
| :---------- | :------ | :--------- |
| Whisper STT | 4-6     | Alta       |
| BGE-M3      | 2-4     | Media      |
| Piper TTS   | 1-2     | Media      |
| Wake Word   | 1       | Baixa      |
| VAD         | 1       | Baixa      |

### 7.3. RAM (32 GB)

```
Whisper Large v3:      ~2200 MB
BGE-M3:                ~2500 MB
Qdrant (indice):       ~ 500 MB
Piper:                 ~ 300 MB
Wake Word + VAD:       ~ 200 MB
Python + buffers:      ~1000 MB
--------------------------------
Total RAM:             ~6700 MB
Livre:                 ~25 GB
```

---

## Referencias

- [00-architecture-overview.md](./00-architecture-overview.md) - Visao geral da arquitetura
- [01-models-spec.md](./01-models-spec.md) - Especificacoes dos modelos
- [07-security.md](./07-security.md) - Estrategia de seguranca
