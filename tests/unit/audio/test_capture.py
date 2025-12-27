"""Testes unitários para o módulo de captura de áudio."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from mascate.audio.capture import AudioCapture, AudioCaptureError, DeviceInfo


def test_audio_capture_initialization():
    """Verifica se a classe inicializa com os parâmetros corretos."""
    capture = AudioCapture(
        sample_rate=16000, channels=1, chunk_size=1024, buffer_seconds=0.5
    )

    assert capture.sample_rate == 16000
    assert capture.channels == 1
    assert capture.chunk_size == 1024
    # 16000 * 0.5 / 1024 ~= 7.8 -> maxlen deve ser 7 (ou 8 dependendo do arredondamento)
    # No código: int(16000 * 0.5 / 1024) = int(7.8125) = 7
    assert capture.circular_buffer.maxlen == 7


@patch("sounddevice.query_devices")
def test_list_devices(mock_query):
    """Verifica a listagem de dispositivos de áudio."""
    mock_query.return_value = [
        {"name": "Mic 1", "max_input_channels": 1, "default_sample_rate": 44100},
        {"name": "Speaker 1", "max_input_channels": 0, "default_sample_rate": 44100},
        {"name": "Mic 2", "max_input_channels": 2, "default_sample_rate": 48000},
    ]

    devices = AudioCapture.list_devices()

    assert len(devices) == 2
    assert devices[0].name == "Mic 1"
    assert devices[1].name == "Mic 2"
    assert isinstance(devices[0], DeviceInfo)


def test_circular_buffer_mechanics():
    """Verifica se o buffer circular mantém apenas os chunks mais recentes."""
    capture = AudioCapture(sample_rate=16000, chunk_size=1000, buffer_seconds=0.3)
    # buffer_len = int(16000 * 0.3 / 1000) = 4

    assert capture.circular_buffer.maxlen == 4

    # Adiciona 5 chunks
    for i in range(5):
        data = np.full((1000, 1), i, dtype="float32")
        capture.circular_buffer.append(data)

    assert len(capture.circular_buffer) == 4
    # O primeiro chunk (0) deve ter sido removido
    assert capture.circular_buffer[0][0] == 1
    assert capture.circular_buffer[-1][0] == 4


@patch("sounddevice.InputStream")
def test_start_stop(mock_stream_class):
    """Verifica se o stream é iniciado e parado corretamente."""
    mock_stream_instance = MagicMock()
    mock_stream_class.return_value = mock_stream_instance

    capture = AudioCapture()
    capture.start()

    assert capture.is_running
    mock_stream_class.assert_called_once()
    mock_stream_instance.start.assert_called_once()

    capture.stop()
    assert not capture.is_running
    mock_stream_instance.stop.assert_called_once()
    mock_stream_instance.close.assert_called_once()


def test_callback_processing():
    """Verifica se o callback de áudio preenche a fila e o buffer."""
    capture = AudioCapture(chunk_size=1024)
    callback_mock = MagicMock()
    capture._callback_fn = callback_mock

    # Simula o callback sendo chamado pelo sounddevice
    test_data = np.random.rand(1024, 1).astype("float32")
    capture._audio_callback(test_data, 1024, None, None)

    # Verifica fila
    chunk_from_queue = capture.get_chunk(block=False)
    assert np.array_equal(chunk_from_queue, test_data)

    # Verifica buffer circular
    assert len(capture.circular_buffer) == 1
    assert np.array_equal(capture.circular_buffer[0], test_data)

    # Verifica callback externo
    callback_mock.assert_called_once()


@patch("sounddevice.InputStream")
def test_start_failure(mock_stream_class):
    """Verifica o tratamento de erro ao falhar ao iniciar o stream."""
    mock_stream_class.side_effect = Exception("Erro de hardware")

    capture = AudioCapture()
    with pytest.raises(AudioCaptureError, match="Não foi possível iniciar captura"):
        capture.start()

    assert not capture.is_running
