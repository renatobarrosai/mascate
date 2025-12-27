"""Transcrição de Áudio (STT) para o Mascate.

Usa o Whisper para transcrever chunks de áudio em texto.
Otimizado para rodar na CPU.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

try:
    # Vamos assumir o uso de pywhispercpp ou similar futuramente.
    # Por enquanto, preparamos a estrutura.
    import pywhispercpp.model as whisper
except ImportError:
    whisper = None

from mascate.core.exceptions import MascateError

logger = logging.getLogger(__name__)


class STTError(MascateError):
    """Erro relacionado à transcrição de áudio."""


class WhisperSTT:
    """Interface para o modelo Whisper STT."""

    def __init__(
        self,
        model_path: str | Path,
        language: str = "pt",
        n_threads: int = 4,
    ) -> None:
        """Inicializa o modelo Whisper.

        Args:
            model_path: Caminho para o modelo (.bin / .gguf).
            language: Código do idioma (ex: 'pt', 'en').
            n_threads: Número de threads para processamento na CPU.

        Raises:
            STTError: Se falhar ao carregar o modelo.
        """
        self.model_path = Path(model_path)
        self.language = language
        self.n_threads = n_threads
        self.model = None

        if not self.model_path.exists():
            raise STTError(f"Modelo Whisper não encontrado em: {model_path}")

        try:
            if whisper:
                self.model = whisper.Model(
                    str(self.model_path),
                    lang=self.language,
                    n_threads=self.n_threads,
                    print_realtime=False,
                    print_progress=False,
                )
                logger.info("Modelo Whisper carregado: %s", self.model_path)
            else:
                logger.warning("pywhispercpp não instalado. STT operará em modo mock.")
        except Exception as e:
            logger.error("Falha ao carregar Whisper: %s", e)
            raise STTError(f"Erro ao inicializar Whisper: {e}") from e

    def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcreve um array de áudio para texto.

        Args:
            audio_data: Array numpy (16kHz, Mono, float32).

        Returns:
            Texto transcrito.
        """
        if not self.model:
            logger.warning("STT executando em modo mock (sem modelo carregado)")
            return "texto de exemplo (mock)"

        try:
            # Whisper espera áudio em float32, 16kHz
            segments = self.model.transcribe(audio_data, lang=self.language)

            # Concatena os segmentos
            text = "".join([s.text for s in segments]).strip()

            # Limpeza básica
            text = self._post_process(text)

            logger.debug("Transcrição concluída: '%s'", text)
            return text
        except Exception as e:
            logger.error("Erro durante a transcrição: %s", e)
            return ""

    def _post_process(self, text: str) -> str:
        """Limpa o texto transcrito.

        Args:
            text: Texto bruto.

        Returns:
            Texto limpo.
        """
        # Remove espaços duplos
        text = " ".join(text.split())

        # Remove tokens comuns de alucinação do Whisper em silêncio (ex: [Música], [Silêncio])
        hallucinations = [
            "[Música]",
            "[Silêncio]",
            "(música)",
            "(silêncio)",
            "Legendas",
            "Obrigado",
        ]
        for h in hallucinations:
            text = text.replace(h, "")

        return text.strip()
