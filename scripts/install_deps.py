#!/usr/bin/env python3
"""Instalacao de dependencias do sistema para o Mascate.

Detecta a distribuicao Linux e instala pacotes necessarios.
Suporta Ubuntu/Debian, Arch Linux e Fedora.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@dataclass
class Distro:
    """Informacoes da distribuicao."""

    name: str
    package_manager: str
    install_cmd: list[str]
    packages: dict[str, str]  # nome generico -> nome do pacote


# Mapeamento de distribuicoes
DISTROS: dict[str, Distro] = {
    "ubuntu": Distro(
        name="Ubuntu/Debian",
        package_manager="apt",
        install_cmd=["sudo", "apt", "install", "-y"],
        packages={
            "ffmpeg": "ffmpeg",
            "playerctl": "playerctl",
            "portaudio": "portaudio19-dev",
            "alsa": "libasound2-dev",
            "pulseaudio": "libpulse-dev",
            "wmctrl": "wmctrl",
            "xdotool": "xdotool",
            "ydotool": "ydotool",
        },
    ),
    "arch": Distro(
        name="Arch Linux",
        package_manager="pacman",
        install_cmd=["sudo", "pacman", "-S", "--noconfirm"],
        packages={
            "ffmpeg": "ffmpeg",
            "playerctl": "playerctl",
            "portaudio": "portaudio",
            "alsa": "alsa-lib",
            "pulseaudio": "libpulse",
            "wmctrl": "wmctrl",
            "xdotool": "xdotool",
            "ydotool": "ydotool",
        },
    ),
    "fedora": Distro(
        name="Fedora",
        package_manager="dnf",
        install_cmd=["sudo", "dnf", "install", "-y"],
        packages={
            "ffmpeg": "ffmpeg",
            "playerctl": "playerctl",
            "portaudio": "portaudio-devel",
            "alsa": "alsa-lib-devel",
            "pulseaudio": "pulseaudio-libs-devel",
            "wmctrl": "wmctrl",
            "xdotool": "xdotool",
            "ydotool": "ydotool",
        },
    ),
}

# Pacotes necessarios (nomes genericos)
REQUIRED_PACKAGES = [
    ("ffmpeg", "Processamento de audio/video"),
    ("playerctl", "Controle de midia MPRIS"),
    ("portaudio", "Biblioteca de audio PortAudio"),
    ("alsa", "Headers ALSA"),
    ("pulseaudio", "Headers PulseAudio"),
]

# Pacotes opcionais (automacao)
OPTIONAL_PACKAGES = [
    ("wmctrl", "Controle de janelas (X11)"),
    ("xdotool", "Simulacao de input (X11)"),
    ("ydotool", "Simulacao de input (Wayland)"),
]


def detect_distro() -> Distro | None:
    """Detecta a distribuicao Linux.

    Returns:
        Distro se detectada, None caso contrario.
    """
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return None

    content = os_release.read_text().lower()

    if "ubuntu" in content or "debian" in content or "mint" in content:
        return DISTROS["ubuntu"]
    elif "arch" in content or "manjaro" in content:
        return DISTROS["arch"]
    elif "fedora" in content or "rhel" in content or "centos" in content:
        return DISTROS["fedora"]

    return None


def check_command(command: str) -> bool:
    """Verifica se um comando existe no PATH.

    Args:
        command: Nome do comando.

    Returns:
        True se existe, False caso contrario.
    """
    return shutil.which(command) is not None


def install_packages(distro: Distro, packages: list[str]) -> bool:
    """Instala pacotes via gerenciador de pacotes.

    Args:
        distro: Informacoes da distribuicao.
        packages: Lista de nomes genericos de pacotes.

    Returns:
        True se instalacao bem-sucedida.
    """
    # Mapeia nomes genericos para nomes especificos da distro
    pkg_names = []
    for pkg in packages:
        if pkg in distro.packages:
            pkg_names.append(distro.packages[pkg])
        else:
            console.print(
                f"  [yellow]WARN[/yellow] Pacote '{pkg}' nao mapeado para {distro.name}"
            )

    if not pkg_names:
        return True

    cmd = distro.install_cmd + pkg_names
    console.print(f"  [dim]Executando: {' '.join(cmd)}[/dim]")

    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        console.print(f"  [red]ERROR[/red] Falha na instalacao: {e}")
        return False
    except FileNotFoundError:
        console.print(
            f"  [red]ERROR[/red] Gerenciador '{distro.package_manager}' nao encontrado"
        )
        return False


def show_packages_table() -> None:
    """Mostra tabela com pacotes a serem instalados."""
    table = Table(
        title="Pacotes do Sistema", show_header=True, header_style="bold cyan"
    )
    table.add_column("Pacote", style="cyan")
    table.add_column("Descricao")
    table.add_column("Tipo", style="green")

    for pkg, desc in REQUIRED_PACKAGES:
        table.add_row(pkg, desc, "Obrigatorio")

    for pkg, desc in OPTIONAL_PACKAGES:
        table.add_row(pkg, desc, "[dim]Opcional[/dim]")

    console.print(table)
    console.print()


def main() -> int:
    """Funcao principal.

    Returns:
        Codigo de saida (0 = sucesso).
    """
    console.print(
        Panel.fit(
            "[bold cyan]Mascate[/bold cyan] - Instalacao de Dependencias do Sistema",
            subtitle="[dim]Assistente de Voz Edge AI[/dim]",
        )
    )
    console.print()

    # Detecta distro
    distro = detect_distro()
    if distro is None:
        console.print("[red]ERROR[/red] Distribuicao Linux nao detectada.")
        console.print("Distribuicoes suportadas: Ubuntu, Debian, Arch, Fedora")
        return 1

    console.print(f"[bold]Distribuicao:[/bold] {distro.name}")
    console.print(f"[bold]Gerenciador:[/bold] {distro.package_manager}")
    console.print()

    show_packages_table()

    # Verifica pacotes ja instalados
    console.print("[bold]Verificando pacotes instalados...[/bold]")
    missing_required: list[str] = []
    missing_optional: list[str] = []

    for pkg, _ in REQUIRED_PACKAGES:
        # Libs precisam ser instaladas, verificamos via pkg manager
        missing_required.append(pkg)

    for pkg, _ in OPTIONAL_PACKAGES:
        if not check_command(pkg):
            missing_optional.append(pkg)
        else:
            console.print(f"  [green]OK[/green] {pkg} ja instalado")

    console.print()

    # Instala pacotes necessarios
    if missing_required:
        console.print(
            f"[bold]Instalando {len(missing_required)} pacotes obrigatorios...[/bold]"
        )
        if not install_packages(distro, missing_required):
            console.print(
                Panel.fit(
                    "[red]Falha ao instalar pacotes obrigatorios[/red]",
                    border_style="red",
                )
            )
            return 1
        console.print("[green]OK[/green] Pacotes obrigatorios instalados.")
        console.print()

    # Instala pacotes opcionais
    if missing_optional:
        console.print(
            f"[bold]Instalando {len(missing_optional)} pacotes opcionais...[/bold]"
        )
        install_packages(distro, missing_optional)
        console.print()

    # Sucesso
    console.print(
        Panel.fit(
            "[bold green]Instalacao concluida![/bold green]",
            border_style="green",
        )
    )
    console.print()

    console.print("[bold]Proximos passos:[/bold]")
    console.print(
        "  1. [cyan]uv sync[/cyan]                              # Deps Python"
    )
    console.print(
        "  2. [cyan]uv run python scripts/download_models.py[/cyan]  # Modelos"
    )
    console.print("  3. [cyan]uv run mascate run[/cyan]                   # Executar")

    return 0


if __name__ == "__main__":
    sys.exit(main())
