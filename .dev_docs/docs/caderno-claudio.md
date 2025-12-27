# 📘 Caderno Técnico: Projeto Mascate - Edge AI Assistant

Soberania de Dados, Performance Edge (<500ms) e Identidade Cultural Brasileira

---

## 1. Visão Geral e Objetivos Estratégicos

O **Mascate** é um assistente de IA de borda (Edge AI) focado em **performance local, privacidade e identidade regional brasileira**.

### 1.1. Objetivos de Performance

- **Latência Alvo:** Time-to-First-Audio inferior a **500ms** através de pipelines de streaming
- **Hardware Alvo:** GPU NVIDIA GTX 1650 (4GB VRAM) e CPU Ryzen 7 (8c/16t)
- **Filosofia:** Extrair performance de servidor de um hardware de consumidor

### 1.2. Identidade "Futurismo Tropical"

A interface e personalidade fogem do padrão asséptico do Vale do Silício:

- **Estética:** "Cyberpunk Tropical" baseada na cultura do Frevo
- **Visual (TUI):** Interface de terminal moderna usando cores saturadas (Neon/Frevo) sobre fundo escuro
- **Voz:** Treinamento de modelos TTS proprietários focados em sotaques regionais (ex: "Ei Painho", "Ariano")
- **Cultura:** Incorporação de elementos pernambucanos e identidade nordestina

---

## 2. Filosofia de Arquitetura: "Cérebro vs. Guarda-Costas"

O sistema opera sob uma divisão estrita de responsabilidades para garantir que a IA seja útil, mas o sistema seja seguro.

### 2.1. O Cérebro (IA - Granite 4.0)

Atua como intérprete soberano e proativo:

- **Função:** Receber fala vaga ("Tira isso daqui"), consultar a memória (RAG) e deduzir a intenção técnica
- **Output:** Gera JSON estruturado com ações específicas
- **Limitação de Segurança:** **NUNCA** executa comandos diretamente
- **Inteligência:** Interpreta linguagem natural e manuais técnicos

### 2.2. O Guarda-Costas (Código - Python)

Atua como Firewall de Execução determinístico:

- **Função:** Recebe o JSON do Cérebro e valida contra regras de segurança
- **Blacklist de Comandos Críticos:** Proíbe comandos perigosos (ex: `rm -rf`) sem confirmação
- **Execução:** Traduz comandos para ações agnósticas do sistema via subprocessos
- **Confirmação:** Exige confirmação física ou verbal para ações perigosas

---

## 3. Estratégia de Memória e Hardware: "VRAM Tetris"

Para evitar erros de _Out of Memory_ (OOM), o sistema utiliza uma hierarquia de memória inspirada em cache de CPUs.

### 3.1. Hierarquia de Memória (L1/L2/L3)

| Nível  | Tipo        | Função                              | Características                                         |
| :----- | :---------- | :---------------------------------- | :------------------------------------------------------ |
| **L1** | VRAM (GPU)  | Contexto imediato e KV Cache do LLM | Janela deslizante de 2048 tokens para consumo linear    |
| **L2** | RAM (CPU)   | Modelos de áudio e Índice Vetorial  | Carregado no boot para busca em milissegundos           |
| **L3** | SSD (Disco) | Base de conhecimento e persistência | Manuais (.md), logs e banco vetorial (`chroma.sqlite3`) |

### 3.2. Alocação de Modelos e Quantização

| Componente        | Modelo Escolhido          | Backend       | Alocação            | Quantização/Estratégia                                                                                  |
| :---------------- | :------------------------ | :------------ | :------------------ | :------------------------------------------------------------------------------------------------------ |
| **Cérebro (LLM)** | IBM Granite 4.0 Hybrid 1B | `llama.cpp`   | **100% GPU** (VRAM) | **Q8_0** - Arquitetura Mamba-2 (consumo linear de memória) permite contextos longos sem estourar os 4GB |
| **Ouvido (STT)**  | Whisper Large v3          | `whisper.cpp` | **100% CPU**        | **Q5_K_M** - Otimizado para inferência em tempo real com streaming                                      |
| **Memória (RAG)** | BAAI/bge-m3 + Qdrant      | ONNX          | **CPU/RAM**         | Busca Híbrida (Densa + Esparsa) com janelas de 8192 tokens                                              |
| **Voz (TTS)**     | Piper (VITS)              | `piper-tts`   | **CPU**             | Fine-tuned High Quality - Latência <200ms com capacidade de fine-tuning                                 |
| **VAD**           | Silero VAD v5             | ONNX          | **CPU**             | Modelo ONNX para corte inteligente de silêncio                                                          |
| **Wake Word**     | openWakeWord              | ONNX          | **CPU**             | Few-shot learning para "Ei Painho" + Low CPU overhead                                                   |

### 3.3. Justificativas Técnicas

- **Granite Mamba-2:** Consumo linear de memória permite processar logs/manuais longos sem estourar VRAM
- **Whisper em CPU:** Libera a GPU completamente para o raciocínio do LLM
- **BGE-M3:** Único modelo que suporta busca híbrida eficiente em português
- **Qdrant Local:** Único motor local que suporta nativamente a saída híbrida do `bge-m3` sem Docker

---

## 4. Pipelines de Execução e Inteligência

### 4.1. Pipeline de Áudio (Streaming Real-Time)

Latência percebida alvo: ~500ms

**Fluxo de Execução:**

1. **Monitoramento Passivo:** `openWakeWord` analisa buffer circular continuamente (Low CPU)
2. **Gatilho de Ativação:** Palavra-chave detectada → Trava buffer (captura 0.5s anteriores) e abre canal
3. **Transcrição Incremental:** Áudio enviado via _stream_ para `whisper.cpp` - texto aparece enquanto o usuário fala
4. **Corte Inteligente (VAD):** `Silero VAD v5` monitora silêncio. Ao detectar >300ms, corta input e envia texto final imediatamente

### 4.2. Pipeline de Memória (RAG)

**Estratégia de Recuperação:**

- **Busca Híbrida:** Combina busca densa (semântica) com busca esparsa (keywords) via BGE-M3
- **Indexação:** Manuais em Markdown são processados e vetorizados no boot
- **Persistência:** Qdrant em modo local armazena vetores em SSD
- **Contexto Dinâmico:** Recupera trechos relevantes baseado na query do usuário

### 4.3. Pipeline de NLP (Raciocínio)

**Fluxo de Processamento:**

1. **Input:** Texto do Whisper + Contexto recuperado do RAG
2. **Trava Lógica (GBNF):** Gramáticas GBNF forçam o Granite a gerar **apenas JSON válido**
   - Elimina alucinações conversacionais
   - Garante segurança na execução
   - Acelera a inferência
3. **Validação:** Python recebe JSON estruturado (ex: `{"acao": "ABRIR", "alvo": "firefox"}`)
4. **Tradução para Comandos Agnósticos:** Executor converte para comandos do sistema
5. **Execução Segura:** Após validação da blacklist, executa via subprocessos

### 4.4. Comandos Agnósticos de Sistema

Camadas de abstração para compatibilidade entre distribuições Linux (Arch/Ubuntu) e futuros SOs:

- **`xdg-open`:** Abrir URLs, pastas e arquivos
- **`playerctl`:** Controle universal de mídia via protocolo MPRIS
- **`pactl/wpctl`:** Controle direto de áudio (PulseAudio/PipeWire)

---

## 5. Stack de Software e Infraestrutura

### 5.1. Core do Sistema

- **Linguagem:** Python 3.12+
- **Estrutura:** Monorepo (`mascate-core`) para versionamento atômico
- **Repositório:** Unificado para facilitar rastreamento de mudanças

### 5.2. Gestão de Dependências (Híbrida)

**Python:**

- **Ferramenta:** `uv` (Astral) para velocidade e isolamento
- **Vantagem:** Gestão rápida de ambientes virtuais

**Sistema:**

- **Script:** `install_deps.py` detecta a distribuição (Arch/Ubuntu)
- **Função:** Instala binários nativos (`ffmpeg`, `playerctl`, `xdg-utils`) via gerenciador correto (`apt` ou `pacman`)

### 5.3. Gestão de Artefatos (Modelos)

Os pesos dos modelos (GGUF/ONNX) não entram no Git:

- **Ferramenta:** `huggingface_hub`
- **Automação:** Script `scripts/download_models.py`
- **Função:** Baixa arquivos exatos com verificação de hash
- **Organização:** Estrutura em `mascate/models/`

### 5.4. Interface (TUI)

**Configuração:**

- **Framework:** `Textual` (Menus navegáveis via mouse/teclado)
- **Features:** Suporte a mouse, configurações interativas

**Runtime HUD:**

- **Framework:** `Rich`
- **Features:** Spinners, Markdown colorido, Logs em tempo real
- **Objetivo:** Feedback visual imediato para o usuário

---

## 6. Sub-Projetos de Soberania (IP Proprietária)

### 6.1. Voz Soberana (Fine-Tuning TTS)

Criação de identidade vocal exclusiva através do **Piper**.

**Objetivo:** Criar voz regional única com identidade brasileira

**Processo Completo:**

1. **Mineração de Áudio:**
   - Scanner automático busca frases foneticamente ricas
   - Foco em **Code-Switching** (termos em inglês + português)
   - Fontes: Entrevistas, palestras (ex: Ariano Suassuna)

2. **Data Augmentation:**
   - Simulação acústica de ambientes brasileiros
   - Biblioteca `Pedalboard` para efeitos realistas

3. **Tratamento de Engenharia:**
   - **De-reverb:** Remoção de reverberação
   - **Normalização:** Padronização em -23 LUFS
   - **Silence Padding:** 100-200ms nas pontas para naturalidade

4. **Treinamento:**
   - Execução em nuvem (AWS/Colab) com créditos
   - Fine-tuning do modelo base Piper

5. **Exportação:**
   - Modelo `.onnx` leve para CPU local
   - Latência <200ms garantida

### 6.2. Ouvido Soberano (Wake Word + Embedding PT-BR)

**Objetivo:** Eliminar falsos positivos e entender sotaques brasileiros

**Estratégia de Treinamento:**

1. **Embedding Base PT-BR:**
   - Treinamento em AWS usando créditos disponíveis
   - Modelo base focado em fonética do português brasileiro

2. **Expansão de Dataset:**
   - Base inicial: 800h de áudio
   - Expansão via simulação: ~14.400h
   - **Pedalboard:** Simulação de ambientes reais
     - Ruído de ventilador
     - Trânsito urbano
     - Reverberação de salas brasileiras
     - Cozinhas, escritórios, etc.

3. **Onboarding do Usuário (Few-Shot):**
   - **Script:** `train_trigger.py`
   - **Processo:** Usuário grava 10 exemplos da própria voz
   - **Output:** Modelo `trigger.onnx` personalizado instantaneamente
   - **Vantagem:** Adaptação à voz específica do usuário

---

## 7. Roteiro de Implementação (WBS Macro)

### Fase 0: Fundação

**Objetivo:** Preparar infraestrutura base

- Setup do Monorepo e `uv`
- Criação do script `download_models.py`
- Download dos pesos iniciais (Granite, Whisper, BGE-M3, Piper)
- Implementação do `install_deps.py` (Detector de Distro)
- Configuração do ambiente de desenvolvimento

### Fase 1: Os Sentidos (Áudio)

**Objetivo:** Implementar pipelines de entrada e saída de áudio

- Implementação do loop de Streaming (`pyaudio` → `whisper.cpp`)
- Integração do `Silero VAD` para corte preciso de silêncio
- Configuração do `openWakeWord` com modelo provisório
- Testes de latência e ajustes de buffer
- Implementação inicial do Piper TTS

### Fase 2: O Cérebro e Memória

**Objetivo:** Integrar raciocínio e recuperação de contexto

- Setup do Qdrant em modo local
- Ingestão de Manuais (Markdown → Vetor)
- Integração `llama.cpp` com Granite 4.0
- Implementação de Gramáticas GBNF para JSON estruturado
- Desenvolvimento do Executor Python (Wrappers `xdg-open`, `playerctl`, etc.)
- Sistema de validação e blacklist de comandos

### Fase 3: Refinamento e Identidade

**Objetivo:** Personalização e polish final

- Treinamento da Voz Customizada (Piper fine-tuning)
- Construção da TUI completa (Textual/Rich)
- Script de Onboarding (`train_trigger.py`)
- Testes de integração end-to-end
- Ajustes de performance e otimização de VRAM
- Documentação de uso e deployment

---

## 8. Analogia de Fixação: Fórmula 1 com Tanque de 4 Litros

O Mascate é como um **Carro de Fórmula 1 com Tanque de 4 Litros**:

- **O Granite (Motor):** Potente, mas a **VRAM (Combustível)** é limitadíssima
- **A Solução:** Não é diminuir o motor, mas usar:
  - **Arquitetura Mamba/GBNF (Aerodinâmica):** Não desperdiçar energia
  - **RAG (Navegação):** Motor não precisa decorar o mapa inteiro
- **Resultado:** Veículo que responde ao piloto (usuário) em tempo real, antes mesmo da curva terminar

---

## 9. Considerações Finais

Este projeto representa uma abordagem única para assistentes de IA:

- **Soberania de Dados:** Todo processamento local, sem dependência de cloud
- **Identidade Cultural:** Valorização da cultura brasileira e regional
- **Eficiência Técnica:** Performance de servidor em hardware consumer
- **Segurança por Design:** Separação clara entre interpretação e execução
- **Extensibilidade:** Arquitetura modular permite expansão futura

O Mascate não é apenas um assistente de voz - é uma demonstração de que é possível criar tecnologia de ponta respeitando privacidade, cultura local e limitações de hardware através de engenharia inteligente.
