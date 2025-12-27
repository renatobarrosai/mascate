"""Base de Conhecimento (RAG Orchestrator).

Coordena Parser, Embeddings e VectorDB para ingestao de documentos.
"""

from __future__ import annotations

import logging
from pathlib import Path

from mascate.core.config import Config
from mascate.intelligence.rag.embeddings import EmbeddingModel
from mascate.intelligence.rag.parser import MarkdownParser
from mascate.intelligence.rag.vectordb import VectorDB

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Gerenciador da base de conhecimento."""

    COLLECTION_NAME = "mascate_knowledge"

    def __init__(self, config: Config) -> None:
        """Inicializa a Knowledge Base.

        Args:
            config: Configuracao global do sistema.
        """
        self.config = config

        # Inicializa componentes
        # Usa caminho persistente para o Qdrant
        qdrant_path = config.data_dir / "qdrant_db"
        self.vectordb = VectorDB(path=qdrant_path)

        self.embedding_model = EmbeddingModel(device="cpu")  # RAG roda na CPU
        self.parser = MarkdownParser()

        # Garante que a collection exista com o tamanho correto do embedding
        # BGE-M3 tem 1024 dimensoes
        self.vectordb.ensure_collection(
            self.COLLECTION_NAME, vector_size=self.embedding_model.embedding_size
        )

    def ingest_directory(self, dir_path: Path) -> int:
        """Processa todos os arquivos .md de um diretorio.

        Args:
            dir_path: Diretorio contendo arquivos Markdown.

        Returns:
            Numero total de chunks indexados.
        """
        if not dir_path.exists():
            logger.error("Diretorio nao encontrado: %s", dir_path)
            return 0

        files = list(dir_path.glob("**/*.md"))
        logger.info("Iniciando ingestao de %d arquivos em %s", len(files), dir_path)

        total_chunks = 0

        for file_path in files:
            chunks = self.parser.parse_file(file_path)
            if not chunks:
                continue

            # Prepara dados para batch insert
            texts = [c.content for c in chunks]

            # Gera embeddings (pode demorar)
            vectors = self.embedding_model.encode(texts)

            # Prepara IDs e Payloads
            # Qdrant requer UUIDs ou inteiros, mas suporta string hash como ID se cuidarmos disso
            # Vamos usar o chunk_id (hash MD5)
            ids = [c.chunk_id for c in chunks]

            payloads = []
            for c in chunks:
                payload = {
                    "content": c.content,
                    "source": c.source_file,
                    "section": c.section,
                }
                payload.update(c.metadata)
                payloads.append(payload)

            # Indexa no Qdrant
            # Converte vectors numpy para list[float]
            vectors_list = vectors.tolist()

            self.vectordb.upsert(
                collection_name=self.COLLECTION_NAME,
                ids=ids,
                vectors=vectors_list,
                payloads=payloads,
            )

            total_chunks += len(chunks)
            logger.debug("Arquivo %s indexado: %d chunks", file_path.name, len(chunks))

        logger.info("Ingestao concluida. Total de chunks: %d", total_chunks)
        return total_chunks

    def search(self, query: str, limit: int = 3) -> list[str]:
        """Busca simples para teste (retorna apenas conteudo).

        A busca real (hibrida) sera no modulo Retriever.
        """
        vector = self.embedding_model.encode(query)
        if hasattr(vector, "tolist"):
            vector = vector.tolist()  # type: ignore

        results = self.vectordb.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=vector,  # type: ignore
            limit=limit,
        )

        return [res.payload["content"] for res in results if res.payload]
