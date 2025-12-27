"""Loader de gramáticas GBNF.

Gerencia o carregamento de arquivos GBNF para o LLM.
"""

from __future__ import annotations

import logging
from pathlib import Path

from mascate.core.exceptions import MascateError

logger = logging.getLogger(__name__)


class GrammarError(MascateError):
    """Erro relacionado a gramáticas."""


class GrammarLoader:
    """Carregador de gramáticas GBNF."""

    def __init__(self, grammar_dir: Path | None = None) -> None:
        """Inicializa o loader.

        Args:
            grammar_dir: Diretório contendo arquivos .gbnf.
                         Se None, usa o diretório local 'grammars'.
        """
        if grammar_dir is None:
            self.grammar_dir = Path(__file__).parent / "grammars"
        else:
            self.grammar_dir = grammar_dir

    def load(self, name: str) -> str:
        """Carrega o conteúdo de uma gramática.

        Args:
            name: Nome do arquivo (sem extensão .gbnf).

        Returns:
            Conteúdo do arquivo GBNF.

        Raises:
            GrammarError: Se o arquivo não for encontrado.
        """
        file_path = self.grammar_dir / f"{name}.gbnf"

        if not file_path.exists():
            raise GrammarError(
                f"Gramática '{name}' não encontrada em {self.grammar_dir}"
            )

        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise GrammarError(f"Erro ao ler gramática {name}: {e}") from e
