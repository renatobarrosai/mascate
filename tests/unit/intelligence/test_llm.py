"""Testes unitários para o LLM Wrapper."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mascate.intelligence.llm.granite import GraniteLLM, LLMError


@patch("mascate.intelligence.llm.granite.Llama")
@patch("mascate.intelligence.llm.granite.LlamaGrammar")
def test_llm_initialization(MockGrammar, MockLlama):
    """Verifica inicialização do Llama."""
    # Mock file exists
    with patch.object(Path, "exists", return_value=True):
        llm = GraniteLLM(model_path="model.gguf")
        MockLlama.assert_called_once()
        assert llm.model_path.name == "model.gguf"


def test_llm_model_not_found():
    """Verifica erro se modelo não existe."""
    with patch.object(Path, "exists", return_value=False), pytest.raises(LLMError):
        GraniteLLM(model_path="ghost.gguf")


@patch("mascate.intelligence.llm.granite.Llama")
@patch("mascate.intelligence.llm.granite.LlamaGrammar")
def test_generate_simple(MockGrammar, MockLlama):
    """Verifica chamada de geração padrão."""
    mock_instance = MagicMock()
    mock_instance.return_value = {"choices": [{"text": '{"action": "test"}'}]}
    MockLlama.return_value = mock_instance

    with patch.object(Path, "exists", return_value=True):
        # Mock grammar loading to avoid file read
        with patch(
            "mascate.intelligence.llm.granite.GrammarLoader.load",
            return_value="root ::= ...",
        ):
            llm = GraniteLLM(model_path="model.gguf")
            response = llm.generate("Hello")

            assert response == '{"action": "test"}'
            mock_instance.assert_called_once()

            # Verifica se prompt contem input
            call_args = mock_instance.call_args
            prompt_sent = call_args[0][0]
            assert "Hello" in prompt_sent
            assert "<|system|>" in prompt_sent


@patch("mascate.intelligence.llm.granite.Llama")
@patch("mascate.intelligence.llm.granite.LlamaGrammar")
def test_generate_streaming(MockGrammar, MockLlama):
    """Verifica geração via streaming."""
    mock_instance = MagicMock()
    # Simula gerador
    mock_instance.return_value = iter(
        [{"choices": [{"text": "{"}]}, {"choices": [{"text": "}"}]}]
    )
    MockLlama.return_value = mock_instance

    with patch.object(Path, "exists", return_value=True), patch(
        "mascate.intelligence.llm.granite.GrammarLoader.load",
        return_value="root ::= ...",
    ):
        llm = GraniteLLM(model_path="model.gguf")
        generator = llm.generate("Hello", stream=True)

        result = list(generator)
        assert result == ["{", "}"]


@patch("mascate.intelligence.llm.granite.Llama", None)
def test_llm_import_error():
    """Verifica erro se biblioteca não instalada."""
    with pytest.raises(LLMError, match="llama-cpp-python nao instalado"):
        GraniteLLM(model_path="model.gguf")
