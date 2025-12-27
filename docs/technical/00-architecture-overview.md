# Mascate - Arquitetura e Design

**Versão:** 1.0  
**Status:** Aprovado para Implementação

---

## 1. Visao Geral

O **Mascate** e um assistente de IA de borda (Edge AI) focado em:

- **Privacidade:** Processamento 100% local, sem dependencia de cloud
- **Performance:** Latencia percebida (Time-to-First-Audio) inferior a **500ms**
- **Identidade Cultural:** Estetica "Futurismo Tropical" com sotaques regionais brasileiros

### 1.1. Hardware Alvo

| Componente  | Especificacao              | Papel                                |
| :---------- | :------------------------- | :----------------------------------- |
| **GPU**     | NVIDIA GTX 1650 (4GB VRAM) | Gargalo critico - exclusiva para LLM |
| **CPU**     | AMD Ryzen 7 (8c/16t)       | Audio, RAG, TTS - potencia de sobra  |
| **RAM**     | 32 GB                      | Modelos de audio e indice vetorial   |
| **Storage** | SSD                        | Base de conhecimento e persistencia  |

### 1.2. Filosofia de Alocacao

> A GPU e "territorio sagrado" e escasso. Ela sera usada exclusivamente para o LLM.
> Todo o resto (STT, TTS, RAG, VAD) roda na CPU.

---

## 2. Arquitetura "Cerebro vs. Guarda-Costas"

O sistema opera sob uma divisao estrita de responsabilidades para garantir que a IA seja util, mas o sistema seja seguro.

```
+-------------------+     JSON      +---------------------+
|                   | ----------->  |                     |
|  CEREBRO (LLM)    |               |  GUARDA-COSTAS     |
|  IBM Granite 4.0  |               |  Python Executor    |
|                   | <-----------  |                     |
+-------------------+   Resultado   +---------------------+
        |                                    |
        v                                    v
  Interpreta linguagem              Valida seguranca
  Consulta RAG                      Executa comandos
  Gera JSON estruturado             Blacklist de riscos
```

### 2.1. O Cerebro (IA - Granite 4.0)

Atua como interprete soberano e proativo:

- **Funcao:** Receber fala vaga ("Tira isso daqui"), consultar a memoria (RAG) e deduzir a intencao tecnica
- **Output:** Gera JSON estruturado com acoes especificas via gramaticas GBNF
- **Limitacao de Seguranca:** **NUNCA** executa comandos diretamente
- **Inteligencia:** Interpreta linguagem natural e manuais tecnicos

### 2.2. O Guarda-Costas (Python)

Atua como Firewall de Execucao deterministico:

- **Funcao:** Recebe o JSON do Cerebro e valida contra regras de seguranca
- **Blacklist:** Proibe comandos perigosos (ex: `rm -rf`) sem confirmacao
- **Execucao:** Traduz comandos para acoes agnosticas do sistema via subprocessos
- **Confirmacao:** Exige confirmacao fisica ou verbal para acoes perigosas

---

## 3. Estrategia de Memoria: "VRAM Tetris"

Para evitar erros de Out of Memory (OOM), o sistema utiliza uma hierarquia de memoria inspirada em cache de CPUs.

### 3.1. Hierarquia L1/L2/L3

| Nivel  | Tipo        | Funcao                              | Caracteristicas                     |
| :----- | :---------- | :---------------------------------- | :---------------------------------- |
| **L1** | VRAM (GPU)  | Contexto imediato e KV Cache do LLM | Janela deslizante de 2048 tokens    |
| **L2** | RAM (CPU)   | Modelos de audio e Indice Vetorial  | Carregado no boot                   |
| **L3** | SSD (Disco) | Base de conhecimento e persistencia | Manuais (.md), logs, banco vetorial |

### 3.2. Calculo de VRAM (GTX 1650 4GB)

```
VRAM Total Disponivel:        4096 MB
- Reserva do Sistema:         - 600 MB
- Modelo Granite 4.0 (Q8_0):  -1300 MB
- Contexto KV Cache (Mamba):  - 300 MB
- Buffers CUDA:               - 400 MB
----------------------------------------
Margem de Seguranca:          ~1500 MB (OK)
```

**Conclusao:** O sistema roda com folga na GPU, sem swapping para RAM.

---

## 4. Stack de Software

### 4.1. Componentes Principais

| Componente        | Modelo/Ferramenta         | Backend     | Alocacao | Quantizacao |
| :---------------- | :------------------------ | :---------- | :------- | :---------- |
| **LLM (Cerebro)** | IBM Granite 4.0 Hybrid 1B | llama.cpp   | 100% GPU | Q8_0        |
| **STT (Ouvido)**  | Whisper Large v3          | whisper.cpp | 100% CPU | Q5_K_M      |
| **TTS (Voz)**     | Piper (VITS)              | piper-tts   | CPU      | ONNX High   |
| **RAG (Memoria)** | BGE-M3 + Qdrant           | ONNX        | CPU/RAM  | FP16        |
| **VAD**           | Silero VAD v5             | ONNX        | CPU      | Padrao      |
| **Wake Word**     | openWakeWord              | ONNX        | CPU      | INT8        |

### 4.2. Justificativas Tecnicas

- **Granite Mamba-2:** Consumo linear de memoria permite processar logs/manuais longos sem estourar VRAM. Treinado para Tool Use.
- **Whisper em CPU:** Libera a GPU completamente para o raciocinio do LLM. Versao `.cpp` otimizada para streaming real-time.
- **BGE-M3:** Unico modelo que suporta busca hibrida (densa + esparsa) eficiente em portugues.
- **Qdrant Local:** Unico motor local que suporta nativamente a saida hibrida do BGE-M3 sem Docker.
- **Piper:** Latencia <200ms com capacidade de fine-tuning para vozes customizadas.

---

## 5. Estrutura de Modulos

```
src/mascate/
+-- audio/              # STT, TTS, VAD, Wake Word
|   +-- stt/            # Whisper integration
|   +-- tts/            # Piper integration
|   +-- vad/            # Silero VAD
|   +-- wake/           # openWakeWord
|
+-- intelligence/       # LLM, RAG, GBNF
|   +-- llm/            # Granite via llama.cpp
|   +-- rag/            # BGE-M3 + Qdrant
|
+-- executor/           # Comandos + seguranca
|   +-- handlers/       # Handlers por tipo de comando
|
+-- core/               # Orquestracao, config, logging
|
+-- interface/          # CLI, HUD (Rich/Textual)
```

### 5.1. Separacao de Responsabilidades

| Modulo          | Responsabilidade                          | NAO pode conter              |
| :-------------- | :---------------------------------------- | :--------------------------- |
| `audio/`        | Processamento de sinal, VAD, IO, STT, TTS | Logica de LLM                |
| `intelligence/` | RAG, inferencia LLM, prompts, GBNF        | IO de sistema                |
| `executor/`     | Parsing de comandos, seguranca, syscalls  | Semantica de linguagem       |
| `core/`         | Orquestracao, estado, config, logging     | Logica de negocio especifica |
| `interface/`    | CLI e HUD                                 | Processamento de dados       |

---

## 6. Projecao de Latencia

Pipeline de streaming para **latencia percebida de ~530ms**:

| Etapa     | Acao                     | Tempo       |
| :-------- | :----------------------- | :---------- |
| T0        | Usuario para de falar    | 0 ms        |
| T1        | VAD (janela de silencio) | +300 ms     |
| T2        | Whisper (finalizacao)    | +50 ms      |
| T3        | RAG (busca vetorial)     | +30 ms      |
| T4        | LLM (primeiro token)     | +50 ms      |
| T5        | Piper (buffer inicial)   | +100 ms     |
| **TOTAL** | **Latencia Percebida**   | **~530 ms** |

> Graças a velocidade do Granite 1B (>80 tokens/s), a geracao de texto e mais rapida
> que a fala, garantindo que o audio nunca engasgue.

---

## 7. Identidade "Futurismo Tropical"

### 7.1. Conceito Visual

- **Estetica:** "Cyberpunk Tropical" baseada na cultura do Frevo
- **Paleta:** Cores saturadas (Neon) sobre fundo escuro
- **Interface:** TUI moderna com Rich/Textual

### 7.2. Personalidade

A personalidade nasce da dicotomia entre Cerebro e Voz:

- **Cerebro (Granite):** Direto, preciso, focado na resolucao do problema tecnico
- **Voz (Custom TTS):** Timbre regional, acolhedor, com sotaque marcante
- **Resultado:** Especialista tecnico competente com roupagem de amigo sabio

### 7.3. Wake Words Planejados

- "Ei Painho" (Nordestino)
- "Ariano" (Referencia cultural)
- Customizaveis via few-shot learning

---

## 8. Analogia de Fixacao

> O Mascate e como um **Carro de Formula 1 com Tanque de 4 Litros**:
>
> - O **Granite (Motor)** e potente, mas a **VRAM (Combustivel)** e limitadissima
> - A solucao nao e diminuir o motor, mas usar:
>   - **Arquitetura Mamba/GBNF (Aerodinamica):** Nao desperdicar energia
>   - **RAG (Navegacao):** Motor nao precisa decorar o mapa inteiro
> - **Resultado:** Veiculo que responde ao piloto em tempo real

---

## Referencias

- [01-models-spec.md](./01-models-spec.md) - Especificacoes detalhadas dos modelos
- [02-pipeline-flow.md](./02-pipeline-flow.md) - Fluxo completo do pipeline
- [07-security.md](./07-security.md) - Estrategia de seguranca do Guarda-Costas
