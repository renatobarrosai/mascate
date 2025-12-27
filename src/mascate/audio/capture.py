"""Captura de áudio do microfone para o Mascate.

Gerencia a entrada de áudio usando sounddevice e mantém um buffer circular
para processamento em tempo real.
"""

from __future__ import annotations

import logging
import queue
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import sounddevice as sd

from mascate.core.exceptions import MascateError

logger = logging.getLogger(__name__)


class AudioCaptureError(MascateError):
    """Erro relacionado à captura de áudio."""


@dataclass
class DeviceInfo:
    """Informações sobre um dispositivo de áudio."""

    id: int
    name: str
    max_input_channels: int
    default_sample_rate: float


class AudioCapture:
    """Captura áudio do microfone e gerencia buffers."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = "float32",
        chunk_size: int = 1024,
        buffer_seconds: float = 0.5,
    ) -> None:
        """Inicializa o capturador de áudio.

        Args:
            sample_rate: Taxa de amostragem em Hz.
            channels: Número de canais.
            dtype: Tipo de dado (ex: 'float32').
            chunk_size: Tamanho do bloco para o callback.
            buffer_seconds: Tamanho do buffer circular em segundos.
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.chunk_size = chunk_size

        # Buffer circular para manter histórico recente
        buffer_len = int((sample_rate * buffer_seconds) / chunk_size)
        self.circular_buffer: deque[np.ndarray] = deque(maxlen=max(1, buffer_len))

        # Fila para comunicação thread-safe com o callback
        self.queue: queue.Queue[np.ndarray] = queue.Queue()

        self.stream: sd.InputStream | None = None
        self._running = False
        self._callback_fn: Callable[[np.ndarray], None] | None = None

    @staticmethod
    def list_devices() -> list[DeviceInfo]:
        """Lista os dispositivos de entrada disponíveis.

        Returns:
            Lista de objetos DeviceInfo.
        """
        devices = sd.query_devices()
        input_devices = []
        for i, dev in enumerate(devices):
            if dev["max_input_channels"] > 0:
                input_devices.append(
                    DeviceInfo(
                        id=i,
                        name=dev["name"],
                        max_input_channels=dev["max_input_channels"],
                        default_sample_rate=dev["default_sample_rate"],
                    )
                )
        return input_devices

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time: Any, status: sd.CallbackFlags
    ) -> None:
        """Callback chamado pelo sounddevice a cada novo bloco de áudio.

        Args:
            indata: Buffer com os dados capturados.
            frames: Número de frames capturados.
            time: Timestamp.
            status: Flags de status do callback.
        """
        if status:
            logger.warning("Status do callback de áudio: %s", status)

        # Copia os dados para evitar problemas de concorrência
        data = indata.copy()

        # Adiciona ao buffer circular (histórico)
        self.circular_buffer.append(data)

        # Adiciona à fila de processamento
        self.queue.put(data)

        # Chama callback externo se definido
        if self._callback_fn:
            self._callback_fn(data)

    def start(
        self,
        device_id: int | None = None,
        callback: Callable[[np.ndarray], None] | None = None,
    ) -> None:
        """Inicia a captura de áudio.

        Args:
            device_id: ID do dispositivo de entrada (opcional).
            callback: Função chamada a cada novo chunk de áudio.

        Raises:
            AudioCaptureError: Se falhar ao abrir o stream.
        """
        if self._running:
            return

        self._callback_fn = callback

        try:
            self.stream = sd.InputStream(
                device=device_id,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
            )
            self.stream.start()
            self._running = True
            logger.info("Captura de áudio iniciada (SR=%d)", self.sample_rate)
        except Exception as e:
            logger.error("Falha ao iniciar stream de áudio: %s", e)
            raise AudioCaptureError(f"Não foi possível iniciar captura: {e}") from e

    def stop(self) -> None:
        """Para a captura de áudio."""
        if not self._running:
            return

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self._running = False
        logger.info("Captura de áudio parada")

    def get_chunk(self, block: bool = True, timeout: float | None = None) -> np.ndarray:
        """Obtém o próximo chunk de áudio da fila.

        Args:
            block: Se deve bloquear até que um chunk esteja disponível.
            timeout: Tempo máximo de espera em segundos.

        Returns:
            Array numpy com o chunk de áudio.

        Raises:
            queue.Empty: Se a fila estiver vazia e block=False ou timeout expirar.
        """
        return self.queue.get(block=block, timeout=timeout)

    def get_buffer_content(self) -> np.ndarray:
        """Retorna o conteúdo atual do buffer circular concatenado.

        Returns:
            Array numpy com todo o áudio no buffer.
        """
        if not self.circular_buffer:
            return np.array([], dtype=self.dtype)
        return np.concatenate(list(self.circular_buffer))

    @property
    def is_running(self) -> bool:
        """Verifica se a captura está ativa."""
        return self._running
