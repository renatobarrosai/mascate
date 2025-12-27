Com certeza. Este documento é o **código-fonte das nossas decisões**. Ele consolida semanas de debate técnico em um plano de arquitetura imutável (até que decidamos mudar, claro).

Aqui está o **DOC 00**, que servirá como a "Bíblia Técnica" do projeto SysVox.

---

# DOC 00: Blueprint de Arquitetura Técnica e Decisões de Design

**Projeto:** SysVox (Assistente Local Técnico com Identidade Regional)
**Versão:** 1.0 (Final Architecture)
**Data:** 21/12/2025
**Status:** Aprovado para Implementação

---

## 1. Premissas de Hardware (O Cenário Físico)

Todo o projeto foi desenhado para extrair a máxima eficiência da seguinte configuração local, sem depender de nuvem.

- **Processador (CPU):** AMD Ryzen 7 (Alta capacidade de multithreading).
- **Placa de Vídeo (GPU):** NVIDIA GTX 1650 (4GB VRAM). _O gargalo crítico._
- **Memória (RAM):** 32 GB.
- **Armazenamento:** SSD (Leitura rápida para RAG).

**Filosofia de Alocação:** A GPU é "território sagrado" e escasso. Ela será usada exclusivamente para o que exige cálculo tensorial pesado (LLM). Todo o resto (Ouvido, Voz, Memória) será offloaded para a CPU (Ryzen), que tem potência de sobra.

---

## 2. A Stack de Software (Seleção Definitiva)

### 2.1. O Cérebro (LLM)

- **Modelo Escolhido:** **IBM Granite 4.0 Hybrid 1B (Mamba-2)**.
- **Arquitetura:** Híbrida (SSM/Mamba + Transformer).
- **Motivo da Escolha:**
- **Eficiência de Memória:** A arquitetura Mamba tem consumo de memória _linear_ (não quadrático) para o contexto. Permite ler manuais e logs gigantes sem estourar os 4GB da GTX 1650.
- **Foco:** Treinado para _Tool Use_ e comandos técnicos (Enterprise/Coding), ideal para um SysAdmin.
- **Alocação:** 100% na GPU.

### 2.2. O Ouvido (STT)

- **Modelo Escolhido:** **Whisper Large v3**.
- **Implementação:** `whisper.cpp` (Otimizado para CPU).
- **Motivo da Escolha:**
- Melhor compreensão do PT-BR, sotaques e termos técnicos (Code-switching).
- Suporte a **Streaming Real-time** (transcreve enquanto o usuário fala).
- **Alocação:** 100% na CPU (4 a 6 Threads).

### 2.3. A Voz (TTS)

- **Modelo Escolhido:** **Piper (Arquitetura VITS)**.
- **Dataset:** Customizado (Single Speaker - ex: "Ariano/Painho").
- **Motivo da Escolha:**
- Baixíssima latência (First Audio Packet em < 200ms).
- Alta fidelidade de prosódia com datasets pequenos (~40 min).
- **Alocação:** 100% na CPU (1 Thread).

### 2.4. A Memória (RAG)

- **Modelo de Embedding:** **BGE-M3 (BAAI General Embedding)**.
- **Motivo da Escolha:**
- Suporte a **Busca Híbrida** (Semântica + Palavra-chave exata). Crucial para diferenciar comandos técnicos parecidos.
- Estado da arte em multilinguismo.
- **Alocação:** CPU/RAM (Sob demanda).

### 2.5. O Gatilho (Wake Word)

- **Modelo Escolhido:** **openWakeWord**.
- **Motivo da Escolha:**
- Treinável para palavras personalizadas ("Ei Painho").
- Consumo de recurso insignificante.
- **Alocação:** CPU (Baixa prioridade).

---

## 3. Fluxo de Latência (Pipeline de Streaming)

O sistema foi desenhado para **Latência Percebida de ~500ms**. O usuário não espera o processamento acabar; ele ouve a resposta assim que ela começa a ser gerada.

| Etapa          | Ação Técnica                          | Tempo Estimado         |
| -------------- | ------------------------------------- | ---------------------- |
| **0. Input**   | Usuário termina de falar.             | 0 ms                   |
| **1. VAD**     | Detecção de silêncio (Segurança).     | +300 ms (Configurável) |
| **2. Whisper** | Processamento final (últimos tokens). | +50 ms                 |
| **3. RAG**     | Busca no Banco Vetorial (RAM).        | +30 ms                 |
| **4. LLM**     | Granite gera o primeiro token (GPU).  | +50 ms                 |
| **5. Piper**   | Buffer inicial e geração de áudio.    | +100 ms                |
| **TOTAL**      | **Tempo até o áudio sair na caixa.**  | **~530 ms**            |

_Nota: Graças à velocidade do Granite 1B (>80 tokens/s), a geração de texto é mais rápida que a fala, garantindo que o áudio nunca engasgue (buffer underrun)._

---

## 4. Estratégia de Identidade e Dados

### 4.1. A Persona (O Contraste)

Foi decidido que a "personalidade" do assistente nasce da dicotomia entre Cérebro e Voz:

- **Cérebro (Granite):** Direto, preciso, "militar", focado na resolução do problema técnico. Não tenta ser engraçado.
- **Voz (Custom TTS):** Timbre regional, acolhedor, com sotaque marcante (ex: Nordestino/Idoso).
- **Resultado:** Um especialista técnico extremamente competente, mas com a roupagem de um velho amigo sábio.

### 4.2. Estratégia de Dataset (Áudio)

Para criar a voz, abandonamos a ideia de transcrição massiva em favor da **Mineração Cirúrgica (Audio Scanning)**:

1. **Fonte:** Áudios de alta qualidade (Broadcast) de um único orador.
2. **Processo:**

- Uso do **WhisperX** para varrer horas de áudio.
- **Filtro de Conteúdo:** Buscar e recortar apenas frases que contenham:
- Termos técnicos/Inglês ("Show", "Design", "Software") para ensinar _Code-Switching_.
- Riqueza fonética (Vogais nasais, encontros consonantais).

- **Target:** Obter ~40 minutos de "ouro" filtrado.

---

## 5. Próximos Passos (Roadmap Macro)

Com a arquitetura travada, o projeto segue para a execução prática:

1. **Fase 1: Preparação de Dados (DOC 02)**

- Script Python de mineração de áudio.
- Criação do Dataset TTS.

2. **Fase 2: Treinamento**

- Fine-tuning do Piper (VITS).
- Treinamento do openWakeWord.

3. **Fase 3: Integração do Backend**

- Configuração do Granite (llama.cpp) + Whisper + RAG.
- Orquestração em Python.

---

Este documento reflete com precisão todas as nossas conversas e decisões? Se sim, ele está "congelado" e podemos avançar para a criação do **Script de Mineração (Fase 1)**.
