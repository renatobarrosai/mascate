"""Parser de Comandos para o Mascate.

Traduz intenções JSON do LLM em objetos Command estruturados.
"""

from __future__ import annotations

import logging
from typing import Any

from mascate.executor.models import ActionType, Command

logger = logging.getLogger(__name__)


class CommandParser:
    """Tradutor de JSON para comandos executáveis."""

    @staticmethod
    def parse(data: dict[str, Any] | str) -> Command:
        """Converte dicionário ou JSON string em Command.

        Args:
            data: Dados vindos do LLM.

        Returns:
            Instância de Command.
        """
        if isinstance(data, str):
            import json

            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logger.error("Falha ao parsear JSON de comando: %s", data)
                return Command(action=ActionType.UNKNOWN, target="", raw_json=data)

        action_str = data.get("action", "unknown")
        target = data.get("target", "")
        params = data.get("params", {})

        # Mapeia string para Enum
        try:
            action = ActionType(action_str)
        except ValueError:
            logger.warning("Ação desconhecida recebida: %s", action_str)
            action = ActionType.UNKNOWN

        return Command(action=action, target=target, params=params, raw_json=str(data))
