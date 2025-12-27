"""Testes unitários para o Retriever."""

from dataclasses import dataclass
from unittest.mock import patch

from mascate.intelligence.rag.retriever import RAGRetriever, SearchResult


@dataclass
class MockScoredPoint:
    score: float
    payload: dict


@patch("mascate.intelligence.rag.knowledge.KnowledgeBase")
def test_retriever_initialization(MockKB):
    """Verifica se o retriever cria índice de texto."""
    kb = MockKB()
    kb.COLLECTION_NAME = "test_coll"

    RAGRetriever(kb)

    kb.vectordb.client.create_payload_index.assert_called_with(
        collection_name="test_coll", field_name="content", field_schema="text"
    )


@patch("mascate.intelligence.rag.knowledge.KnowledgeBase")
def test_dense_search(MockKB):
    """Verifica se a busca densa é executada e formatada."""
    kb = MockKB()
    kb.COLLECTION_NAME = "test_coll"

    # Mock do embedding
    kb.embedding_model.encode.return_value = [0.1, 0.2]

    # Mock do Qdrant search
    kb.vectordb.search.return_value = [
        MockScoredPoint(score=0.9, payload={"content": "Texto 1", "source": "doc1"}),
        MockScoredPoint(score=0.8, payload={"content": "Texto 2", "source": "doc2"}),
    ]

    retriever = RAGRetriever(kb)
    results = retriever.search("query teste", top_k=2)

    assert len(results) == 2
    assert results[0].content == "Texto 1"
    assert results[0].score == 0.9

    kb.vectordb.search.assert_called_once()


@patch("mascate.intelligence.rag.knowledge.KnowledgeBase")
def test_format_context(MockKB):
    """Verifica formatação do contexto para LLM."""
    retriever = RAGRetriever(MockKB())

    results = [
        SearchResult(content="Info A", source="docA", score=0.9, metadata={}),
        SearchResult(content="Info B", source="docB", score=0.8, metadata={}),
    ]

    context = retriever.format_context(results)

    assert "<doc id='1' source='docA'>" in context
    assert "Info A" in context
    assert "<doc id='2' source='docB'>" in context
    assert "Info B" in context


@patch("mascate.intelligence.rag.knowledge.KnowledgeBase")
def test_format_context_empty(MockKB):
    """Verifica formatação sem resultados."""
    retriever = RAGRetriever(MockKB())
    context = retriever.format_context([])
    assert "Nenhuma informacao relevante" in context
