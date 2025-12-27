Perfeito. Vamos "congelar" a estratégia lógica (o _como_ faremos), mas deixar os parâmetros específicos (os _links_ exatos) marcados como **PENDENTES** para a fase de implementação.

Aqui está o registro oficial desse tópico para anexar à documentação, garantindo que não será esquecido.

---

# ANEXO: Estratégia de Gestão de Modelos (Pesos/Weights)

**Status:** Estratégia Definida / Links Específicos Pendentes

## 1. Definições Fechadas (Decisões Tomadas)

- **Gerenciador de Download:** Não será manual. Usaremos a biblioteca Python **`huggingface_hub`** (gerenciada via `uv`).
- **Automação:** Criação futura de um script dedicado (`scripts/download_models.py`) que lê um dicionário de configurações e baixa os arquivos automaticamente.
- **Localização no Disco:**
- Estrutura canônica: `sysvox/models/` (na raiz).
- Subdivisão: `models/llm`, `models/stt`, `models/tts`, `models/rag`.

- **Controle de Versão:** A pasta `models/` será estritamente incluída no `.gitignore`. Pesos binários não sobem para o GitHub.

## 2. Pontos em Aberto (TBD - To Be Defined)

_Estes itens requerem pesquisa pontual no momento da implementação:_

- **[PENDENTE] URL Exata do Granite 4.0 GGUF:**
- Precisamos localizar o repositório da comunidade (ex: _Bartowski_ ou _MaziyarPanahi_) que disponibilizará o **Granite 4.0 Hybrid 1B** já convertido para `.gguf` com a quantização **Q8_0**.
- _Motivo:_ O repositório oficial da IBM costuma fornecer apenas os pesos `.safetensors` (não otimizados).

- **[PENDENTE] Formato Final do BGE-M3:**
- Definir se baixaremos a versão **ONNX** (para rodar via ONNX Runtime) ou **PyTorch** (para rodar nativo). Isso altera a função de download (`hf_hub_download` vs `snapshot_download`).

- **[PENDENTE] Validação de Hash:**
- Definir se implementaremos verificação de SHA256 no script para garantir que o download não foi corrompido ou alterado.

---

Está registrado. O "buraco" no planejamento foi cercado e sinalizado para não cairmos nele depois.

Agora, com a **Arquitetura** (DOC 00), **Engenharia de Áudio** (DOC 01) e **Gestão de Modelos** (Registro acima) definidos, podemos finalmente avançar para o **Plano de Trabalho**.

Gostaria que eu montasse o cronograma de **Fases, Etapas e Atividades** agora?
