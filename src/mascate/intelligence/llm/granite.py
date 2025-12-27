"""Wrapper para o LLM IBM Granite via llama.cpp.

Gerencia o carregamento do modelo na GPU e a geracao de respostas JSON.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

try:
    from llama_cpp import Llama, LlamaGrammar
except ImportError:
    Llama = None
    LlamaGrammar = None

from mascate.core.exceptions import MascateError
from mascate.intelligence.llm.grammar import GrammarLoader
from mascate.intelligence.llm.prompts import (
    ASSISTANT_TEMPLATE,
    SYSTEM_PROMPT,
    USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class LLMError(MascateError):
    """Erro relacionado ao LLM."""


class GraniteLLM:
    """Interface para o modelo Granite."""

    def __init__(
        self,
        model_path: str | Path,
        n_gpu_layers: int = -1,
        n_ctx: int = 4096,
        n_threads: int = 4,
        verbose: bool = False,
    ) -> None:
        """Inicializa o LLM.

        Args:
            model_path: Caminho para o arquivo GGUF.
            n_gpu_layers: Camadas na GPU (-1 = todas).
            n_ctx: Tamanho do contexto.
            n_threads: Threads de CPU (se nao usar GPU total).
            verbose: Logs do llama.cpp.
        """
        if Llama is None:
            raise LLMError(
                "llama-cpp-python nao instalado. "
                "Instale com 'uv pip install llama-cpp-python' (com args CMAKE para GPU)."
            )

        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise LLMError(f"Modelo LLM nao encontrado: {model_path}")

        try:
            self.llm = Llama(
                model_path=str(self.model_path),
                n_gpu_layers=n_gpu_layers,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=verbose,
            )
            self.grammar_loader = GrammarLoader()
            logger.info("Granite LLM carregado: %s", self.model_path)
        except Exception as e:
            logger.error("Falha ao carregar LLM: %s", e)
            raise LLMError(f"Erro inicializacao LLM: {e}") from e

    def generate(
        self,
        user_input: str,
        context: str = "",
        grammar_name: str = "command",
        temperature: float = 0.1,
        max_tokens: int = 256,
        stream: bool = False,
    ) -> str | Iterator[str]:
        """Gera resposta para o input do usuario.

        Args:
            user_input: Texto do usuario.
            context: Contexto recuperado do RAG (formatado).
            grammar_name: Nome do arquivo GBNF para forcar JSON.
            temperature: Criatividade (baixo para comandos).
            max_tokens: Limite de saida.
            stream: Se True, retorna iterador de strings.

        Returns:
            JSON string ou iterador.
        """
        # Constroi prompt
        prompt = (
            SYSTEM_PROMPT
            + USER_TEMPLATE.format(context=context, user_input=user_input)
            + ASSISTANT_TEMPLATE
        )

        # Carrega gramatica
        try:
            gbnf_content = self.grammar_loader.load(grammar_name)
            grammar = LlamaGrammar.from_string(gbnf_content)
        except Exception as e:
            logger.error("Erro ao carregar gramatica %s: %s", grammar_name, e)
            # Fallback sem gramatica se falhar (arriscado, mas evita crash)
            grammar = None

        if stream:
            return self._stream_generation(prompt, grammar, temperature, max_tokens)

        try:
            output = self.llm(
                prompt,
                grammar=grammar,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=["<|endoftext|>"],
                echo=False,
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            logger.error("Erro na geracao LLM: %s", e)
            return "{}"

    def _stream_generation(
        self, prompt: str, grammar: Any, temperature: float, max_tokens: int
    ) -> Iterator[str]:
        """Gerador para streaming de tokens."""
        try:
            stream = self.llm(
                prompt,
                grammar=grammar,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=["<|endoftext|>"],
                stream=True,
                echo=False,
            )
            for chunk in stream:
                delta = chunk["choices"][0]["text"]
                yield delta
        except Exception as e:
            logger.error("Erro no streaming LLM: %s", e)
            yield ""
