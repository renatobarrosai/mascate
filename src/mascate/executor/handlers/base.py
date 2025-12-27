"""Interface base para os Handlers de Comando do Mascate."""

from __future__ import annotations

import logging
import subprocess
from abc import ABC, abstractmethod

from mascate.executor.models import Command

logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """Classe base abstrata para todos os handlers."""

    @abstractmethod
    def execute(self, command: Command) -> bool:
        """Executa o comando.

        Args:
            command: Objeto de comando validado.

        Returns:
            True se a execução foi bem-sucedida.
        """
        pass

    def run_process(self, args: list[str], detach: bool = True) -> bool:
        """Helper para rodar processos do sistema.

        Args:
            args: Lista de argumentos do comando.
            detach: Se deve rodar em background (desacoplado).

        Returns:
            True se iniciou com sucesso.
        """
        try:
            logger.debug("Executando processo: %s", " ".join(args))
            if detach:
                subprocess.Popen(
                    args,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            else:
                subprocess.run(args, check=True, capture_output=True)
            return True
        except Exception as e:
            logger.error("Falha ao rodar processo %s: %s", args[0], e)
            return False
