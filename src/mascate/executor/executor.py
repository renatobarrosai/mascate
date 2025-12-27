"""Executor Central do Mascate.

Orquestra parsing, segurança e execução de comandos.
"""

from __future__ import annotations

import logging
from typing import Any

from mascate.core.config import Config
from mascate.executor.models import RiskLevel
from mascate.executor.parser import CommandParser
from mascate.executor.registry import get_handler
from mascate.executor.security import SecurityError, SecurityGuard

logger = logging.getLogger(__name__)


class Executor:
    """Responsável por executar comandos de forma segura."""

    def __init__(self, config: Config) -> None:
        """Inicializa o executor.

        Args:
            config: Configuração global.
        """
        self.config = config
        self.guard = SecurityGuard(config)
        self.parser = CommandParser()

    def execute_intent(
        self, intent_data: dict[str, Any] | str, confirmed: bool = False
    ) -> str:
        """Orquestra o fluxo completo de execução.

        Args:
            intent_data: Dados da intenção vindos do Brain.
            confirmed: Se o usuário confirmou a execução (para comandos HIGH risk).

        Returns:
            Mensagem de feedback para o usuário.
        """
        # 1. Parsing
        command = self.parser.parse(intent_data)
        logger.info(
            "Executando intenção: %s (%s)", command.action.value, command.target
        )

        # 2. Validação de Segurança
        try:
            self.guard.validate(command)
        except SecurityError as e:
            logger.error("Bloqueio de segurança: %s", e)
            return f"Desculpe, não posso fazer isso por segurança: {e}"

        # 3. Verificação de Autorização (Confirmação)
        if not self.guard.is_authorized(command, user_confirmed=confirmed):
            if command.risk_level == RiskLevel.HIGH:
                return f"CONFIRM_REQUIRED:{command.action.value}:{command.target}"
            return "Comando não autorizado."

        # 4. Execução
        handler = get_handler(command.action)
        if not handler:
            if command.action.value == "reply":
                return command.target  # Resposta direta do LLM
            return f"Ação '{command.action.value}' não implementada ou não suportada."

        success = handler.execute(command)

        if success:
            return f"Pronto! Executei {command.action.value} para {command.target}."
        else:
            return f"Tentei, mas houve um erro ao executar {command.action.value}."
