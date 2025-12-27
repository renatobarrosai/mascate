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

# Pacotes CUDA (NVIDIA)
CUDA_PACKAGES: dict[str, dict[str, str]] = {
    "ubuntu": {
        "cuda-toolkit": "nvidia-cuda-toolkit",
        "cuda-dev": "nvidia-cuda-dev",
    },
    "arch": {
        "cuda-toolkit": "cuda",
        "cuda-dev": "cuda",
    },
    "fedora": {
        "cuda-toolkit": "cuda",
        "cuda-dev": "cuda-devel",
    },
}


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


def check_nvidia_gpu() -> bool:
    """Verifica se existe GPU NVIDIA no sistema.

    Returns:
        True se GPU NVIDIA detectada.
    """
    if shutil.which("nvidia-smi"):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0 and result.stdout.strip() != ""
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fallback: verifica lspci
    if shutil.which("lspci"):
        try:
            result = subprocess.run(
                ["lspci"], capture_output=True, text=True, check=False
            )
            return "nvidia" in result.stdout.lower()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return False


def install_cuda_packages(distro: Distro) -> bool:
    """Instala pacotes CUDA para a distribuicao.

    Args:
        distro: Informacoes da distribuicao.

    Returns:
        True se instalacao bem-sucedida.
    """
    # Encontra o mapeamento CUDA para esta distro
    cuda_pkgs = None
    for distro_key in CUDA_PACKAGES:
        if distro_key in distro.name.lower():
            cuda_pkgs = CUDA_PACKAGES[distro_key]
            break

    if not cuda_pkgs:
        console.print(f"  [yellow]WARN[/yellow] CUDA nao mapeado para {distro.name}")
        return False

    pkg_names = list(cuda_pkgs.values())
    cmd = distro.install_cmd + pkg_names
    console.print(f"  [dim]Executando: {' '.join(cmd)}[/dim]")

    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        console.print(f"  [red]ERROR[/red] Falha na instalacao CUDA: {e}")
        return False
    except FileNotFoundError:
        console.print(
            f"  [red]ERROR[/red] Gerenciador '{distro.package_manager}' nao encontrado"
        )
        return False


def main() -> int:
    """Funcao principal.

    Returns:
        Codigo de saida (0 = sucesso).
    """
    import argparse

    parser = argparse.ArgumentParser(description="Instala dependencias do sistema")
    parser.add_argument(
        "--cuda",
        action="store_true",
        help="Tambem instala CUDA toolkit (para GPU NVIDIA)",
    )
    parser.add_argument(
        "--skip-optional",
        action="store_true",
        help="Pula instalacao de pacotes opcionais",
    )
    args = parser.parse_args()

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
    if missing_optional and not args.skip_optional:
        console.print(
            f"[bold]Instalando {len(missing_optional)} pacotes opcionais...[/bold]"
        )
        install_packages(distro, missing_optional)
        console.print()

    # Instala CUDA se solicitado ou se GPU NVIDIA detectada
    if args.cuda or check_nvidia_gpu():
        has_nvcc = shutil.which("nvcc") is not None
        if has_nvcc:
            console.print("[green]OK[/green] CUDA toolkit ja instalado")
        else:
            console.print()
            console.print(
                "[bold]GPU NVIDIA detectada. Instalando CUDA toolkit...[/bold]"
            )
            if install_cuda_packages(distro):
                console.print("[green]OK[/green] CUDA toolkit instalado")
            else:
                console.print(
                    "[yellow]WARN[/yellow] CUDA nao instalado. "
                    "Visite: https://developer.nvidia.com/cuda-downloads"
                )
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
        "  1. [cyan]uv run python scripts/setup.py[/cyan]        # Setup completo (CUDA + modelos)"
    )
    console.print(
        "  2. [cyan]uv run mascate check[/cyan]                  # Verificar instalacao"
    )
    console.print("  3. [cyan]uv run mascate run --hotkey-only[/cyan]      # Executar")

    return 0


if __name__ == "__main__":
    sys.exit(main())
