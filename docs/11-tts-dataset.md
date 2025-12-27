# 11. Especificacoes de Tratamento de Dataset para TTS

**Projeto:** Mascate
**Foco:** Preparacao de audio pre-existente para Fine-Tuning do Piper (VITS).
**Responsavel:** Engenharia de Audio.

---

## 1. Visao Geral

Este documento define as especificacoes tecnicas para tratamento de audio destinado ao fine-tuning do modelo TTS (Piper). O objetivo e transformar material bruto heterogeneo (podcasts, entrevistas, gravacoes antigas) em um dataset uniforme e de alta qualidade.

**Principio:** O modelo de IA aprende "tudo o que ouve". Qualidade do input determina qualidade do output.

---

## 2. Especificacoes do Arquivo Final ("Gold Master")

Independente da origem do audio, o arquivo final **DEVE** ter estas caracteristicas:

| Parametro       | Valor Obrigatorio | Notas Tecnicas                                                   |
| --------------- | ----------------- | ---------------------------------------------------------------- |
| **Sample Rate** | 22050 Hz          | Resample com algoritmo de fase linear. Variacao causa artefatos. |
| **Bit Depth**   | 16-bit PCM        | Integer, nao 32-bit float. Aplicar Dither ao converter.          |
| **Canais**      | Mono              | Piper soma canais se receber stereo (cancelamento de fase).      |
| **Formato**     | WAV               | Sem compressao (nada de MP3/OGG no dataset final).               |
| **Duracao**     | 3s a 10s (media)  | >15s estoura VRAM, <1s nao alinha corretamente.                  |

---

## 3. Criterios de Triagem

### 3.1. Deal Breakers (Descartar Imediatamente)

| Problema                  | Motivo                                            | Excecao                                   |
| ------------------------- | ------------------------------------------------- | ----------------------------------------- |
| **Sobreposicao de Vozes** | IA tenta replicar duas vozes, cria "voz fantasma" | Nenhuma                                   |
| **Musica de Fundo**       | Contamina o timbre da voz                         | Separacao de stems com UVR5 sem artefatos |
| **Reverb Excessivo**      | De-reverb deixa voz "fina" ou artificial          | De-reverb limpo sem artefatos             |

### 3.2. Consistencia Timbrica

Audios de periodos diferentes (2010 vs 2024) tem vozes diferentes (envelhecimento, microfones).

**Estrategia:**

1. Escolher **UM** periodo ou **UMA** sessao como "Voz Mestra"
2. Aplicar **Match EQ** em audios de outras fontes (iZotope Ozone, FabFilter)
3. Objetivo: modelo nao pode perceber troca de microfone

---

## 4. Workflow de Pos-Producao

**Objetivo:** 50 arquivos diferentes soarem como mesma sessao.

### 4.1. Restauracao (Cleaning)

| Etapa                 | Acao                                    | Parametros                            |
| --------------------- | --------------------------------------- | ------------------------------------- |
| **Spectral De-noise** | Remover Hiss, Hum 60Hz, ar-condicionado | Noise Floor < -60dB                   |
| **De-Click**          | Remover cliques de boca                 | Automatico com revisao                |
| **De-Esser**          | Controlar sibilancia ("S" rasgando)     | Agressivo (-6dB a -10dB em S)         |
| **Breath Control**    | Atenuar respiracoes ruidosas            | -10dB (NAO apagar, manter humanidade) |

### 4.2. Dinamica e Loudness

| Etapa                 | Especificacao                                                  |
| --------------------- | -------------------------------------------------------------- |
| **Normalizacao LUFS** | -23 LUFS (Integrated) OU -16 LUFS (escolher um e manter)       |
| **Compressao**        | Transparente, reduzir gama dinamica (voz constante > variacao) |

**NAO usar:** Peak Normalization simples (batida na mesa faz voz ficar baixa).

### 4.3. Edicao e Recorte (Slicing)

**Onde Cortar:** Silencios logicos (ponto final, virgula respirada).

**Silence Padding (Regra de Ouro):**

| Posicao           | Duracao       | Nota               |
| ----------------- | ------------- | ------------------ |
| **Inicio (Head)** | 100ms a 200ms | Deixar o ar entrar |
| **Fim (Tail)**    | 200ms a 300ms | Deixar o ar sair   |

**NUNCA** cortar no zero da onda sonora da voz.

---

## 5. Checklist de Entrega

Antes de passar para transcricao, verificar:

- [ ] Formato WAV 22050Hz Mono 16-bit
- [ ] Sem musica de fundo ou vozes secundarias
- [ ] Todos os arquivos soam como mesmo microfone (EQ Match)
- [ ] Mesmo volume percebido (LUFS constante)
- [ ] Silence Padding no inicio e fim de cada arquivo
- [ ] Nomeacao sequencial (`dataset_001.wav`, `dataset_002.wav`...)

---

## 6. Ferramentas Recomendadas

### Separacao de Voz

- **[Ultimate Vocal Remover (UVR5)](https://github.com/Anjok07/ultimatevocalremovergui)** - SOTA Open Source para remover musica de fundo

### Normalizacao em Lote

- **Reaper** (Batch Converter)
- **FFmpeg** (linha de comando)

### Referencia de Qualidade

- **[LJ Speech Dataset](https://keithito.com/LJ-Speech-Dataset/)** - Baixar e analisar espectro para comparar nivel de ruido e EQ

---

## 7. Proximos Passos

Apos tratamento do audio:

1. **Transcricao:** Criar arquivos de texto correspondentes
2. **Selecao Linguistica:** Priorizar frases que cubram fonemas do portugues
3. **Validacao:** Conferir alinhamento audio-texto

---

_Documento consolidado de `.dev_docs/docs/doc_01-spec-tratamento-dataset.md`_
