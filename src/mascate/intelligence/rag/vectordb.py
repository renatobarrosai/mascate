"""Interface para Banco de Dados Vetorial (Qdrant).

Gerencia conexao, criacao de collections e operacoes de CRUD.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
except ImportError:
    QdrantClient = None
    models = None

from mascate.core.exceptions import MascateError

logger = logging.getLogger(__name__)


class VectorDBError(MascateError):
    """Erro relacionado ao banco vetorial."""


class VectorDB:
    """Gerenciador do Qdrant."""

    def __init__(self, path: Path | str = ":memory:") -> None:
        """Inicializa conexao com Qdrant.

        Args:
            path: Caminho para persistencia em disco ou ':memory:'.
        """
        if QdrantClient is None:
            raise VectorDBError(
                "qdrant-client nao instalado. Instale com 'uv pip install qdrant-client'."
            )

        self.path = str(path)
        try:
            self.client = QdrantClient(path=self.path)
            logger.info("Qdrant inicializado em: %s", self.path)
        except Exception as e:
            logger.error("Falha ao iniciar Qdrant: %s", e)
            raise VectorDBError(f"Erro Qdrant: {e}") from e

    def ensure_collection(self, name: str, vector_size: int) -> None:
        """Garante que a collection exista com a configuracao correta.

        Args:
            name: Nome da collection.
            vector_size: Dimensao dos vetores (ex: 1024).
        """
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == name for c in collections)

            if not exists:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    ),
                )
                logger.info("Collection '%s' criada (size=%d)", name, vector_size)
        except Exception as e:
            raise VectorDBError(f"Falha ao criar collection {name}: {e}") from e

    def upsert(
        self,
        collection_name: str,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> None:
        """Insere ou atualiza vetores.

        Args:
            collection_name: Nome da collection.
            ids: Lista de IDs unicos (hash strings).
            vectors: Lista de vetores (embeddings).
            payloads: Metadados associados.
        """
        if len(ids) != len(vectors) or len(ids) != len(payloads):
            raise VectorDBError(
                "Listas de ids, vectors e payloads devem ter mesmo tamanho"
            )

        try:
            # Qdrant local suporta batch upsert
            self.client.upsert(
                collection_name=collection_name,
                points=models.Batch(
                    ids=ids,
                    vectors=vectors,
                    payloads=payloads,
                ),
            )
            logger.debug("Upsert de %d pontos em '%s'", len(ids), collection_name)
        except Exception as e:
            raise VectorDBError(f"Falha no upsert: {e}") from e

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: float = 0.0,
    ) -> list[models.ScoredPoint]:
        """Busca os vizinhos mais proximos.

        Args:
            collection_name: Nome da collection.
            query_vector: Vetor da query.
            limit: Numero maximo de resultados.
            score_threshold: Score minimo (cosseno similarity).

        Returns:
            Lista de ScoredPoint com payload e score.
        """
        try:
            return self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )
        except Exception as e:
            logger.error("Erro na busca: %s", e)
            return []
