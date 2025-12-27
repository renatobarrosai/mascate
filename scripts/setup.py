#!/usr/bin/env python3
"""Setup completo do Mascate - Instalacao automatizada.

Este script automatiza todo o processo de instalacao:
1. Dependencias do sistema (ffmpeg, portaudio, etc.)
2. Deteccao e configuracao de GPU NVIDIA/CUDA
3. Compilacao de llama-cpp-python com suporte CUDA
4. Instalacao de pywhispercpp
5. Download dos modelos de IA
6. Criacao do arquivo de configuracao
7. Verificacao final

Uso:
    uv run python scripts/setup.py          # Setup completo
    uv run python scripts/setup.py --check  # Apenas verificar status
    uv run python scripts/setup.py --cuda   # Apenas setup CUDA
    uv run python scripts/setup.py --models # Apenas baixar modelos
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

if TYPE_CHECKING:
    from collections.abc import Sequence

console = Console()


class GPUVendor(Enum):
    """Fabricante de GPU."""

    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    NONE = "none"


@dataclass
class GPUInfo:
    """Informacoes da GPU."""

    vendor: GPUVendor
    name: str
    vram_mb: int
    cuda_version: str | None
    compute_capability: str | None


@dataclass
class SystemInfo:
    """Informacoes do sistema."""

    distro: str
    distro_id: str
    python_version: str
    gpu: GPUInfo | None
    cuda_available: bool
    has_uv: bool


# Mapeamento de arquiteturas CUDA por serie de GPU
CUDA_ARCHITECTURES: dict[str, str] = {
    "RTX 40": "89",  # Ada Lovelace
    "RTX 30": "86",  # Ampere
    "RTX 20": "75",  # Turing
    "GTX 16": "75",  # Turing
    "GTX 10": "61",  # Pascal
    "TITAN V": "70",  # Volta
    "TITAN RTX": "75",
    "A100": "80",
    "A10": "86",
    "A6000": "86",
    "A5000": "86",
    "A4000": "86",
}


def run_command(
    cmd: Sequence[str],
    capture: bool = True,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Executa um comando e retorna o resultado.

    Args:
        cmd: Comando e argumentos.
        capture: Se True, captura stdout/stderr.
        check: Se True, levanta excecao em caso de erro.
        env: Variaveis de ambiente adicionais.

    Returns:
        Resultado do comando.
    """
    full_env = os.environ.copy()
    if env:
        full_env.update(env)

    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=check,
        env=full_env,
    )


def detect_distro() -> tuple[str, str]:
    """Detecta a distribuicao Linux.

    Returns:
        Tupla (nome_display, id) da distribuicao.
    """
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return "Unknown", "unknown"

    content = os_release.read_text()
    name = "Unknown"
    distro_id = "unknown"

    for line in content.splitlines():
        if line.startswith("PRETTY_NAME="):
            name = line.split("=", 1)[1].strip('"')
        elif line.startswith("ID="):
            distro_id = line.split("=", 1)[1].strip('"')

    return name, distro_id


def detect_gpu() -> GPUInfo | None:
    """Detecta GPU e suas capacidades.

    Returns:
        GPUInfo se GPU encontrada, None caso contrario.
    """
    # Tenta nvidia-smi primeiro
    if shutil.which("nvidia-smi"):
        try:
            result = run_command(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader,nounits",
                ]
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(",")
                name = parts[0].strip()
                vram = int(parts[1].strip()) if len(parts) > 1 else 0

                # Detecta versao CUDA
                cuda_version = None
                cuda_result = run_command(
                    [
                        "nvidia-smi",
                        "--query-gpu=driver_version",
                        "--format=csv,noheader",
                    ],
                    check=False,
                )
                if cuda_result.returncode == 0 and shutil.which("nvcc"):
                    # Tenta nvcc para versao exata do CUDA
                    nvcc_result = run_command(["nvcc", "--version"], check=False)
                    if nvcc_result.returncode == 0:
                        for line in nvcc_result.stdout.splitlines():
                            if "release" in line.lower():
                                # "Cuda compilation tools, release 12.1, V12.1.66"
                                parts = line.split("release")
                                if len(parts) > 1:
                                    cuda_version = parts[1].split(",")[0].strip()
                                    break

                # Detecta compute capability
                compute_cap = None
                for gpu_series, arch in CUDA_ARCHITECTURES.items():
                    if gpu_series in name:
                        compute_cap = arch
                        break

                return GPUInfo(
                    vendor=GPUVendor.NVIDIA,
                    name=name,
                    vram_mb=vram,
                    cuda_version=cuda_version,
                    compute_capability=compute_cap,
                )
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            pass

    # Tenta lspci para outras GPUs
    if shutil.which("lspci"):
        try:
            result = run_command(["lspci"], check=False)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    line_lower = line.lower()
                    if "vga" in line_lower or "3d" in line_lower:
                        if "nvidia" in line_lower:
                            return GPUInfo(
                                vendor=GPUVendor.NVIDIA,
                                name=line.split(":")[-1].strip(),
                                vram_mb=0,
                                cuda_version=None,
                                compute_capability=None,
                            )
                        elif "amd" in line_lower or "radeon" in line_lower:
                            return GPUInfo(
                                vendor=GPUVendor.AMD,
                                name=line.split(":")[-1].strip(),
                                vram_mb=0,
                                cuda_version=None,
                                compute_capability=None,
                            )
                        elif "intel" in line_lower:
                            return GPUInfo(
                                vendor=GPUVendor.INTEL,
                                name=line.split(":")[-1].strip(),
                                vram_mb=0,
                                cuda_version=None,
                                compute_capability=None,
                            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return None


def check_cuda_toolkit() -> bool:
    """Verifica se o CUDA toolkit esta instalado.

    Returns:
        True se nvcc esta disponivel.
    """
    return shutil.which("nvcc") is not None


def gather_system_info() -> SystemInfo:
    """Coleta informacoes completas do sistema.

    Returns:
        SystemInfo com dados do sistema.
    """
    distro_name, distro_id = detect_distro()
    gpu = detect_gpu()
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    cuda_available = check_cuda_toolkit()
    has_uv = shutil.which("uv") is not None

    return SystemInfo(
        distro=distro_name,
        distro_id=distro_id,
        python_version=python_version,
        gpu=gpu,
        cuda_available=cuda_available,
        has_uv=has_uv,
    )


def show_system_info(info: SystemInfo) -> None:
    """Exibe informacoes do sistema em uma tabela.

    Args:
        info: Informacoes do sistema.
    """
    table = Table(title="Informacoes do Sistema", show_header=False)
    table.add_column("Item", style="cyan")
    table.add_column("Valor")

    table.add_row("Distribuicao", info.distro)
    table.add_row("Python", info.python_version)
    table.add_row(
        "uv", "[green]Instalado[/green]" if info.has_uv else "[red]Nao encontrado[/red]"
    )

    if info.gpu:
        gpu_str = f"{info.gpu.name}"
        if info.gpu.vram_mb > 0:
            gpu_str += f" ({info.gpu.vram_mb} MB)"
        table.add_row("GPU", gpu_str)
        table.add_row("Fabricante", info.gpu.vendor.value.upper())

        if info.gpu.vendor == GPUVendor.NVIDIA:
            cuda_str = info.gpu.cuda_version or "[yellow]Nao detectado[/yellow]"
            table.add_row("CUDA Version", cuda_str)
            table.add_row(
                "CUDA Toolkit",
                "[green]Instalado[/green]"
                if info.cuda_available
                else "[yellow]Nao instalado[/yellow]",
            )
            if info.gpu.compute_capability:
                table.add_row("Compute Capability", f"sm_{info.gpu.compute_capability}")
    else:
        table.add_row("GPU", "[yellow]Nao detectada[/yellow]")

    console.print(table)
    console.print()


def install_system_deps(_distro_id: str) -> bool:
    """Instala dependencias do sistema.

    Args:
        _distro_id: ID da distribuicao (reservado para uso futuro).

    Returns:
        True se instalacao bem-sucedida.
    """
    console.print("[bold]Instalando dependencias do sistema...[/bold]")

    # Executa o script de dependencias existente
    script_path = Path(__file__).parent / "install_deps.py"
    if script_path.exists():
        try:
            result = run_command(
                [sys.executable, str(script_path)],
                capture=False,
                check=False,
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    console.print("[yellow]Script install_deps.py nao encontrado[/yellow]")
    return False


def install_cuda_toolkit(distro_id: str) -> bool:
    """Instala CUDA toolkit.

    Args:
        distro_id: ID da distribuicao.

    Returns:
        True se instalacao bem-sucedida.
    """
    console.print("[bold]Instalando CUDA Toolkit...[/bold]")

    install_cmds: dict[str, list[str]] = {
        "ubuntu": ["sudo", "apt", "install", "-y", "nvidia-cuda-toolkit"],
        "debian": ["sudo", "apt", "install", "-y", "nvidia-cuda-toolkit"],
        "arch": ["sudo", "pacman", "-S", "--noconfirm", "cuda"],
        "fedora": ["sudo", "dnf", "install", "-y", "cuda"],
    }

    # Normaliza distro_id
    for key in install_cmds:
        if key in distro_id.lower():
            cmd = install_cmds[key]
            console.print(f"  [dim]Executando: {' '.join(cmd)}[/dim]")
            try:
                result = run_command(cmd, capture=False, check=False)
                if result.returncode == 0:
                    console.print("  [green]OK[/green] CUDA Toolkit instalado")
                    return True
            except subprocess.CalledProcessError:
                pass

    console.print("  [yellow]WARN[/yellow] Instalacao automatica nao disponivel")
    console.print("  Visite: https://developer.nvidia.com/cuda-downloads")
    return False


def compile_llama_cpp_cuda(gpu_info: GPUInfo | None) -> bool:
    """Compila llama-cpp-python com suporte CUDA.

    Args:
        gpu_info: Informacoes da GPU.

    Returns:
        True se compilacao bem-sucedida.
    """
    console.print("[bold]Compilando llama-cpp-python com CUDA...[/bold]")
    console.print("  [dim]Isso pode levar alguns minutos...[/dim]")

    # Define CMAKE_ARGS
    cmake_args = "-DGGML_CUDA=on"
    if gpu_info and gpu_info.compute_capability:
        cmake_args += f" -DCMAKE_CUDA_ARCHITECTURES={gpu_info.compute_capability}"
        console.print(
            f"  [dim]Usando arquitetura CUDA: sm_{gpu_info.compute_capability}[/dim]"
        )

    env = {
        "CMAKE_ARGS": cmake_args,
        "FORCE_CMAKE": "1",
    }

    # Primeiro remove versao existente
    console.print("  Removendo versao anterior...")
    run_command(
        ["uv", "pip", "uninstall", "llama-cpp-python", "-y"],
        check=False,
    )

    # Instala com CUDA
    console.print("  Compilando (pode demorar 5-10 minutos)...")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Compilando llama-cpp-python...", total=None)
            result = run_command(
                [
                    "uv",
                    "pip",
                    "install",
                    "llama-cpp-python",
                    "--no-cache-dir",
                    "--force-reinstall",
                ],
                env=env,
                capture=False,
                check=False,
            )
            progress.update(task, completed=True)

        if result.returncode == 0:
            console.print("  [green]OK[/green] llama-cpp-python compilado com CUDA")
            return True
        else:
            console.print("  [red]ERRO[/red] Falha na compilacao")
            return False
    except Exception as e:
        console.print(f"  [red]ERRO[/red] {e}")
        return False


def compile_llama_cpp_cpu() -> bool:
    """Instala llama-cpp-python versao CPU.

    Returns:
        True se instalacao bem-sucedida.
    """
    console.print("[bold]Instalando llama-cpp-python (CPU)...[/bold]")

    try:
        result = run_command(
            ["uv", "pip", "install", "llama-cpp-python", "--no-cache-dir"],
            capture=False,
            check=False,
        )
        if result.returncode == 0:
            console.print("  [green]OK[/green] llama-cpp-python instalado (CPU)")
            return True
    except Exception as e:
        console.print(f"  [red]ERRO[/red] {e}")

    return False


def install_whisper(use_cuda: bool = False) -> bool:
    """Instala pywhispercpp.

    Args:
        use_cuda: Se True, compila com CUDA.

    Returns:
        True se instalacao bem-sucedida.
    """
    console.print("[bold]Instalando pywhispercpp...[/bold]")

    env = {}
    if use_cuda:
        env["CMAKE_ARGS"] = "-DWHISPER_CUDA=ON"
        console.print("  [dim]Compilando com suporte CUDA...[/dim]")

    try:
        result = run_command(
            ["uv", "pip", "install", "pywhispercpp", "--no-cache-dir"],
            env=env if env else None,
            capture=False,
            check=False,
        )
        if result.returncode == 0:
            console.print("  [green]OK[/green] pywhispercpp instalado")
            return True
    except Exception as e:
        console.print(f"  [red]ERRO[/red] {e}")

    return False


def download_models() -> bool:
    """Baixa os modelos de IA.

    Returns:
        True se download bem-sucedido.
    """
    console.print("[bold]Baixando modelos de IA...[/bold]")
    console.print("  [dim]Tamanho total: ~2.4 GB[/dim]")

    script_path = Path(__file__).parent / "download_models.py"
    if script_path.exists():
        try:
            result = run_command(
                [sys.executable, str(script_path)],
                capture=False,
                check=False,
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    console.print("[red]ERRO[/red] Script download_models.py nao encontrado")
    return False


def create_config() -> bool:
    """Cria arquivo de configuracao.

    Returns:
        True se criacao bem-sucedida.
    """
    config_dir = Path.home() / ".config" / "mascate"
    config_file = config_dir / "config.toml"
    example_file = Path(__file__).parent.parent / "config.toml.example"

    if config_file.exists():
        console.print(f"[yellow]Config ja existe:[/yellow] {config_file}")
        if not Confirm.ask("Sobrescrever?", default=False):
            return True

    config_dir.mkdir(parents=True, exist_ok=True)

    if example_file.exists():
        shutil.copy(example_file, config_file)
        console.print(f"[green]OK[/green] Config criado: {config_file}")
        return True

    console.print("[red]ERRO[/red] config.toml.example nao encontrado")
    return False


def verify_installation() -> bool:
    """Verifica se a instalacao esta completa.

    Returns:
        True se tudo OK.
    """
    console.print("[bold]Verificando instalacao...[/bold]")

    checks: list[tuple[str, str, bool]] = []

    # Verifica llama-cpp-python
    try:
        result = run_command(
            [sys.executable, "-c", "from llama_cpp import Llama; print('ok')"],
            check=False,
        )
        checks.append(("llama-cpp-python", "LLM inference", result.returncode == 0))
    except Exception:
        checks.append(("llama-cpp-python", "LLM inference", False))

    # Verifica pywhispercpp
    try:
        result = run_command(
            [sys.executable, "-c", "from pywhispercpp.model import Model; print('ok')"],
            check=False,
        )
        checks.append(("pywhispercpp", "Speech-to-Text", result.returncode == 0))
    except Exception:
        checks.append(("pywhispercpp", "Speech-to-Text", False))

    # Verifica modelos
    models_dir = Path.home() / ".local" / "share" / "mascate" / "models"
    models = [
        ("granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf", "LLM Granite"),
        ("ggml-large-v3-q5_0.bin", "Whisper STT"),
        ("silero_vad.onnx", "Silero VAD"),
        ("pt_BR-faber-medium.onnx", "Piper TTS"),
    ]

    for model_file, desc in models:
        exists = (models_dir / model_file).exists()
        checks.append((model_file, desc, exists))

    # Verifica config
    config_file = Path.home() / ".config" / "mascate" / "config.toml"
    checks.append(("config.toml", "Configuracao", config_file.exists()))

    # Mostra tabela
    table = Table(title="Status da Instalacao", show_header=True)
    table.add_column("Componente", style="cyan")
    table.add_column("Descricao")
    table.add_column("Status")

    all_ok = True
    for name, desc, ok in checks:
        status = "[green]OK[/green]" if ok else "[red]FALTANDO[/red]"
        table.add_row(name, desc, status)
        if not ok:
            all_ok = False

    console.print(table)
    return all_ok


def run_full_setup() -> int:
    """Executa o setup completo.

    Returns:
        Codigo de saida (0 = sucesso).
    """
    console.print(
        Panel.fit(
            "[bold cyan]Mascate[/bold cyan] - Setup Automatizado",
            subtitle="[dim]Assistente de Voz Edge AI para Linux[/dim]",
        )
    )
    console.print()

    # 1. Coleta informacoes do sistema
    console.print("[bold cyan]1/7[/bold cyan] Detectando sistema...")
    info = gather_system_info()
    show_system_info(info)

    if not info.has_uv:
        console.print("[red]ERRO[/red] 'uv' nao encontrado. Instale com:")
        console.print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        return 1

    # 2. Instala dependencias do sistema
    console.print("[bold cyan]2/7[/bold cyan] Dependencias do sistema")
    if not install_system_deps(info.distro_id):
        console.print("[yellow]WARN[/yellow] Algumas dependencias podem estar faltando")

    # 3. Setup CUDA (se NVIDIA)
    use_cuda = False
    if info.gpu and info.gpu.vendor == GPUVendor.NVIDIA:
        console.print()
        console.print("[bold cyan]3/7[/bold cyan] Configuracao CUDA")

        if not info.cuda_available and Confirm.ask(
            "CUDA Toolkit nao encontrado. Instalar?", default=True
        ):
            install_cuda_toolkit(info.distro_id)
            # Re-verifica
            info.cuda_available = check_cuda_toolkit()

        if info.cuda_available:
            use_cuda = Confirm.ask(
                "Compilar com suporte CUDA (recomendado)?", default=True
            )
    else:
        console.print()
        console.print(
            "[bold cyan]3/7[/bold cyan] [dim]CUDA nao disponivel (GPU nao-NVIDIA)[/dim]"
        )

    # 4. Compila llama-cpp-python
    console.print()
    console.print("[bold cyan]4/7[/bold cyan] llama-cpp-python")
    if use_cuda:
        if not compile_llama_cpp_cuda(info.gpu):
            console.print("[yellow]Tentando versao CPU como fallback...[/yellow]")
            compile_llama_cpp_cpu()
    else:
        compile_llama_cpp_cpu()

    # 5. Instala whisper
    console.print()
    console.print("[bold cyan]5/7[/bold cyan] pywhispercpp")
    install_whisper(use_cuda=use_cuda)

    # 6. Baixa modelos
    console.print()
    console.print("[bold cyan]6/7[/bold cyan] Download de modelos")
    if Confirm.ask("Baixar modelos de IA (~2.4 GB)?", default=True):
        download_models()

    # 7. Cria config
    console.print()
    console.print("[bold cyan]7/7[/bold cyan] Configuracao")
    create_config()

    # Verificacao final
    console.print()
    all_ok = verify_installation()

    if all_ok:
        console.print()
        console.print(
            Panel.fit(
                "[bold green]Setup concluido com sucesso![/bold green]\n\n"
                "Execute o Mascate com:\n"
                "  [cyan]uv run mascate run --hotkey-only[/cyan]",
                border_style="green",
            )
        )
        return 0
    else:
        console.print()
        console.print(
            Panel.fit(
                "[bold yellow]Setup incompleto[/bold yellow]\n\n"
                "Alguns componentes estao faltando.\n"
                "Execute novamente ou instale manualmente.",
                border_style="yellow",
            )
        )
        return 1


def run_check_only() -> int:
    """Apenas verifica o status da instalacao.

    Returns:
        Codigo de saida.
    """
    console.print(
        Panel.fit(
            "[bold cyan]Mascate[/bold cyan] - Verificacao de Instalacao",
        )
    )
    console.print()

    info = gather_system_info()
    show_system_info(info)

    if verify_installation():
        return 0
    return 1


def run_cuda_only() -> int:
    """Apenas configura CUDA.

    Returns:
        Codigo de saida.
    """
    console.print(
        Panel.fit(
            "[bold cyan]Mascate[/bold cyan] - Setup CUDA",
        )
    )
    console.print()

    info = gather_system_info()
    show_system_info(info)

    if not info.gpu or info.gpu.vendor != GPUVendor.NVIDIA:
        console.print("[red]ERRO[/red] GPU NVIDIA nao detectada")
        return 1

    if not info.cuda_available and Confirm.ask("Instalar CUDA Toolkit?", default=True):
        install_cuda_toolkit(info.distro_id)

    if compile_llama_cpp_cuda(info.gpu):
        install_whisper(use_cuda=True)
        return 0
    return 1


def run_models_only() -> int:
    """Apenas baixa modelos.

    Returns:
        Codigo de saida.
    """
    console.print(
        Panel.fit(
            "[bold cyan]Mascate[/bold cyan] - Download de Modelos",
        )
    )
    console.print()

    if download_models():
        return 0
    return 1


def main() -> int:
    """Funcao principal.

    Returns:
        Codigo de saida.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup automatizado do Mascate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  uv run python scripts/setup.py          # Setup completo
  uv run python scripts/setup.py --check  # Verificar status
  uv run python scripts/setup.py --cuda   # Apenas CUDA
  uv run python scripts/setup.py --models # Apenas modelos
        """,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Apenas verificar status da instalacao",
    )
    parser.add_argument(
        "--cuda",
        action="store_true",
        help="Apenas configurar CUDA e recompilar libs",
    )
    parser.add_argument(
        "--models",
        action="store_true",
        help="Apenas baixar modelos",
    )

    args = parser.parse_args()

    try:
        if args.check:
            return run_check_only()
        elif args.cuda:
            return run_cuda_only()
        elif args.models:
            return run_models_only()
        else:
            return run_full_setup()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelado pelo usuario[/yellow]")
        return 130


if __name__ == "__main__":
    sys.exit(main())
