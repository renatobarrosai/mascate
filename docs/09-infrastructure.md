# Mascate - Infraestrutura

**Versao:** 1.0  
**Status:** Aprovado para Implementacao

Este documento define a estrategia de infraestrutura, repositorio e distribuicao.

---

## 1. Estrutura de Repositorio (Monorepo)

Para agilizar o desenvolvimento e facilitar distribuicao, adotamos **Repositorio Unico**.

### Arvore de Arquivos

```
mascate/
+-- src/
|   +-- mascate/
|       +-- __init__.py
|       +-- audio/           # STT, TTS, VAD, Wake Word
|       |   +-- __init__.py
|       |   +-- capture.py
|       |   +-- wake_word.py
|       |   +-- vad.py
|       |   +-- stt.py
|       |   +-- tts.py
|       +-- intelligence/    # RAG, LLM, GBNF
|       |   +-- __init__.py
|       |   +-- rag.py
|       |   +-- llm.py
|       |   +-- prompts.py
|       +-- executor/        # Comandos, Seguranca
|       |   +-- __init__.py
|       |   +-- dispatcher.py
|       |   +-- security.py
|       |   +-- handlers/
|       +-- interface/       # CLI, Rich, Logs
|       |   +-- __init__.py
|       |   +-- hud.py
|       |   +-- cli.py
|       +-- core/            # Orquestrador, Config
|           +-- __init__.py
|           +-- config.py
|           +-- state.py
|           +-- main.py
+-- tests/
|   +-- unit/
|   +-- integration/
|   +-- e2e/
+-- knowledge_base/
|   +-- sistema/
|   +-- apps/
|   +-- comandos/
+-- models/                  # (gitignore)
+-- scripts/
|   +-- install_deps.py
|   +-- download_models.py
+-- grammars/
|   +-- json_grammar.gbnf
+-- logs/                    # (gitignore)
+-- pyproject.toml
+-- config.toml
+-- README.md
```

---

## 2. Gestao de Dependencias (Estrategia Hibrida)

O sistema depende de duas camadas com ferramentas diferentes.

### Camada A: Python (Gerenciada pelo `uv`)

- **Ferramenta:** `uv` (Astral)
- **Arquivo:** `pyproject.toml`
- **Funcao:** Bibliotecas Python (llama-cpp-python, qdrant-client, etc)

### Camada B: Sistema Operacional (Gerenciada por Script)

- **Ferramenta:** Script `scripts/install_deps.py`
- **Funcao:** Detecta a distro e chama o gerenciador correto

---

## 3. Script de Dependencias (install_deps.py)

### Mapeamento de Pacotes

| Pacote         | Arch (pacman) | Ubuntu (apt)      |
| :------------- | :------------ | :---------------- |
| FFmpeg         | `ffmpeg`      | `ffmpeg`          |
| PlayerCtl      | `playerctl`   | `playerctl`       |
| ydotool        | `ydotool`     | `ydotool`         |
| XDG Utils      | `xdg-utils`   | `xdg-utils`       |
| PortAudio      | `portaudio`   | `libportaudio2`   |
| Build Tools    | `base-devel`  | `build-essential` |
| Python Headers | `python`      | `python3-dev`     |

### Implementacao

```python
import subprocess
import platform
from pathlib import Path

def detect_distro() -> str:
    """Detecta a distribuicao Linux."""
    os_release = Path("/etc/os-release")
    if os_release.exists():
        content = os_release.read_text()
        if "arch" in content.lower():
            return "arch"
        elif "ubuntu" in content.lower() or "debian" in content.lower():
            return "debian"
    return "unknown"

def install_packages(distro: str):
    """Instala pacotes do sistema."""
    packages = {
        "arch": {
            "manager": ["sudo", "pacman", "-S", "--noconfirm"],
            "packages": ["ffmpeg", "playerctl", "ydotool", "xdg-utils", "portaudio"]
        },
        "debian": {
            "manager": ["sudo", "apt", "install", "-y"],
            "packages": ["ffmpeg", "playerctl", "ydotool", "xdg-utils", "libportaudio2"]
        }
    }

    config = packages.get(distro)
    if not config:
        raise ValueError(f"Distro nao suportada: {distro}")

    cmd = config["manager"] + config["packages"]
    subprocess.run(cmd, check=True)
```

---

## 4. Configuracao (pyproject.toml)

```toml
[project]
name = "mascate"
version = "0.1.0"
description = "Edge AI Voice Assistant for Linux"
requires-python = ">=3.12"

dependencies = [
    # LLM
    "llama-cpp-python",

    # Audio
    "sounddevice",
    "numpy",

    # STT/TTS
    "openwakeword",
    "piper-tts",

    # RAG
    "qdrant-client",
    "FlagEmbedding",

    # Interface
    "rich",
    "textual",

    # Config
    "tomli",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "ruff",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## 5. Fluxo de Setup (Onboarding)

O usuario segue 3 passos:

```bash
# 1. Clone
git clone https://github.com/user/mascate.git
cd mascate

# 2. Dependencias de Sistema (pede sudo)
python scripts/install_deps.py

# 3. Run (uv baixa Python, cria venv, instala libs)
uv run mascate
```

---

## 6. Arquivos de Configuracao

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/

# Modelos (binarios grandes)
models/
*.gguf
*.onnx
*.bin
*.safetensors

# Logs
logs/
*.log

# Config local
.env
.env.local

# IDE
.vscode/
.idea/

# Qdrant data
data/qdrant/
```

### config.toml

Ver documento [03-implementation-plan.md](./03-implementation-plan.md) para estrutura completa.

---

## 7. Logging

```python
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging(config):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    handler = RotatingFileHandler(
        log_dir / "mascate.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )

    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[handler, logging.StreamHandler()]
    )
```

---

## 8. Vantagens da Abordagem

- **Sem Docker:** Acesso nativo ao hardware (GPU/Audio)
- **Portabilidade:** Suporta Arch e Ubuntu/Debian
- **Velocidade:** `uv` e extremamente rapido
- **Simplicidade:** 3 comandos para setup completo

---

## Referencias

- [03-implementation-plan.md](./03-implementation-plan.md) - Plano de implementacao
- [04-model-management.md](./04-model-management.md) - Gestao de modelos
