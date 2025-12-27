"""Modelos de dados para o Executor do Mascate.

Define as ações suportadas e os níveis de risco associados.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionType(Enum):
    """Tipos de ações que o Mascate pode executar."""

    OPEN_APP = "open_app"
    OPEN_URL = "open_url"
    MEDIA_CONTROL = "media_control"
    FILE_OP = "file_op"
    SYSTEM_OP = "system_op"
    REPLY = "reply"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Níveis de risco para execução de comandos."""

    LOW = "low"  # Executar diretamente (ex: abrir app)
    MEDIUM = "medium"  # Logar e executar (ex: controle de volume)
    HIGH = "high"  # Pedir confirmação verbal/física (ex: apagar arquivo)
    CRITICAL = "critical"  # Bloquear sempre (ex: rm -rf /)


@dataclass
class Command:
    """Representação de um comando pronto para execução."""

    action: ActionType
    target: str
    params: dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    raw_json: str = ""

    def __post_init__(self) -> None:
        """Determina o nível de risco básico baseado na ação."""
        if self.action == ActionType.FILE_OP:
            # Operações de arquivo são high por padrão até serem validadas
            self.risk_level = RiskLevel.HIGH
        elif self.action == ActionType.SYSTEM_OP:
            self.risk_level = RiskLevel.HIGH
        elif self.action == ActionType.REPLY:
            self.risk_level = RiskLevel.LOW
