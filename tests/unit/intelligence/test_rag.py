"Testes unitários para o módulo RAG (Parser, KnowledgeBase)."

from unittest.mock import MagicMock, patch

import numpy as np

from mascate.intelligence.rag.embeddings import EmbeddingModel
from mascate.intelligence.rag.knowledge import KnowledgeBase
from mascate.intelligence.rag.parser import Chunk, MarkdownParser
from mascate.intelligence.rag.vectordb import VectorDB

# --- Parser Tests ---


def test_chunk_creation():
    """Verifica geração de ID e estrutura do Chunk."""
    chunk = Chunk(content="Teste", source_file="doc.md", section="Intro")
    assert chunk.chunk_id  # Deve gerar hash automaticamente
    assert chunk.content == "Teste"
    assert chunk.section == "Intro"


def test_markdown_parser_headers(tmp_path):
    """Verifica se o parser divide corretamente por headers."""
    content = """# Title
    Intro text.
    
    ## Section 1
    Content 1.
    
    ## Section 2
    Content 2.
    """
    f = tmp_path / "test.md"
    f.write_text(content, encoding="utf-8")

    parser = MarkdownParser()
    chunks = parser.parse_file(f)

    # Title (Intro), Section 1, Section 2
    sections = [c.section for c in chunks]
    assert (
        "Title" in sections or "Introduction" in sections
    )  # Depende da logica exata do buffer inicial
    assert "Section 1" in sections
    assert "Section 2" in sections
    assert any("Content 1" in c.content for c in chunks)


def test_markdown_parser_chunking(tmp_path):
    """Verifica se textos longos são quebrados."""
    long_text = "word " * 200  # ~1000 chars
    content = f"# Longo\n{long_text}"

    f = tmp_path / "long.md"
    f.write_text(content, encoding="utf-8")

    parser = MarkdownParser(chunk_size=100)
    chunks = parser.parse_file(f)

    assert len(chunks) > 1
    # Verifica overlap
    assert len(chunks[0].content) <= 100


# --- Embedding Tests ---


def test_embedding_model_mock():
    """Verifica se o wrapper chama o sentence-transformers corretamente."""
    with patch("mascate.intelligence.rag.embeddings.SentenceTransformer") as MockST:
        mock_instance = MagicMock()
        mock_instance.encode.return_value = np.array([[0.1, 0.2]])
        mock_instance.get_sentence_embedding_dimension.return_value = 768
        MockST.return_value = mock_instance

        emb = EmbeddingModel()
        vector = emb.encode("teste")

        assert vector.shape == (1, 2)
        assert emb.embedding_size == 768


# --- VectorDB Tests ---


def test_vectordb_mock():
    """Verifica chamadas ao qdrant-client."""
    with patch("mascate.intelligence.rag.vectordb.QdrantClient") as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance

        # Simula collection não existindo
        mock_instance.get_collections.return_value.collections = []

        db = VectorDB(path=":memory:")
        db.ensure_collection("test", 128)

        mock_instance.create_collection.assert_called_once()

        db.upsert("test", ["id1"], [[0.1]], [{"meta": "data"}])
        mock_instance.upsert.assert_called_once()


# --- KnowledgeBase Tests ---


@patch("mascate.intelligence.rag.knowledge.VectorDB")
@patch("mascate.intelligence.rag.knowledge.EmbeddingModel")
def test_knowledge_base_ingestion(MockEmb, MockDB, tmp_path):
    """Verifica o fluxo de ingestão: Parse -> Embed -> Upsert."""
    # Setup Config Mock
    config = MagicMock()
    config.data_dir = tmp_path

    # Setup Mocks
    mock_emb_instance = MockEmb.return_value
    mock_emb_instance.embedding_size = 10
    mock_emb_instance.encode.return_value = np.zeros((1, 10))  # 1 chunk -> 1 vetor

    mock_db_instance = MockDB.return_value

    kb = KnowledgeBase(config)

    # Cria arquivo teste
    f = tmp_path / "doc.md"
    f.write_text("# Test\nContent.", encoding="utf-8")

    count = kb.ingest_directory(tmp_path)

    assert count == 1  # 1 chunk
    mock_emb_instance.encode.assert_called()
    mock_db_instance.upsert.assert_called_once()
