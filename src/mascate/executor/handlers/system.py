"""Handler de operacoes de sistema para o Mascate.

Gerencia operacoes de sistema como volume, brilho, energia, etc.
"""

from __future__ import annotations

import logging
import subprocess

from mascate.executor.handlers.base import BaseHandler
from mascate.executor.models import ActionType, Command

logger = logging.getLogger(__name__)


class SystemHandler(BaseHandler):
    """Executa operacoes de sistema de forma segura."""

    @property
    def supported_actions(self) -> list[ActionType]:
        """Retorna as acoes suportadas por este handler."""
        return [ActionType.SYSTEM_OP]

    def execute(self, command: Command) -> bool:
        """Executa a operacao de sistema.

        Args:
            command: Comando com target sendo a operacao e params com detalhes.

        Returns:
            True se executado com sucesso.
        """
        operation = command.target.lower()

        logger.info("SystemHandler executando operacao: %s", operation)

        try:
            if operation in ("volume", "vol"):
                return self._handle_volume(command.params)
            elif operation in ("brightness", "brilho"):
                return self._handle_brightness(command.params)
            elif operation in ("shutdown", "desligar"):
                return self._handle_power("shutdown")
            elif operation in ("reboot", "reiniciar"):
                return self._handle_power("reboot")
            elif operation in ("suspend", "suspender", "sleep", "dormir"):
                return self._handle_power("suspend")
            elif operation in ("lock", "bloquear"):
                return self._lock_screen()
            elif operation in ("wifi"):
                return self._handle_wifi(command.params)
            elif operation in ("bluetooth", "bt"):
                return self._handle_bluetooth(command.params)
            elif operation in ("notification", "notify", "notificar"):
                return self._send_notification(command.params)
            else:
                logger.warning("Operacao de sistema desconhecida: %s", operation)
                return False
        except Exception as e:
            logger.error("Erro na operacao de sistema '%s': %s", operation, e)
            return False

    def _handle_volume(self, params: dict) -> bool:
        """Controla o volume do sistema.

        Args:
            params: Deve conter 'action' (up/down/mute/unmute/set) e opcionalmente 'value'.

        Returns:
            True se executado com sucesso.
        """
        action = params.get("action", "get")
        value = params.get("value", 5)  # Default: 5%

        try:
            if action == "up":
                subprocess.run(
                    ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{value}%"],
                    check=True,
                    capture_output=True,
                )
            elif action == "down":
                subprocess.run(
                    ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"-{value}%"],
                    check=True,
                    capture_output=True,
                )
            elif action == "mute":
                subprocess.run(
                    ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"],
                    check=True,
                    capture_output=True,
                )
            elif action == "unmute":
                subprocess.run(
                    ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"],
                    check=True,
                    capture_output=True,
                )
            elif action == "toggle":
                subprocess.run(
                    ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
                    check=True,
                    capture_output=True,
                )
            elif action == "set":
                subprocess.run(
                    ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"],
                    check=True,
                    capture_output=True,
                )
            else:
                logger.warning("Acao de volume desconhecida: %s", action)
                return False

            logger.info("Volume: %s (value=%s)", action, value)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Falha ao controlar volume: %s", e)
            return False

    def _handle_brightness(self, params: dict) -> bool:
        """Controla o brilho da tela.

        Args:
            params: Deve conter 'action' (up/down/set) e opcionalmente 'value'.

        Returns:
            True se executado com sucesso.
        """
        action = params.get("action", "get")
        value = params.get("value", 10)  # Default: 10%

        try:
            if action == "up":
                subprocess.run(
                    ["brightnessctl", "set", f"+{value}%"],
                    check=True,
                    capture_output=True,
                )
            elif action == "down":
                subprocess.run(
                    ["brightnessctl", "set", f"{value}%-"],
                    check=True,
                    capture_output=True,
                )
            elif action == "set":
                subprocess.run(
                    ["brightnessctl", "set", f"{value}%"],
                    check=True,
                    capture_output=True,
                )
            else:
                logger.warning("Acao de brilho desconhecida: %s", action)
                return False

            logger.info("Brilho: %s (value=%s)", action, value)
            return True
        except FileNotFoundError:
            logger.error(
                "brightnessctl nao encontrado. Instale com: sudo apt install brightnessctl"
            )
            return False
        except subprocess.CalledProcessError as e:
            logger.error("Falha ao controlar brilho: %s", e)
            return False

    def _handle_power(self, action: str) -> bool:
        """Gerencia acoes de energia (REQUER CONFIRMACAO).

        Args:
            action: shutdown, reboot, ou suspend.

        Returns:
            True se o comando foi iniciado.
        """
        try:
            if action == "shutdown":
                subprocess.run(["systemctl", "poweroff"], check=True)
            elif action == "reboot":
                subprocess.run(["systemctl", "reboot"], check=True)
            elif action == "suspend":
                subprocess.run(["systemctl", "suspend"], check=True)
            else:
                return False

            logger.info("Acao de energia executada: %s", action)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Falha na acao de energia: %s", e)
            return False

    def _lock_screen(self) -> bool:
        """Bloqueia a tela.

        Returns:
            True se bloqueado com sucesso.
        """
        try:
            # Tenta diferentes metodos de bloqueio
            commands = [
                ["loginctl", "lock-session"],
                ["gnome-screensaver-command", "-l"],
                ["xdg-screensaver", "lock"],
            ]

            for cmd in commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    logger.info("Tela bloqueada via: %s", cmd[0])
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            logger.error("Nenhum metodo de bloqueio disponivel")
            return False
        except Exception as e:
            logger.error("Falha ao bloquear tela: %s", e)
            return False

    def _handle_wifi(self, params: dict) -> bool:
        """Controla o WiFi.

        Args:
            params: Deve conter 'action' (on/off/toggle).

        Returns:
            True se executado com sucesso.
        """
        action = params.get("action", "toggle")

        try:
            if action == "on":
                subprocess.run(
                    ["nmcli", "radio", "wifi", "on"], check=True, capture_output=True
                )
            elif action == "off":
                subprocess.run(
                    ["nmcli", "radio", "wifi", "off"], check=True, capture_output=True
                )
            elif action == "toggle":
                # Verifica estado atual
                result = subprocess.run(
                    ["nmcli", "radio", "wifi"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                current = result.stdout.strip()
                new_state = "off" if current == "enabled" else "on"
                subprocess.run(
                    ["nmcli", "radio", "wifi", new_state],
                    check=True,
                    capture_output=True,
                )
            else:
                return False

            logger.info("WiFi: %s", action)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Falha ao controlar WiFi: %s", e)
            return False

    def _handle_bluetooth(self, params: dict) -> bool:
        """Controla o Bluetooth.

        Args:
            params: Deve conter 'action' (on/off/toggle).

        Returns:
            True se executado com sucesso.
        """
        action = params.get("action", "toggle")

        try:
            if action == "on":
                subprocess.run(
                    ["bluetoothctl", "power", "on"], check=True, capture_output=True
                )
            elif action == "off":
                subprocess.run(
                    ["bluetoothctl", "power", "off"], check=True, capture_output=True
                )
            elif action == "toggle":
                # Verifica estado atual via rfkill
                result = subprocess.run(
                    ["rfkill", "list", "bluetooth"],
                    capture_output=True,
                    text=True,
                )
                is_blocked = "Soft blocked: yes" in result.stdout
                new_state = "on" if is_blocked else "off"
                subprocess.run(
                    ["bluetoothctl", "power", new_state],
                    check=True,
                    capture_output=True,
                )
            else:
                return False

            logger.info("Bluetooth: %s", action)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Falha ao controlar Bluetooth: %s", e)
            return False

    def _send_notification(self, params: dict) -> bool:
        """Envia uma notificacao do sistema.

        Args:
            params: Deve conter 'title' e 'body'.

        Returns:
            True se enviado com sucesso.
        """
        title = params.get("title", "Mascate")
        body = params.get("body", "")
        urgency = params.get("urgency", "normal")  # low, normal, critical

        try:
            subprocess.run(
                ["notify-send", "-u", urgency, title, body],
                check=True,
                capture_output=True,
            )
            logger.info("Notificacao enviada: %s", title)
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Falha ao enviar notificacao: %s", e)
            return False
