# 📘 Caderno Técnico: Projeto Mascate (Edge AI Assistant)

**Versão:** 2.0 (Definitiva para Desenvolvimento)
**Status:** Pronto para Execução
**Meta:** Soberania de Dados, Performance Edge (<1s) e Identidade Cultural Brasileira.

---

## 1. Filosofia de Arquitetura

### 1.1. O Conceito "Cérebro vs. Guarda-Costas"

O sistema opera sob uma divisão estrita de responsabilidades para garantir que a IA seja útil, mas o sistema seja seguro.

- **O Cérebro (IA - Granite 4.0):** Atua como intérprete soberano. Sua função é receber a fala vaga ("Tira isso daqui"), consultar a memória (RAG) e deduzir a intenção técnica, gerando um JSON estruturado. Ele **nunca** executa comandos.

- **O Guarda-Costas (Código - Python):** Atua como Firewall de Execução. Ele recebe o JSON, valida contra uma _Blacklist_ de segurança (ex: proíbe `rm -rf` sem confirmação) e só então executa a ação via subprocessos do sistema.

### 1.2. Identidade "Futurismo Tropical"

A interface e a personalidade fogem do padrão asséptico do Vale do Silício.

- **Visual (TUI):** Interface de terminal moderna usando cores saturadas (Neon/Frevo) sobre fundo escuro.

- **Voz:** Treinamento de modelos TTS proprietários focados em sotaques reais (ex: "Ei Painho", "Ariano").

---

## 2. Hardware e Alocação de Recursos ("VRAM Tetris")

O sistema foi desenhado para extrair performance de servidor de um hardware de consumidor (**Target:** Ryzen 7 + GTX 1650 4GB).

| Componente        | Modelo Escolhido              | Backend     | Alocação            | Justificativa Técnica                                                                                                 |
| ----------------- | ----------------------------- | ----------- | ------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Cérebro (LLM)** | **IBM Granite 4.0 Hybrid 1B** | `llama.cpp` | **100% GPU** (VRAM) | Arquitetura Mamba-2 (consumo linear de memória) permite contextos longos (logs/manuais) sem estourar os 4GB da placa. |

|
| **Ouvido (STT)** | **Whisper Large v3** | `whisper.cpp` | **100% CPU** | Rodar na CPU libera a GPU para o raciocínio. A versão `whisper.cpp` é otimizada para inferência em tempo real.

|
| **Memória (RAG)** | **BAAI/bge-m3** | ONNX | **CPU/RAM** | Suporte a Busca Híbrida (Densa + Esparsa) e janelas de contexto de 8192 tokens.

|
| **Voz (TTS)** | **Piper (VITS)** | `piper-tts` | **CPU** | Baixíssima latência (<200ms) e capacidade de Fine-Tuning para vozes customizadas.

|
| **Banco Vetorial** | **Qdrant (Local Mode)** | Rust/Python | **RAM/SSD** | Único motor local que suporta nativamente a saída híbrida do `bge-m3` sem precisar de Docker.

|

---

## 3. Stack de Software e Infraestrutura

### 3.1. Core do Sistema

- **Linguagem:** Python 3.10+.
- **Estrutura:** Monorepo (`sysvox-core`) para versionamento atômico.

- **Gestão de Dependências (Híbrida):**
- **Python:** Gerenciado via `uv` (Astral) para velocidade e isolamento.

- **Sistema:** Script `install_deps.py` que detecta a distro (Arch/Ubuntu) e instala binários nativos (`ffmpeg`, `playerctl`, `xdg-utils`).

### 3.2. Gestão de Artefatos (Modelos) [NOVO]

Os pesos dos modelos (GGUF/ONNX) não entram no Git.

- **Ferramenta:** `huggingface_hub`.
- **Automação:** Script `scripts/download_models.py`.
- **Função:** Baixa os arquivos exatos definidos na arquitetura (com verificação de hash) e organiza na pasta `sysvox/models/`.

### 3.3. Interface (TUI)

- **Configuração:** `Textual` (Menus navegáveis via mouse/teclado).

- **Runtime HUD:** `Rich` (Spinners, Markdown colorido, Logs em tempo real).

---

## 4. Estratégia de Dados e Pipelines

### 4.1. Pipeline de Áudio (Streaming Real-Time)

Latência percebida alvo: ~500ms.

1.  **Monitoramento:** `openWakeWord` analisa o buffer circular continuamente (Low CPU).

2.  **Gatilho:** Palavra-chave ("Ei Painho") detectada -> Trava o buffer (pega 0.5s passados) e abre o canal.

3.  **Transcrição Incremental:** O áudio é enviado via _stream_ para o `whisper.cpp`. O texto aparece na tela enquanto o usuário fala.

4.  **Corte (VAD):** O `Silero VAD v5` monitora o silêncio. Ao detectar >300ms de silêncio, corta o input e envia o texto final imediatamente.

### 4.2. Pipeline de Memória (RAG L1/L2/L3)

- **L1 (VRAM):** KV Cache do Granite (Conversa imediata).
- **L2 (RAM):** Índice Qdrant + Modelo Embedding. Carregado no boot para busca instantânea.
- **L3 (SSD):** Persistência de Manuais (.md), Logs e Banco Vetorial.

### 4.3. Pipeline de NLP (Raciocínio)

- **Input:** Texto do Whisper + Contexto do RAG.
- **Trava Lógica:** **GBNF (Grammars)**. O Granite é forçado matematicamente a gerar apenas JSON válido.

- **Executor:** O Python recebe o JSON `{"acao": "ABRIR", "alvo": "firefox"}` e traduz para comandos agnósticos (`xdg-open`).

---

## 5. Sub-Projetos de Soberania (Áudio)

### 5.1. Voz Soberana (TTS Custom)

- **Objetivo:** Criar voz regional única.
- **Método:** Mineração de áudio (ex: entrevistas) + Data Augmentation.
- **Processo:** Script de "Scanner" que busca frases foneticamente ricas e com termos em inglês ("Code-Switching").

- **Engenharia:** Tratamento de áudio (De-reverb, Normalização -23 LUFS) -> Fine-Tuning do Piper na Nuvem -> Exportação `.onnx` para CPU local.

### 5.2. Ouvido Soberano (Wake Word)

- **Objetivo:** Eliminar falsos positivos e entender sotaques.
- **Método:** Treinamento de um Embedding Base PT-BR na AWS (via créditos).
- **Dataset:** Expansão de 800h para ~14.000h usando simulação acústica (Ruído de ventilador, trânsito, reverberação) via biblioteca `Pedalboard`.

- **Onboarding do Usuário [NOVO]:** Script local `train_trigger.py`. O usuário grava 10 exemplos da sua voz e o sistema gera um modelo `trigger.onnx` leve instantaneamente (Few-Shot).

---

## 6. Roteiro de Implementação (WBS Macro)

1. **Fase 0: Fundação**

- Setup do Monorepo e `uv`.
- Criação do script `download_models.py` e download dos pesos iniciais.
- Implementação do `install_deps.py` (Detector de Distro).

2. **Fase 1: Os Sentidos (Áudio)**

- Implementação do loop de Streaming (`pyaudio` -> `whisper.cpp`).
- Integração do `Silero VAD` para corte preciso.
- Configuração do `openWakeWord` com modelo provisório.

3. **Fase 2: O Cérebro e Memória**

- Setup do Qdrant e Ingestão de Manuais (Markdown -> Vetor).
- Integração `llama.cpp` com Granite 4.0 + Gramática GBNF.
- Desenvolvimento do Executor Python (Wrappers `xdg-open`).

4. **Fase 3: Refinamento e Identidade**

- Treinamento da Voz Customizada (Piper).
- Construção da TUI (Textual/Rich).
- Script de Onboarding (`train_trigger.py`).
