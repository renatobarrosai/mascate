"""Handlers de comandos especificos."""

from __future__ import annotations

from mascate.executor.handlers.app import AppHandler
from mascate.executor.handlers.base import BaseHandler
from mascate.executor.handlers.browser import BrowserHandler
from mascate.executor.handlers.file import FileHandler
from mascate.executor.handlers.media import MediaHandler
from mascate.executor.handlers.system import SystemHandler

__all__ = [
    "AppHandler",
    "BaseHandler",
    "BrowserHandler",
    "FileHandler",
    "MediaHandler",
    "SystemHandler",
]
