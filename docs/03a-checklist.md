# Mascate - Checklist de Desenvolvimento

**Versao:** 1.1  
**Ultima Atualizacao:** 2024-12-27

Este documento e um checklist rapido para acompanhamento diario do progresso.
Para detalhes completos, consulte [03-implementation-plan.md](./03-implementation-plan.md).

---

## Legenda

- ✅ Concluido
- 🔄 Em Progresso
- ⏳ Pendente
- ❌ Bloqueado

---

## FASE 0: Fundacao ✅

### Etapa 0.1: Estrutura do Projeto ✅

- [x] 0.1.1 Criar estrutura de diretorios
- [x] 0.1.2 Configurar pyproject.toml
- [x] 0.1.3 Configurar .gitignore
- [x] 0.1.4 Criar config.toml exemplo
- [x] 0.1.5 Criar README.md
- [x] 0.1.6 Criar AGENTS.md

### Etapa 0.2: Sistema de Configuracao ✅

- [x] 0.2.1 Criar dataclasses de config
- [x] 0.2.2 Implementar Config.load() com TOML
- [x] 0.2.3 Implementar validacao de paths
- [x] 0.2.4 Criar excecoes customizadas
- [x] 0.2.5 Criar sistema de logging

### Etapa 0.3: Dependencias de Sistema ✅

- [x] 0.3.1 Implementar detect_distro()
- [x] 0.3.2 Mapear pacotes por distro
- [x] 0.3.3 Implementar install_packages()
- [x] 0.3.4 Verificacao de ja instalados

### Etapa 0.4: Download de Modelos ✅

- [x] 0.4.1 Criar ModelSpec dataclass
- [x] 0.4.2 Definir lista de modelos
- [x] 0.4.3 Implementar download via HF Hub
- [x] 0.4.4 Implementar verificacao SHA256
- [x] 0.4.5 Adicionar progress bar (Rich)

### Etapa 0.5: CLI Base ✅

- [x] 0.5.1 Criar grupo de comandos Click
- [x] 0.5.2 Implementar comando `version`
- [x] 0.5.3 Implementar comando `check`
- [x] 0.5.4 Implementar comando `run`

### Teste E2E Fase 0 ✅

- [x] Clone + `uv sync` funciona
- [x] `mascate version` mostra versao
- [x] `mascate check` mostra deps
- [x] `install_deps.py` instala deps
- [x] `download_models.py` baixa modelos
- [x] Config carrega de TOML

---

## FASE 1: Pipeline de Áudio ⏳

### Etapa 1.1: Captura de Áudio ⏳

- [ ] 1.1.1 Criar classe AudioCapture
- [ ] 1.1.2 Implementar lista de dispositivos
- [ ] 1.1.3 Implementar callback de captura
- [ ] 1.1.4 Implementar buffer circular
- [ ] 1.1.5 Criar testes unitários

### Etapa 1.2: Wake Word Detection ⏳

- [ ] 1.2.1 Criar classe WakeWordDetector
- [ ] 1.2.2 Carregar modelo de wake word
- [ ] 1.2.3 Implementar processo de detecção
- [ ] 1.2.4 Implementar threshold configurável
- [ ] 1.2.5 Implementar callback de ativação
- [ ] 1.2.6 Criar testes unitários

### Etapa 1.3: Voice Activity Detection ⏳

- [ ] 1.3.1 Criar classe VADProcessor
- [ ] 1.3.2 Carregar modelo Silero
- [ ] 1.3.3 Implementar detecção de voz
- [ ] 1.3.4 Implementar detecção de silêncio
- [ ] 1.3.5 Implementar máquina de estados
- [ ] 1.3.6 Criar testes unitários

### Etapa 1.4: Speech-to-Text ⏳

- [ ] 1.4.1 Criar classe WhisperSTT
- [ ] 1.4.2 Carregar modelo Whisper
- [ ] 1.4.3 Implementar transcrição batch
- [ ] 1.4.4 Implementar pós-processamento
- [ ] 1.4.5 Implementar detecção de idioma
- [ ] 1.4.6 Criar testes unitários

### Etapa 1.5: Integração Pipeline ⏳

- [ ] 1.5.1 Criar classe AudioPipeline
- [ ] 1.5.2 Implementar fluxo de dados
- [ ] 1.5.3 Implementar eventos/callbacks
- [ ] 1.5.4 Criar testes de integração

### Teste E2E Fase 1

- [ ] Wake word ativa o sistema
- [ ] VAD detecta fim de fala
- [ ] Texto transcrito com precisão > 90%
- [ ] Latência < 200ms

---

## FASE 2: Cérebro e Memória ⏳

### Etapa 2.1: Base de Conhecimento ⏳

- [ ] 2.1.1 Criar classe KnowledgeBase
- [ ] 2.1.2 Implementar parser de Markdown
- [ ] 2.1.3 Implementar chunking de texto
- [ ] 2.1.4 Setup Qdrant local
- [ ] 2.1.5 Integrar BGE-M3 embeddings
- [ ] 2.1.6 Implementar ingestão de docs
- [ ] 2.1.7 Criar testes unitários

### Etapa 2.2: Busca RAG ⏳

- [ ] 2.2.1 Criar classe RAGRetriever
- [ ] 2.2.2 Implementar busca densa
- [ ] 2.2.3 Implementar busca esparsa (BM25)
- [ ] 2.2.4 Implementar fusão híbrida
- [ ] 2.2.5 Implementar formatação de contexto
- [ ] 2.2.6 Criar testes unitários

### Etapa 2.3: Gramáticas GBNF ⏳

- [ ] 2.3.1 Criar gramática base JSON
- [ ] 2.3.2 Criar gramática de comandos
- [ ] 2.3.3 Criar gramática de confirmação
- [ ] 2.3.4 Implementar loader de gramáticas
- [ ] 2.3.5 Criar testes de validação

### Etapa 2.4: Integração LLM ⏳

- [ ] 2.4.1 Criar classe GraniteLLM
- [ ] 2.4.2 Implementar carregamento de modelo
- [ ] 2.4.3 Implementar geração com GBNF
- [ ] 2.4.4 Implementar templates de prompt
- [ ] 2.4.5 Implementar streaming
- [ ] 2.4.6 Criar testes unitários

### Etapa 2.5: Integração Cérebro ⏳

- [ ] 2.5.1 Criar classe Brain
- [ ] 2.5.2 Implementar fluxo RAG → LLM
- [ ] 2.5.3 Implementar parser de resposta
- [ ] 2.5.4 Criar testes de integração

### Teste E2E Fase 2

- [ ] Query retorna docs relevantes
- [ ] LLM gera JSON válido 100%
- [ ] GBNF previne alucinações
- [ ] Latência RAG + LLM < 300ms

---

## FASE 3: Executor e Segurança ⏳

### Etapa 3.1: Parser de Comandos ⏳

- [ ] 3.1.1 Criar dataclass Command
- [ ] 3.1.2 Criar enum de ActionType
- [ ] 3.1.3 Criar CommandParser
- [ ] 3.1.4 Implementar validação de schema
- [ ] 3.1.5 Criar testes unitários

### Etapa 3.2: Camada de Segurança ⏳

- [ ] 3.2.1 Criar classe SecurityGuard
- [ ] 3.2.2 Implementar blacklist de comandos
- [ ] 3.2.3 Implementar whitelist de paths
- [ ] 3.2.4 Implementar detector de risk level
- [ ] 3.2.5 Implementar fluxo de confirmação
- [ ] 3.2.6 Criar testes unitários

### Etapa 3.3: Handlers de Comandos ⏳

- [ ] 3.3.1 Criar interface BaseHandler
- [ ] 3.3.2 Implementar AppHandler
- [ ] 3.3.3 Implementar BrowserHandler
- [ ] 3.3.4 Implementar MediaHandler
- [ ] 3.3.5 Implementar FileHandler
- [ ] 3.3.6 Implementar SystemHandler
- [ ] 3.3.7 Criar registry de handlers
- [ ] 3.3.8 Criar testes unitários

### Etapa 3.4: Integração Executor ⏳

- [ ] 3.4.1 Criar classe Executor
- [ ] 3.4.2 Implementar fluxo de execução
- [ ] 3.4.3 Implementar feedback de resultado
- [ ] 3.4.4 Criar testes de integração

### Teste E2E Fase 3

- [ ] LOW risk executam diretamente
- [ ] HIGH risk pedem confirmação
- [ ] CRITICAL são bloqueados
- [ ] Firefox abre com xdg-open
- [ ] playerctl controla mídia

---

## FASE 4: Feedback e Interface ⏳

### Etapa 4.1: Text-to-Speech ⏳

- [ ] 4.1.1 Criar classe PiperTTS
- [ ] 4.1.2 Carregar modelo pt-BR
- [ ] 4.1.3 Implementar síntese de áudio
- [ ] 4.1.4 Implementar playback
- [ ] 4.1.5 Implementar streaming
- [ ] 4.1.6 Criar templates de resposta
- [ ] 4.1.7 Criar testes unitários

### Etapa 4.2: Interface TUI ⏳

- [ ] 4.2.1 Criar HUD básico com Rich
- [ ] 4.2.2 Implementar indicador de estado
- [ ] 4.2.3 Implementar indicador de áudio
- [ ] 4.2.4 Implementar log em tempo real
- [ ] 4.2.5 Implementar diálogo de confirmação
- [ ] 4.2.6 Criar testes unitários

### Etapa 4.3: Orquestrador Principal ⏳

- [ ] 4.3.1 Criar enum de Estados
- [ ] 4.3.2 Criar classe Orchestrator
- [ ] 4.3.3 Implementar máquina de estados
- [ ] 4.3.4 Implementar loop principal
- [ ] 4.3.5 Implementar graceful shutdown
- [ ] 4.3.6 Integrar com CLI
- [ ] 4.3.7 Criar testes de integração

### Teste E2E Fase 4

- [ ] TTS fala claramente
- [ ] HUD mostra estados
- [ ] Fluxo completo funciona
- [ ] Ctrl+C fecha graciosamente

---

## FASE 5: Validação Final ⏳

### Etapa 5.1: Testes de Performance ⏳

- [ ] 5.1.1 Latência Wake Word < 50ms
- [ ] 5.1.2 Latência STT < 150ms
- [ ] 5.1.3 Latência LLM < 200ms
- [ ] 5.1.4 Latência total < 500ms
- [ ] 5.1.5 Uso de VRAM < 4GB

### Etapa 5.2: Testes de Estabilidade ⏳

- [ ] 5.2.1 1h contínuo sem crash
- [ ] 5.2.2 100 comandos seguidos
- [ ] 5.2.3 Edge cases tratados

### Etapa 5.3: Documentação e Demo ⏳

- [ ] 5.3.1 Documentação de instalação
- [ ] 5.3.2 Documentação de uso
- [ ] 5.3.3 Vídeo demo
- [ ] 5.3.4 Release notes

### Critérios de Aceite PoC

- [ ] Latência total < 500ms
- [ ] Precisão STT > 90%
- [ ] 0 crashes em 1h
- [ ] 4 pilares funcionando
- [ ] Documentação completa
- [ ] Demo gravado

---

## Resumo de Progresso

| Fase              | Status | Progresso |
| ----------------- | ------ | --------- |
| Fase 0: Fundacao  | ✅     | 100%      |
| Fase 1: Audio     | ⏳     | 0%        |
| Fase 2: Cerebro   | ⏳     | 0%        |
| Fase 3: Executor  | ⏳     | 0%        |
| Fase 4: Interface | ⏳     | 0%        |
| Fase 5: Validacao | ⏳     | 0%        |
| **Total**         | 🔄     | **~17%**  |

---

## Proximas Atividades (Backlog Imediato)

1. **1.1.1** - Criar classe AudioCapture
2. **1.1.2** - Implementar lista de dispositivos
3. **1.1.3** - Implementar callback de captura
4. **1.1.4** - Implementar buffer circular
5. **1.1.5** - Criar testes unitarios

---

_Atualizar este checklist conforme atividades sao concluidas._
