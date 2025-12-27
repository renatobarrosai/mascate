# Mascate

**Assistente de Voz Edge AI para Linux**

Mascate e um assistente de voz local-first focado em privacidade, baixa latencia e identidade cultural brasileira. Processa comandos de voz inteiramente no dispositivo, sem dependencia de cloud.

---

## Caracteristicas

- **100% Local:** Nenhum dado sai do seu computador
- **Baixa Latencia:** <500ms do comando ao feedback
- **Edge AI:** Otimizado para hardware de consumo (GTX 1650 4GB + 32GB RAM)
- **Identidade Brasileira:** Voz e personalidade "Futurismo Tropical"

---

## Arquitetura

```
+------------------+     +------------------+     +------------------+
|     AUDIO        |     |   INTELLIGENCE   |     |    EXECUTOR      |
|   (Ouvido/Voz)   | --> |    (Cerebro)     | --> | (Guarda-Costas)  |
+------------------+     +------------------+     +------------------+
| - Wake Word      |     | - Granite LLM    |     | - Validacao      |
| - STT (Whisper)  |     | - RAG (BGE-M3)   |     | - Blacklist      |
| - TTS (Piper)    |     | - GBNF Grammar   |     | - Execucao       |
| - VAD (Silero)   |     | - Qdrant         |     | - Seguranca      |
+------------------+     +------------------+     +------------------+
```

### Cerebro vs Guarda-Costas

- **Cerebro (Granite LLM):** Interpreta linguagem natural, consulta RAG, gera JSON estruturado. NUNCA executa comandos.
- **Guarda-Costas (Python):** Recebe JSON, valida seguranca, executa via subprocessos. Nao julga semantica, julga RISCO.

---

## Stack Tecnologica

| Componente     | Tecnologia                       | Execucao   |
| -------------- | -------------------------------- | ---------- |
| LLM            | IBM Granite 4.0 Hybrid 1B (Q8_0) | GPU (VRAM) |
| STT            | Whisper Large v3 (Q5_K_M)        | CPU        |
| TTS            | Piper (VITS)                     | CPU        |
| Embeddings     | BGE-M3                           | CPU        |
| Banco Vetorial | Qdrant (local mode)              | CPU        |
| VAD            | Silero v5                        | CPU        |
| Wake Word      | openWakeWord                     | CPU        |

---

## Requisitos

### Hardware Minimo

- GPU: NVIDIA GTX 1650 (4GB VRAM) ou AMD equivalente
- RAM: 16GB (32GB recomendado)
- CPU: 8+ cores
- Storage: 20GB para modelos

### Software

- Linux (Ubuntu 22.04+ ou Arch)
- Python 3.12+
- CUDA 12.x ou ROCm (AMD)

---

## Instalacao

```bash
# Clonar repositorio
git clone https://github.com/seu-usuario/mascate.git
cd mascate

# Instalar dependencias Python (via uv)
uv sync

# Instalar dependencias do sistema
uv run python scripts/install_deps.py

# Baixar modelos
uv run python scripts/download_models.py

# Executar
uv run mascate run
```

---

## Estrutura do Projeto

```
mascate/
├── src/mascate/
│   ├── audio/           # STT, TTS, VAD, Wake Word
│   ├── intelligence/    # LLM, RAG, GBNF
│   ├── executor/        # Comandos, seguranca
│   ├── core/            # Orquestracao, config
│   └── interface/       # CLI, HUD
├── scripts/
│   ├── download_models.py
│   └── install_deps.py
├── tests/
├── docs/                # Documentacao tecnica
└── config.toml          # Configuracao
```

---

## Documentacao

Documentacao tecnica completa em `docs/`:

- [Arquitetura](docs/00-architecture-overview.md)
- [Especificacoes de Modelos](docs/01-models-spec.md)
- [Fluxo do Pipeline](docs/02-pipeline-flow.md)
- [Plano de Implementacao](docs/03-implementation-plan.md)
- [Seguranca](docs/07-security.md)

---

## Comandos Suportados (PoC)

Foco nos 4 pilares que cobrem 80% do uso:

### Navegador

- "Abre o YouTube"
- "Pesquisa Python no Google"

### Midia

- "Toca musica"
- "Proxima faixa"
- "Pausa"

### Arquivos

- "Abre a pasta Downloads"
- "Cria uma pasta chamada projetos"

### Aplicativos

- "Abre o VS Code"
- "Fecha o Firefox"

---

## Status do Projeto

**Fase Atual:** PoC Fase 0 (Fundacao)

- [x] Documentacao consolidada
- [ ] Estrutura de codigo
- [ ] Download de modelos
- [ ] Pipeline de audio
- [ ] Integracao LLM
- [ ] Executor seguro

---

## Licenca

MIT License

---

## Contribuicao

Contribuicoes sao bem-vindas! Veja [AGENTS.md](AGENTS.md) para convencoes de codigo.
