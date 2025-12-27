# Mascate

**Assistente de Voz Local para Linux**

Mascate e um assistente de voz que roda 100% no seu computador, sem enviar dados para a nuvem. Focado em privacidade, baixa latencia e integracao nativa com o desktop Linux.

```
Voce: "Abre o Firefox"
Mascate: [Abre o Firefox]
Mascate: "Pronto, Firefox aberto."
```

---

## Destaques

- **100% Offline** - Processamento local, seus dados nunca saem do computador
- **Baixa Latencia** - Resposta em menos de 500ms
- **Codigo Aberto** - MIT License, contribuicoes bem-vindas
- **Modular** - Use apenas os componentes que precisar

---

## Status do Projeto

> **Fase Atual: Prova de Conceito (PoC)**
>
> O projeto esta em desenvolvimento ativo. Funcionalidades basicas estao implementadas,
> mas ainda nao esta pronto para uso em producao.

| Componente       | Status      |
| ---------------- | ----------- |
| Captura de Audio | Funcional   |
| Ativacao Hotkey  | Funcional   |
| Wake Word        | Parcial [1] |
| STT (Whisper)    | Funcional   |
| TTS (Piper)      | Funcional   |
| LLM (Granite)    | Funcional   |
| Executor         | Funcional   |
| Interface (HUD)  | Funcional   |

[1] Wake word requer Python < 3.12 (limitacao do tflite-runtime)

---

## Requisitos

### Hardware

| Componente | Minimo         | Recomendado        |
| ---------- | -------------- | ------------------ |
| GPU        | GTX 1650 (4GB) | RTX 3060 (12GB)    |
| RAM        | 16GB           | 32GB               |
| CPU        | 4 cores        | 8+ cores           |
| Disco      | 20GB livre     | SSD com 50GB livre |

### Software

- Linux (Ubuntu 22.04+, Fedora 38+, Arch)
- Python 3.12+
- CUDA 12.x (NVIDIA) ou ROCm (AMD)

---

## Inicio Rapido

```bash
# 1. Clone o repositorio
git clone https://github.com/seu-usuario/mascate.git
cd mascate

# 2. Instale as dependencias Python
uv sync

# 3. Instale dependencias do sistema
uv run python scripts/install_deps.py

# 4. Baixe os modelos de IA (~10GB)
uv run python scripts/download_models.py

# 5. Crie o arquivo de configuracao
mkdir -p ~/.config/mascate
cp config.toml.example ~/.config/mascate/config.toml

# 6. Execute
uv run mascate run
```

Para instrucoes detalhadas, veja o [Guia de Instalacao](docs/getting-started.md).

---

## Uso Basico

### Ativacao

- **Hotkey:** Pressione `Ctrl+Shift+M` (padrao)
- **Wake Word:** Diga "Mascate" (requer configuracao adicional)

### Comandos Suportados

| Categoria | Exemplos                                         |
| --------- | ------------------------------------------------ |
| Apps      | "Abre o Firefox", "Abre o VS Code"               |
| Web       | "Pesquisa no Google por clima", "Abre o YouTube" |
| Midia     | "Toca musica", "Proxima faixa", "Pausa"          |
| Sistema   | "Aumenta o volume", "Bloqueia a tela"            |
| Arquivos  | "Abre a pasta Downloads", "Lista arquivos"       |

Para lista completa, veja o [Guia do Usuario](docs/user-guide.md).

---

## Documentacao

| Documento                                       | Descricao                   |
| ----------------------------------------------- | --------------------------- |
| [Inicio Rapido](docs/getting-started.md)        | Instalacao passo a passo    |
| [Guia do Usuario](docs/user-guide.md)           | Comandos e funcionalidades  |
| [Configuracao](docs/configuration.md)           | Referencia do config.toml   |
| [Arquitetura](docs/architecture.md)             | Visao tecnica do sistema    |
| [Desenvolvimento](docs/development.md)          | Guia para contribuidores    |
| [Solucao de Problemas](docs/troubleshooting.md) | Problemas comuns e solucoes |

---

## Stack Tecnologica

| Componente | Tecnologia             | Papel                   |
| ---------- | ---------------------- | ----------------------- |
| LLM        | IBM Granite 4.0 (1B)   | Interpretacao de intent |
| STT        | Whisper Large v3       | Fala para texto         |
| TTS        | Piper                  | Texto para fala         |
| VAD        | Silero v5              | Deteccao de voz         |
| Embeddings | BGE-M3                 | Busca semantica (RAG)   |
| Backend    | llama.cpp, whisper.cpp | Inferencia otimizada    |

---

## Contribuindo

Contribuicoes sao bem-vindas! Veja o [Guia de Desenvolvimento](docs/development.md).

```bash
# Rodar testes
uv run pytest

# Verificar codigo
uv run ruff check src tests
uv run ruff format src tests
```

---

## Licenca

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## Links

- [Documentacao Completa](docs/)
- [Reportar Bug](https://github.com/seu-usuario/mascate/issues)
- [Discussoes](https://github.com/seu-usuario/mascate/discussions)
