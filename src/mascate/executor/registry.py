"""Registro central de Handlers do Mascate."""

from __future__ import annotations

from mascate.executor.handlers.app import AppHandler
from mascate.executor.handlers.base import BaseHandler
from mascate.executor.handlers.browser import BrowserHandler
from mascate.executor.handlers.file import FileHandler
from mascate.executor.handlers.media import MediaHandler
from mascate.executor.handlers.system import SystemHandler
from mascate.executor.models import ActionType

HANDLERS: dict[ActionType, type[BaseHandler]] = {
    ActionType.OPEN_APP: AppHandler,
    ActionType.OPEN_URL: BrowserHandler,
    ActionType.MEDIA_CONTROL: MediaHandler,
    ActionType.FILE_OP: FileHandler,
    ActionType.SYSTEM_OP: SystemHandler,
}


def get_handler(action: ActionType) -> BaseHandler | None:
    """Obtém uma instância do handler para a ação.

    Args:
        action: Tipo de ação.

    Returns:
        Instância do handler ou None se não encontrado.
    """
    handler_class = HANDLERS.get(action)
    if handler_class:
        return handler_class()
    return None
