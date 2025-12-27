"""Testes de integração para o Orquestrador."""

from unittest.mock import MagicMock

import pytest

from mascate.core.orchestrator import Orchestrator, SystemState


@pytest.fixture
def mocks():
    """Cria todos os mocks necessários para o orquestrador."""
    return {
        "audio": MagicMock(),
        "brain": MagicMock(),
        "executor": MagicMock(),
        "hud": MagicMock(),
    }


def test_orchestrator_initialization(mocks):
    """Verifica se o orquestrador inicializa no estado correto."""
    orc = Orchestrator(mocks["audio"], mocks["brain"], mocks["executor"], mocks["hud"])
    assert orc.state == SystemState.INITIALIZING


def test_orchestrator_wake_word_transition(mocks):
    """Verifica se a wake word muda o estado para LISTENING."""
    orc = Orchestrator(mocks["audio"], mocks["brain"], mocks["executor"], mocks["hud"])
    orc._handle_wake_word()

    assert orc.state == SystemState.LISTENING
    mocks["hud"].update_state.assert_called_with("LISTENING")


def test_orchestrator_full_cycle(mocks):
    """Verifica o ciclo completo: Transcrição -> Brain -> Executor -> IDLE."""
    orc = Orchestrator(mocks["audio"], mocks["brain"], mocks["executor"], mocks["hud"])

    # Setup mocks
    mock_intent = MagicMock()
    # raw_json pode ser string (será convertido para dict) ou já dict
    mock_intent.raw_json = '{"action": "test"}'
    mocks["brain"].process.return_value = mock_intent
    mocks["executor"].execute_intent.return_value = "Sucesso"

    # Simula chegada de transcrição
    orc._handle_transcription("abrir firefox")

    # Verifica fluxo
    mocks["brain"].process.assert_called_once_with("abrir firefox")
    # O orchestrator converte raw_json string para dict antes de passar ao executor
    mocks["executor"].execute_intent.assert_called_once_with({"action": "test"})
    mocks["hud"].set_interaction.assert_called_with("abrir firefox", "Sucesso")
    assert orc.state == SystemState.IDLE


def test_orchestrator_stop(mocks):
    """Verifica o desligamento gracioso."""
    orc = Orchestrator(mocks["audio"], mocks["brain"], mocks["executor"], mocks["hud"])
    orc._running = True

    orc.stop()

    assert not orc._running
    assert orc.state == SystemState.SHUTTING_DOWN
    mocks["audio"].stop.assert_called_once()
    mocks["hud"].stop.assert_called_once()
