Sim, temos um último ponto técnico crucial para registrar antes de virarmos a chave para a Interface Visual.

Precisamos formalizar a decisão do **Monorepo** e a estratégia do **Script de Instalação Híbrido** (que detecta se é Arch ou Ubuntu). Se não documentarmos isso agora, quando você for configurar o ambiente amanhã, vai bater a dúvida: _"Crio repositórios separados? Como eu organizo as pastas?"_.

Aqui está o documento de encerramento da fase de "Infraestrutura e Backend".

---

````markdown
# Estratégia de Infraestrutura, Repositório e Distribuição

**Projeto:** Assistente de Controle Local (PoC)
**Foco:** Organização de Código e Gestão de Dependências de Sistema (Pareto)
**Data:** 21/12/2025

---

## 1. Estrutura de Repositório (Monorepo)

Para agilizar o desenvolvimento da PoC e facilitar a distribuição, adotamos um **Repositório Único (`sysvox-core`)**. Isso evita problemas de versionamento entre os módulos.

### Árvore de Arquivos

```text
/sysvox-core
│
├── /src                   # (O Código - 20% que faz tudo funcionar)
│   ├── /brain             # Lógica do Granite, Prompts e Gramáticas GBNF
│   ├── /ears              # Whisper (STT) e OpenWakeWord
│   ├── /voice             # Kokoro (TTS)
│   ├── /executor          # Script Python que roda os comandos (XDG/Playerctl)
│   └── main.py            # Orquestrador central
│
├── /knowledge_base        # (A Memória RAG - Markdown)
│   ├── /sistema           # Manuais: ubuntu_basics.md, hyprland.md
│   └── /apps              # Manuais: git_cheatsheet.md, atalhos_navegador.md
│
├── /scripts               # (Automação de Infra)
│   ├── install_deps.py    # Script "Detector de Distro" (vê item 2)
│   └── download_models.py # Script que baixa os GGUF do HuggingFace
│
├── pyproject.toml         # Gestão de dependências Python (via 'uv')
├── .env                   # Configs locais (ex: TERMINAL_APP=ghostty)
└── README.md              # Instruções de Setup
```
````

---

## 2. Gestão de Dependências (Estratégia Híbrida)

O sistema depende de duas camadas. Usaremos ferramentas diferentes para gerenciar cada uma, garantindo compatibilidade entre Arch Linux (Dev) e Ubuntu (Cliente).

### Camada A: Python (Gerenciada pelo `uv`)

- **Ferramenta:** `uv` (Astral).
- **Função:** Garante que bibliotecas como `llama-cpp-python`, `chromadb` e `fastapi` sejam idênticas em qualquer máquina.
- **Arquivo:** `pyproject.toml`.

### Camada B: Sistema Operacional (Gerenciada por Script Python)

- **Ferramenta:** Script `scripts/install_deps.py`.
- **Lógica:** O Python não tem um gerenciador universal de binários de sistema. O script detecta a distro e chama o gerenciador correto (`apt` ou `pacman`).

#### Dicionário de Tradução (Mapping)

O script conterá este mapa para traduzir os nomes dos pacotes automaticamente:

| Pacote Necessário    | Nome no Arch (`pacman`) | Nome no Ubuntu (`apt`) |
| -------------------- | ----------------------- | ---------------------- |
| **Media Controller** | `playerctl`             | `playerctl`            |
| **Audio Backend**    | `ffmpeg`                | `ffmpeg`               |
| **System Utils**     | `xdg-utils`             | `xdg-utils`            |
| **Compiladores**     | `base-devel`            | `build-essential`      |
| **Python Headers**   | `python`                | `python3-dev`          |

---

## 3. Fluxo de Setup (Onboarding)

O usuário (ou investidor) seguirá apenas 3 passos:

1. **Clone:** `git clone sysvox-core`
2. **System Prep:** `python scripts/install_deps.py` (Pede sudo, instala ffmpeg/playerctl).
3. **Run:** `uv run main.py` (O `uv` baixa o Python, cria o venv, instala libs e roda).

---

## 4. Conclusão da Infraestrutura

Esta abordagem elimina a necessidade de contêineres pesados (Docker) para a PoC, mantendo o acesso nativo ao hardware (GPU/Áudio) que é vital para a latência <1s, ao mesmo tempo que suporta as duas principais famílias Linux (Debian e Arch).

```

***

### Sobre o próximo tema: Interface Visual

Não há mais pendências de infraestrutura.
Você pode começar com suas **dúvidas sobre a Interface Visual**.

Na verdade, esse é o momento perfeito para isso, pois já definimos o "Cérebro" (Granite) e os "Músculos" (Comandos). Agora precisamos definir o "Rosto" do sistema. Como o usuário vê que o sistema está ouvindo? Como o sistema mostra que está pensando?

Pode mandar as dúvidas!

```
