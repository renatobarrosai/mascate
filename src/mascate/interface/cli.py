"""CLI do Mascate."""

from __future__ import annotations

import sys


def main() -> int:
    """Entry point da CLI.

    Returns:
        Codigo de saida.
    """
    try:
        import click
    except ImportError:
        print("Erro: click nao instalado.")
        print("Execute: uv sync")
        return 1

    from mascate.core.logging import setup_logging

    @click.group()
    @click.option("--debug/--no-debug", default=False, help="Modo debug")
    @click.pass_context
    def cli(ctx: click.Context, debug: bool) -> None:
        """Mascate - Assistente de Voz Edge AI para Linux."""
        ctx.ensure_object(dict)
        ctx.obj["debug"] = debug
        setup_logging()

    @cli.command()
    @click.pass_context
    def run(_ctx: click.Context) -> None:
        """Executa o loop principal do Mascate."""
        from rich.console import Console

        console = Console()
        console.print("[bold green]Mascate v0.1.0[/bold green]")
        console.print("Assistente de Voz Edge AI para Linux")
        console.print()
        console.print("[yellow]Status:[/yellow] Em desenvolvimento (Fase 0)")
        console.print()
        console.print("[dim]Pressione Ctrl+C para sair[/dim]")

        try:
            # TODO: Implementar loop principal
            import time

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[dim]Ate logo![/dim]")

    @cli.command()
    def version() -> None:
        """Mostra a versao do Mascate."""
        from mascate import __version__

        print(f"Mascate v{__version__}")

    @cli.command()
    def check() -> None:
        """Verifica a instalacao e dependencias."""
        from rich.console import Console
        from rich.table import Table

        console = Console()
        console.print("[bold]Verificando instalacao...[/bold]")
        console.print()

        table = Table(title="Status de Dependencias")
        table.add_column("Componente", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Notas")

        # Verifica dependencias
        checks = [
            ("Python", True, f"v{sys.version_info.major}.{sys.version_info.minor}"),
            ("Click", True, "CLI framework"),
            ("Rich", True, "Terminal UI"),
        ]

        # Tenta importar dependencias opcionais
        try:
            import sounddevice  # noqa: F401

            checks.append(("sounddevice", True, "Audio I/O"))
        except ImportError:
            checks.append(("sounddevice", False, "pip install sounddevice"))

        try:
            import numpy

            checks.append(("numpy", True, f"v{numpy.__version__}"))
        except ImportError:
            checks.append(("numpy", False, "pip install numpy"))

        try:
            from huggingface_hub import __version__ as hf_version

            checks.append(("huggingface_hub", True, f"v{hf_version}"))
        except ImportError:
            checks.append(("huggingface_hub", False, "pip install huggingface-hub"))

        for name, ok, note in checks:
            status = "[green]OK[/green]" if ok else "[red]MISSING[/red]"
            table.add_row(name, status, note)

        console.print(table)

    return cli(standalone_mode=False) or 0


if __name__ == "__main__":
    sys.exit(main())
