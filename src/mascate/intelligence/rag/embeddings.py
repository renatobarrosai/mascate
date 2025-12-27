"""Gerador de Embeddings para o RAG.

Utiliza BGE-M3 (via sentence-transformers) para converter texto em vetores.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from mascate.core.exceptions import MascateError

logger = logging.getLogger(__name__)


class EmbeddingError(MascateError):
    """Erro relacionado a geracao de embeddings."""


class EmbeddingModel:
    """Wrapper para modelo de embedding (BGE-M3)."""

    def __init__(self, model_name: str = "BAAI/bge-m3", device: str = "cpu") -> None:
        """Inicializa o modelo de embedding.

        Args:
            model_name: ID do modelo no Hugging Face.
            device: 'cpu' ou 'cuda'.

        Raises:
            EmbeddingError: Se sentence-transformers nao estiver instalado.
        """
        if SentenceTransformer is None:
            raise EmbeddingError(
                "sentence-transformers nao instalado. "
                "Instale com 'uv pip install sentence-transformers'."
            )

        self.model_name = model_name
        self.device = device
        self.model: Any = None

        try:
            # Carrega modelo. Para BGE-M3, trust_remote_code=False geralmente funciona,
            # mas alguns modelos recentes exigem True. O padrao BAAI/bge-m3 é seguro.
            self.model = SentenceTransformer(model_name, device=device)
            logger.info("Modelo de embedding carregado: %s (%s)", model_name, device)
        except Exception as e:
            logger.error("Falha ao carregar modelo de embedding: %s", e)
            raise EmbeddingError(f"Erro no modelo {model_name}: {e}") from e

    def encode(self, texts: str | list[str]) -> np.ndarray:
        """Gera vetores para o texto fornecido.

        Args:
            texts: String unica ou lista de strings.

        Returns:
            Array numpy com os embeddings.
        """
        if self.model is None:
            raise EmbeddingError("Modelo nao inicializado")

        try:
            # BGE-M3 recomenda instrucoes para queries em retrieval tasks,
            # mas para documentos raw nao precisa.
            # Aqui simplificamos usando encode direto.
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            return embeddings
        except Exception as e:
            logger.error("Erro ao gerar embedding: %s", e)
            raise EmbeddingError(f"Falha no encode: {e}") from e

    @property
    def embedding_size(self) -> int:
        """Retorna a dimensao do vetor (ex: 1024 para BGE-M3)."""
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 0
