# 📘 Caderno Técnico: Projeto Mascate (Versão Final)

O intuito deste documento é fornecer clareza total aos responsáveis pelo desenvolvimento sobre as ferramentas, bibliotecas e estratégias deliberadas para extrair performance de servidor de um hardware de consumidor local.

## 1. Visão Geral e Objetivos Estratégicos

O **Mascate** é um assistente de IA de borda (Edge AI) focado em **performance local, privacidade e identidade regional**.

- **Performance Alvo:** Latência percebida (Time-to-First-Audio) inferior a **500ms** através de pipelines de streaming.
- **Hardware Alvo:** GPU NVIDIA GTX 1650 (4GB VRAM) e CPU Ryzen 7 (8c/16t).
- **Estética:** "Cyberpunk Tropical" baseada na cultura do Frevo (cores saturadas sobre fundo escuro).

---

## 2. Arquitetura "Cérebro vs. Guarda-Costas"

O sistema opera em uma divisão soberana de responsabilidades para garantir segurança absoluta e flexibilidade linguística:

- **O Cérebro (Granite 4.0 H-1B):** Atua como o intérprete proativo que deduz intenções a partir de linguagem natural e manuais (RAG).
- **O Guarda-Costas (Python Firewall):** Um executor determinístico que recebe comandos estruturados e valida riscos através de uma **Blacklist de Comandos Críticos** (ex: `rm -rf`), exigindo confirmação física ou verbal para ações perigosas.

---

## 3. Estratégia de Memória e Hardware: "VRAM Tetris"

Para evitar erros de _Out of Memory_ (OOM), o sistema utiliza uma hierarquia de memória inspirada em cache de CPUs:

- **L1 (VRAM - GPU):** Contexto imediato e KV Cache do LLM. Limitado a uma **janela deslizante de 2048 tokens** para manter o consumo linear.
- **L2 (RAM - CPU):** Modelos de áudio e Índice Vetorial do Qdrant. Carregados no boot para busca em milissegundos.
- **L3 (SSD - Disco):** Base de conhecimento (.md), banco de dados persistente (`chroma.sqlite3`) e logs.

### Alocação de Modelos e Quantização

| Componente        | Ferramenta                | Alocação | Estratégia/Quantização                     |
| :---------------- | :------------------------ | :------- | :----------------------------------------- |
| **LLM (Cérebro)** | IBM Granite 4.0 Hybrid 1B | GPU      | **Q8_0** (Arquitetura Mamba-2)             |
| **STT (Ouvido)**  | Whisper Large v3          | CPU      | **Q5_K_M** via `whisper.cpp` (Streaming)   |
| **RAG (Memória)** | BGE-M3 + Qdrant           | CPU      | **Busca Híbrida** (Densa + Esparsa)        |
| **TTS (Voz)**     | Piper (VITS)              | CPU      | **Fine-tuned High Quality** (Voz regional) |
| **VAD**           | Silero VAD v5             | CPU      | Modelo ONNX para corte inteligente         |
| **Wake Word**     | openWakeWord              | CPU      | **Few-shot** ("Ei Painho")                 |

---

## 4. Pipeline de Execução e Inteligência

### 4.1. Inferência Estruturada (GBNF)

Utilizaremos **Gramáticas GBNF** nativas do `llama.cpp` para forçar o Granite a responder estritamente em **JSON**. Isso elimina alucinações conversacionais, garante segurança e acelera a inferência.

### 4.2. Comandos Agnósticos de Sistema

O executor Python utilizará camadas de abstração para garantir compatibilidade entre distribuições Linux (Arch/Ubuntu) e futuros SOs:

- `xdg-open`: Para abrir URLs, pastas e arquivos.
- `playerctl`: Controle universal de mídia via protocolo MPRIS.
- `pactl/wpctl`: Controle direto de áudio (PulseAudio/PipeWire).

### 4.3. Pipeline de Áudio em Streaming

O **whisper.cpp** processará o áudio em janelas deslizantes enquanto o usuário fala. O **Silero VAD** atuará como a "tesoura inteligente", detectando o fim da fala (>300ms de silêncio) para disparar a ação do cérebro instantaneamente.

---

## 5. Subprojetos de Soberania (IP Proprietária)

### 5.1. Voz Soberana (Fine-Tuning TTS)

Criação de identidade vocal exclusiva através do **Piper**.

- **Dataset:** Mineração cirúrgica de áudios (ex: Ariano Suassuna) focada em frases com **Code-Switching** (termos técnicos misturados ao português).
- **Tratamento:** Normalização a -23 LUFS, remoção de reverb e inserção de _Silence Padding_ (100-200ms nas pontas).
- **Treino:** Executado em nuvem (AWS/Colab) para exportação de modelo `.onnx` leve para a CPU local.

### 5.2. Ouvido Soberano (Embedding PT-BR)

Treinamento de um modelo de embedding de áudio nativo para Wake Word.

- **Estratégia:** Uso de créditos de nuvem (AWS/Google) para treinar uma base soberana com ~14.400 horas de áudio aumentadas via **Pedalboard** (simulando cozinhas, trânsito e salas brasileiras).

---

## 6. Infraestrutura de Desenvolvimento

- **Repositório:** Monorepo unificado (`sysvox-core`) para versionamento atômico.
- **Gestão de Dependências:** `uv` (Astral) para Python e um script `install_deps.py` para ferramentas binárias do sistema (detectando `apt` ou `pacman`).
- **Interface (TUI):** Desenvolvida com `Textual` (configurações e suporte a mouse) e `Rich` (HUD de operação e spinners animadores).
- **Gestão de Modelos:** Script `download_models.py` utilizando `huggingface_hub` para baixar pesos (.gguf/.bin/.onnx) fora do controle do Git.

---

### Analogia de Fixação:

O Mascate é como um **Carro de Fórmula 1 com Tanque de 4 Litros**:

- O **Granite (Motor)** é potente, mas a **VRAM (Combustível)** é limitadíssima.
- A solução não é diminuir o motor, mas usar a **Arquitetura Mamba/GBNF (Aerodinâmica)** para não desperdiçar energia e o **RAG (Navegação)** para o motor não precisar decorar o mapa inteiro.
- O resultado é um veículo que responde ao piloto (usuário) em tempo real, antes mesmo da curva terminar.
