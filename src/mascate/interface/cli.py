"""Interface de Linha de Comando (CLI) do Mascate.

Ponto de entrada para execução e gerenciamento do assistente.
"""

from __future__ import annotations

import logging
import sys

import click
from rich.logging import RichHandler

from mascate.audio.capture import AudioCapture
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


@click.group()
def main() -> None:
    """Mascate - Assistente de Voz Edge AI."""
    pass


@main.command()
def version() -> None:
    """Exibe a versão do Mascate."""
    click.echo("Mascate v0.1.0")


@main.command()
def check() -> None:
    """Verifica dependências e ambiente."""
    config = Config.load()
    click.echo(f"Config carregada de: {config.data_dir}")
    click.echo("Verificando modelos...")

    models = [
        (
            "Granite LLM",
            config.llm.model_path
            or config.models_dir / "granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf",
        ),
        ("Whisper STT", config.models_dir / "ggml-large-v3-q5_0.bin"),
        ("Silero VAD", config.models_dir / "silero_vad.onnx"),
        ("Piper TTS", config.models_dir / "pt_BR-faber-medium.onnx"),
    ]

    for name, path in models:
        status = "[OK]" if path.exists() else "[MISSING]"
        click.echo(f"{status} {name}: {path}")


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
        capture = AudioCapture(
            sample_rate=config.audio.sample_rate,
            channels=config.audio.channels,
            chunk_size=config.audio.chunk_size,
        )

        # 1.2 Wake Word Detector
        wake_detector = WakeWordDetector(
            wakeword=config.audio.wake_word,
            threshold=config.audio.vad_threshold,
        )

        # 1.3 VAD
        vad_model = config.models_dir / "silero_vad.onnx"
        vad_processor = VADProcessor(
            model_path=vad_model,
            threshold=0.5,
        )

        # 1.4 STT
        stt_model = config.models_dir / "ggml-large-v3-q5_0.bin"
        stt = WhisperSTT(model_path=stt_model)

        # 1.5 Audio Pipeline
        audio_pipeline = AudioPipeline(capture, wake_detector, vad_processor, stt)

        # 2. Inteligência - Knowledge Base
        kb = KnowledgeBase(config)

        # 2.2 RAG Retriever
        retriever = RAGRetriever(kb)

        # 2.3 LLM
        llm_model = (
            config.llm.model_path
            or config.models_dir / "granite-4.0-hybridmamba-1b-instruct-Q8_0.gguf"
        )
        llm = GraniteLLM(
            model_path=llm_model,
            n_gpu_layers=config.llm.n_gpu_layers,
            n_ctx=config.llm.n_ctx,
        )

        # 2.4 Brain
        brain = Brain(llm, retriever)

        # 3. Execução
        executor = Executor(config)

        # 4. Interface - HUD
        hud = HUD()

        # 4.2 TTS (opcional)
        tts_model = config.models_dir / "pt_BR-faber-medium.onnx"
        tts = None
        if tts_model.exists():
            try:
                tts = PiperTTS(model_path=tts_model)
            except Exception as e:
                logger.warning("TTS nao disponivel: %s", e)

        # 5. Orquestração
        orchestrator = Orchestrator(audio_pipeline, brain, executor, hud, tts=tts)

        orchestrator.start()

    except Exception as e:
        logger.critical("Erro fatal ao iniciar Mascate: %s", e)
        if debug:
            logger.exception("Traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
