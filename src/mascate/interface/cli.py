"""Interface de Linha de Comando (CLI) do Mascate.

Ponto de entrada para execução e gerenciamento do assistente.
"""

from __future__ import annotations

import logging
import sys

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from mascate.audio.capture import AudioCapture
from mascate.audio.hotkey import HotkeyListener
from mascate.audio.pipeline import AudioPipeline
from mascate.audio.stt.whisper import WhisperSTT
from mascate.audio.tts.piper import PiperTTS
from mascate.audio.vad.processor import VADProcessor
from mascate.audio.wake.detector import WakeWordDetector
from mascate.core.config import Config
from mascate.core.orchestrator import Orchestrator
from mascate.executor.executor import Executor
from mascate.intelligence.brain import Brain
from mascate.intelligence.llm.granite import GraniteLLM
from mascate.intelligence.rag.knowledge import KnowledgeBase
from mascate.intelligence.rag.retriever import RAGRetriever
from mascate.interface.hud import HUD

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
)

logger = logging.getLogger("mascate")
console = Console()


@click.group()
def main() -> None:
    """Mascate - Assistente de Voz Edge AI."""
    pass


@main.command()
def version() -> None:
    """Exibe a versão do Mascate."""
    console.print(
        Panel.fit(
            "[bold cyan]Mascate[/bold cyan] v0.1.0",
            subtitle="[dim]Assistente de Voz Edge AI[/dim]",
        )
    )


@main.command()
def check() -> None:
    """Verifica dependências e ambiente."""
    console.print(
        Panel.fit(
            "[bold cyan]Mascate[/bold cyan] - Verificacao de Sistema",
            subtitle="[dim]Assistente de Voz Edge AI[/dim]",
        )
    )
    console.print()

    config = Config.load()

    # Tabela de configuracao
    config_table = Table(title="Configuracao", show_header=True, header_style="bold")
    config_table.add_column("Item", style="cyan")
    config_table.add_column("Valor")

    config_table.add_row("Config Dir", str(config.data_dir.parent / "mascate"))
    config_table.add_row("Models Dir", str(config.models_dir))
    config_table.add_row(
        "Hotkey", config.audio.hotkey if config.audio.hotkey_enabled else "Desabilitado"
    )
    config_table.add_row(
        "Hotkey Only", "Sim" if config.audio.hotkey_only else "Nao (Wake Word ativo)"
    )

    console.print(config_table)
    console.print()

    # Tabela de modelos
    models_table = Table(title="Modelos", show_header=True, header_style="bold")
    models_table.add_column("Status", justify="center")
    models_table.add_column("Modelo", style="cyan")
    models_table.add_column("Arquivo")

    models = [
        (
            "Granite LLM",
            config.llm.model_path
            or config.models_dir / "granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf",
        ),
        ("Whisper STT", config.models_dir / "ggml-large-v3-q5_0.bin"),
        ("Silero VAD", config.models_dir / "silero_vad.onnx"),
        ("Piper TTS", config.models_dir / "pt_BR-faber-medium.onnx"),
        ("Piper TTS Config", config.models_dir / "pt_BR-faber-medium.onnx.json"),
    ]

    all_ok = True
    for name, path in models:
        exists = path.exists()
        if not exists:
            all_ok = False
        status = "[green]OK[/green]" if exists else "[red]FALTA[/red]"
        models_table.add_row(status, name, str(path.name))

    console.print(models_table)
    console.print()

    # Verificar dependencias Python opcionais
    deps_table = Table(
        title="Dependencias Opcionais", show_header=True, header_style="bold"
    )
    deps_table.add_column("Status", justify="center")
    deps_table.add_column("Pacote", style="cyan")
    deps_table.add_column("Uso")

    # llama-cpp-python
    try:
        from llama_cpp import Llama  # noqa: F401

        deps_table.add_row("[green]OK[/green]", "llama-cpp-python", "LLM (Granite)")
    except ImportError:
        deps_table.add_row("[red]FALTA[/red]", "llama-cpp-python", "LLM (Granite)")
        all_ok = False

    # pywhispercpp
    try:
        import pywhispercpp  # noqa: F401

        deps_table.add_row("[green]OK[/green]", "pywhispercpp", "STT (Whisper)")
    except ImportError:
        deps_table.add_row("[yellow]FALTA[/yellow]", "pywhispercpp", "STT (Whisper)")

    # pynput
    try:
        from pynput import keyboard  # noqa: F401

        deps_table.add_row("[green]OK[/green]", "pynput", "Hotkey")
    except ImportError:
        deps_table.add_row("[red]FALTA[/red]", "pynput", "Hotkey")
        all_ok = False

    console.print(deps_table)
    console.print()

    # Resultado final
    if all_ok:
        console.print(
            Panel.fit(
                "[bold green]Sistema pronto para uso![/bold green]\n\n"
                "Execute: [cyan]uv run mascate run[/cyan]",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                "[bold yellow]Sistema incompleto[/bold yellow]\n\n"
                "Alguns componentes estao faltando.\n"
                "Execute: [cyan]uv run python scripts/download_models.py[/cyan]",
                border_style="yellow",
            )
        )


@main.command()
@click.option("--debug", is_flag=True, help="Habilita logs de debug.")
def run(debug: bool) -> None:
    """Inicia o assistente Mascate."""
    try:
        config = Config.load()
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            config.debug = True

        logger.info("Inicializando componentes...")

        # 1. Áudio - Captura
        logger.info("  Inicializando captura de audio...")
        capture = AudioCapture(
            sample_rate=config.audio.sample_rate,
            channels=config.audio.channels,
            chunk_size=config.audio.chunk_size,
        )

        # 1.2 Hotkey Listener (se habilitado)
        hotkey_listener = None
        if config.audio.hotkey_enabled:
            logger.info("  Inicializando hotkey listener (%s)...", config.audio.hotkey)
            hotkey_listener = HotkeyListener(hotkey=config.audio.hotkey)

        # 1.3 Wake Word Detector (se nao estiver em modo hotkey_only)
        wake_detector = None
        if not config.audio.hotkey_only:
            logger.info("  Inicializando wake word detector...")
            try:
                wake_detector = WakeWordDetector(
                    wakeword=config.audio.wake_word,
                    threshold=config.audio.vad_threshold,
                )
            except Exception as e:
                logger.warning("Wake word nao disponivel: %s", e)
                if not hotkey_listener:
                    raise RuntimeError(
                        "Nem hotkey nem wake word disponiveis. "
                        "Habilite hotkey_enabled ou instale openwakeword."
                    ) from e

        # 1.4 VAD
        logger.info("  Inicializando VAD...")
        vad_model = config.models_dir / "silero_vad.onnx"
        vad_processor = VADProcessor(
            model_path=vad_model,
            threshold=config.audio.vad_threshold,
        )

        # 1.5 STT
        logger.info("  Inicializando STT...")
        stt_model = config.models_dir / "ggml-large-v3-q5_0.bin"
        stt = WhisperSTT(model_path=stt_model)

        # 1.6 Audio Pipeline (com hotkey_listener)
        logger.info("  Montando pipeline de audio...")
        audio_pipeline = AudioPipeline(
            capture=capture,
            wake_detector=wake_detector,
            vad_processor=vad_processor,
            stt=stt,
            hotkey_listener=hotkey_listener,
        )

        # 2. Inteligência
        logger.info("  Inicializando RAG...")
        kb = KnowledgeBase(config)
        retriever = RAGRetriever(kb)

        logger.info("  Inicializando LLM...")
        llm_model = (
            config.llm.model_path
            or config.models_dir / "granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf"
        )
        llm = GraniteLLM(
            model_path=llm_model,
            n_gpu_layers=config.llm.n_gpu_layers,
            n_ctx=config.llm.n_ctx,
        )

        brain = Brain(llm, retriever)

        # 3. Execução
        logger.info("  Inicializando executor...")
        executor = Executor(config)

        # 4. Interface - HUD
        logger.info("  Inicializando HUD...")
        hud = HUD()

        # 4.2 TTS (opcional)
        tts = None
        tts_model = config.models_dir / "pt_BR-faber-medium.onnx"
        if tts_model.exists():
            logger.info("  Inicializando TTS...")
            try:
                tts = PiperTTS(model_path=tts_model)
            except Exception as e:
                logger.warning("TTS nao disponivel: %s", e)

        # 5. Orquestração
        logger.info("  Iniciando orquestrador...")
        orchestrator = Orchestrator(audio_pipeline, brain, executor, hud, tts=tts)

        # Mostra informacao de ativacao
        if config.audio.hotkey_enabled:
            logger.info("Pressione [%s] para ativar", config.audio.hotkey)
        if wake_detector:
            logger.info("Ou diga '%s' para ativar", config.audio.wake_word)

        orchestrator.start()

    except KeyboardInterrupt:
        logger.info("Encerrando...")
    except Exception as e:
        logger.critical("Erro fatal ao iniciar Mascate: %s", e)
        if debug:
            logger.exception("Traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
