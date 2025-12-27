"""Testes unitários para o detector de Wake Word."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from mascate.audio.wake.detector import WakeWordDetector, WakeWordError


@patch("mascate.audio.wake.detector.Model")
def test_wake_word_initialization(mock_model_class):
    """Verifica se o detector inicializa corretamente com o modelo mockado."""
    # Configura o mock do modelo
    mock_instance = MagicMock()
    mock_instance.models = {"hey_mascate": {}}
    mock_model_class.return_value = mock_instance

    detector = WakeWordDetector(wakeword="hey_mascate", threshold=0.6)

    assert detector.wakeword == "hey_mascate"
    assert detector.threshold == 0.6
    mock_model_class.assert_called_once()


@patch("mascate.audio.wake.detector.Model")
def test_wake_word_detection_success(mock_model_class):
    """Verifica se a detecção chama o callback e retorna o score correto."""
    mock_instance = MagicMock()
    mock_instance.models = {"hey_mascate": {}}
    # Simula o buffer de predição do openWakeWord
    mock_instance.prediction_buffer = {"hey_mascate": [0.1, 0.8]}
    mock_model_class.return_value = mock_instance

    detector = WakeWordDetector(wakeword="hey_mascate", threshold=0.5)

    callback = MagicMock()
    detector.on_activation(callback)

    test_audio = np.zeros(1280, dtype="float32")
    score = detector.process(test_audio)

    assert score == 0.8
    callback.assert_called_once()
    mock_instance.predict.assert_called_once_with(test_audio)


@patch("mascate.audio.wake.detector.Model")
def test_wake_word_no_detection(mock_model_class):
    """Verifica se scores abaixo do threshold não ativam o sistema."""
    mock_instance = MagicMock()
    mock_instance.models = {"hey_mascate": {}}
    mock_instance.prediction_buffer = {"hey_mascate": [0.1, 0.2]}
    mock_model_class.return_value = mock_instance

    detector = WakeWordDetector(wakeword="hey_mascate", threshold=0.5)

    callback = MagicMock()
    detector.on_activation(callback)

    test_audio = np.zeros(1280, dtype="float32")
    score = detector.process(test_audio)

    assert score == 0.2
    callback.assert_not_called()


@patch("mascate.audio.wake.detector.Model")
def test_wake_word_fallback(mock_model_class):
    """Verifica se o detector usa o primeiro modelo disponível se o alvo não existir."""
    mock_instance = MagicMock()
    mock_instance.models = {"alexa": {}, "ok_google": {}}
    mock_model_class.return_value = mock_instance

    # Tentando usar 'hey_mascate' que não está na lista acima
    detector = WakeWordDetector(wakeword="hey_mascate")

    assert detector.wakeword == "alexa"


def test_wake_word_import_error():
    """Verifica o erro quando a lib não está presente."""
    with patch("mascate.audio.wake.detector.Model", None):
        with pytest.raises(WakeWordError, match="openwakeword não está instalado"):
            WakeWordDetector()
