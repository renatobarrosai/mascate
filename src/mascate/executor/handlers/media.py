"""Handler para controle de mídia (MPRIS)."""

import logging

from mascate.executor.handlers.base import BaseHandler
from mascate.executor.models import Command

logger = logging.getLogger(__name__)


class MediaHandler(BaseHandler):
    """Controla players de mídia compatíveis com MPRIS via playerctl."""

    def execute(self, command: Command) -> bool:
        action = command.target.lower()

        # Mapeamento de comandos falados para comandos do playerctl
        cmd_map = {
            "play": "play",
            "pausa": "pause",
            "pause": "pause",
            "toca": "play-pause",
            "proxima": "next",
            "anterior": "previous",
            "stop": "stop",
        }

        pctl_cmd = cmd_map.get(action, action)

        logger.debug("Mídia: %s -> playerctl %s", action, pctl_cmd)
        # playerctl costuma ser rápido, rodamos síncrono para checar erro
        return self.run_process(["playerctl", pctl_cmd], detach=False)
