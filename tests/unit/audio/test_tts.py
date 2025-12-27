"""Testes unitários para o módulo TTS (Piper e Templates)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from mascate.audio.tts.piper import PiperTTS
from mascate.audio.tts.templates import get_response


def test_templates_response():
    """Verifica se os templates retornam frases válidas e formatadas."""
    resp = get_response("success")
    assert any(phrase[:5] in resp for phrase in ["Pront", "Feito", "Cert", "Tudo"])

    resp_confirm = get_response("confirm", action="apagar arquivo")
    assert "apagar arquivo" in resp_confirm


@patch("mascate.audio.tts.piper.piper", None)  # Força modo mock
def test_piper_tts_mock_mode():
    """Verifica se o Piper entra em modo mock quando a lib ou modelo falta."""
    with patch.object(Path, "exists", return_value=False):
        tts = PiperTTS(model_path="ghost.onnx")
        audio = tts.synthesize("Teste")

        assert isinstance(audio, np.ndarray)
        assert audio.size > 0  # Silêncio gerado pelo mock


@patch("mascate.audio.tts.piper.sd.play")
@patch("mascate.audio.tts.piper.piper")
def test_piper_speak_call(mock_piper, mock_sd_play):
    """Verifica se o fluxo de fala chama o sounddevice."""
    mock_voice = MagicMock()
    mock_piper.PiperVoice.load.return_value = mock_voice

    # Simula stream de áudio
    mock_voice.synthesize_stream.return_value = [b"\x00\x00" * 100]
    mock_voice.config.sample_rate = 22050

    with patch.object(Path, "exists", return_value=True):
        tts = PiperTTS(model_path="model.onnx")
        tts.speak("Olá")

        mock_sd_play.assert_called_once()
        args, kwargs = mock_sd_play.call_args
        assert kwargs["samplerate"] == 22050
        assert isinstance(args[0], np.ndarray)
