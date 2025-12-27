Perfeito. Vamos formalizar esses detalhes técnicos.

Este documento complementa o **DOC 00**, focando especificamente nas configurações de implementação (Quantização e Latência), servindo como guia de configuração para o momento do _deploy_.

---

# ANEXO TÉCNICO: Especificações de Implementação e Performance

**Referência:** Arquitetura SysVox (Ryzen 7 + GTX 1650 4GB)
**Data:** 21/12/2025

---

## 1. Tabela Mestra de Ferramentas e Configurações (A Stack)

Esta tabela define exatamente qual arquivo de modelo baixar, qual nível de compressão (quantização) usar e onde ele deve rodar.

| Componente        | Modelo Específico                        | Engine / Backend            | Quantização (Precisão)           | Alocação de Hardware     | Consumo Estimado |
| ----------------- | ---------------------------------------- | --------------------------- | -------------------------------- | ------------------------ | ---------------- |
| **Cérebro (LLM)** | **IBM Granite 4.0 Hybrid 1B** (Instruct) | `llama.cpp` (Suporte Mamba) | **Q8_0** (Alta Precisão)         | **100% GPU** (VRAM)      | ~1.3 GB VRAM     |
| **Ouvido (STT)**  | **Whisper Large v3**                     | `whisper.cpp`               | **Q5_K_M** (Equilíbrio Vel/Qual) | **100% CPU** (4 Threads) | ~2.2 GB RAM      |
| **Memória (RAG)** | **BAAI BGE-M3**                          | `ONNX Runtime` ou `PyTorch` | **FP16** (Padrão)                | **CPU** (Sob demanda)    | ~1.5 GB RAM      |
| **Voz (TTS)**     | **Piper** (pt_BR Custom)                 | `piper-tts`                 | **ONNX High** (Padrão)           | **CPU** (1 Thread)       | ~300 MB RAM      |
| **Gatilho**       | **openWakeWord**                         | `tflite` / `onnx`           | **INT8** (Padrão)                | **CPU** (Low Priority)   | ~150 MB RAM      |

### 📝 Notas de Engenharia:

- **Granite em Q8:** Optamos pela quantização Q8 (quase sem perda) em vez de Q4 porque o modelo é pequeno (1B). Com 4GB de VRAM, temos luxo de usar a melhor qualidade possível para maximizar a inteligência.
- **Whisper em Q5:** A versão Q5_K_M do Whisper Large v3 tem perda de precisão imperceptível para áudio, mas roda muito mais leve na CPU que a versão FP16.

---

## 2. Projeção de Latência (Pipeline de Streaming)

Esta tabela reflete o **"Time-to-First-Audio"** (Tempo até o usuário ouvir o primeiro som), considerando o processamento paralelo (Streaming).

**Cenário:** Usuário termina uma frase de comando médio.

| Sequência | Ação do Sistema              | Duração (ms) | Status do Processamento                                                  |
| --------- | ---------------------------- | ------------ | ------------------------------------------------------------------------ |
| **T0**    | Usuário para de falar.       | 0 ms         | O Whisper já processou 95% da frase durante a fala.                      |
| **T1**    | **VAD (Janela de Silêncio)** | +300 ms      | Sistema aguarda para confirmar que não é apenas uma pausa para respirar. |
| **T2**    | **Whisper (Finalização)**    | +50 ms       | Processa os últimos tokens e pontuação final.                            |
| **T3**    | **RAG (Busca Vetorial)**     | +30 ms       | BGE-M3 busca o contexto na RAM (instrução matemática rápida).            |
| **T4**    | **LLM (Primeiro Token)**     | +50 ms       | Granite (na GPU) gera a primeira palavra da resposta.                    |
| **T5**    | **Piper (Buffer Inicial)**   | +100 ms      | Gera o áudio da primeira frase/trecho e envia para a saída.              |
| **TOTAL** | **Latência Percebida**       | **~530 ms**  | **Sensação de conversa natural fluida.**                                 |

---

## 3. Gestão de Memória da GPU (O "Fit" na GTX 1650)

Cálculo de segurança para garantir que o sistema não trave por falta de memória de vídeo (OOM - Out of Memory).

- **VRAM Total Disponível:** 4096 MB (4 GB)
- **Reserva do Sistema (Windows/Monitor):** -600 MB
- **Modelo Granite 4.0 (Q8_0):** -1300 MB
- **Contexto KV Cache (Mamba-2 Linear):** -300 MB (Mesmo com textos longos)
- **Buffers de Inferência (CUDA):** -400 MB
- **Margem de Segurança (Livre):** **~1.5 GB**

**Conclusão:** O sistema roda com "folga" na GPU, garantindo que não haverá _swapping_ para a RAM (o que mataria a performance).

---

Este documento está salvo e registrado. Podemos prosseguir com o **DOC 02 (Scripting e Mineração de Dados)** agora?
