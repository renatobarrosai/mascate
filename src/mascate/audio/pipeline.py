"""Pipeline de Áudio do Mascate.

Orquestra a captura, detecção de wake word, VAD e STT em um fluxo único.
Suporta ativação via wake word ou hotkey de teclado.
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable

import numpy as np

from mascate.audio.capture import AudioCapture
from mascate.audio.hotkey import HotkeyListener
from mascate.audio.stt.whisper import WhisperSTT
from mascate.audio.vad.processor import VADProcessor, VADState
from mascate.audio.wake.detector import WakeWordDetector

logger = logging.getLogger(__name__)

# Silero VAD v5 requer chunks de exatamente 512 samples a 16kHz
VAD_CHUNK_SIZE = 512


class AudioPipeline:
    """Orquestrador do pipeline de áudio."""

    def __init__(
        self,
        capture: AudioCapture,
        wake_detector: WakeWordDetector | None,
        vad_processor: VADProcessor,
        stt: WhisperSTT,
        hotkey_listener: HotkeyListener | None = None,
    ) -> None:
        """Inicializa o pipeline.

        Args:
            capture: Instância de AudioCapture.
            wake_detector: Instância de WakeWordDetector (pode ser None se usar hotkey).
            vad_processor: Instância de VADProcessor.
            stt: Instância de WhisperSTT.
            hotkey_listener: Instância de HotkeyListener para ativação via teclado.
        """
        self.capture = capture
        self.wake_detector = wake_detector
        self.vad_processor = vad_processor
        self.stt = stt
        self.hotkey_listener = hotkey_listener

        self._on_transcription_cb: Callable[[str], None] | None = None
        self._on_activation_cb: Callable[[], None] | None = None

        self._running = False
        self._thread: threading.Thread | None = None
        self._is_listening = False
        self._audio_buffer: list[np.ndarray] = []

        # Buffer para acumular samples até ter 512 para o VAD
        self._vad_accumulator: np.ndarray = np.array([], dtype=np.float32)

        # Configura hotkey listener se fornecido
        if self.hotkey_listener:
            self.hotkey_listener.on_activate(self._handle_activation)

    def on_activation(self, callback: Callable[[], None]) -> None:
        """Define callback para detecção de wake word ou hotkey."""
        self._on_activation_cb = callback

    def on_transcription(self, callback: Callable[[str], None]) -> None:
        """Define callback para resultado do STT."""
        self._on_transcription_cb = callback

    def start(self) -> None:
        """Inicia o pipeline em uma thread separada."""
        if self._running:
            return

        self._running = True
        self.capture.start()

        # Inicia hotkey listener se disponível
        if self.hotkey_listener:
            self.hotkey_listener.start()

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Pipeline de áudio iniciado")

    def stop(self) -> None:
        """Para o pipeline."""
        self._running = False

        # Para hotkey listener
        if self.hotkey_listener:
            self.hotkey_listener.stop()

        if self._thread:
            self._thread.join(timeout=2.0)
        self.capture.stop()
        logger.info("Pipeline de áudio parado")

    def trigger_activation(self) -> None:
        """Dispara ativação manualmente (útil para CLI ou hotkey externo)."""
        if not self._is_listening:
            self._handle_activation()

    def _run_loop(self) -> None:
        """Loop principal de processamento de áudio."""
        while self._running:
            try:
                # Obtém chunk da captura (bloqueia por 100ms se vazio)
                try:
                    chunk = self.capture.get_chunk(timeout=0.1)
                except Exception:
                    continue

                # Flatten chunk se necessário (pode vir como [N, 1])
                if chunk.ndim > 1:
                    chunk = chunk.flatten()

                if not self._is_listening:
                    # Modo IDLE: procurando Wake Word (se detector disponível)
                    if self.wake_detector:
                        score = self.wake_detector.process(chunk)
                        if score >= self.wake_detector.threshold:
                            self._handle_activation()
                    # Se não tem wake_detector, ativação é apenas via hotkey
                else:
                    # Modo LISTENING: processando VAD e acumulando áudio
                    self._audio_buffer.append(chunk)

                    # Processa VAD com chunks de 512 samples
                    state = self._process_vad_chunked(chunk)

                    if state == VADState.END_OF_SPEECH:
                        self._handle_end_of_speech()

            except Exception as e:
                logger.error("Erro no loop do pipeline: %s", e)
                time.sleep(0.1)

    def _process_vad_chunked(self, audio_chunk: np.ndarray) -> VADState:
        """Processa áudio pelo VAD em chunks de 512 samples.

        Args:
            audio_chunk: Chunk de áudio do capturador (qualquer tamanho).

        Returns:
            O estado atual do VAD após processar todos os sub-chunks.
        """
        # Acumula samples
        self._vad_accumulator = np.concatenate([self._vad_accumulator, audio_chunk])

        state = VADState.IDLE

        # Processa enquanto houver chunks completos de 512 samples
        while len(self._vad_accumulator) >= VAD_CHUNK_SIZE:
            vad_chunk = self._vad_accumulator[:VAD_CHUNK_SIZE]
            self._vad_accumulator = self._vad_accumulator[VAD_CHUNK_SIZE:]

            state = self.vad_processor.process(vad_chunk)

            # Se detectou fim de fala, retorna imediatamente
            if state == VADState.END_OF_SPEECH:
                return state

        return state

    def _handle_activation(self) -> None:
        """Trata a ativação pela Wake Word ou Hotkey."""
        source = "Hotkey" if self.hotkey_listener else "Wake Word"
        logger.info("Sistema ativado via %s", source)
        self._is_listening = True
        self._audio_buffer = []
        self._vad_accumulator = np.array([], dtype=np.float32)

        # Inclui o buffer circular da captura para não perder o início da fala
        history = list(self.capture.circular_buffer)
        for hist_chunk in history:
            if hist_chunk.ndim > 1:
                hist_chunk = hist_chunk.flatten()
            self._audio_buffer.append(hist_chunk)

        if self._on_activation_cb:
            self._on_activation_cb()

    def _handle_end_of_speech(self) -> None:
        """Trata o fim da fala e inicia transcrição."""
        logger.info("Fim de fala detectado, iniciando transcrição...")
        self._is_listening = False

        # Concatena áudio acumulado
        if not self._audio_buffer:
            self.vad_processor.confirm_end()
            self._vad_accumulator = np.array([], dtype=np.float32)
            return

        full_audio = np.concatenate(self._audio_buffer)

        # Transcreve (STT)
        text = self.stt.transcribe(full_audio)

        if text and self._on_transcription_cb:
            self._on_transcription_cb(text)

        # Reseta VAD e buffers para próxima interação
        self.vad_processor.confirm_end()
        self._audio_buffer = []
        self._vad_accumulator = np.array([], dtype=np.float32)
