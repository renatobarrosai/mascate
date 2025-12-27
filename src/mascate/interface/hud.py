"""Interface Visual (HUD) para o Mascate.

Usa Rich e Textual para exibir o estado do assistente e logs no terminal.
"""

from __future__ import annotations

import logging
from datetime import datetime

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

logger = logging.getLogger(__name__)


class HUD:
    """Interface de usuário em modo texto (TUI) para o Mascate."""

    def __init__(self, version: str = "0.1.0") -> None:
        """Inicializa o HUD.

        Args:
            version: Versão do sistema.
        """
        self.console = Console()
        self.version = version
        self.state = "INICIALIZANDO"
        self.audio_level = 0.0
        self.last_transcript = ""
        self.last_response = ""
        self.logs: list[str] = []
        self._live: Live | None = None

    def update_state(self, state: str) -> None:
        """Atualiza o estado atual (ex: LISTENING, PROCESSING)."""
        self.state = state
        self._refresh()

    def update_audio_level(self, level: float) -> None:
        """Atualiza o indicador de volume (0.0 a 1.0)."""
        self.audio_level = level
        self._refresh()

    def add_log(self, message: str, level: str = "INFO") -> None:
        """Adiciona uma mensagem ao log visual do HUD."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {level}: {message}")
        if len(self.logs) > 5:
            self.logs.pop(0)
        self._refresh()

    def set_interaction(self, user_text: str, assistant_text: str) -> None:
        """Atualiza a última interação exibida."""
        self.last_transcript = user_text
        self.last_response = assistant_text
        self._refresh()

    def _create_view(self) -> Panel:
        """Gera o layout visual do HUD."""
        # Indicador de Estado e Versão
        header = Table.grid(expand=True)
        header.add_column(justify="left")
        header.add_column(justify="right")

        state_color = "green" if self.state == "IDLE" else "yellow"
        if self.state == "LISTENING":
            state_color = "bold red"

        header.add_row(
            Text.assemble(("MASCATE ", "bold cyan"), (f"v{self.version}", "dim")),
            Text(f"● {self.state}", style=state_color),
        )

        # VU Meter (Barra de Áudio)
        audio_progress = Progress(
            TextColumn("Áudio:"),
            BarColumn(bar_width=20, complete_style="green", finished_style="green"),
            expand=False,
        )
        audio_progress.add_task("volume", total=1.0, completed=self.audio_level)

        # Área de Interação
        interaction = Table.grid(expand=True)
        if self.last_transcript:
            interaction.add_row(
                Text(f"[USER] > {self.last_transcript}", style="italic yellow")
            )
        if self.last_response:
            interaction.add_row(
                Text(f"[BOT]  < {self.last_response}", style="bold green")
            )

        # Logs
        log_text = Text("\n".join(self.logs), style="dim white")

        # Composição Final
        content = Group(
            header,
            audio_progress,
            Text(""),  # Espaçador
            interaction,
            Text("─" * 40, style="dim"),
            log_text,
        )

        return Panel(content, border_style="cyan", title="Terminal de Controle")

    def _refresh(self) -> None:
        """Atualiza a exibição Live se estiver ativa."""
        if self._live:
            self._live.update(self._create_view())

    def start(self) -> Live:
        """Inicia a exibição em tempo real."""
        self._live = Live(
            self._create_view(), console=self.console, refresh_per_second=10
        )
        self._live.start()
        return self._live

    def stop(self) -> None:
        """Para a exibição em tempo real."""
        if self._live:
            self._live.stop()
            self._live = None
