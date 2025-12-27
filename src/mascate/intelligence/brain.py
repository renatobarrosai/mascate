"""Cérebro do Mascate.

Orquestra RAG e LLM para transformar intenção do usuário em comandos estruturados.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from mascate.intelligence.llm.granite import GraniteLLM
from mascate.intelligence.rag.retriever import RAGRetriever

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Intenção estruturada extraída do LLM."""

    action: str
    target: str
    params: dict[str, Any]
    raw_json: str


class Brain:
    """O Cérebro do sistema."""

    def __init__(self, llm: GraniteLLM, retriever: RAGRetriever) -> None:
        """Inicializa o cérebro.

        Args:
            llm: Instância do GraniteLLM.
            retriever: Instância do RAGRetriever.
        """
        self.llm = llm
        self.retriever = retriever

    def process(self, user_input: str) -> Intent | None:
        """Processa a entrada do usuário e retorna uma intenção.

        Args:
            user_input: Texto falado pelo usuário.

        Returns:
            Objeto Intent ou None se falhar.
        """
        logger.info("Processando input: '%s'", user_input)

        # 1. Recupera contexto relevante (RAG)
        # Busca documentos que ajudem a entender comandos ou procedimentos
        search_results = self.retriever.search(user_input, top_k=3)
        context = self.retriever.format_context(search_results)

        logger.debug("Contexto recuperado: %d documentos", len(search_results))

        # 2. Gera resposta estruturada (LLM + GBNF)
        # O prompt e a gramática forçam a saída JSON
        json_output = self.llm.generate(
            user_input=user_input,
            context=context,
            grammar_name="command",
            temperature=0.1,  # Baixa criatividade para precisão
        )

        # 3. Faz parsing e validação básica
        if isinstance(json_output, str):
            return self._parse_response(json_output)

        # Se for iterator (streaming), teríamos que acumular.
        # O método generate padrão já retorna string completa.
        return None

    def _parse_response(self, json_str: str) -> Intent | None:
        """Converte string JSON em objeto Intent."""
        try:
            data = json.loads(json_str)

            # Validação básica de schema (já garantida pelo GBNF, mas bom checar)
            action = data.get("action")
            target = data.get("target")

            if not action:
                logger.warning("JSON gerado sem campo 'action': %s", json_str)
                return None

            return Intent(
                action=action,
                target=target or "",
                params=data.get("params", {}),
                raw_json=json_str,
            )
        except json.JSONDecodeError as e:
            logger.error("LLM gerou JSON inválido: %s. Erro: %s", json_str, e)
            return None
        except Exception as e:
            logger.error("Erro ao processar resposta do LLM: %s", e)
            return None
