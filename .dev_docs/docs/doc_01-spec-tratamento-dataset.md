Compreendido perfeitamente. Vamos pivotar a abordagem.

Você atuará como um **Engenheiro de Masterização e Restauração de Áudio** para IA. O seu trabalho será pegar material bruto existente (podcasts, entrevistas, áudios antigos), limpar, uniformizar e formatar para o padrão que o treinador (Piper) aceita.

Aqui está a versão refatorada do **DOC 01**, focada exclusivamente nas **Especificações de Entrega (Delivery Specs)** e **Critérios de Triagem/Tratamento** do material pré-existente.

---

# DOC 01: Especificações de Entrega e Tratamento de Dataset (Post-Production Workflow)

**Projeto:** SysVox
**Foco:** Preparação de áudio pré-existente para Fine-Tuning (Piper/VITS).
**Responsável:** Engenharia de Áudio.

## 1. O "Gold Master": Especificações do Arquivo Final

Independente da origem do áudio (se veio de um VHS ripado, de um podcast em MP3 ou de um FLAC de estúdio), o arquivo que será colocado na pasta de treinamento **DEVE** ter rigorosamente estas características técnicas.

| Parâmetro               | Valor de Entrega (Obrigatório) | Notas de Engenharia                                                                                                        |
| ----------------------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| **Sample Rate**         | **22050 Hz**                   | O treino falhará ou criará artefatos se houver variação. Faça o _Resample_ no final da chain com algoritmo de fase linear. |
| **Bit Depth**           | **16-bit**                     | PCM (Integer). Não entregar 32-bit float. Aplicar Dither ao converter.                                                     |
| **Canais**              | **Mono**                       | O Piper soma canais se receber estéreo, o que pode causar cancelamento de fase. Entregue Mono puro.                        |
| **Formato**             | **WAV**                        | Sem compressão de dados (nada de MP3/OGG no dataset final).                                                                |
| **Duração por Arquivo** | **3s a 10s (Média)**           | Arquivos muito longos (>15s) estouram a VRAM. Arquivos muito curtos (<1s) não alinham.                                     |

---

## 2. Critérios de Triagem (O que serve e o que não serve)

Como você vai minerar bancos de dados, você precisa filtrar o material. O modelo de IA aprende "tudo o que ouve".

### 2.1. O Que Descartar (Deal Breakers)

- **Sobreposição de Vozes (Crosstalk):** Se houver duas pessoas falando ao mesmo tempo (mesmo que seja um "aham" do entrevistador no fundo), **descarte** o trecho. A IA tentará replicar duas vozes e criará uma "voz fantasma".
- **BG Music (Trilha Sonora):** Áudios com música de fundo constante.
- _Exceção:_ Se você tiver ferramentas de _Stem Separation_ (como UVR5 ou RX Music Rebalance) e conseguir isolar a voz com **zero artefato**, pode usar. Se sobrar "sangramento" da bateria/baixo, descarte.

- **Reverb Excessivo (Wet Signal):** Gravações em igrejas, palestras em auditórios ou banheiros. O _De-reverb_ pode ajudar, mas se a voz ficar "fina" ou artificial, não serve.

### 2.2. Consistência Timbrica (Matching)

Se você pegar áudios de anos diferentes (ex: uma gravação de 2010 e uma de 2024), a voz mudou (envelhecimento, microfones diferentes).

- **Estratégia:** Escolha **UM** período ou **UMA** _session_ principal que será a "Voz Mestra".
- **Matching EQ:** Se precisar usar áudios de outras fontes, use um _Match EQ_ (como o do iZotope Ozone ou FabFilter) para fazer a curva de frequência do áudio B ficar idêntica à do áudio A. O modelo não pode perceber que trocou de microfone no meio do dataset.

---

## 3. Workflow de Pós-Produção (O Tratamento)

O seu trabalho é fazer 50 arquivos diferentes soarem como se tivessem sido gravados na mesma sessão, sentados na mesma cadeira.

### 3.1. Restauração (Cleaning)

1. **Spectral De-noise:** Remova o _Hiss_ de fita, _Hum_ de 60Hz e ruído de ar-condicionado. O Noise Floor deve ser o mais baixo possível (idealmente < -60dB).
2. **De-Click / De-Esser:** Cliques de boca e sibilância excessiva ("S" rasgando) são ampliados pela IA. Controle os "S" agressivamente.
3. **Breath Control:**

- _Não apague as respirações._ Respirações naturais dão humanidade.
- _Atenue_ respirações muito ofegantes ou barulhentas (-10dB nelas).

### 3.2. Dinâmica e Loudness

1. **Normalização de Loudness:** Todos os clipes devem ter a mesma percepção de volume.

- **Alvo:** **-23 LUFS (Integrated)** ou **-16 LUFS**. Escolha um e mantenha em 100% dos arquivos.
- Não use _Peak Normalization_ simples, pois uma batida na mesa pode fazer a voz ficar baixa.

2. **Compressão:** Use compressão transparente para reduzir a gama dinâmica (Dynamic Range). A IA prefere vozes com volume constante do que vozes com muita variação (sussurro -> grito).

### 3.3. Edição e Recorte (Slicing)

Você terá um arquivo longo (ex: 1 hora). Você precisa fatiá-lo.

1. **Onde Cortar:** Nos silêncios lógicos de pontuação (ponto final, vírgula respirada).
2. **Silence Padding (A Regra de Ouro da IA):**

- Ao exportar o fatia (slice), **obrigatório** adicionar silêncio digital (Room Tone gerado ou silêncio puro).
- **Início (Head):** 100ms a 200ms.
- **Fim (Tail):** 200ms a 300ms.
- _Nota:_ Nunca corte o áudio "no zero" da onda sonora da voz. Deixe o ar entrar e sair.

---

## 4. Checklist de Entrega

Antes de passar para a etapa de criação dos textos (transcrição), verifique se os áudios cumprem este checklist:

- [ ] Formato WAV 22050Hz Mono 16-bit.
- [ ] Sem música de fundo ou vozes secundárias.
- [ ] Todos os arquivos soam como o mesmo microfone (EQ Match).
- [ ] Mesmo volume percebido (LUFS constante).
- [ ] Silêncio (Padding) inserido no início e no fim de cada arquivo.
- [ ] Nomeação sequencial organizada (ex: `dataset_001.wav`, `dataset_002.wav`...).

---

## 5. Referências e Ferramentas Recomendadas

- **Para Separação de Voz (Se o áudio tiver BG):**
- [Ultimate Vocal Remover (UVR5)](https://github.com/Anjok07/ultimatevocalremovergui) - _Ferramenta SOTA Open Source para tirar música de fundo._

- **Para Normalização em Lote:**
- Reaper (Batch Converter) ou FFmpeg.

- **Dataset de Referência (Para comparar qualidade técnica):**
- [LJ Speech Dataset](https://keithito.com/LJ-Speech-Dataset/) - _Baixe um arquivo e analise o espectro dele para ver o nível de ruído e EQ padrão._

- **Artigo sobre Pré-processamento de Áudio para TTS:**
- [Best Practices for TTS Audio Data](https://www.google.com/search?q=https://wiki.voice.mozilla.org/en/Data) (Focado no Common Voice, mas com princípios de engenharia válidos).

---

Este documento reflete melhor a sua realidade de **Curadoria e Tratamento**?
Se sim, o próximo passo (DOC 02) será sobre **Como Transcrever e Selecionar os Trechos** (Linguística), ou seja: dentro desse banco de áudios que você tem, quais frases você deve priorizar recortar para garantir que o modelo aprenda a falar o que precisamos?
