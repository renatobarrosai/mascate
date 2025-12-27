"""Handler para abrir aplicativos."""

from mascate.executor.handlers.base import BaseHandler
from mascate.executor.models import Command


class AppHandler(BaseHandler):
    """Executa aplicativos instalados no sistema."""

    def execute(self, command: Command) -> bool:
        # Usa o target como o nome do executável
        # No Linux, o ideal seria procurar o .desktop, mas para a PoC
        # rodar o binário diretamente via binário ou xdg-open funciona.
        return self.run_process([command.target])
