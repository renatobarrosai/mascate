"""Testes para o HotkeyListener."""

from unittest.mock import MagicMock, patch

import pytest

from mascate.audio.hotkey import HotkeyError, HotkeyListener, parse_hotkey


class TestParseHotkey:
    """Testes para a funcao parse_hotkey."""

    def test_parse_simple_hotkey(self):
        """Testa parsing de hotkey simples."""
        result = parse_hotkey("ctrl+m")
        assert result == {"ctrl", "m"}

    def test_parse_complex_hotkey(self):
        """Testa parsing de hotkey com multiplas teclas."""
        result = parse_hotkey("ctrl+shift+m")
        assert result == {"ctrl", "shift", "m"}

    def test_parse_super_key(self):
        """Testa parsing com tecla super/meta."""
        result = parse_hotkey("super+space")
        assert result == {"cmd", "space"}

    def test_parse_win_key(self):
        """Testa parsing com tecla win (alias para super)."""
        result = parse_hotkey("win+e")
        assert result == {"cmd", "e"}

    def test_parse_function_key(self):
        """Testa parsing com tecla de funcao."""
        result = parse_hotkey("ctrl+f1")
        assert result == {"ctrl", "f1"}

    def test_parse_case_insensitive(self):
        """Testa que parsing e case insensitive."""
        result = parse_hotkey("CTRL+SHIFT+M")
        assert result == {"ctrl", "shift", "m"}

    def test_parse_with_spaces(self):
        """Testa que espacos sao ignorados."""
        result = parse_hotkey("ctrl + shift + m")
        assert result == {"ctrl", "shift", "m"}

    def test_parse_empty_raises_error(self):
        """Testa que string vazia levanta erro."""
        with pytest.raises(HotkeyError, match="cannot be empty"):
            parse_hotkey("")

    def test_parse_only_plus_raises_error(self):
        """Testa que string so com + levanta erro."""
        with pytest.raises(HotkeyError, match="No valid keys"):
            parse_hotkey("+++")


class TestHotkeyListener:
    """Testes para a classe HotkeyListener."""

    @patch("mascate.audio.hotkey.keyboard")
    def test_initialization(self, mock_keyboard):
        """Testa inicializacao do listener."""
        listener = HotkeyListener(hotkey="ctrl+m")

        assert listener.hotkey_str == "ctrl+m"
        assert listener.target_keys == {"ctrl", "m"}
        assert not listener.is_running

    @patch("mascate.audio.hotkey.keyboard", None)
    def test_initialization_without_pynput(self):
        """Testa erro quando pynput nao esta instalado."""
        with pytest.raises(HotkeyError, match="pynput nao esta instalado"):
            HotkeyListener()

    @patch("mascate.audio.hotkey.keyboard")
    def test_start_stop(self, mock_keyboard):
        """Testa start e stop do listener."""
        mock_listener_instance = MagicMock()
        mock_keyboard.Listener.return_value = mock_listener_instance

        listener = HotkeyListener(hotkey="ctrl+m")
        listener.start()

        assert listener.is_running
        mock_keyboard.Listener.assert_called_once()
        mock_listener_instance.start.assert_called_once()

        listener.stop()

        assert not listener.is_running
        mock_listener_instance.stop.assert_called_once()

    @patch("mascate.audio.hotkey.keyboard")
    def test_callback_registration(self, mock_keyboard):
        """Testa registro de callback."""
        callback = MagicMock()
        listener = HotkeyListener(hotkey="ctrl+m")
        listener.on_activate(callback)

        assert listener._on_activate == callback

    @patch("mascate.audio.hotkey.keyboard")
    def test_normalize_key_special(self, mock_keyboard):
        """Testa normalizacao de teclas especiais."""
        listener = HotkeyListener(hotkey="ctrl+m")

        # Mock de tecla especial (ctrl_l)
        mock_key = MagicMock()
        mock_key.name = "ctrl_l"

        result = listener._normalize_key(mock_key)
        assert result == "ctrl"

    @patch("mascate.audio.hotkey.keyboard")
    def test_normalize_key_char(self, mock_keyboard):
        """Testa normalizacao de teclas de caractere."""
        listener = HotkeyListener(hotkey="ctrl+m")

        # Mock de tecla de caractere
        mock_key = MagicMock(spec=["char"])
        mock_key.char = "M"

        result = listener._normalize_key(mock_key)
        assert result == "m"

    @patch("mascate.audio.hotkey.keyboard")
    def test_key_detection(self, mock_keyboard):
        """Testa deteccao de hotkey completa."""
        callback = MagicMock()
        listener = HotkeyListener(hotkey="ctrl+m", on_activate=callback)

        # Simula pressionamento de ctrl
        mock_ctrl = MagicMock()
        mock_ctrl.name = "ctrl_l"
        listener._on_press(mock_ctrl)

        # Callback nao deve ser chamado ainda
        callback.assert_not_called()

        # Simula pressionamento de m
        mock_m = MagicMock(spec=["char"])
        mock_m.char = "m"

        # Patch threading.Thread para executar callback sincronamente
        with patch("threading.Thread") as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            listener._on_press(mock_m)

            # Thread deve ser criada com o callback
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()

    @patch("mascate.audio.hotkey.keyboard")
    def test_key_release(self, mock_keyboard):
        """Testa liberacao de tecla."""
        listener = HotkeyListener(hotkey="ctrl+m")

        # Simula pressionamento
        mock_ctrl = MagicMock()
        mock_ctrl.name = "ctrl_l"
        listener._on_press(mock_ctrl)

        assert "ctrl" in listener._pressed_keys

        # Simula liberacao
        listener._on_release(mock_ctrl)

        assert "ctrl" not in listener._pressed_keys

    @patch("mascate.audio.hotkey.keyboard")
    def test_double_start(self, mock_keyboard):
        """Testa que start duplo e ignorado."""
        mock_listener_instance = MagicMock()
        mock_keyboard.Listener.return_value = mock_listener_instance

        listener = HotkeyListener(hotkey="ctrl+m")
        listener.start()
        listener.start()  # Segunda chamada deve ser ignorada

        # Listener deve ser criado apenas uma vez
        assert mock_keyboard.Listener.call_count == 1
