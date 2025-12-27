"""Testes unitários para o módulo Whisper STT."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from mascate.audio.stt.whisper import STTError, WhisperSTT


@patch("mascate.audio.stt.whisper.whisper")
def test_whisper_initialization(mock_whisper):
    """Verifica se o Whisper inicializa corretamente."""
    mock_model = MagicMock()
    mock_whisper.Model.return_value = mock_model

    # Simula arquivo de modelo existindo
    with patch.object(Path, "exists", return_value=True):
        stt = WhisperSTT(model_path="models/whisper.bin", language="pt")

        assert stt.language == "pt"
        mock_whisper.Model.assert_called_once()


def test_whisper_model_not_found():
    """Verifica erro quando o arquivo do modelo não existe."""
    with patch.object(Path, "exists", return_value=False):
        with pytest.raises(STTError, match="Modelo Whisper não encontrado"):
            WhisperSTT(model_path="non_existent.bin")


@patch("mascate.audio.stt.whisper.whisper")
def test_transcription_success(mock_whisper):
    """Verifica o fluxo de transcrição bem-sucedido."""
    mock_model = MagicMock()
    mock_whisper.Model.return_value = mock_model

    # Simula retorno do transcribe
    mock_segment = MagicMock()
    mock_segment.text = " Abrir o Firefox. "
    mock_model.transcribe.return_value = [mock_segment]

    with patch.object(Path, "exists", return_value=True):
        stt = WhisperSTT(model_path="models/whisper.bin")
        audio_data = np.zeros(16000, dtype=np.float32)

        result = stt.transcribe(audio_data)

        assert result == "Abrir o Firefox."
        mock_model.transcribe.assert_called_once()


def test_post_process_cleanup():
    """Verifica a limpeza de alucinações e espaços."""
    # Como WhisperSTT não precisa do modelo para testar o método privado
    # vamos usar uma pequena gambiarra para testar a lógica interna
    with patch.object(Path, "exists", return_value=True):
        with patch("mascate.audio.stt.whisper.whisper", None):
            stt = WhisperSTT(model_path="dummy.bin")

            raw_text = "  [Música]  Abrir o Spotify.   [Silêncio]  "
            cleaned = stt._post_process(raw_text)

            assert cleaned == "Abrir o Spotify."


@patch("mascate.audio.stt.whisper.whisper")
def test_transcription_failure(mock_whisper):
    """Verifica comportamento em caso de falha na transcrição."""
    mock_model = MagicMock()
    mock_whisper.Model.return_value = mock_model
    mock_model.transcribe.side_effect = Exception("Crash no C++")

    with patch.object(Path, "exists", return_value=True):
        stt = WhisperSTT(model_path="dummy.bin")
        audio_data = np.zeros(16000, dtype=np.float32)

        result = stt.transcribe(audio_data)

        assert result == ""
