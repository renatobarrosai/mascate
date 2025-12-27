"""Testes de integração para o Executor."""

from unittest.mock import MagicMock, patch

import pytest

from mascate.executor.executor import Executor


@pytest.fixture
def executor():
    """Cria instância do executor com config mockada."""
    config = MagicMock()
    config.security.blacklist_commands = ["rm -rf"]
    config.security.protected_paths = ["/etc"]
    return Executor(config)


def test_executor_full_flow_low_risk(executor):
    """Testa fluxo completo para comando de baixo risco (abrir app)."""
    intent = {"action": "open_app", "target": "firefox"}

    with patch("subprocess.Popen") as mock_popen:
        feedback = executor.execute_intent(intent)

        assert "Pronto" in feedback
        assert "open_app" in feedback
        mock_popen.assert_called_once()


def test_executor_security_block(executor):
    """Testa se o executor bloqueia intenções maliciosas."""
    intent = {"action": "open_app", "target": "rm -rf /"}

    with patch("subprocess.Popen") as mock_popen:
        feedback = executor.execute_intent(intent)

        assert "segurança" in feedback
        mock_popen.assert_not_called()


def test_executor_confirmation_required(executor):
    """Testa se comandos de alto risco pedem confirmação."""
    # Acessar /etc eleva o risco para HIGH no nosso Guarda-Costas
    intent = {"action": "open_app", "target": "ls /etc"}

    feedback = executor.execute_intent(intent, confirmed=False)

    assert "CONFIRM_REQUIRED" in feedback

    # Agora com confirmação
    with patch("subprocess.Popen") as mock_popen:
        feedback_ok = executor.execute_intent(intent, confirmed=True)
        assert "Pronto" in feedback_ok
        mock_popen.assert_called_once()
