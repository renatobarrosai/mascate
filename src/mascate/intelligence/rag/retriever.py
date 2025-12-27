"""Retriever RAG (Busca Hibrida).

Recupera documentos relevantes usando busca vetorial (densa) e keywords.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from mascate.intelligence.rag.knowledge import KnowledgeBase

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Resultado de busca unificado."""

    content: str
    source: str
    score: float
    metadata: dict


class RAGRetriever:
    """Recupera informacao da Knowledge Base."""

    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        """Inicializa o retriever.

        Args:
            knowledge_base: Instancia da KB populada.
        """
        self.kb = knowledge_base

        # Garante indice de texto para busca esparsa (keyword match)
        try:
            self.kb.vectordb.client.create_payload_index(
                collection_name=self.kb.COLLECTION_NAME,
                field_name="content",
                field_schema="text",
            )
            logger.info("Indice de texto criado para campo 'content'")
        except Exception as e:
            # Pode falhar se ja existir ou se for :memory: sem suporte persistente complexo
            logger.debug("Aviso ao criar indice de texto: %s", e)

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        """Busca hibrida (Densa + Keyword).

        Args:
            query: Pergunta do usuario.
            top_k: Numero de resultados finais.

        Returns:
            Lista de SearchResult ordenada por relevancia.
        """
        # 1. Busca Densa (Semantica)
        dense_results = self._search_dense(query, limit=top_k * 2)

        # 2. Busca Esparsa (Keyword/Texto) - Simplificada via Qdrant Scroll/Filter
        # Nota: Qdrant local nao tem um endpoint de "search text" puro rankeado como BM25 nativo exposto facilmente
        # sem plugins, mas podemos confiar na busca vetorial como primaria e boostar com keywords se necessario.
        # Para esta PoC, vamos focar na busca Densa que ja é muito forte com BGE-M3.
        # Se precisarmos de keyword exata, filtramos os dense results.

        # Por enquanto, retornamos os resultados densos convertidos
        results = []
        for res in dense_results:
            if not res.payload:
                continue

            results.append(
                SearchResult(
                    content=res.payload.get("content", ""),
                    source=res.payload.get("source", "unknown"),
                    score=res.score,
                    metadata=res.payload,
                )
            )

        return results[:top_k]

    def _search_dense(self, query: str, limit: int) -> list:
        """Executa busca vetorial."""
        vector = self.kb.embedding_model.encode(query)
        if hasattr(vector, "tolist"):
            vector = vector.tolist()

        return self.kb.vectordb.search(
            collection_name=self.kb.COLLECTION_NAME,
            query_vector=vector,  # type: ignore
            limit=limit,
            score_threshold=0.3,  # Filtra lixo irrelevante
        )

    def format_context(self, results: list[SearchResult]) -> str:
        """Formata resultados para o prompt do LLM.

        Args:
            results: Lista de resultados.

        Returns:
            String formatada com XML tags ou similar.
        """
        if not results:
            return "Nenhuma informacao relevante encontrada."

        context_parts = []
        for i, res in enumerate(results, 1):
            context_parts.append(
                f"<doc id='{i}' source='{res.source}'>\n{res.content}\n</doc>"
            )

        return "\n\n".join(context_parts)
