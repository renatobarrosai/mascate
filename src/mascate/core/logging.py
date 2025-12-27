"""Sistema de logging do Mascate.

Configura logging estruturado com suporte a Rich para output colorido.
"""

from __future__ import annotations

import logging
import sys

# Formato padrao de log
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: int = logging.INFO,
    use_rich: bool = True,
) -> logging.Logger:
    """Configura o sistema de logging.

    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        use_rich: Se True, usa Rich para output colorido.

    Returns:
        Logger principal configurado.
    """
    logger = logging.getLogger("mascate")
    logger.setLevel(level)

    # Remove handlers existentes
    logger.handlers.clear()

    if use_rich:
        try:
            from rich.logging import RichHandler

            handler = RichHandler(
                rich_tracebacks=True,
                show_time=True,
                show_path=True,
            )
            handler.setFormatter(logging.Formatter("%(message)s"))
        except ImportError:
            # Fallback para handler padrao
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))

    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Obtem um logger filho do logger principal.

    Args:
        name: Nome do modulo (ex: 'audio.stt', 'intelligence.llm').

    Returns:
        Logger configurado para o modulo.
    """
    return logging.getLogger(f"mascate.{name}")
