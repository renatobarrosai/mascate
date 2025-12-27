# Mascate - Guia para Agentes de Codificação (AGENTS.md)

Este documento estabelece as convenções de desenvolvimento e os comandos operacionais para os agentes de codificação (como o Opencode) que trabalham no projeto **Mascate**. O objetivo é garantir consistência, aderência ao estilo e eficiência operacional.

---

## 1. Visão Geral do Projeto (Contexto)

**Mascate** é um Assistente de Voz local-first para Linux, focado em privacidade, baixa latência e otimização para hardware de consumo (AMD/NVIDIA). Ele utiliza uma arquitetura de pipeline rigorosa para processamento de áudio e LLM.

- **Fase Atual:** Prova de Conceito (PoC) Fase 0 (Fundação). O foco é estabelecer a estrutura, dependências (`uv`), e a infraestrutura de download de modelos.
- **Linguagem:** Python 3.12+ (Tipagem estrita).
- **Gerenciamento de Pacotes:** `uv`.
- **Configuração:** `pyproject.toml` (metadados), `config.toml` (configuração da aplicação).
- **Estilo & Linting:** `ruff`.
- **Testes:** `pytest` (Unitário, Integração, E2E).

---

## 2. Comandos Operacionais (Build, Lint, Testes)

Todos os comandos devem ser executados a partir da raiz do repositório (`/home/renato/programacao/open-source/mascate-v2`).

### 2.1. Instalação e Ambiente

| Comando   | Descrição                                                                       |
| :-------- | :------------------------------------------------------------------------------ |
| `uv sync` | Instala todas as dependências especificadas no `pyproject.toml` e no `uv.lock`. |

### 2.2. Execução Principal

| Comando                                    | Descrição                                                                           |
| :----------------------------------------- | :---------------------------------------------------------------------------------- |
| `uv run python scripts/install_deps.py`    | Instala dependências de SO (ffmpeg, playerctl, etc.) - Pode requerer `sudo`.        |
| `uv run python scripts/download_models.py` | Baixa os modelos LLM GGUF/ONNX necessários para a aplicação.                        |
| `uv run mascate run`                       | Executa o loop principal da aplicação (quando o _entry point_ estiver configurado). |

### 2.3. Linting e Formatação

O projeto utiliza `ruff` para linting e formatação.

| Comando                             | Descrição                                                                                                 |
| :---------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| `uv run ruff check src tests`       | Verifica problemas de linting nos diretórios `src` e `tests`.                                             |
| `uv run ruff format src tests`      | Formata o código automaticamente, aplicando o estilo configurado. **(Aplicar antes de qualquer commit!)** |
| `uv run ruff check src tests --fix` | Verifica e aplica correções automáticas de linting.                                                       |

### 2.4. Testes

O projeto utiliza `pytest` para execução de testes.

| Comando                                                           | Descrição                                                                                                                     |
| :---------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- |
| `uv run pytest`                                                   | Roda a suíte completa de testes (unitários, integração e E2E) contidos no diretório `tests/`.                                 |
| `uv run pytest tests/path/to/my_test_file.py`                     | Roda todos os testes em um arquivo específico.                                                                                |
| `uv run pytest tests/path/to/my_test_file.py::test_function_name` | **Comando para Rodar Teste Único:** Roda uma função de teste específica. Substitua `test_function_name` pelo nome exato.      |
| `uv run pytest -k "keyword"`                                      | Roda testes contendo a _keyword_ no nome do arquivo, da classe ou da função. Útil para rodar testes relacionados a um tópico. |
| `uv run pytest --cov=src`                                         | Roda os testes com relatórios de cobertura de código.                                                                         |

---

## 3. Convenções de Código e Estilo (Python)

Os agentes devem seguir estritamente estas diretrizes.

### 3.1. Tipagem (Type Hints)

- **Obrigatória:** Todos os parâmetros e valores de retorno de funções públicas e privadas devem ser explicitamente tipados (PEP 484).
- **Typing Imports:** Utilize `from __future__ import annotations` em todos os módulos para sintaxe moderna de type hints (stringifying).
- **Strictness:** O uso de `Any` deve ser evitado e, quando usado, necessita de uma justificativa em comentário.

### 3.2. Nomenclatura (Naming Conventions)

- **Módulos:** Nomes curtos, em _snake_case_ (ex: `audio_processor.py`).
- **Classes:** Nomes em _PascalCase_ (ex: `AudioProcessor`, `LLMClient`).
- **Funções/Métodos/Variáveis:** Nomes em _snake_case_ (ex: `process_audio`, `user_input_text`).
- **Constantes:** Nomes em _SCREAMING_SNAKE_CASE_ (ex: `MAX_LATENCY_MS`, `DEFAULT_MODEL_PATH`).
- **Variáveis Privadas:** Devem ser prefixadas com um sublinhado (ex: `_internal_state`).

### 3.3. Imports

- **Ordem:** Seguir o padrão `isort` (manejado automaticamente pelo `ruff`).
  1. Standard Library imports
  2. Third-party imports
  3. Local/Project imports
- **Absolute Imports:** Preferir a utilização de _absolute imports_ para módulos internos.
  - _Correto:_ `from mascate.core.config import Config`
  - _Incorreto:_ `from .config import Config`
- **Agrupamento:** Cada grupo de import pode ter um comentário separador (`# Third-party imports`, `# Local imports`).

### 3.4. Estrutura e Arquitetura

O agente deve respeitar a separação de responsabilidades estabelecida na arquitetura:

| Diretório (src/mascate/) | Descrição da Responsabilidade                                                                   |
| :----------------------- | :---------------------------------------------------------------------------------------------- |
| `audio/`                 | **APENAS** processamento de sinal, VAD, IO bruto, STT, TTS (Ouvido e Voz).                      |
| `intelligence/`          | **APENAS** RAG, inferência de LLM, engenharia de prompt (Cérebro e Memória).                    |
| `executor/`              | **APENAS** parsing de comandos, verificações de segurança, chamadas de sistema (Guarda-Costas). |
| `core/`                  | **APENAS** orquestração, máquina de estados, carregamento de configuração e logging.            |
| `interface/`             | **APENAS** CLI e _Heads-Up Display_ (Interface).                                                |

**Nenhuma lógica de LLM deve vazar para o módulo `audio`, e nenhuma lógica de I/O de sistema deve vazar para `intelligence`.**

### 3.5. Tratamento de Erros

- **Specific Exceptions:** Exceções específicas e relevantes devem ser levantadas e tratadas (`raise AudioInitError(...)` em vez de `raise Exception(...)`).
- **Logging:** Sempre utilizar o módulo de logging do Python (configurado via `core`) para registrar exceções. Nunca utilizar `print()` para debug ou logs operacionais.
- **Validação:** Inputs críticos (como caminhos de modelo, arquivos de configuração) devem ser validados o mais cedo possível.

---

## 4. Estratégia de Desenvolvimento para Agentes

### 4.1. Refatoração e Modificação

1. **Leitura:** Antes de modificar qualquer arquivo, utilize o `Read` tool para entender o contexto e convenções locais.
2. **Teste de Validação:** Identificar e rodar os testes relevantes para a funcionalidade a ser modificada.
3. **Verificação (Pós-Modificação):**
   a. Aplicar formatação: `uv run ruff format src tests`
   b. Checar linting: `uv run ruff check src tests` (e corrigir se houver erros)
   c. Rodar a suíte completa de testes: `uv run pytest`

### 4.2. Geração de Código Novo

- **Idem Convenções:** Seguir rigorosamente as convenções de Nomenclatura, Tipagem e Estrutura (Seção 3).
- **Testes Inclusos:** Qualquer funcionalidade nova deve vir acompanhada de testes unitários localizados no diretório `tests/` que mirem cobertura de 100% da nova lógica.

---

## 5. Base de Conhecimento (Documentação Consolidada)

A documentação técnica do projeto está organizada em `docs/`:

### 5.1. Documentos Principais

| Arquivo                            | Descrição                                                                       |
| :--------------------------------- | :------------------------------------------------------------------------------ |
| `docs/00-architecture-overview.md` | Visão geral da arquitetura, Cérebro vs Guarda-Costas, VRAM Tetris               |
| `docs/01-models-spec.md`           | Especificações detalhadas de todos os modelos (Granite, Whisper, Piper, BGE-M3) |
| `docs/02-pipeline-flow.md`         | Fluxo completo das 10 etapas, máquina de estados, latência                      |
| `docs/03-implementation-plan.md`   | Plano de trabalho com 5 fases e checklists                                      |
| `docs/04-model-management.md`      | Download e gestão de modelos via huggingface_hub                                |
| `docs/05-rag-memory.md`            | Arquitetura RAG com BGE-M3 + Qdrant                                             |
| `docs/06-gbnf-strategy.md`         | Gramáticas GBNF para inferência estruturada                                     |
| `docs/07-security.md`              | Estratégia de segurança (Guarda-Costas, Blacklist)                              |
| `docs/08-commands-strategy.md`     | Comandos agnósticos (xdg-open, playerctl)                                       |
| `docs/09-infrastructure.md`        | Monorepo, pyproject.toml, install_deps.py                                       |
| `docs/10-ui-identity.md`           | Identidade visual "Futurismo Tropical", TUI                                     |
| `docs/11-tts-dataset.md`           | Spec de tratamento de áudio para fine-tuning TTS                                |

### 5.2. Referências (Base de Conhecimento para RAG)

| Arquivo                            | Descrição                                             |
| :--------------------------------- | :---------------------------------------------------- |
| `docs/references/system-apps.md`   | Mapeamento de aplicativos e suas categorias (GUI/CLI) |
| `docs/references/ubuntu-basics.md` | Comandos básicos Ubuntu/GNOME, 4 pilares universais   |

### 5.3. Documentação Histórica

Documentos originais (pré-consolidação) estão arquivados em `.dev_docs/` para referência histórica. **Não modificar estes arquivos.**

_Fim do Documento_
