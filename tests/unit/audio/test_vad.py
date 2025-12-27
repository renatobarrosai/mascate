"""Testes unitários para o processador VAD."""

from unittest.mock import MagicMock, patch, sys

import numpy as np
import pytest

# Mock onnxruntime before importing the processor if it's not available
mock_ort = MagicMock()
if "onnxruntime" not in sys.modules:
    sys.modules["onnxruntime"] = mock_ort

from mascate.audio.vad.processor import VADError, VADProcessor, VADState


def test_vad_initialization():
    """Verifica se o VAD inicializa corretamente com o mock do ONNX."""
    with patch(
        "mascate.audio.vad.processor.ort.InferenceSession"
    ) as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        processor = VADProcessor(model_path="dummy.onnx", threshold=0.6)

        assert processor.threshold == 0.6
        assert processor.state == VADState.IDLE
        mock_session_class.assert_called_once_with("dummy.onnx")


def test_vad_state_transitions():
    """Verifica as transições de estado IDLE -> SPEAKING -> END_OF_SPEECH."""
    with patch(
        "mascate.audio.vad.processor.ort.InferenceSession"
    ) as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # 300ms de silêncio / (512 samples / 16k) ~= 9.3 -> 9 chunks
        processor = VADProcessor(model_path="dummy.onnx", min_silence_duration_ms=300)

        # Simula resposta do ONNX: [probabilidade, h, c]
        # Caso 1: Fala detectada (prob = 0.8)
        mock_session.run.return_value = [
            np.array([[0.8]], dtype=np.float32),
            np.zeros((2, 1, 64), dtype=np.float32),
            np.zeros((2, 1, 64), dtype=np.float32),
        ]

        chunk = np.zeros(512, dtype=np.float32)
        state = processor.process(chunk)
        assert state == VADState.SPEAKING

        # Caso 2: Silêncio (prob = 0.1)
        mock_session.run.return_value = [
            np.array([[0.1]], dtype=np.float32),
            np.zeros((2, 1, 64), dtype=np.float32),
            np.zeros((2, 1, 64), dtype=np.float32),
        ]

        # Processa 8 chunks de silêncio (ainda deve estar em SPEAKING)
        for _ in range(8):
            state = processor.process(chunk)
            assert state == VADState.SPEAKING

        # O 9º chunk de silêncio deve disparar END_OF_SPEECH
        state = processor.process(chunk)
        assert state == VADState.END_OF_SPEECH


def test_vad_reset():
    """Verifica se o reset limpa o estado corretamente."""
    with patch(
        "mascate.audio.vad.processor.ort.InferenceSession"
    ) as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        processor = VADProcessor(model_path="dummy.onnx")
        processor.state = VADState.SPEAKING
        processor._silence_counter = 5

        processor.reset()
        assert processor.state == VADState.IDLE
        assert processor._silence_counter == 0


def test_vad_import_error():
    """Verifica o erro quando o onnxruntime não está presente."""
    with patch("mascate.audio.vad.processor.ort", None):
        with pytest.raises(VADError, match="onnxruntime não encontrado"):
            VADProcessor(model_path="dummy.onnx")
