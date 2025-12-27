"""Testes de integração para o pipeline de áudio."""

from unittest.mock import MagicMock, patch

import numpy as np

from mascate.audio.pipeline import AudioPipeline
from mascate.audio.vad.processor import VADState


@patch("mascate.audio.capture.sd.InputStream")
def test_pipeline_flow(mock_stream):
    """Testa o fluxo completo do pipeline de áudio (mockado)."""
    # 1. Setup Mocks
    capture = MagicMock()
    wake_detector = MagicMock()
    wake_detector.threshold = 0.5
    vad_processor = MagicMock()
    stt = MagicMock()
    stt.transcribe.return_value = "abrir o firefox"

    pipeline = AudioPipeline(capture, wake_detector, vad_processor, stt)

    # 2. Callbacks
    activation_called = MagicMock()
    transcription_result = []

    pipeline.on_activation(activation_called)
    pipeline.on_transcription(lambda t: transcription_result.append(t))

    # 3. Simulação de Ativação
    pipeline._handle_activation()
    assert activation_called.called
    assert pipeline._is_listening

    # 4. Simulação de fala e fim de fala
    pipeline._audio_buffer.append(np.zeros(1024))
    vad_processor.process.return_value = VADState.END_OF_SPEECH

    pipeline._handle_end_of_speech()

    # 5. Verificações Finais
    assert not pipeline._is_listening
    assert transcription_result == ["abrir o firefox"]
    stt.transcribe.assert_called_once()


def test_pipeline_handle_activation():
    """Verifica se a ativação limpa buffers e chama callbacks."""
    pipeline = AudioPipeline(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    pipeline.capture.circular_buffer = [np.ones(10), np.ones(10)]
    callback = MagicMock()
    pipeline.on_activation(callback)

    pipeline._handle_activation()

    assert pipeline._is_listening
    assert len(pipeline._audio_buffer) == 2
    callback.assert_called_once()


def test_pipeline_handle_end_of_speech():
    """Verifica se o fim de fala dispara STT e reseta estados."""
    pipeline = AudioPipeline(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    pipeline._is_listening = True
    pipeline._audio_buffer = [np.zeros(100)]
    pipeline.stt.transcribe.return_value = "teste"

    result = []
    pipeline.on_transcription(result.append)

    pipeline._handle_end_of_speech()

    assert not pipeline._is_listening
    assert result == ["teste"]
    pipeline.vad_processor.confirm_end.assert_called_once()
