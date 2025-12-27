"""Testes unitários para o Guarda-Costas (Security)."""

from unittest.mock import MagicMock

import pytest

from mascate.executor.models import ActionType, Command, RiskLevel
from mascate.executor.security import SecurityError, SecurityGuard


@pytest.fixture
def mock_config():
    """Mock da configuração de segurança."""
    config = MagicMock()
    config.security.blacklist_commands = ["rm -rf", "mkfs", "dd"]
    config.security.protected_paths = ["/etc", "/boot"]
    return config


def test_security_blacklist_block(mock_config):
    """Verifica se comandos na blacklist disparam SecurityError."""
    guard = SecurityGuard(mock_config)
    cmd = Command(action=ActionType.FILE_OP, target="rm -rf /")

    with pytest.raises(SecurityError, match="Comando proibido"):
        guard.validate(cmd)

    assert cmd.risk_level == RiskLevel.CRITICAL


def test_security_protected_path(mock_config):
    """Verifica se caminhos protegidos elevam o risco para HIGH."""
    guard = SecurityGuard(mock_config)
    cmd = Command(action=ActionType.OPEN_APP, target="ls /etc")

    risk = guard.validate(cmd)

    assert risk == RiskLevel.HIGH
    assert cmd.risk_level == RiskLevel.HIGH


def test_security_shell_injection(mock_config):
    """Verifica bloqueio de injeção de shell."""
    guard = SecurityGuard(mock_config)
    # Tentativa de concatenar comandos com ';'
    cmd = Command(action=ActionType.OPEN_APP, target="firefox; ls")

    with pytest.raises(SecurityError, match="Caracteres especiais"):
        guard.validate(cmd)


def test_authorization_flow(mock_config):
    """Verifica lógica de autorização baseada em confirmação."""
    guard = SecurityGuard(mock_config)

    # LOW risk - autorizado sempre
    cmd_low = Command(action=ActionType.OPEN_APP, target="firefox")
    assert guard.is_authorized(cmd_low) is True

    # HIGH risk - requer confirmação
    cmd_high = Command(action=ActionType.FILE_OP, target="edit /etc/fstab")
    cmd_high.risk_level = RiskLevel.HIGH
    assert guard.is_authorized(cmd_high, user_confirmed=False) is False
    assert guard.is_authorized(cmd_high, user_confirmed=True) is True

    # CRITICAL - nunca autorizado
    cmd_crit = Command(action=ActionType.UNKNOWN, target="bad")
    cmd_crit.risk_level = RiskLevel.CRITICAL
    assert guard.is_authorized(cmd_crit, user_confirmed=True) is False
