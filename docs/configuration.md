# Referencia de Configuracao

Guia completo de todas as opcoes do arquivo `config.toml`.

**Localizacao:** `~/.config/mascate/config.toml`

---

## Indice

1. [Estrutura do Arquivo](#1-estrutura-do-arquivo)
2. [Secao general](#2-secao-general)
3. [Secao audio](#3-secao-audio)
4. [Secao llm](#4-secao-llm)
5. [Secao rag](#5-secao-rag)
6. [Secao security](#6-secao-security)
7. [Secao paths](#7-secao-paths)
8. [Configuracoes por Perfil](#8-configuracoes-por-perfil)

---

## 1. Estrutura do Arquivo

O arquivo usa formato TOML. Exemplo minimo:

```toml
[general]
debug = false

[audio]
hotkey_enabled = true
hotkey = "ctrl+shift+m"

[llm]
n_gpu_layers = -1
```

---

## 2. Secao general

Configuracoes gerais da aplicacao.

```toml
[general]
debug = false
log_level = "INFO"
```

| Opcao       | Tipo   | Padrao  | Descricao                                 |
| ----------- | ------ | ------- | ----------------------------------------- |
| `debug`     | bool   | `false` | Ativa modo debug com logs detalhados      |
| `log_level` | string | `INFO`  | Nivel de log: DEBUG, INFO, WARNING, ERROR |

---

## 3. Secao audio

Configuracoes de captura de audio e ativacao.

```toml
[audio]
sample_rate = 16000
channels = 1
chunk_size = 1024
vad_threshold = 0.5
wake_word = "mascate"

# Ativacao por hotkey
hotkey_enabled = true
hotkey = "ctrl+shift+m"
hotkey_only = true
```

### 3.1 Captura de Audio

| Opcao         | Tipo | Padrao | Descricao                  |
| ------------- | ---- | ------ | -------------------------- |
| `sample_rate` | int  | 16000  | Taxa de amostragem (Hz)    |
| `channels`    | int  | 1      | Canais de audio (1 = mono) |
| `chunk_size`  | int  | 1024   | Amostras por chunk         |

### 3.2 Deteccao de Voz (VAD)

| Opcao           | Tipo  | Padrao | Descricao                 |
| --------------- | ----- | ------ | ------------------------- |
| `vad_threshold` | float | 0.5    | Sensibilidade (0.0 a 1.0) |

Valores mais altos = menos sensivel (ignora ruidos fracos)
Valores mais baixos = mais sensivel (pode captar ruido)

### 3.3 Wake Word

| Opcao       | Tipo   | Padrao    | Descricao           |
| ----------- | ------ | --------- | ------------------- |
| `wake_word` | string | "mascate" | Palavra de ativacao |

### 3.4 Ativacao por Hotkey

| Opcao            | Tipo   | Padrao           | Descricao                  |
| ---------------- | ------ | ---------------- | -------------------------- |
| `hotkey_enabled` | bool   | `true`           | Ativa ativacao por tecla   |
| `hotkey`         | string | `"ctrl+shift+m"` | Combinacao de teclas       |
| `hotkey_only`    | bool   | `true`           | Desativa wake word se true |

**Formato do hotkey:**

- Modificadores: `ctrl`, `shift`, `alt`, `super` (tecla Windows/Meta)
- Separador: `+`
- Tecla: letra minuscula ou nome especial (`space`, `enter`, `f1`, etc.)

**Exemplos:**

```toml
hotkey = "ctrl+shift+m"       # Ctrl + Shift + M
hotkey = "alt+space"          # Alt + Espaco
hotkey = "super+a"            # Super + A
hotkey = "ctrl+alt+v"         # Ctrl + Alt + V
```

### 3.5 STT (Speech-to-Text)

```toml
[audio.stt]
model = "ggml-large-v3-q5_0.bin"
language = "pt"
n_threads = 4
```

| Opcao       | Tipo   | Padrao                   | Descricao             |
| ----------- | ------ | ------------------------ | --------------------- |
| `model`     | string | `ggml-large-v3-q5_0.bin` | Arquivo do modelo     |
| `language`  | string | `pt`                     | Idioma (pt, en, auto) |
| `n_threads` | int    | 4                        | Threads para CPU      |

### 3.6 TTS (Text-to-Speech)

```toml
[audio.tts]
model = "pt_BR-faber-medium.onnx"
```

| Opcao   | Tipo   | Padrao                    | Descricao     |
| ------- | ------ | ------------------------- | ------------- |
| `model` | string | `pt_BR-faber-medium.onnx` | Modelo de voz |

---

## 4. Secao llm

Configuracoes do modelo de linguagem (Granite).

```toml
[llm]
model = "granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf"
n_gpu_layers = -1
n_ctx = 4096
n_batch = 512
temperature = 0.1
max_tokens = 256
```

| Opcao          | Tipo   | Padrao | Descricao                            |
| -------------- | ------ | ------ | ------------------------------------ |
| `model`        | string | -      | Arquivo do modelo GGUF               |
| `n_gpu_layers` | int    | -1     | Camadas na GPU (-1 = todas)          |
| `n_ctx`        | int    | 4096   | Tamanho do contexto (tokens)         |
| `n_batch`      | int    | 512    | Tamanho do batch                     |
| `temperature`  | float  | 0.1    | Aleatoriedade (0.0 = deterministico) |
| `max_tokens`   | int    | 256    | Limite de tokens na resposta         |

### 4.1 Alocacao GPU/CPU

| `n_gpu_layers` | Comportamento                  |
| -------------- | ------------------------------ |
| `-1`           | Todas as camadas na GPU        |
| `0`            | Apenas CPU (sem GPU)           |
| `N`            | N camadas na GPU, resto na CPU |

**Para GPU com pouca VRAM:** Reduza `n_gpu_layers` gradualmente ate caber.

### 4.2 Ajuste de Temperature

| Valor | Comportamento         | Uso               |
| ----- | --------------------- | ----------------- |
| 0.0   | Sempre mesma resposta | Comandos precisos |
| 0.1   | Quase deterministico  | Recomendado       |
| 0.5   | Alguma variacao       | Conversacao       |
| 1.0   | Alta variacao         | Criatividade      |

---

## 5. Secao rag

Configuracoes do sistema de memoria (RAG).

```toml
[rag]
collection_name = "mascate_knowledge"
embedding_model = "BAAI/bge-m3"
embedding_device = "cpu"
top_k = 3
```

| Opcao              | Tipo   | Padrao              | Descricao                 |
| ------------------ | ------ | ------------------- | ------------------------- |
| `collection_name`  | string | `mascate_knowledge` | Nome da colecao no Qdrant |
| `embedding_model`  | string | `BAAI/bge-m3`       | Modelo de embeddings      |
| `embedding_device` | string | `cpu`               | Dispositivo (cpu ou cuda) |
| `top_k`            | int    | 3                   | Documentos a recuperar    |

---

## 6. Secao security

Configuracoes de seguranca.

```toml
[security]
require_confirmation = true

blacklist_commands = [
    "rm -rf",
    "rm -r",
    "dd if=",
    "mkfs",
    "format",
    "> /dev/",
    "chmod 777",
    ":(){ :|:& };:",
    "curl | sh",
    "wget | sh",
]

protected_paths = [
    "/etc",
    "/boot",
    "/sys",
    "/proc",
    "/dev",
    "/root",
    "/var/log",
]
```

### 6.1 Confirmacao

| Opcao                  | Tipo | Padrao | Descricao                         |
| ---------------------- | ---- | ------ | --------------------------------- |
| `require_confirmation` | bool | `true` | Pedir confirmacao para acoes HIGH |

### 6.2 Blacklist de Comandos

Lista de padroes sempre bloqueados. Usa correspondencia de substring.

```toml
blacklist_commands = [
    "rm -rf",        # Delecao recursiva forcada
    "dd if=",        # Escrita direta em disco
    "mkfs",          # Formatacao
    "> /dev/",       # Redirecionamento para devices
]
```

**Adicionar novo padrao:**

```toml
blacklist_commands = [
    "rm -rf",
    "meu_comando_perigoso",  # Adicionado
]
```

### 6.3 Paths Protegidos

Diretorios que requerem confirmacao ou sao bloqueados:

```toml
protected_paths = [
    "/etc",          # Configuracoes do sistema
    "/boot",         # Arquivos de boot
    "~/.ssh",        # Chaves SSH
]
```

---

## 7. Secao paths

Caminhos de arquivos e diretorios.

```toml
[paths]
models_dir = "~/.local/share/mascate/models"
data_dir = "~/.local/share/mascate"
cache_dir = "~/.cache/mascate"
```

| Opcao        | Tipo   | Padrao                          | Descricao            |
| ------------ | ------ | ------------------------------- | -------------------- |
| `models_dir` | string | `~/.local/share/mascate/models` | Diretorio de modelos |
| `data_dir`   | string | `~/.local/share/mascate`        | Dados da aplicacao   |
| `cache_dir`  | string | `~/.cache/mascate`              | Cache temporario     |

**Nota:** `~` e expandido para o diretorio home do usuario.

---

## 8. Configuracoes por Perfil

### 8.1 Minimo (CPU apenas, baixa memoria)

```toml
[general]
debug = false

[audio]
hotkey_enabled = true
hotkey_only = true

[llm]
n_gpu_layers = 0    # CPU apenas
n_ctx = 2048        # Contexto menor
```

### 8.2 Balanceado (GPU com 4GB VRAM)

```toml
[general]
debug = false

[audio]
hotkey_enabled = true
hotkey_only = true

[llm]
n_gpu_layers = -1   # Tudo na GPU
n_ctx = 4096
temperature = 0.1
```

### 8.3 Maximo (GPU com 8GB+ VRAM)

```toml
[general]
debug = false

[audio]
hotkey_enabled = true
hotkey_only = false  # Wake word ativo
wake_word = "mascate"

[llm]
n_gpu_layers = -1
n_ctx = 8192        # Contexto maior
max_tokens = 512

[rag]
top_k = 5           # Mais documentos
```

---

## Arquivo Completo de Exemplo

```toml
# Mascate - Configuracao
# ~/.config/mascate/config.toml

[general]
debug = false
log_level = "INFO"

[audio]
sample_rate = 16000
channels = 1
chunk_size = 1024
vad_threshold = 0.5
wake_word = "mascate"

hotkey_enabled = true
hotkey = "ctrl+shift+m"
hotkey_only = true

[audio.stt]
model = "ggml-large-v3-q5_0.bin"
language = "pt"
n_threads = 4

[audio.tts]
model = "pt_BR-faber-medium.onnx"

[llm]
model = "granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf"
n_gpu_layers = -1
n_ctx = 4096
n_batch = 512
temperature = 0.1
max_tokens = 256

[rag]
collection_name = "mascate_knowledge"
embedding_model = "BAAI/bge-m3"
embedding_device = "cpu"
top_k = 3

[security]
require_confirmation = true
blacklist_commands = [
    "rm -rf",
    "rm -r",
    "dd if=",
    "mkfs",
    "format",
]
protected_paths = [
    "/etc",
    "/boot",
    "/sys",
    "/proc",
]

[paths]
models_dir = "~/.local/share/mascate/models"
data_dir = "~/.local/share/mascate"
cache_dir = "~/.cache/mascate"
```

---

[Voltar ao README](../README.md) | [Anterior: Guia do Usuario](user-guide.md) | [Proximo: Arquitetura](architecture.md)
