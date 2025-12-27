"""Detecção de palavra de ativação (Wake Word) para o Mascate.

Usa o openWakeWord para detectar quando o usuário diz a palavra de comando.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

import numpy as np

try:
    from openwakeword.model import Model
except ImportError:
    # Fallback para ambientes sem a lib instalada (ex: CI)
    Model = None

from mascate.core.exceptions import MascateError

logger = logging.getLogger(__name__)


class WakeWordError(MascateError):
    """Erro relacionado à detecção de wake word."""


class WakeWordDetector:
    """Detecta a palavra de ativação em chunks de áudio."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        wakeword: str = "hey_mascate",
        threshold: float = 0.5,
        inference_framework: str = "onnx",
    ) -> None:
        """Inicializa o detector de wake word.

        Args:
            model_path: Caminho para o modelo customizado (opcional).
            wakeword: Nome da palavra de ativação a monitorar.
            threshold: Sensibilidade da detecção (0.0 a 1.0).
            inference_framework: Framework de inferência ('onnx' ou 'tflite').

        Raises:
            WakeWordError: Se o openWakeWord não estiver instalado ou falhar no carregamento.
        """
        if Model is None:
            raise WakeWordError(
                "openwakeword não está instalado. "
                "Instale com 'uv pip install openwakeword'."
            )

        self.wakeword = wakeword
        self.threshold = threshold
        self._on_activation_cb: Callable[[], None] | None = None

        try:
            # Se model_path for fornecido, usa ele. Caso contrário, tenta carregar o padrão.
            models = [str(model_path)] if model_path else None

            self.model = Model(
                wakeword_models=models, inference_framework=inference_framework
            )

            # Verifica se o modelo solicitado está disponível
            if wakeword not in self.model.models:
                # Se não encontrar, lista os disponíveis para log
                available = list(self.model.models.keys())
                logger.warning(
                    "Palavra '%s' não encontrada no modelo. Disponíveis: %s",
                    wakeword,
                    available,
                )
                # Tenta usar a primeira disponível como fallback se não for modelo custom
                if not model_path and available:
                    self.wakeword = available[0]
                    logger.info("Usando fallback: %s", self.wakeword)

            logger.info("Detector de Wake Word inicializado: %s", self.wakeword)
        except Exception as e:
            logger.error("Falha ao carregar modelo de Wake Word: %s", e)
            raise WakeWordError(f"Falha ao carregar openwakeword: {e}") from e

    def process(self, audio_chunk: np.ndarray) -> float:
        """Processa um chunk de áudio e verifica a palavra de ativação.

        Args:
            audio_chunk: Array numpy (16kHz, Mono, float32 ou int16).

        Returns:
            Score de confiança da detecção (0.0 a 1.0).
        """
        # openWakeWord espera int16 ou float32 em 16kHz
        # O modelo processa chunks internamente e mantém o estado
        self.model.predict(audio_chunk)

        # Obtém o score para a palavra alvo
        score = self.model.prediction_buffer[self.wakeword][-1]

        if score >= self.threshold:
            logger.info("Wake word detectada! Score: %.2f", score)
            if self._on_activation_cb:
                self._on_activation_cb()

        return float(score)

    def on_activation(self, callback: Callable[[], None]) -> None:
        """Define o callback a ser chamado na ativação.

        Args:
            callback: Função sem argumentos.
        """
        self._on_activation_cb = callback

    @property
    def available_models(self) -> list[str]:
        """Retorna a lista de modelos carregados."""
        return list(self.model.models.keys())
