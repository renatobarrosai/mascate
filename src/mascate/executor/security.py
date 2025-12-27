"""Segurança (Guarda-Costas) do Mascate.

Valida comandos antes da execução para evitar danos ao sistema.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from mascate.core.config import Config
from mascate.executor.models import Command, RiskLevel

logger = logging.getLogger(__name__)

# Padrões de shell injection a bloquear
SHELL_INJECTION_PATTERN = re.compile(
    r"[;&|><`\n]"  # Operadores de shell básicos
    r"|\$\("  # Subshell $(...)
    r"|\$\{"  # Expansão de variável ${...}
    r"|`[^`]*`"  # Backticks
    r"|\|\|"  # OR lógico
    r"|&&"  # AND lógico
)


class SecurityError(Exception):
    """Erro de segurança disparado pelo Guarda-Costas."""


class SecurityGuard:
    """Validador determinístico de segurança."""

    def __init__(self, config: Config) -> None:
        """Inicializa o validador.

        Args:
            config: Configuração global contendo a blacklist.
        """
        self.config = config
        self.blacklist = [cmd.lower() for cmd in config.security.blacklist_commands]
        self.protected_paths = [Path(p) for p in config.security.protected_paths]

    def validate(self, command: Command) -> RiskLevel:
        """Avalia o risco de um comando e valida contra a blacklist.

        Args:
            command: O comando a ser validado.

        Returns:
            O RiskLevel atualizado.

        Raises:
            SecurityError: Se o comando for terminantemente proibido (CRITICAL).
        """
        # 1. Verifica Blacklist no target e nos params
        full_command_str = f"{command.target} {command.params!s}".lower()

        for forbidden in self.blacklist:
            if forbidden in full_command_str:
                logger.critical("Comando bloqueado pela BLACKLIST: %s", forbidden)
                command.risk_level = RiskLevel.CRITICAL
                raise SecurityError(f"Comando proibido detectado: {forbidden}")

        # 2. Verifica caminhos protegidos com validação de path real
        if command.target:
            self._check_protected_paths(command)

        # 3. Detecta injeção de shell
        if command.target:
            if SHELL_INJECTION_PATTERN.search(command.target):
                logger.critical(
                    "Injeção de shell detectada no target: %s", command.target
                )
                command.risk_level = RiskLevel.CRITICAL
                raise SecurityError(
                    "Caracteres especiais de shell não permitidos no target."
                )

        # 4. Verifica params por injeção também
        for key, value in command.params.items():
            if isinstance(value, str) and SHELL_INJECTION_PATTERN.search(value):
                logger.critical(
                    "Injeção de shell detectada no param '%s': %s", key, value
                )
                command.risk_level = RiskLevel.CRITICAL
                raise SecurityError(
                    f"Caracteres especiais de shell não permitidos no param '{key}'."
                )

        return command.risk_level

    def _check_protected_paths(self, command: Command) -> None:
        """Verifica se o comando tenta acessar caminhos protegidos.

        Args:
            command: O comando a verificar.
        """
        # Extrai possíveis paths do target
        potential_paths = self._extract_paths(command.target)

        for path_str in potential_paths:
            try:
                # Resolve o path para evitar truques com ../
                target_path = Path(path_str).resolve()

                for protected in self.protected_paths:
                    protected_resolved = protected.resolve()

                    # Verifica se o target está dentro de um path protegido
                    try:
                        target_path.relative_to(protected_resolved)
                        logger.warning(
                            "Acesso a caminho protegido detectado: %s", target_path
                        )
                        command.risk_level = RiskLevel.HIGH
                        return
                    except ValueError:
                        # Não é relativo, não está protegido
                        continue
            except Exception:
                # Path inválido, ignora
                continue

    def _extract_paths(self, text: str) -> list[str]:
        """Extrai possíveis caminhos de um texto.

        Args:
            text: Texto a analisar.

        Returns:
            Lista de strings que parecem ser caminhos.
        """
        paths = []

        # Padrão para paths absolutos ou relativos
        path_pattern = re.compile(r"(?:^|[\s\"'])([/~][^\s\"']*|\.\.?/[^\s\"']*)")

        for match in path_pattern.finditer(text):
            paths.append(match.group(1))

        # Se o texto inteiro parece um path
        if text.startswith(("/", "~", "./", "../")):
            paths.append(text)

        return paths

    def is_authorized(self, command: Command, user_confirmed: bool = False) -> bool:
        """Verifica se o comando tem autorização para rodar.

        Args:
            command: Comando validado.
            user_confirmed: Se o usuário já deu OK físico/verbal.

        Returns:
            True se autorizado.
        """
        if command.risk_level == RiskLevel.CRITICAL:
            return False

        if command.risk_level == RiskLevel.HIGH:
            return user_confirmed

        return True
