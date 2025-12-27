"""Testes unitários para o Command Parser."""

from mascate.executor.models import ActionType, RiskLevel
from mascate.executor.parser import CommandParser


def test_parse_valid_command():
    """Verifica parsing de um comando válido."""
    data = {"action": "open_app", "target": "firefox", "params": {"private": True}}

    cmd = CommandParser.parse(data)

    assert cmd.action == ActionType.OPEN_APP
    assert cmd.target == "firefox"
    assert cmd.params["private"] is True
    assert cmd.risk_level == RiskLevel.LOW


def test_parse_file_op_risk():
    """Verifica se operações de arquivo recebem risco HIGH."""
    data = {"action": "file_op", "target": "meu_projeto"}

    cmd = CommandParser.parse(data)

    assert cmd.action == ActionType.FILE_OP
    assert cmd.risk_level == RiskLevel.HIGH


def test_parse_unknown_action():
    """Verifica comportamento com ação inexistente."""
    data = {"action": "explodir_computador", "target": "agora"}

    cmd = CommandParser.parse(data)

    assert cmd.action == ActionType.UNKNOWN


def test_parse_json_string():
    """Verifica se o parser aceita strings JSON diretamente."""
    json_str = '{"action": "open_url", "target": "https://google.com"}'

    cmd = CommandParser.parse(json_str)

    assert cmd.action == ActionType.OPEN_URL
    assert cmd.target == "https://google.com"
