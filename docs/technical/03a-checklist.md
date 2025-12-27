# Mascate - Checklist de Desenvolvimento

**Versao:** 1.2  
**Ultima Atualizacao:** 2024-12-27

Este documento e um checklist rapido para acompanhamento diario do progresso.
Para detalhes completos, consulte [03-implementation-plan.md](./03-implementation-plan.md).

---

## Legenda

- [x] Concluido
- [ ] Pendente
- [B] Bloqueado

---

## FASE 0: Fundacao [COMPLETA]

### Etapa 0.1: Estrutura do Projeto

- [x] 0.1.1 Criar estrutura de diretorios
- [x] 0.1.2 Configurar pyproject.toml
- [x] 0.1.3 Configurar .gitignore
- [x] 0.1.4 Criar config.toml exemplo
- [x] 0.1.5 Criar README.md
- [x] 0.1.6 Criar AGENTS.md

### Etapa 0.2: Sistema de Configuracao

- [x] 0.2.1 Criar dataclasses de config
- [x] 0.2.2 Implementar Config.load() com TOML
- [x] 0.2.3 Implementar validacao de paths
- [x] 0.2.4 Criar excecoes customizadas
- [x] 0.2.5 Criar sistema de logging

### Etapa 0.3: Dependencias de Sistema

- [x] 0.3.1 Implementar detect_distro()
- [x] 0.3.2 Mapear pacotes por distro
- [x] 0.3.3 Implementar install_packages()
- [x] 0.3.4 Verificacao de ja instalados

### Etapa 0.4: Download de Modelos

- [x] 0.4.1 Criar ModelSpec dataclass
- [x] 0.4.2 Definir lista de modelos
- [x] 0.4.3 Implementar download via HF Hub
- [x] 0.4.4 Implementar verificacao SHA256
- [x] 0.4.5 Adicionar progress bar (Rich)

### Etapa 0.5: CLI Base

- [x] 0.5.1 Criar grupo de comandos Click
- [x] 0.5.2 Implementar comando `version`
- [x] 0.5.3 Implementar comando `check`
- [x] 0.5.4 Implementar comando `run`

### Teste E2E Fase 0

- [x] Clone + `uv sync` funciona
- [x] `mascate version` mostra versao
- [x] `mascate check` mostra deps
- [x] `install_deps.py` instala deps
- [x] `download_models.py` baixa modelos
- [x] Config carrega de TOML

---

## FASE 1: Pipeline de Audio [COMPLETA]

### Etapa 1.1: Captura de Audio

- [x] 1.1.1 Criar classe AudioCapture
- [x] 1.1.2 Implementar lista de dispositivos
- [x] 1.1.3 Implementar callback de captura
- [x] 1.1.4 Implementar buffer circular
- [x] 1.1.5 Criar testes unitarios

### Etapa 1.2: Wake Word Detection

- [x] 1.2.1 Criar classe WakeWordDetector
- [x] 1.2.2 Carregar modelo de wake word (openWakeWord)
- [x] 1.2.3 Implementar processo de deteccao
- [x] 1.2.4 Implementar threshold configuravel
- [x] 1.2.5 Implementar callback de ativacao
- [ ] 1.2.6 Criar testes unitarios

### Etapa 1.3: Voice Activity Detection

- [x] 1.3.1 Criar classe VADProcessor
- [x] 1.3.2 Carregar modelo Silero (ONNX)
- [x] 1.3.3 Implementar deteccao de voz
- [x] 1.3.4 Implementar deteccao de silencio
- [x] 1.3.5 Implementar maquina de estados
- [x] 1.3.6 Corrigir chunk size (512 samples para Silero v5)
- [ ] 1.3.7 Criar testes unitarios

### Etapa 1.4: Speech-to-Text

- [x] 1.4.1 Criar classe WhisperSTT
- [x] 1.4.2 Carregar modelo Whisper (pywhispercpp)
- [x] 1.4.3 Implementar transcricao batch
- [x] 1.4.4 Implementar pos-processamento
- [x] 1.4.5 Implementar deteccao de idioma
- [ ] 1.4.6 Criar testes unitarios

### Etapa 1.5: Integracao Pipeline

- [x] 1.5.1 Criar classe AudioPipeline
- [x] 1.5.2 Implementar fluxo de dados
- [x] 1.5.3 Implementar eventos/callbacks
- [x] 1.5.4 Implementar chunking correto para VAD
- [ ] 1.5.5 Criar testes de integracao

### Teste E2E Fase 1

- [ ] Wake word ativa o sistema
- [ ] VAD detecta fim de fala
- [ ] Texto transcrito com precisao > 90%
- [ ] Latencia < 200ms

---

## FASE 2: Cerebro e Memoria [COMPLETA]

### Etapa 2.1: Base de Conhecimento

- [x] 2.1.1 Criar classe KnowledgeBase
- [x] 2.1.2 Implementar parser de Markdown
- [x] 2.1.3 Implementar chunking de texto
- [x] 2.1.4 Setup Qdrant local
- [x] 2.1.5 Integrar BGE-M3 embeddings
- [x] 2.1.6 Implementar ingestao de docs
- [ ] 2.1.7 Criar testes unitarios

### Etapa 2.2: Busca RAG

- [x] 2.2.1 Criar classe RAGRetriever
- [x] 2.2.2 Implementar busca densa
- [ ] 2.2.3 Implementar busca esparsa (BM25)
- [ ] 2.2.4 Implementar fusao hibrida
- [x] 2.2.5 Implementar formatacao de contexto
- [ ] 2.2.6 Criar testes unitarios

### Etapa 2.3: Gramaticas GBNF

- [x] 2.3.1 Criar gramatica base JSON
- [x] 2.3.2 Criar gramatica de comandos
- [ ] 2.3.3 Criar gramatica de confirmacao
- [x] 2.3.4 Implementar loader de gramaticas
- [ ] 2.3.5 Criar testes de validacao

### Etapa 2.4: Integracao LLM

- [x] 2.4.1 Criar classe GraniteLLM
- [x] 2.4.2 Implementar carregamento de modelo
- [x] 2.4.3 Implementar geracao com GBNF
- [x] 2.4.4 Implementar templates de prompt
- [x] 2.4.5 Implementar streaming
- [ ] 2.4.6 Criar testes unitarios

### Etapa 2.5: Integracao Cerebro

- [x] 2.5.1 Criar classe Brain
- [x] 2.5.2 Implementar fluxo RAG -> LLM
- [x] 2.5.3 Implementar parser de resposta
- [ ] 2.5.4 Criar testes de integracao

### Teste E2E Fase 2

- [ ] Query retorna docs relevantes
- [ ] LLM gera JSON valido 100%
- [ ] GBNF previne alucinacoes
- [ ] Latencia RAG + LLM < 300ms

---

## FASE 3: Executor e Seguranca [COMPLETA]

### Etapa 3.1: Parser de Comandos

- [x] 3.1.1 Criar dataclass Command
- [x] 3.1.2 Criar enum de ActionType
- [x] 3.1.3 Criar CommandParser
- [x] 3.1.4 Implementar validacao de schema
- [ ] 3.1.5 Criar testes unitarios

### Etapa 3.2: Camada de Seguranca

- [x] 3.2.1 Criar classe SecurityGuard
- [x] 3.2.2 Implementar blacklist de comandos
- [x] 3.2.3 Implementar whitelist de paths (path validation real)
- [x] 3.2.4 Implementar detector de risk level
- [x] 3.2.5 Implementar fluxo de confirmacao
- [x] 3.2.6 Implementar regex de shell injection robusto
- [ ] 3.2.7 Criar testes unitarios

### Etapa 3.3: Handlers de Comandos

- [x] 3.3.1 Criar interface BaseHandler
- [x] 3.3.2 Implementar AppHandler
- [x] 3.3.3 Implementar BrowserHandler
- [x] 3.3.4 Implementar MediaHandler
- [x] 3.3.5 Implementar FileHandler
- [x] 3.3.6 Implementar SystemHandler
- [x] 3.3.7 Criar registry de handlers
- [ ] 3.3.8 Criar testes unitarios

### Etapa 3.4: Integracao Executor

- [x] 3.4.1 Criar classe Executor
- [x] 3.4.2 Implementar fluxo de execucao
- [x] 3.4.3 Implementar feedback de resultado
- [ ] 3.4.4 Criar testes de integracao

### Teste E2E Fase 3

- [ ] LOW risk executam diretamente
- [ ] HIGH risk pedem confirmacao
- [ ] CRITICAL sao bloqueados
- [ ] Firefox abre com xdg-open
- [ ] playerctl controla midia

---

## FASE 4: Feedback e Interface [COMPLETA]

### Etapa 4.1: Text-to-Speech

- [x] 4.1.1 Criar classe PiperTTS
- [x] 4.1.2 Carregar modelo pt-BR
- [x] 4.1.3 Implementar sintese de audio
- [x] 4.1.4 Implementar playback
- [x] 4.1.5 Implementar streaming
- [x] 4.1.6 Criar templates de resposta
- [ ] 4.1.7 Criar testes unitarios

### Etapa 4.2: Interface TUI

- [x] 4.2.1 Criar HUD basico com Rich
- [x] 4.2.2 Implementar indicador de estado
- [x] 4.2.3 Implementar indicador de audio
- [x] 4.2.4 Implementar log em tempo real
- [x] 4.2.5 Implementar dialogo de confirmacao
- [ ] 4.2.6 Criar testes unitarios

### Etapa 4.3: Orquestrador Principal

- [x] 4.3.1 Criar enum de Estados (incluindo CONFIRMING)
- [x] 4.3.2 Criar classe Orchestrator
- [x] 4.3.3 Implementar maquina de estados
- [x] 4.3.4 Implementar loop principal
- [x] 4.3.5 Implementar graceful shutdown
- [x] 4.3.6 Integrar com CLI
- [x] 4.3.7 Integrar TTS ao orchestrator
- [x] 4.3.8 Implementar fluxo de confirmacao verbal
- [ ] 4.3.9 Criar testes de integracao

### Teste E2E Fase 4

- [ ] TTS fala claramente
- [ ] HUD mostra estados
- [ ] Fluxo completo funciona
- [ ] Ctrl+C fecha graciosamente

---

## FASE 5: Validacao Final [PENDENTE]

### Etapa 5.1: Testes de Performance

- [ ] 5.1.1 Latencia Wake Word < 50ms
- [ ] 5.1.2 Latencia STT < 150ms
- [ ] 5.1.3 Latencia LLM < 200ms
- [ ] 5.1.4 Latencia total < 500ms
- [ ] 5.1.5 Uso de VRAM < 4GB

### Etapa 5.2: Testes de Estabilidade

- [ ] 5.2.1 1h continuo sem crash
- [ ] 5.2.2 100 comandos seguidos
- [ ] 5.2.3 Edge cases tratados

### Etapa 5.3: Documentacao e Demo

- [ ] 5.3.1 Documentacao de instalacao
- [ ] 5.3.2 Documentacao de uso
- [ ] 5.3.3 Video demo
- [ ] 5.3.4 Release notes

### Criterios de Aceite PoC

- [ ] Latencia total < 500ms
- [ ] Precisao STT > 90%
- [ ] 0 crashes em 1h
- [ ] 4 pilares funcionando
- [ ] Documentacao completa
- [ ] Demo gravado

---

## Resumo de Progresso

| Fase              | Status | Progresso |
| ----------------- | ------ | --------- |
| Fase 0: Fundacao  | [DONE] | 100%      |
| Fase 1: Audio     | [DONE] | 90%       |
| Fase 2: Cerebro   | [DONE] | 85%       |
| Fase 3: Executor  | [DONE] | 95%       |
| Fase 4: Interface | [DONE] | 90%       |
| Fase 5: Validacao | [WIP]  | 0%        |
| **Total**         |        | **~75%**  |

---

## Proximas Atividades (Backlog Imediato)

1. Criar testes unitarios para modulos audio (wake, vad, stt)
2. Criar testes unitarios para modulos executor (handlers, security)
3. Implementar busca hibrida no RAG (BM25 + Dense)
4. Rodar testes E2E completos
5. Iniciar validacao de performance

---

## Bugs Corrigidos nesta Revisao

- [x] GBNF command.gbnf - quote faltando na rule action
- [x] VAD chunk size mismatch (512 vs 1024)
- [x] Dependencias faltantes no pyproject.toml
- [x] Shell injection regex incompleto
- [x] Protected paths usando substring match
- [x] Intent.raw_json passado incorretamente ao executor
- [x] Emojis hardcoded no HUD

---

_Atualizar este checklist conforme atividades sao concluidas._
