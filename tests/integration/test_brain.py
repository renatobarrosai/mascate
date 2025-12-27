"""Testes de integração para o Cérebro (Brain)."""

from unittest.mock import MagicMock

from mascate.intelligence.brain import Brain, Intent
from mascate.intelligence.rag.retriever import SearchResult


def test_brain_process_flow():
    """Testa o fluxo completo: Input -> RAG -> LLM -> Intent."""
    # 1. Mock Retriever
    retriever = MagicMock()
    retriever.search.return_value = [
        SearchResult(content="Doc 1", source="manual.md", score=0.9, metadata={})
    ]
    retriever.format_context.return_value = "<doc>Doc 1</doc>"

    # 2. Mock LLM
    llm = MagicMock()
    # Simula resposta JSON válida
    llm.generate.return_value = (
        '{"action": "open_app", "target": "firefox", "params": {"new_window": true}}'
    )

    # 3. Inicializa Brain
    brain = Brain(llm, retriever)

    # 4. Processa input
    intent = brain.process("abra o firefox")

    # 5. Validações
    assert isinstance(intent, Intent)
    assert intent.action == "open_app"
    assert intent.target == "firefox"
    assert intent.params["new_window"] is True

    # Verifica chamadas
    retriever.search.assert_called_with("abra o firefox", top_k=3)
    llm.generate.assert_called_once()

    # Verifica se contexto foi passado pro LLM
    call_kwargs = llm.generate.call_args[1]
    assert call_kwargs["context"] == "<doc>Doc 1</doc>"
    assert call_kwargs["user_input"] == "abra o firefox"


def test_brain_invalid_json():
    """Testa comportamento quando LLM falha em gerar JSON válido."""
    retriever = MagicMock()
    retriever.search.return_value = []
    retriever.format_context.return_value = ""

    llm = MagicMock()
    # Simula JSON quebrado (embora GBNF devesse prevenir, pode ocorrer <endoftext> prematuro)
    llm.generate.return_value = '{"action": "open_app", "target": "fire'

    brain = Brain(llm, retriever)
    intent = brain.process("abra")

    assert intent is None


def test_brain_missing_fields():
    """Testa comportamento quando JSON falta campos obrigatórios."""
    retriever = MagicMock()
    llm = MagicMock()
    # Falta 'action'
    llm.generate.return_value = '{"target": "firefox"}'

    brain = Brain(llm, retriever)
    intent = brain.process("abra")

    assert intent is None
