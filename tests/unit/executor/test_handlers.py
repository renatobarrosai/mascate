"""Testes unitários para os Handlers de Comando."""

from unittest.mock import patch

from mascate.executor.handlers.app import AppHandler
from mascate.executor.handlers.browser import BrowserHandler
from mascate.executor.handlers.media import MediaHandler
from mascate.executor.models import ActionType, Command


@patch("subprocess.Popen")
def test_app_handler(mock_popen):
    """Verifica se AppHandler tenta executar o alvo."""
    handler = AppHandler()
    cmd = Command(action=ActionType.OPEN_APP, target="firefox")

    success = handler.execute(cmd)

    assert success is True
    mock_popen.assert_called_once()
    args, _ = mock_popen.call_args
    assert "firefox" in args[0]


@patch("subprocess.Popen")
def test_browser_handler_url(mock_popen):
    """Verifica se BrowserHandler usa xdg-open para URLs."""
    handler = BrowserHandler()
    cmd = Command(action=ActionType.OPEN_URL, target="https://google.com")

    handler.execute(cmd)

    mock_popen.assert_called_once()
    args, _ = mock_popen.call_args
    assert "xdg-open" in args[0]
    assert "https://google.com" in args[0]


@patch("subprocess.Popen")
def test_browser_handler_search(mock_popen):
    """Verifica se BrowserHandler converte busca em URL do Google."""
    handler = BrowserHandler()
    cmd = Command(action=ActionType.OPEN_URL, target="python tutorial")

    handler.execute(cmd)

    args, _ = mock_popen.call_args
    url = args[0][1]
    assert "google.com/search?q=python+tutorial" in url


@patch("subprocess.run")
def test_media_handler(mock_run):
    """Verifica se MediaHandler usa playerctl."""
    handler = MediaHandler()
    cmd = Command(action=ActionType.MEDIA_CONTROL, target="proxima")

    handler.execute(cmd)

    mock_run.assert_called_once()
    args, _ = mock_run.call_args
    assert "playerctl" in args[0]
    assert "next" in args[0]
