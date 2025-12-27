"""Handler para abrir URLs no navegador."""

from mascate.executor.handlers.base import BaseHandler
from mascate.executor.models import Command


class BrowserHandler(BaseHandler):
    """Abre URLs usando o navegador padrão via xdg-open."""

    def execute(self, command: Command) -> bool:
        url = command.target
        if not url.startswith(("http://", "https://")):
            # Se não for URL, trata como pesquisa (Google)
            url = f"https://www.google.com/search?q={url.replace(' ', '+')}"

        return self.run_process(["xdg-open", url])
