#!/usr/bin/env python3
"""Download de modelos para o Mascate.

Baixa modelos do Hugging Face Hub para o diretorio local.
Verifica integridade via SHA256.
Mostra progresso com Rich.
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table

# Diretorio padrao para modelos
DEFAULT_MODELS_DIR = Path.home() / ".local" / "share" / "mascate" / "models"

console = Console()


@dataclass
class ModelSpec:
    """Especificacao de um modelo."""

    name: str
    repo_id: str
    filename: str
    description: str
    size_gb: float
    sha256: str | None = None  # Hash para verificacao


# Modelos necessarios para o Mascate
MODELS: list[ModelSpec] = [
    ModelSpec(
        name="granite-1b",
        repo_id="ibm-granite/granite-4.0-hybridmamba-1b-instruct-GGUF",
        filename="granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf",
        description="IBM Granite 4.0 Hybrid 1B - LLM principal (Q8_0)",
        size_gb=1.2,
    ),
    ModelSpec(
        name="whisper-large-v3",
        repo_id="ggerganov/whisper.cpp",
        filename="ggml-large-v3-q5_0.bin",
        description="Whisper Large v3 - STT (Q5_0)",
        size_gb=1.1,
    ),
    ModelSpec(
        name="silero-vad",
        repo_id="snakers4/silero-vad",
        filename="silero_vad.onnx",
        description="Silero VAD v5 - Deteccao de voz (ONNX)",
        size_gb=0.002,  # ~2MB
    ),
    ModelSpec(
        name="piper-tts-pt-br",
        repo_id="rhasspy/piper-voices",
        filename="pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx",
        description="Piper TTS pt-BR Faber Medium - Sintese de voz",
        size_gb=0.065,  # ~65MB
    ),
    ModelSpec(
        name="piper-tts-pt-br-config",
        repo_id="rhasspy/piper-voices",
        filename="pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json",
        description="Piper TTS pt-BR Faber Medium - Config JSON",
        size_gb=0.001,  # ~1KB
    ),
    # BGE-M3 sera baixado via sentence-transformers automaticamente
]


def get_models_dir() -> Path:
    """Retorna o diretorio de modelos.

    Returns:
        Path para o diretorio de modelos.
    """
    models_dir = DEFAULT_MODELS_DIR
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def verify_sha256(file_path: Path, expected_hash: str) -> bool:
    """Verifica o hash SHA256 de um arquivo.

    Args:
        file_path: Caminho para o arquivo.
        expected_hash: Hash esperado.

    Returns:
        True se o hash corresponde, False caso contrario.
    """
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest() == expected_hash


def verify_sha256_with_progress(
    file_path: Path,
    expected_hash: str,
    progress: Progress,
    task_id: TaskID,
) -> bool:
    """Verifica o hash SHA256 de um arquivo com barra de progresso.

    Args:
        file_path: Caminho para o arquivo.
        expected_hash: Hash esperado.
        progress: Instancia de Rich Progress.
        task_id: ID da task de progresso.

    Returns:
        True se o hash corresponde, False caso contrario.
    """
    file_size = file_path.stat().st_size
    progress.update(task_id, total=file_size)

    sha256_hash = hashlib.sha256()
    bytes_read = 0

    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256_hash.update(chunk)
            bytes_read += len(chunk)
            progress.update(task_id, completed=bytes_read)

    return sha256_hash.hexdigest() == expected_hash


class ProgressCallback:
    """Callback para progresso de download do huggingface_hub."""

    def __init__(self, progress: Progress, task_id: TaskID) -> None:
        """Inicializa o callback.

        Args:
            progress: Instancia de Rich Progress.
            task_id: ID da task de progresso.
        """
        self.progress = progress
        self.task_id = task_id
        self._last_bytes = 0

    def __call__(self, bytes_downloaded: int, total_bytes: int) -> None:
        """Atualiza a barra de progresso.

        Args:
            bytes_downloaded: Bytes baixados ate agora.
            total_bytes: Total de bytes.
        """
        if total_bytes > 0:
            self.progress.update(self.task_id, total=total_bytes)
        self.progress.update(self.task_id, completed=bytes_downloaded)


def get_final_filename(model: ModelSpec) -> str:
    """Extrai o nome final do arquivo (sem subdiretórios).

    Args:
        model: Especificacao do modelo.

    Returns:
        Nome do arquivo sem path.
    """
    # Se o filename tem subdiretorios (ex: pt/pt_BR/faber/medium/file.onnx)
    # retorna apenas o nome do arquivo
    return Path(model.filename).name


def download_model(
    model: ModelSpec,
    models_dir: Path,
    progress: Progress,
) -> bool:
    """Baixa um modelo do Hugging Face Hub.

    Args:
        model: Especificacao do modelo.
        models_dir: Diretorio destino.
        progress: Instancia de Rich Progress.

    Returns:
        True se download bem-sucedido, False caso contrario.
    """
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        console.print("[red]Erro: huggingface_hub nao instalado.[/red]")
        console.print("Execute: [cyan]uv pip install huggingface-hub[/cyan]")
        return False

    # Nome final do arquivo (sem subdiretorios)
    final_filename = get_final_filename(model)
    output_path = models_dir / final_filename

    # Verifica se ja existe
    if output_path.exists():
        console.print(f"  [green]OK[/green] {model.name} ja existe")

        if model.sha256:
            verify_task = progress.add_task(
                f"[cyan]Verificando hash {model.name}...",
                total=None,
            )
            if verify_sha256_with_progress(
                output_path, model.sha256, progress, verify_task
            ):
                progress.remove_task(verify_task)
                console.print("  [green]OK[/green] Hash verificado")
                return True
            else:
                progress.remove_task(verify_task)
                console.print("  [yellow]WARN[/yellow] Hash invalido, re-baixando...")
                output_path.unlink()
        else:
            return True

    # Cria task de download
    download_task = progress.add_task(
        f"[cyan]Baixando {model.name}",
        total=int(model.size_gb * 1024 * 1024 * 1024),  # Estimativa inicial
    )

    try:
        # huggingface_hub usa tqdm internamente, vamos usar nosso callback
        downloaded_path = hf_hub_download(
            repo_id=model.repo_id,
            filename=model.filename,
            local_dir=models_dir,
            local_dir_use_symlinks=False,
        )

        # Marca como completo
        progress.update(download_task, completed=progress.tasks[download_task].total)
        progress.remove_task(download_task)

        downloaded_path = Path(downloaded_path)

        # Se o arquivo foi baixado em subdiretorio, move para a raiz
        if (
            downloaded_path.name != final_filename
            or downloaded_path.parent != models_dir
        ):
            final_path = models_dir / final_filename
            # Move o arquivo
            import shutil

            shutil.move(str(downloaded_path), str(final_path))
            console.print(f"  [green]OK[/green] Movido para {final_path}")
            # Limpa subdiretorios vazios
            try:
                for parent in downloaded_path.parents:
                    if parent == models_dir:
                        break
                    if parent.exists() and not any(parent.iterdir()):
                        parent.rmdir()
            except Exception:
                pass  # Ignora erros ao limpar diretorios
        else:
            console.print(f"  [green]OK[/green] Salvo em {downloaded_path}")

        # Verifica hash se disponivel
        if model.sha256:
            verify_task = progress.add_task(
                f"[cyan]Verificando hash {model.name}...",
                total=None,
            )
            if verify_sha256_with_progress(
                output_path, model.sha256, progress, verify_task
            ):
                progress.remove_task(verify_task)
                console.print("  [green]OK[/green] Hash verificado")
            else:
                progress.remove_task(verify_task)
                console.print("  [red]ERROR[/red] Hash invalido!")
                return False

        return True

    except Exception as e:
        progress.remove_task(download_task)
        console.print(f"  [red]ERROR[/red] Falha ao baixar: {e}")
        return False


def show_models_table() -> None:
    """Mostra tabela com modelos a serem baixados."""
    table = Table(title="Modelos a Baixar", show_header=True, header_style="bold cyan")
    table.add_column("Nome", style="cyan")
    table.add_column("Descricao")
    table.add_column("Tamanho", justify="right", style="green")
    table.add_column("Repo", style="dim")

    for model in MODELS:
        table.add_row(
            model.name,
            model.description,
            f"{model.size_gb:.1f} GB",
            model.repo_id,
        )

    console.print(table)
    console.print()


def main() -> int:
    """Funcao principal.

    Returns:
        Codigo de saida (0 = sucesso).
    """
    console.print(
        Panel.fit(
            "[bold cyan]Mascate[/bold cyan] - Download de Modelos",
            subtitle="[dim]Assistente de Voz Edge AI[/dim]",
        )
    )
    console.print()

    models_dir = get_models_dir()
    console.print(f"[bold]Diretorio de modelos:[/bold] {models_dir}")
    console.print()

    show_models_table()

    total = len(MODELS)
    success = 0
    total_size = sum(m.size_gb for m in MODELS)

    console.print(f"[bold]Total:[/bold] {total} modelos (~{total_size:.1f} GB)")
    console.print()

    # Progress bar principal
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True,
    ) as progress:
        for i, model in enumerate(MODELS, 1):
            console.print(f"[bold][{i}/{total}][/bold] {model.name}")
            console.print(f"    [dim]{model.description}[/dim]")

            if download_model(model, models_dir, progress):
                success += 1
            console.print()

    # Resultado final
    console.print()

    if success == total:
        console.print(
            Panel.fit(
                f"[bold green]Sucesso![/bold green] {success}/{total} modelos baixados",
                border_style="green",
            )
        )
        return 0
    else:
        console.print(
            Panel.fit(
                f"[bold yellow]Aviso:[/bold yellow] {success}/{total} modelos baixados\n"
                f"[red]{total - success} modelo(s) falharam[/red]",
                border_style="yellow",
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
