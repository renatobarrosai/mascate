# Plano de Campo de Batalha - Mascate v0.1.0

Este documento descreve o passo a passo para levar o Mascate do estado atual (codigo estruturado com testes mockados) para um sistema funcional em ambiente real.

**Data:** 2024-12-27
**Status:** Em progresso

---

## Indice

1. [Diagnostico Atual](#1-diagnostico-atual)
2. [Pre-requisitos](#2-pre-requisitos)
3. [Fase 1: Infraestrutura Minima](#3-fase-1-infraestrutura-minima)
4. [Fase 2: Dependencias GPU](#4-fase-2-dependencias-gpu)
5. [Fase 3: Teste Integrado](#5-fase-3-teste-integrado)
6. [Fase 4: Polish](#6-fase-4-polish)
7. [Comandos de Referencia](#7-comandos-de-referencia)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Diagnostico Atual

### O que existe

| Componente    | Codigo | Testes  | Status                               |
| ------------- | ------ | ------- | ------------------------------------ |
| Audio Capture | Sim    | Mockado | Precisa testar com mic real          |
| VAD (Silero)  | Sim    | Mockado | Precisa do modelo ONNX               |
| STT (Whisper) | Sim    | Mockado | Precisa do modelo + pywhispercpp     |
| TTS (Piper)   | Sim    | Mockado | Precisa do modelo ONNX               |
| Wake Word     | Sim    | Mockado | Incompativel com Python 3.12         |
| Hotkey        | Sim    | Mockado | Precisa testar no X11                |
| LLM (Granite) | Sim    | Mockado | Precisa do modelo + llama-cpp-python |
| RAG           | Sim    | Mockado | Precisa do Qdrant + BGE-M3           |
| Executor      | Sim    | Mockado | Precisa testar comandos reais        |
| CLI           | Sim    | Parcial | Falta passar HotkeyListener          |

### O que falta

1. **Modelos nao baixados** (~7GB total)
   - Granite LLM: ~1.2GB
   - Whisper Large v3: ~1.1GB
   - Silero VAD: ~2MB (faltando no script)
   - Piper TTS: ~100MB (faltando no script)
   - BGE-M3: ~2GB (baixado automaticamente)

2. **Dependencias opcionais nao instaladas**
   - `llama-cpp-python` - requer compilacao com CUDA
   - `pywhispercpp` - requer compilacao com CUDA

3. **Bug no CLI**
   - HotkeyListener nao esta sendo passado para AudioPipeline

---

## 2. Pre-requisitos

### Hardware

| Componente | Minimo         | Recomendado     |
| ---------- | -------------- | --------------- |
| GPU NVIDIA | GTX 1650 (4GB) | RTX 3060 (8GB+) |
| RAM        | 16GB           | 32GB            |
| Disco      | 20GB livres    | SSD             |
| Microfone  | Qualquer       | USB dedicado    |

### Software

```bash
# Verificar Python
python --version  # Precisa ser 3.12+

# Verificar CUDA
nvcc --version    # Precisa ser 11.x ou 12.x
nvidia-smi        # Verificar driver

# Verificar uv
uv --version
```

### Display Server

```bash
# Verificar se esta em X11 ou Wayland
echo $XDG_SESSION_TYPE

# Hotkey funciona melhor em X11
# Se estiver em Wayland, use X11 ou atalho do sistema
```

---

## 3. Fase 1: Infraestrutura Minima

**Objetivo:** Conseguir rodar `uv run mascate run` sem crash
**Tempo estimado:** 30 minutos

### 3.1 Instalar dependencias do sistema

```bash
cd /home/renato/programacao/open-source/mascate-v2
uv run python scripts/install_deps.py
```

Isso instala: ffmpeg, playerctl, portaudio, alsa, pulseaudio, wmctrl, xdotool

### 3.2 Criar arquivo de configuracao

```bash
mkdir -p ~/.config/mascate
cp config.toml.example ~/.config/mascate/config.toml
```

Edite `~/.config/mascate/config.toml` se necessario:

```toml
[audio]
hotkey_enabled = true
hotkey = "ctrl+shift+m"
hotkey_only = true  # Importante: desativa wake word

[llm]
n_gpu_layers = -1  # Todas camadas na GPU
```

### 3.3 Atualizar script de download (PENDENTE)

O script `scripts/download_models.py` precisa ser atualizado para incluir:

- Silero VAD v5 (`silero_vad.onnx`)
- Piper TTS pt-BR (`pt_BR-faber-medium.onnx`)

**Modelo Silero VAD:**

- Repo: `snakers4/silero-vad`
- Arquivo: `silero_vad.onnx` (v5)
- Tamanho: ~2MB

**Modelo Piper TTS:**

- Repo: `rhasspy/piper-voices`
- Arquivo: `pt_BR-faber-medium.onnx` + `.json`
- Tamanho: ~100MB

### 3.4 Corrigir CLI (PENDENTE)

O arquivo `src/mascate/interface/cli.py` precisa passar o HotkeyListener para o AudioPipeline:

```python
# Atual (linha 112):
audio_pipeline = AudioPipeline(capture, wake_detector, vad_processor, stt)

# Corrigido:
from mascate.audio.hotkey import HotkeyListener

hotkey_listener = None
if config.audio.hotkey_enabled:
    hotkey_listener = HotkeyListener(
        hotkey=config.audio.hotkey,
        on_activate_callback=None,  # Pipeline configura depois
    )

audio_pipeline = AudioPipeline(
    capture,
    wake_detector if not config.audio.hotkey_only else None,
    vad_processor,
    stt,
    hotkey_listener=hotkey_listener,
)
```

### 3.5 Baixar modelos

```bash
uv run python scripts/download_models.py
```

### 3.6 Verificar instalacao

```bash
uv run mascate check
```

Saida esperada:

```
[OK] Granite LLM: ~/.local/share/mascate/models/granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf
[OK] Whisper STT: ~/.local/share/mascate/models/ggml-large-v3-q5_0.bin
[OK] Silero VAD: ~/.local/share/mascate/models/silero_vad.onnx
[OK] Piper TTS: ~/.local/share/mascate/models/pt_BR-faber-medium.onnx
```

---

## 4. Fase 2: Dependencias GPU

**Objetivo:** Compilar llama-cpp-python e pywhispercpp com CUDA
**Tempo estimado:** 1-2 horas (inclui compilacao)

### 4.1 Instalar llama-cpp-python com CUDA

```bash
# Limpa cache se houver instalacao anterior
uv cache clean

# Instala com CUDA (NVIDIA)
CMAKE_ARGS="-DGGML_CUDA=on" uv pip install llama-cpp-python --reinstall --no-cache-dir

# OU para ROCm (AMD)
CMAKE_ARGS="-DGGML_HIPBLAS=on" uv pip install llama-cpp-python --reinstall --no-cache-dir
```

**Verificar instalacao:**

```python
from llama_cpp import Llama
print("llama-cpp-python instalado com sucesso")
```

### 4.2 Instalar pywhispercpp

```bash
# Com CUDA
uv pip install pywhispercpp

# Verificar
python -c "import pywhispercpp; print('OK')"
```

**Nota:** pywhispercpp pode precisar de compilacao manual em alguns sistemas.

Alternativa (whisper.cpp direto):

```bash
# Clone whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp

# Compile com CUDA
make GGML_CUDA=1

# Use o binario diretamente ou via Python bindings
```

### 4.3 Testar carregamento do LLM

```python
from pathlib import Path
from llama_cpp import Llama

model_path = Path.home() / ".local/share/mascate/models/granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf"
llm = Llama(model_path=str(model_path), n_gpu_layers=-1, n_ctx=2048)
print("Modelo carregado!")

# Teste simples
response = llm("Hello, how are you?", max_tokens=32)
print(response)
```

### 4.4 Testar carregamento do STT

```python
from pathlib import Path
from pywhispercpp.model import Model

model_path = Path.home() / ".local/share/mascate/models/ggml-large-v3-q5_0.bin"
whisper = Model(str(model_path), n_threads=4)
print("Whisper carregado!")
```

---

## 5. Fase 3: Teste Integrado

**Objetivo:** Pipeline completo funcionando
**Tempo estimado:** 1 hora

### 5.1 Testar captura de audio

```bash
# Lista dispositivos
arecord -l

# Testa gravacao
arecord -d 5 -f S16_LE -r 16000 test.wav
aplay test.wav
```

### 5.2 Testar hotkey

```bash
# Inicia o Mascate
uv run mascate run --debug

# Pressione Ctrl+Shift+M
# Deve mostrar "Sistema ativado via Hotkey" nos logs
```

**Se hotkey nao funcionar:**

1. Verifique se esta em X11: `echo $XDG_SESSION_TYPE`
2. Verifique conflitos: `gsettings list-recursively | grep -i "ctrl.*shift.*m"`
3. Tente outra combinacao no config.toml

### 5.3 Testar VAD

Apos ativar com hotkey:

1. Fale algo
2. Pare de falar
3. Deve mostrar "Fim de fala detectado" nos logs

**Se VAD nao detectar:**

- Ajuste `vad_threshold` no config.toml (0.3 = mais sensivel, 0.7 = menos)

### 5.4 Testar STT

Apos VAD detectar fim de fala:

1. Deve mostrar "Transcrito: 'texto falado'" nos logs
2. Verifique se o portugues esta sendo reconhecido

**Se STT falhar:**

- Verifique se o modelo existe
- Verifique logs de erro do Whisper

### 5.5 Testar LLM

Apos STT transcrever:

1. Deve mostrar intent parseado
2. Exemplo: "Abre a calculadora" -> `{"action": "open_app", "target": "gnome-calculator"}`

**Se LLM falhar:**

- Verifique VRAM disponivel: `nvidia-smi`
- Reduza `n_gpu_layers` no config.toml

### 5.6 Testar Executor

Apos LLM gerar intent:

1. Deve executar o comando
2. Exemplo: Calculadora abre

**Se Executor falhar:**

- Verifique se o app existe: `which gnome-calculator`
- Verifique logs de seguranca

---

## 6. Fase 4: Polish

**Objetivo:** Experiencia suave
**Tempo estimado:** Opcional

### 6.1 Habilitar TTS

```toml
# config.toml - TTS e habilitado automaticamente se modelo existir
```

Teste: Apos executar comando, Mascate deve falar o feedback.

### 6.2 Ajustar HUD

O HUD mostra:

- Estado atual (IDLE, LISTENING, PROCESSING, etc.)
- Ultima interacao
- Logs do sistema

### 6.3 Ajustar thresholds

```toml
[audio]
vad_threshold = 0.5  # Ajuste conforme ruido ambiente

[llm]
temperature = 0.1    # Mais baixo = mais deterministico
```

### 6.4 Testar comandos diversos

```
"Abre o Firefox"
"Que horas sao"
"Aumenta o volume"
"Abre o terminal"
"Pausa a musica"
```

---

## 7. Comandos de Referencia

### Instalacao completa

```bash
# 1. Deps do sistema
uv run python scripts/install_deps.py

# 2. Config
mkdir -p ~/.config/mascate
cp config.toml.example ~/.config/mascate/config.toml

# 3. Deps Python com GPU
CMAKE_ARGS="-DGGML_CUDA=on" uv pip install llama-cpp-python --reinstall
uv pip install pywhispercpp

# 4. Modelos
uv run python scripts/download_models.py

# 5. Verificar
uv run mascate check

# 6. Executar
uv run mascate run
```

### Debug

```bash
# Com logs detalhados
uv run mascate run --debug

# Apenas verificar
uv run mascate check

# Versao
uv run mascate version
```

### Testes

```bash
# Todos os testes
uv run pytest

# Apenas unitarios
uv run pytest tests/unit/

# Com cobertura
uv run pytest --cov=src
```

---

## 8. Troubleshooting

### "CUDA not available"

```bash
# Verifique CUDA
nvcc --version
nvidia-smi

# Reinstale llama-cpp-python
CMAKE_ARGS="-DGGML_CUDA=on" uv pip install llama-cpp-python --reinstall --no-cache-dir
```

### "Model not found"

```bash
# Verifique modelos
ls -la ~/.local/share/mascate/models/

# Re-baixe
uv run python scripts/download_models.py
```

### "Hotkey not working"

```bash
# Verifique display server
echo $XDG_SESSION_TYPE  # Deve ser "x11"

# Se Wayland, use X11 ou configure atalho do sistema
```

### "No audio device"

```bash
# Liste dispositivos
arecord -l

# Verifique PulseAudio/PipeWire
pactl info
```

### "Out of memory"

```toml
# config.toml - reduza camadas na GPU
[llm]
n_gpu_layers = 20  # Ao inves de -1
n_ctx = 2048       # Ao inves de 4096
```

---

## Checklist Final

```
[ ] Dependencias do sistema instaladas
[ ] config.toml criado
[ ] llama-cpp-python compilado com CUDA
[ ] pywhispercpp instalado
[ ] Modelos baixados (Granite, Whisper, Silero, Piper)
[ ] uv run mascate check passa
[ ] Hotkey ativa o sistema
[ ] VAD detecta fim de fala
[ ] STT transcreve portugues
[ ] LLM gera intent correto
[ ] Executor abre aplicativos
[ ] TTS fala feedback (opcional)
```

---

## Proximos Passos Apos Funcionando

1. **Treinar comandos** - Testar varios comandos e ajustar prompts
2. **Ajustar RAG** - Adicionar documentos de conhecimento
3. **Expandir handlers** - Adicionar mais acoes (automacao, scripts)
4. **Fine-tuning** - Treinar voz TTS personalizada (opcional)

---

[Voltar para Desenvolvimento](../development.md)
