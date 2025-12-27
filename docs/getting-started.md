# Guia de Instalacao

Este guia vai te levar do zero ate o Mascate funcionando no seu computador.

**Tempo estimado:** 15-30 minutos (dependendo da velocidade de download)

---

## Indice

1. [Pre-requisitos](#1-pre-requisitos)
2. [Instalacao](#2-instalacao)
3. [Configuracao](#3-configuracao)
4. [Primeiro Uso](#4-primeiro-uso)
5. [Proximos Passos](#5-proximos-passos)

---

## 1. Pre-requisitos

### 1.1 Hardware

Antes de comecar, verifique se seu computador atende aos requisitos:

| Componente | Minimo                  | Como verificar |
| ---------- | ----------------------- | -------------- |
| GPU NVIDIA | GTX 1650 (4GB VRAM)     | `nvidia-smi`   |
| RAM        | 16GB                    | `free -h`      |
| Disco      | 20GB livres             | `df -h`        |
| Microfone  | Qualquer USB ou onboard | `arecord -l`   |

> **AMD GPU?** O projeto suporta ROCm, mas os testes foram feitos primariamente em NVIDIA.

### 1.2 Sistema Operacional

- Ubuntu 22.04+ (recomendado)
- Fedora 38+
- Arch Linux
- Outras distros baseadas em Debian/RHEL

### 1.3 Dependencias de Sistema

O script de instalacao cuida disso automaticamente, mas se preferir instalar manualmente:

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install -y \
    python3.12 python3.12-venv \
    ffmpeg portaudio19-dev \
    playerctl brightnessctl \
    libnotify-bin
```

**Fedora:**

```bash
sudo dnf install -y \
    python3.12 \
    ffmpeg portaudio-devel \
    playerctl brightnessctl \
    libnotify
```

**Arch:**

```bash
sudo pacman -S \
    python \
    ffmpeg portaudio \
    playerctl brightnessctl \
    libnotify
```

### 1.4 CUDA (para GPU NVIDIA)

Verifique se o CUDA esta instalado:

```bash
nvcc --version
# Deve mostrar CUDA 12.x
```

Se nao estiver instalado, siga o [guia oficial da NVIDIA](https://developer.nvidia.com/cuda-downloads).

---

## 2. Instalacao

### 2.1 Instalar o uv (gerenciador de pacotes)

O Mascate usa o `uv` para gerenciar dependencias Python:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reinicie o terminal ou execute:

```bash
source ~/.bashrc  # ou ~/.zshrc
```

Verifique a instalacao:

```bash
uv --version
# uv 0.x.x
```

### 2.2 Clonar o Repositorio

```bash
git clone https://github.com/seu-usuario/mascate.git
cd mascate
```

### 2.3 Instalar Dependencias Python

```bash
uv sync
```

Este comando:

- Cria um ambiente virtual automaticamente
- Instala todas as dependencias do `pyproject.toml`
- Tempo estimado: 2-5 minutos

### 2.4 Instalar Dependencias do Sistema

```bash
uv run python scripts/install_deps.py
```

O script vai:

- Detectar sua distribuicao Linux
- Instalar pacotes necessarios (pode pedir senha sudo)
- Verificar se tudo esta funcionando

### 2.5 Baixar Modelos de IA

```bash
uv run python scripts/download_models.py
```

Este e o passo mais demorado. Os modelos sao:

| Modelo             | Tamanho | Funcao              |
| ------------------ | ------- | ------------------- |
| Granite 4.0 (Q8_0) | ~1.3GB  | LLM (interpretacao) |
| Whisper Large v3   | ~3GB    | STT (fala → texto)  |
| Piper pt-BR        | ~100MB  | TTS (texto → fala)  |
| Silero VAD         | ~2MB    | Deteccao de voz     |
| BGE-M3             | ~2GB    | Embeddings (RAG)    |

**Tempo estimado:** 10-30 minutos (dependendo da conexao)

Os modelos sao salvos em `~/.local/share/mascate/models/`

---

## 3. Configuracao

### 3.1 Criar Arquivo de Configuracao

```bash
mkdir -p ~/.config/mascate
cp config.toml.example ~/.config/mascate/config.toml
```

### 3.2 Configuracao Minima

Edite `~/.config/mascate/config.toml`:

```toml
[general]
debug = false

[audio]
# Ativacao por atalho de teclado (recomendado)
hotkey_enabled = true
hotkey = "ctrl+shift+m"
hotkey_only = true  # Desativa wake word

[llm]
# Camadas na GPU (-1 = todas, 0 = apenas CPU)
n_gpu_layers = -1
```

Para configuracao completa, veja [Referencia de Configuracao](configuration.md).

### 3.3 Verificar Instalacao

Execute o comando de verificacao:

```bash
uv run mascate check
```

Saida esperada:

```
Mascate - Verificacao de Sistema

[OK] Python 3.12.x
[OK] CUDA disponivel (12.x)
[OK] Modelo LLM encontrado
[OK] Modelo STT encontrado
[OK] Modelo TTS encontrado
[OK] Dispositivo de audio detectado
[OK] Configuracao valida

Sistema pronto para uso!
```

Se algum item falhar, veja [Solucao de Problemas](troubleshooting.md).

---

## 4. Primeiro Uso

### 4.1 Iniciar o Mascate

```bash
uv run mascate run
```

Voce vera a interface no terminal:

```
╭─────────────────────────────────────╮
│         MASCATE v0.1.0              │
├─────────────────────────────────────┤
│ Status: IDLE                        │
│ Hotkey: Ctrl+Shift+M                │
├─────────────────────────────────────┤
│ Aguardando ativacao...              │
╰─────────────────────────────────────╯
```

### 4.2 Testar Comandos

1. **Pressione `Ctrl+Shift+M`** para ativar
2. O status muda para `LISTENING`
3. **Diga um comando:** "Abre a calculadora"
4. O Mascate processa e executa

### 4.3 Comandos para Testar

Comece com comandos simples:

```
"Abre a calculadora"
"Que horas sao"
"Aumenta o volume"
"Abre o Firefox"
```

### 4.4 Parar o Mascate

Pressione `Ctrl+C` para encerrar.

---

## 5. Proximos Passos

Agora que o Mascate esta funcionando:

1. **[Guia do Usuario](user-guide.md)** - Lista completa de comandos
2. **[Configuracao](configuration.md)** - Personalize o comportamento
3. **[Solucao de Problemas](troubleshooting.md)** - Se algo nao funcionar

---

## Resumo dos Comandos

```bash
# Instalacao (uma vez)
git clone https://github.com/seu-usuario/mascate.git
cd mascate
uv sync
uv run python scripts/install_deps.py
uv run python scripts/download_models.py
mkdir -p ~/.config/mascate
cp config.toml.example ~/.config/mascate/config.toml

# Uso diario
cd mascate
uv run mascate run

# Verificacao
uv run mascate check
uv run mascate version
```

---

[Voltar ao README](../README.md) | [Proximo: Guia do Usuario](user-guide.md)
