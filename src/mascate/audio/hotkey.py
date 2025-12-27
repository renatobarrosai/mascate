"""Listener de atalho de teclado para ativacao do Mascate.

Alternativa ao Wake Word para ativacao via hotkey global.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pynput.keyboard import Key, KeyCode

try:
    from pynput import keyboard
except ImportError:
    keyboard = None  # type: ignore[assignment]

from mascate.core.exceptions import MascateError

logger = logging.getLogger(__name__)


class HotkeyError(MascateError):
    """Erro relacionado ao listener de hotkey."""


# Mapeamento de nomes de teclas para objetos Key do pynput
KEY_NAMES: dict[str, str] = {
    "ctrl": "ctrl",
    "control": "ctrl",
    "alt": "alt",
    "shift": "shift",
    "super": "cmd",
    "win": "cmd",
    "meta": "cmd",
    "cmd": "cmd",
    "space": "space",
    "enter": "enter",
    "return": "enter",
    "tab": "tab",
    "esc": "esc",
    "escape": "esc",
    "f1": "f1",
    "f2": "f2",
    "f3": "f3",
    "f4": "f4",
    "f5": "f5",
    "f6": "f6",
    "f7": "f7",
    "f8": "f8",
    "f9": "f9",
    "f10": "f10",
    "f11": "f11",
    "f12": "f12",
}


def parse_hotkey(hotkey_str: str) -> set[str]:
    """Converte string de hotkey para conjunto de teclas.

    Args:
        hotkey_str: String no formato "ctrl+shift+m" ou "super+space".

    Returns:
        Conjunto de nomes de teclas normalizados.

    Raises:
        HotkeyError: Se a string de hotkey for invalida.
    """
    if not hotkey_str:
        raise HotkeyError("Hotkey string cannot be empty")

    parts = hotkey_str.lower().replace(" ", "").split("+")
    keys: set[str] = set()

    for part in parts:
        if not part:
            continue

        # Verifica se e uma tecla especial conhecida
        if part in KEY_NAMES:
            keys.add(KEY_NAMES[part])
        elif len(part) == 1:
            # Tecla de caractere simples (a-z, 0-9)
            keys.add(part)
        else:
            # Tenta usar como esta (pode ser tecla especial do pynput)
            keys.add(part)

    if not keys:
        raise HotkeyError(f"No valid keys found in hotkey: {hotkey_str}")

    return keys


class HotkeyListener:
    """Listener de hotkey global para ativacao do sistema."""

    def __init__(
        self,
        hotkey: str = "ctrl+shift+m",
        on_activate: Callable[[], None] | None = None,
    ) -> None:
        """Inicializa o listener de hotkey.

        Args:
            hotkey: String de hotkey no formato "ctrl+shift+m".
            on_activate: Callback chamado quando a hotkey e pressionada.

        Raises:
            HotkeyError: Se pynput nao estiver instalado.
        """
        if keyboard is None:
            raise HotkeyError(
                "pynput nao esta instalado. Instale com 'uv pip install pynput'."
            )

        self.hotkey_str = hotkey
        self.target_keys = parse_hotkey(hotkey)
        self._on_activate = on_activate
        self._pressed_keys: set[str] = set()
        self._listener: keyboard.Listener | None = None
        self._running = False
        self._lock = threading.Lock()

        logger.info("HotkeyListener configurado: %s", hotkey)

    def on_activate(self, callback: Callable[[], None]) -> None:
        """Define o callback de ativacao.

        Args:
            callback: Funcao chamada quando a hotkey e pressionada.
        """
        self._on_activate = callback

    def start(self) -> None:
        """Inicia o listener de hotkey em background."""
        if self._running:
            return

        self._running = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()
        logger.info("HotkeyListener iniciado (aguardando %s)", self.hotkey_str)

    def stop(self) -> None:
        """Para o listener de hotkey."""
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None
        logger.info("HotkeyListener parado")

    def _normalize_key(self, key: Key | KeyCode | None) -> str | None:
        """Normaliza uma tecla para string comparavel.

        Args:
            key: Objeto de tecla do pynput.

        Returns:
            String normalizada da tecla ou None.
        """
        if key is None:
            return None

        # Teclas especiais (Key.ctrl, Key.alt, etc.)
        if hasattr(key, "name"):
            name = key.name.lower()
            # Normaliza variantes (ctrl_l, ctrl_r -> ctrl)
            if name.startswith("ctrl"):
                return "ctrl"
            if name.startswith("alt"):
                return "alt"
            if name.startswith("shift"):
                return "shift"
            if name in ("cmd", "cmd_l", "cmd_r", "super", "super_l", "super_r"):
                return "cmd"
            return name

        # Teclas de caractere (KeyCode)
        if hasattr(key, "char") and key.char:
            return key.char.lower()

        # Teclas com vk (virtual key code)
        if hasattr(key, "vk") and key.vk:
            return str(key.vk)

        return None

    def _on_press(self, key: Key | KeyCode | None) -> None:
        """Handler de tecla pressionada.

        Args:
            key: Tecla pressionada.
        """
        normalized = self._normalize_key(key)
        if normalized is None:
            return

        with self._lock:
            self._pressed_keys.add(normalized)

            # Verifica se todas as teclas do hotkey estao pressionadas
            if self.target_keys.issubset(self._pressed_keys):
                logger.info("Hotkey detectada: %s", self.hotkey_str)
                if self._on_activate:
                    # Executa callback em thread separada para nao bloquear
                    threading.Thread(target=self._on_activate, daemon=True).start()

    def _on_release(self, key: Key | KeyCode | None) -> None:
        """Handler de tecla liberada.

        Args:
            key: Tecla liberada.
        """
        normalized = self._normalize_key(key)
        if normalized is None:
            return

        with self._lock:
            self._pressed_keys.discard(normalized)

    @property
    def is_running(self) -> bool:
        """Retorna se o listener esta ativo."""
        return self._running
