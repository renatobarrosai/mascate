"Testes unitários para o Grammar Loader."

import pytest

from mascate.intelligence.llm.grammar import GrammarError, GrammarLoader


def test_grammar_loader_default_path():
    """Verifica se o loader encontra o diretório padrão."""
    loader = GrammarLoader()
    assert loader.grammar_dir.name == "grammars"
    assert loader.grammar_dir.exists()


def test_load_command_grammar():
    """Verifica se consegue carregar a gramática de comando."""
    loader = GrammarLoader()
    content = loader.load("command")
    assert "root ::=" in content
    # Check for escaped quote as it appears in GBNF
    assert '\\"action\\":' in content


def test_load_non_existent_grammar():
    """Verifica erro ao carregar gramática inexistente."""
    loader = GrammarLoader()
    with pytest.raises(GrammarError, match="não encontrada"):
        loader.load("non_existent")


def test_custom_grammar_dir(tmp_path):
    """Verifica carregamento de diretório customizado."""
    custom_grammar = tmp_path / "custom.gbnf"
    custom_grammar.write_text('root ::= "test"', encoding="utf-8")

    loader = GrammarLoader(grammar_dir=tmp_path)
    content = loader.load("custom")

    assert content == 'root ::= "test"'
