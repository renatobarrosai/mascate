"""Detecção de Atividade de Voz (VAD) para o Mascate.

Usa o Silero VAD para identificar quando há fala no áudio e gerenciar
os estados de fala/silêncio.
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

import numpy as np

try:
    import onnxruntime as ort
except ImportError:
    ort = None

from mascate.core.exceptions import MascateError

logger = logging.getLogger(__name__)


class VADState(Enum):
    """Estados do processador VAD."""

    IDLE = "idle"
    SPEAKING = "speaking"
    END_OF_SPEECH = "end_of_speech"


class VADError(MascateError):
    """Erro relacionado ao processamento de VAD."""


class VADProcessor:
    """Processa áudio para detectar presença de fala."""

    def __init__(
        self,
        model_path: str | Path,
        sample_rate: int = 16000,
        threshold: float = 0.5,
        min_silence_duration_ms: int = 300,
    ) -> None:
        """Inicializa o processador VAD.

        Args:
            model_path: Caminho para o arquivo .onnx do Silero VAD.
            sample_rate: Taxa de amostragem (8k ou 16k suportados).
            threshold: Probabilidade mínima para considerar como fala.
            min_silence_duration_ms: Milissegundos de silêncio para considerar fim de fala.

        Raises:
            VADError: Se falhar ao carregar o modelo ONNX.
        """
        if ort is None:
            raise VADError(
                "onnxruntime não encontrado. Instale com 'uv pip install onnxruntime'."
            )

        self.sample_rate = sample_rate
        self.threshold = threshold
        self.min_silence_chunks = int(
            (min_silence_duration_ms * sample_rate) / (1000 * 512)
        )  # Silero v5 usa blocos de 512 samples

        try:
            self.session = ort.InferenceSession(str(model_path))
            logger.info("Modelo VAD carregado: %s", model_path)
        except Exception as e:
            logger.error("Falha ao carregar modelo VAD: %s", e)
            raise VADError(f"Erro ao inicializar VAD: {e}") from e

        self.reset()

    def reset(self) -> None:
        """Reseta o estado interno e o estado do modelo."""
        self.state = VADState.IDLE
        self._h = np.zeros((2, 1, 64), dtype=np.float32)  # Hidden state Silero v5
        self._c = np.zeros((2, 1, 64), dtype=np.float32)  # Cell state Silero v5
        self._silence_counter = 0
        self._speech_detected = False

    def process(self, audio_chunk: np.ndarray) -> VADState:
        """Processa um chunk de áudio e atualiza o estado.

        Args:
            audio_chunk: Array numpy (deve ter 512 samples para Silero v5).

        Returns:
            O estado atual do VAD.
        """
        # Garante que o chunk tenha 512 samples (requisito do Silero v5 em 16kHz)
        if len(audio_chunk) != 512:
            # Se for diferente, poderíamos fazer padding ou truncamento,
            # mas o ideal é que o AudioCapture envie chunks compatíveis.
            # Aqui vamos apenas registrar e tentar processar se possível.
            pass

        # Prepara entrada para o modelo
        # Silero espera [batch, samples]
        x = audio_chunk.reshape(1, -1).astype(np.float32)
        sr = np.array([self.sample_rate], dtype=np.int64)

        # Inferência
        ort_inputs = {
            "input": x,
            "sr": sr,
            "h": self._h,
            "c": self._c,
        }

        out, h_out, c_out = self.session.run(None, ort_inputs)

        # Atualiza estados internos do modelo (LSTM)
        self._h, self._c = h_out, c_out

        prob = out[0][0]

        # Lógica da máquina de estados
        if prob >= self.threshold:
            self._silence_counter = 0
            if self.state == VADState.IDLE:
                self.state = VADState.SPEAKING
                logger.debug("VAD: Início de fala detectado (prob=%.2f)", prob)
            self._speech_detected = True
        else:
            if self.state == VADState.SPEAKING:
                self._silence_counter += 1
                if self._silence_counter >= self.min_silence_chunks:
                    self.state = VADState.END_OF_SPEECH
                    logger.debug("VAD: Fim de fala detectado")

        return self.state

    def confirm_end(self) -> None:
        """Confirma que o fim de fala foi processado e volta para IDLE."""
        self.reset()
