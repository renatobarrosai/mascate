"""Sintetizador de Voz (TTS) para o Mascate usando Piper.

Gera áudio a partir de texto de forma local e eficiente.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import sounddevice as sd

try:
    # A lib piper-tts costuma ser usada via binário ou wrapper
    # Aqui preparamos a estrutura para chamar o modelo ONNX do Piper
    import piper
except ImportError:
    piper = None

from mascate.core.exceptions import MascateError

logger = logging.getLogger(__name__)


class TTSError(MascateError):
    """Erro relacionado à síntese de voz."""


class PiperTTS:
    """Interface para o sintetizador Piper."""

    def __init__(
        self,
        model_path: str | Path,
        config_path: str | Path | None = None,
        use_cuda: bool = False,
    ) -> None:
        """Inicializa o sintetizador.

        Args:
            model_path: Caminho para o modelo .onnx do Piper.
            config_path: Caminho para o arquivo .json de configuração do modelo.
            use_cuda: Se deve tentar usar aceleração GPU (opcional para Piper).
        """
        self.model_path = Path(model_path)
        self.config_path = (
            Path(config_path)
            if config_path
            else self.model_path.with_suffix(".onnx.json")
        )

        if not self.model_path.exists():
            logger.warning(
                "Modelo Piper não encontrado em %s. TTS operará em modo mock.",
                model_path,
            )
            self.voice = None
        else:
            try:
                # O Piper Python wrapper carrega o modelo ONNX
                if piper:
                    self.voice = piper.PiperVoice.load(
                        str(self.model_path),
                        config_path=str(self.config_path),
                        use_cuda=use_cuda,
                    )
                    logger.info(
                        "Modelo de voz Piper carregado: %s", self.model_path.name
                    )
                else:
                    self.voice = None
            except Exception as e:
                logger.error("Falha ao carregar Piper: %s", e)
                self.voice = None

    def synthesize(self, text: str) -> np.ndarray:
        """Sintetiza texto em um array de áudio.

        Args:
            text: O texto a ser falado.

        Returns:
            Array numpy com o áudio (int16 ou float32).
        """
        if not self.voice:
            logger.warning("Simulando voz (MOCK): %s", text)
            # Retorna silêncio se não houver modelo
            return np.zeros(16000, dtype=np.int16)

        try:
            # O Piper gera áudio em chunks (bytes)
            # Vamos acumular para reprodução simples ou streaming
            audio_bytes = b""
            for audio_chunk in self.voice.synthesize_stream(text):
                audio_bytes += audio_chunk

            # Converte bytes para numpy int16 (formato padrão do Piper)
            return np.frombuffer(audio_bytes, dtype=np.int16)
        except Exception as e:
            logger.error("Erro na síntese de voz: %s", e)
            return np.array([], dtype=np.int16)

    def speak(self, text: str, block: bool = True) -> None:
        """Sintetiza e reproduz o áudio imediatamente.

        Args:
            text: Texto para falar.
            block: Se deve esperar a fala terminar.
        """
        audio = self.synthesize(text)
        if audio.size == 0:
            return

        try:
            # Piper costuma usar 22050Hz por padrão, mas varia por modelo
            # Pegamos do config se disponível ou usamos padrão
            sample_rate = self.voice.config.sample_rate if self.voice else 22050

            sd.play(audio, samplerate=sample_rate)
            if block:
                sd.wait()
        except Exception as e:
            logger.error("Erro na reprodução de áudio: %s", e)
