"""Testes unitários para a Interface Visual (HUD)."""

from rich.panel import Panel

from mascate.interface.hud import HUD


def test_hud_initialization():
    """Verifica se o HUD inicializa com os valores corretos."""
    hud = HUD(version="1.2.3")
    assert hud.version == "1.2.3"
    assert hud.state == "INICIALIZANDO"
    assert len(hud.logs) == 0


def test_hud_state_update():
    """Verifica se o estado é atualizado corretamente."""
    hud = HUD()
    hud.update_state("LISTENING")
    assert hud.state == "LISTENING"


def test_hud_log_rotation():
    """Verifica se os logs mantêm apenas as últimas 5 mensagens."""
    hud = HUD()
    for i in range(10):
        hud.add_log(f"Mensagem {i}")

    assert len(hud.logs) == 5
    assert "Mensagem 9" in hud.logs[-1]
    assert "Mensagem 0" not in hud.logs


def test_hud_view_generation():
    """Verifica se o HUD gera um objeto Panel válido do Rich."""
    hud = HUD()
    hud.set_interaction("Oi", "Olá")
    view = hud._create_view()

    assert isinstance(view, Panel)
    # A verificação de conteúdo interno do Rich é complexa,
    # então validamos a estrutura básica do objeto retornado.
    assert view.title == "Terminal de Controle"
