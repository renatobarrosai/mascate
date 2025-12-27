# Solucao de Problemas

Guia para resolver problemas comuns do Mascate.

---

## Indice

1. [Hotkey nao Funciona](#1-hotkey-nao-funciona)
2. [Audio nao Captura](#2-audio-nao-captura)
3. [Modelos nao Carregam](#3-modelos-nao-carregam)
4. [GPU nao Detectada](#4-gpu-nao-detectada)
5. [Erros de Dependencia](#5-erros-de-dependencia)
6. [Problemas de Performance](#6-problemas-de-performance)
7. [Comandos nao Executam](#7-comandos-nao-executam)
8. [Logs e Diagnostico](#8-logs-e-diagnostico)

---

## 1. Hotkey nao Funciona

### 1.1 Wayland (GNOME 42+, Fedora)

**Sintoma:** Hotkey nao ativa em Wayland.

**Causa:** Wayland bloqueia acesso global ao teclado por seguranca.

**Solucoes:**

**Opcao A - Usar X11 temporariamente:**

```bash
# Na tela de login, clique na engrenagem e selecione "GNOME on Xorg"
```

**Opcao B - Usar atalho do sistema:**

1. Abra Configuracoes > Teclado > Atalhos
2. Adicione um atalho personalizado:
   - Nome: `Mascate`
   - Comando: `mascate activate` (quando implementado)
   - Atalho: Escolha uma combinacao

**Opcao C - Verificar se esta em Wayland:**

```bash
echo $XDG_SESSION_TYPE
# Se mostrar "wayland", voce esta em Wayland
# Se mostrar "x11", o problema e outro
```

### 1.2 Conflito com Outro Programa

**Sintoma:** Hotkey funciona as vezes ou nunca.

**Solucao:**

1. Verifique se outro programa usa o mesmo atalho:

```bash
# Liste atalhos do GNOME
gsettings list-recursively | grep -i "ctrl.*shift.*m"
```

2. Mude o hotkey no `config.toml`:

```toml
[audio]
hotkey = "ctrl+alt+m"  # Tente outra combinacao
```

**Combinacoes recomendadas:**

| Hotkey             | Conflitos Comuns    |
| ------------------ | ------------------- |
| `ctrl+shift+m`     | Mute em alguns apps |
| `ctrl+alt+m`       | Geralmente livre    |
| `super+m`          | Minimizar janela    |
| `ctrl+shift+space` | Boa alternativa     |

### 1.3 Permissoes de Input

**Sintoma:** Erro de permissao ao iniciar.

**Solucao:**

```bash
# Adicione seu usuario ao grupo input
sudo usermod -aG input $USER

# Faca logout e login novamente
```

### 1.4 pynput nao Instalado

**Sintoma:** Erro `ModuleNotFoundError: No module named 'pynput'`

**Solucao:**

```bash
uv sync  # Reinstala dependencias
```

---

## 2. Audio nao Captura

### 2.1 Nenhum Dispositivo Detectado

**Sintoma:** Erro "No audio device found" ou lista vazia.

**Diagnostico:**

```bash
# Liste dispositivos de audio
arecord -l

# Saida esperada:
# card 0: PCH [HDA Intel PCH], device 0: ALC...
```

**Se nenhum dispositivo aparecer:**

1. Verifique conexao fisica do microfone
2. Verifique se o driver de audio esta carregado:

```bash
lsmod | grep snd
```

3. Reinstale drivers de audio:

```bash
# Ubuntu
sudo apt install --reinstall alsa-base pulseaudio

# Fedora
sudo dnf reinstall alsa-lib pulseaudio
```

### 2.2 Microfone Mutado

**Sintoma:** Dispositivo detectado mas sem captura.

**Solucao:**

```bash
# Interface grafica
pavucontrol  # Aba "Input Devices" > Desmute

# Linha de comando
pactl set-source-mute @DEFAULT_SOURCE@ 0
```

### 2.3 Permissao de Acesso ao Microfone

**Sintoma:** Erro de permissao ao acessar dispositivo.

**Solucao:**

```bash
# Adicione ao grupo audio
sudo usermod -aG audio $USER

# Logout e login
```

### 2.4 PipeWire vs PulseAudio

**Sintoma:** Problemas em sistemas com PipeWire.

**Diagnostico:**

```bash
# Verifique qual esta rodando
systemctl --user status pipewire
systemctl --user status pulseaudio
```

**Se usar PipeWire, instale compatibilidade:**

```bash
# Ubuntu 22.04+
sudo apt install pipewire-pulse

# Fedora
sudo dnf install pipewire-pulseaudio
```

---

## 3. Modelos nao Carregam

### 3.1 Arquivo nao Encontrado

**Sintoma:** `FileNotFoundError` para modelo.

**Diagnostico:**

```bash
# Verifique se os modelos existem
ls -la ~/.local/share/mascate/models/

# Saida esperada:
# granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf
# ggml-large-v3-q5_0.bin
# pt_BR-faber-medium.onnx
```

**Se estiverem faltando:**

```bash
uv run python scripts/download_models.py
```

### 3.2 Espaco em Disco Insuficiente

**Sintoma:** Download falha ou modelo corrompido.

**Diagnostico:**

```bash
df -h ~/.local/share/mascate/
# Precisa de pelo menos 10GB livres
```

**Solucao:**

1. Libere espaco em disco
2. Ou mude o diretorio de modelos:

```toml
[paths]
models_dir = "/outro/disco/com/espaco/models"
```

### 3.3 Download Incompleto

**Sintoma:** Modelo existe mas com tamanho errado.

**Diagnostico:**

```bash
# Verifique tamanhos
ls -lh ~/.local/share/mascate/models/

# Tamanhos esperados (aproximados):
# granite*.gguf   ~1.3GB
# ggml-large*.bin ~3.0GB
# *.onnx          ~100MB
```

**Se tamanhos estiverem errados:**

```bash
# Delete e baixe novamente
rm ~/.local/share/mascate/models/granite*.gguf
uv run python scripts/download_models.py
```

### 3.4 Erro de Formato do Modelo

**Sintoma:** `Invalid model format` ou erro de parsing.

**Causa:** Modelo incompativel ou corrompido.

**Solucao:**

```bash
# Delete modelos e baixe novamente
rm -rf ~/.local/share/mascate/models/
uv run python scripts/download_models.py
```

---

## 4. GPU nao Detectada

### 4.1 CUDA nao Instalado

**Sintoma:** `CUDA not available` ou modelo roda apenas na CPU.

**Diagnostico:**

```bash
# Verifique CUDA
nvcc --version
# Deve mostrar CUDA 11.x ou 12.x

# Verifique driver NVIDIA
nvidia-smi
# Deve mostrar GPU e driver
```

**Se nvcc nao encontrado:**

```bash
# Ubuntu
sudo apt install nvidia-cuda-toolkit

# Ou instale via NVIDIA (recomendado):
# https://developer.nvidia.com/cuda-downloads
```

### 4.2 Driver Desatualizado

**Sintoma:** GPU detectada mas erros de CUDA.

**Diagnostico:**

```bash
nvidia-smi
# Verifique a versao do driver
# Driver Version: 535.xxx ou superior recomendado
```

**Atualizacao:**

```bash
# Ubuntu
sudo apt update
sudo apt install nvidia-driver-535  # ou versao mais recente

# Reinicie
sudo reboot
```

### 4.3 VRAM Insuficiente

**Sintoma:** `CUDA out of memory` ou crash ao carregar modelo.

**Diagnostico:**

```bash
nvidia-smi
# Verifique "Memory-Usage"
# Precisa de ~4GB livres para o Granite
```

**Solucoes:**

1. Feche outros programas usando GPU (navegador, jogos)
2. Reduza camadas na GPU:

```toml
[llm]
n_gpu_layers = 20  # Ao inves de -1 (todas)
```

3. Use modelo menor (se disponivel)

### 4.4 AMD GPU (ROCm)

**Sintoma:** GPU AMD nao detectada.

**Diagnostico:**

```bash
rocminfo
# Deve listar sua GPU
```

**Se nao detectar:**

1. Instale ROCm: https://rocm.docs.amd.com/
2. Verifique compatibilidade da GPU (RX 5000+ recomendado)

---

## 5. Erros de Dependencia

### 5.1 Python Versao Incorreta

**Sintoma:** `SyntaxError` ou `ModuleNotFoundError` estranhos.

**Diagnostico:**

```bash
python --version
# Precisa ser 3.12+
```

**Solucao:**

```bash
# Ubuntu
sudo apt install python3.12

# Use pyenv para multiplas versoes:
curl https://pyenv.run | bash
pyenv install 3.12
pyenv local 3.12
```

### 5.2 uv nao Encontrado

**Sintoma:** `command not found: uv`

**Solucao:**

```bash
# Instale uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Recarregue o shell
source ~/.bashrc  # ou ~/.zshrc
```

### 5.3 Bibliotecas de Sistema Faltando

**Sintoma:** Erros de `ImportError` para bibliotecas nativas.

**Erros comuns e solucoes:**

```bash
# portaudio (para pyaudio)
# Erro: "portaudio.h not found"
sudo apt install portaudio19-dev  # Ubuntu
sudo dnf install portaudio-devel  # Fedora

# ffmpeg (para audio)
# Erro: "ffmpeg not found"
sudo apt install ffmpeg  # Ubuntu
sudo dnf install ffmpeg  # Fedora

# libnotify (para notificacoes)
sudo apt install libnotify-bin  # Ubuntu
sudo dnf install libnotify      # Fedora
```

### 5.4 Conflito de Versoes

**Sintoma:** Erros apos atualizar dependencias.

**Solucao:**

```bash
# Limpe e reinstale
rm -rf .venv uv.lock
uv sync
```

---

## 6. Problemas de Performance

### 6.1 STT Muito Lento

**Sintoma:** Demora mais de 5 segundos para transcrever.

**Diagnostico:**

- Verifique se esta usando GPU
- Modelo Whisper large e pesado

**Solucoes:**

1. Use modelo menor (se disponivel):

```toml
[audio.stt]
model = "ggml-medium-q5_0.bin"  # Mais rapido
```

2. Aumente threads de CPU:

```toml
[audio.stt]
n_threads = 8  # Ajuste para seu CPU
```

### 6.2 LLM Lento

**Sintoma:** Resposta demora mais de 3 segundos.

**Solucoes:**

1. Verifique se GPU esta sendo usada:

```bash
# Durante execucao, verifique uso de GPU
nvidia-smi -l 1
```

2. Reduza contexto se necessario:

```toml
[llm]
n_ctx = 2048     # Menor = mais rapido
max_tokens = 128 # Limite a resposta
```

### 6.3 Alto Uso de RAM

**Sintoma:** Sistema fica lento, swap alto.

**Solucoes:**

1. Feche programas desnecessarios
2. Reduza configuracoes:

```toml
[llm]
n_ctx = 2048

[rag]
top_k = 2  # Menos documentos
```

### 6.4 Latencia Geral Alta

**Sintoma:** Tempo total acima de 5 segundos.

**Diagnostico:**

```bash
# Execute com debug
DEBUG=1 uv run mascate run
```

**Otimizacoes:**

1. Use hotkey ao inves de wake word (evita STT extra)
2. Mantenha modelos carregados (nao reinicie frequentemente)
3. Use SSD ao inves de HDD

---

## 7. Comandos nao Executam

### 7.1 Comando Bloqueado pela Seguranca

**Sintoma:** Mensagem "Comando bloqueado por seguranca".

**Causa:** Comando esta na blacklist ou acessa path protegido.

**Solucao:**

1. Verifique `config.toml`:

```toml
[security]
blacklist_commands = [...]  # Veja se seu comando esta aqui
protected_paths = [...]     # Veja se o path esta protegido
```

2. Se for intencional, remova da blacklist (com cuidado!)

### 7.2 Aplicativo nao Encontrado

**Sintoma:** "Aplicativo X nao encontrado".

**Diagnostico:**

```bash
# Verifique se o app existe
which firefox  # ou nome do app
```

**Solucao:**

1. Instale o aplicativo
2. Ou adicione ao PATH se instalado em local nao-padrao

### 7.3 Comando Mal Interpretado

**Sintoma:** LLM entende errado o que voce disse.

**Solucoes:**

1. Fale mais claramente/devagar
2. Use comandos mais diretos:
   - "Abre Firefox" ao inves de "Pode abrir o navegador pra mim?"
3. Verifique se STT transcreveu corretamente (logs)

### 7.4 Confirmacao Travada

**Sintoma:** Pediu confirmacao mas nao aceita resposta.

**Solucao temporaria:**

1. Pressione `Ctrl+C` para cancelar
2. Desative confirmacao se necessario:

```toml
[security]
require_confirmation = false  # Menos seguro!
```

---

## 8. Logs e Diagnostico

### 8.1 Ativar Modo Debug

```toml
[general]
debug = true
log_level = "DEBUG"
```

### 8.2 Ver Logs em Tempo Real

```bash
# Logs detalhados
uv run mascate run 2>&1 | tee mascate.log
```

### 8.3 Informacoes do Sistema

Colete estas informacoes ao reportar bugs:

```bash
# Sistema
uname -a
cat /etc/os-release

# Python
python --version
uv --version

# GPU
nvidia-smi  # ou rocminfo para AMD

# Audio
arecord -l
pactl info

# Mascate
uv run mascate version
```

### 8.4 Reportar Bug

Ao abrir uma issue no GitHub, inclua:

1. Descricao do problema
2. Passos para reproduzir
3. Saida do comando com erro
4. Informacoes do sistema (secao 8.3)
5. Arquivo `config.toml` (remova dados sensiveis)

---

## Checklist Rapido

Se algo nao funciona, verifique nesta ordem:

```
[ ] Python 3.12+ instalado?
[ ] uv instalado e no PATH?
[ ] Dependencias instaladas (uv sync)?
[ ] Modelos baixados?
[ ] config.toml existe e esta correto?
[ ] Nao esta em Wayland (para hotkey)?
[ ] GPU detectada (nvidia-smi)?
[ ] Microfone funcionando (arecord -l)?
[ ] Espaco em disco suficiente?
```

---

## Ainda com Problemas?

1. Consulte a [documentacao completa](../README.md)
2. Abra uma issue no GitHub com as informacoes da secao 8.4
3. Verifique issues existentes para problemas similares

---

[Voltar ao README](../README.md) | [Anterior: Desenvolvimento](development.md)
