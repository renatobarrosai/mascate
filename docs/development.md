# Guia de Desenvolvimento

Guia para contribuidores e desenvolvedores do Mascate.

---

## Indice

1. [Ambiente de Desenvolvimento](#1-ambiente-de-desenvolvimento)
2. [Estrutura do Projeto](#2-estrutura-do-projeto)
3. [Padroes de Codigo](#3-padroes-de-codigo)
4. [Testes](#4-testes)
5. [Fluxo de Trabalho](#5-fluxo-de-trabalho)
6. [Guias por Modulo](#6-guias-por-modulo)

---

## 1. Ambiente de Desenvolvimento

### 1.1 Requisitos

- Python 3.12+
- uv (gerenciador de pacotes)
- Git

### 1.2 Setup Inicial

```bash
# Clone o repositorio
git clone https://github.com/seu-usuario/mascate.git
cd mascate

# Instale dependencias (incluindo dev)
uv sync --extra dev

# Verifique a instalacao
uv run pytest --version
uv run ruff --version
```

### 1.3 IDE Recomendada

**VS Code** com extensoes:

- Python (Microsoft)
- Ruff (Astral)
- TOML (Even Better)

**Configuracao sugerida** (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

---

## 2. Estrutura do Projeto

```
mascate/
├── src/mascate/           # Codigo fonte
│   ├── audio/             # Processamento de audio
│   ├── intelligence/      # LLM e RAG
│   ├── executor/          # Execucao de comandos
│   ├── core/              # Orquestracao e config
│   └── interface/         # CLI e HUD
├── tests/                 # Testes
│   ├── unit/              # Testes unitarios
│   ├── integration/       # Testes de integracao
│   └── e2e/               # Testes end-to-end
├── scripts/               # Scripts auxiliares
├── docs/                  # Documentacao
│   └── technical/         # Docs tecnicos detalhados
├── pyproject.toml         # Configuracao do projeto
├── config.toml.example    # Exemplo de configuracao
└── AGENTS.md              # Guia para agentes de IA
```

---

## 3. Padroes de Codigo

### 3.1 Estilo

O projeto usa **Ruff** para linting e formatacao.

```bash
# Verificar problemas
uv run ruff check src tests

# Corrigir automaticamente
uv run ruff check src tests --fix

# Formatar codigo
uv run ruff format src tests
```

### 3.2 Type Hints

**Obrigatorio** em todas as funcoes publicas:

```python
# Correto
def process_audio(audio: np.ndarray, sample_rate: int = 16000) -> str:
    """Processa audio e retorna transcricao."""
    ...

# Incorreto
def process_audio(audio, sample_rate=16000):
    ...
```

Use `from __future__ import annotations` para sintaxe moderna:

```python
from __future__ import annotations

def get_items() -> list[str]:  # Em vez de List[str]
    ...
```

### 3.3 Docstrings

Use formato Google:

```python
def validate_command(command: Command, config: Config) -> bool:
    """Valida um comando contra regras de seguranca.

    Args:
        command: Comando a ser validado.
        config: Configuracao contendo regras.

    Returns:
        True se o comando e seguro para execucao.

    Raises:
        SecurityError: Se o comando for bloqueado.
    """
```

### 3.4 Nomenclatura

| Tipo       | Convencao       | Exemplo            |
| ---------- | --------------- | ------------------ |
| Modulos    | snake_case      | `audio_capture.py` |
| Classes    | PascalCase      | `AudioCapture`     |
| Funcoes    | snake_case      | `process_audio`    |
| Constantes | SCREAMING_SNAKE | `MAX_AUDIO_LENGTH` |
| Privados   | \_prefixo       | `_internal_buffer` |

### 3.5 Imports

Ordem (gerenciada pelo Ruff):

1. Standard library
2. Third-party
3. Local

```python
# Standard library
import logging
from pathlib import Path

# Third-party
import numpy as np
from pydantic import BaseModel

# Local
from mascate.core.config import Config
from mascate.executor.models import Command
```

Prefira imports absolutos:

```python
# Correto
from mascate.core.config import Config

# Evite
from .config import Config
```

---

## 4. Testes

### 4.1 Estrutura de Testes

```
tests/
├── unit/                  # Funcoes isoladas
│   ├── audio/
│   ├── executor/
│   └── intelligence/
├── integration/           # Modulos integrados
└── e2e/                   # Fluxo completo
```

### 4.2 Comandos

```bash
# Rodar todos os testes
uv run pytest

# Testes especificos
uv run pytest tests/unit/
uv run pytest tests/unit/executor/test_security.py
uv run pytest tests/unit/executor/test_security.py::test_blacklist

# Com cobertura
uv run pytest --cov=src --cov-report=html

# Verbose
uv run pytest -v

# Parar no primeiro erro
uv run pytest -x
```

### 4.3 Escrevendo Testes

```python
"""Testes para o modulo de seguranca."""

import pytest
from mascate.executor.security import SecurityGuard
from mascate.executor.models import Command, ActionType


class TestSecurityGuard:
    """Testes para SecurityGuard."""

    def test_allows_safe_command(self, config):
        """Comando seguro deve ser permitido."""
        guard = SecurityGuard(config)
        cmd = Command(action=ActionType.OPEN_APP, target="firefox")

        # Act
        result = guard.validate(cmd)

        # Assert
        assert guard.is_authorized(cmd)

    def test_blocks_blacklisted_command(self, config):
        """Comando na blacklist deve ser bloqueado."""
        guard = SecurityGuard(config)
        cmd = Command(action=ActionType.FILE_OP, target="rm -rf /")

        # Act & Assert
        with pytest.raises(SecurityError):
            guard.validate(cmd)


@pytest.fixture
def config():
    """Fixture de configuracao para testes."""
    return Config()
```

### 4.4 Fixtures Comuns

Localizadas em `tests/conftest.py`:

```python
@pytest.fixture
def config():
    """Configuracao padrao."""
    return Config()

@pytest.fixture
def audio_sample():
    """Amostra de audio para testes."""
    return np.zeros(16000, dtype=np.float32)
```

---

## 5. Fluxo de Trabalho

### 5.1 Criando uma Feature

```bash
# 1. Crie uma branch
git checkout -b feature/nome-da-feature

# 2. Faca alteracoes...

# 3. Rode os testes
uv run pytest

# 4. Verifique o codigo
uv run ruff check src tests --fix
uv run ruff format src tests

# 5. Commit
git add .
git commit -m "feat: descricao da feature"

# 6. Push
git push origin feature/nome-da-feature
```

### 5.2 Convencao de Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefixo     | Uso                 |
| ----------- | ------------------- |
| `feat:`     | Nova funcionalidade |
| `fix:`      | Correcao de bug     |
| `docs:`     | Documentacao        |
| `test:`     | Testes              |
| `refactor:` | Refatoracao         |
| `chore:`    | Manutencao          |

Exemplos:

```
feat: add hotkey activation support
fix: resolve VAD chunk size mismatch
docs: update installation guide
test: add security guard unit tests
```

### 5.3 Checklist Pre-Commit

- [ ] Testes passando: `uv run pytest`
- [ ] Lint limpo: `uv run ruff check src tests`
- [ ] Formatado: `uv run ruff format src tests`
- [ ] Documentacao atualizada (se aplicavel)

---

## 6. Guias por Modulo

### 6.1 Adicionando um Handler

Para adicionar um novo tipo de comando:

1. **Crie o handler** em `src/mascate/executor/handlers/`:

```python
# src/mascate/executor/handlers/calendar.py
"""Handler para operacoes de calendario."""

from mascate.executor.handlers.base import BaseHandler
from mascate.executor.models import Command


class CalendarHandler(BaseHandler):
    """Gerencia eventos de calendario."""

    def execute(self, command: Command) -> bool:
        action = command.params.get("action", "list")

        if action == "list":
            return self._list_events()
        elif action == "add":
            return self._add_event(command.params)

        return False

    def _list_events(self) -> bool:
        # Implementacao...
        return True

    def _add_event(self, params: dict) -> bool:
        # Implementacao...
        return True
```

2. **Registre no registry** (`src/mascate/executor/registry.py`):

```python
from mascate.executor.handlers.calendar import CalendarHandler

HANDLERS = {
    ActionType.CALENDAR: CalendarHandler,
    # ... outros handlers
}
```

3. **Adicione o ActionType** (`src/mascate/executor/models.py`):

```python
class ActionType(str, Enum):
    CALENDAR = "calendar"
    # ... outros tipos
```

4. **Crie testes** (`tests/unit/executor/test_handlers.py`):

```python
class TestCalendarHandler:
    def test_list_events(self):
        handler = CalendarHandler()
        cmd = Command(action=ActionType.CALENDAR, target="", params={"action": "list"})
        assert handler.execute(cmd) is True
```

### 6.2 Modificando Prompts do LLM

Prompts estao em `src/mascate/intelligence/llm/prompts.py`:

```python
SYSTEM_PROMPT = """
Voce e o Mascate, um assistente de voz para Linux.
Analise o pedido do usuario e responda com JSON estruturado.

Formato de resposta:
{"action": "...", "target": "...", "params": {...}}
"""
```

Ao modificar:

1. Teste com varios inputs
2. Verifique se o JSON gerado e valido
3. Adicione exemplos nos testes

### 6.3 Adicionando Configuracao

1. **Adicione o campo** em `src/mascate/core/config.py`:

```python
@dataclass
class AudioConfig:
    sample_rate: int = 16000
    nova_opcao: bool = False  # Nova opcao
```

2. **Documente** em `config.toml.example`:

```toml
[audio]
nova_opcao = false  # Descricao da opcao
```

3. **Atualize a documentacao** em `docs/configuration.md`

---

## Referencias

- [AGENTS.md](../AGENTS.md) - Guia para agentes de codificacao
- [Arquitetura](architecture.md) - Visao tecnica do sistema
- [Ruff](https://docs.astral.sh/ruff/) - Linter e formatter
- [pytest](https://docs.pytest.org/) - Framework de testes

---

[Voltar ao README](../README.md) | [Anterior: Arquitetura](architecture.md) | [Proximo: Troubleshooting](troubleshooting.md)
