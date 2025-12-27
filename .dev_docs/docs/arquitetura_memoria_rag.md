Com certeza. Registrar essas decisões arquiteturais é fundamental, pois mudamos o "motor" do sistema (o modelo de Embedding) e definimos como vamos gerenciar os recursos escassos (VRAM) versus os abundantes (RAM/SSD).

Aqui está o documento técnico consolidado, pronto para ser salvo como `arquitetura_memoria_rag.md`.

---

```markdown
# Estratégia de Arquitetura de Memória e Inteligência (RAG)

**Projeto:** Assistente de Controle Local (PoC)
**Foco:** Definição do Modelo de Embedding, Fluxo de Dados e Hierarquia de Hardware.
**Data:** 21/12/2025

---

## 1. O Motor de Busca Semântica (Embedding)

Revisamos a decisão anterior (modelo leve) e optamos por um modelo **SOTA (State of the Art)**, aproveitando a capacidade de CPU (Ryzen 7) e RAM (32GB) do hardware alvo para maximizar a precisão.

- **Modelo Escolhido:** `BAAI/bge-m3` (Flagship).
- **Justificativa Técnica:**
  - **Janela de Contexto:** Suporta **8192 tokens**. Permite ler manuais inteiros sem necessidade de algoritmos complexos de "fatiamento" (chunking).
  - **Busca Híbrida:** Realiza busca Densa (significado) e Esparsa (palavras-chave) simultaneamente. Garante que termos técnicos ("Thunar", "Hyprland") sejam encontrados mesmo se o conceito for vago.
  - **Multilinguagem:** Suporte nativo e robusto ao Português Brasileiro.
- **Impacto no Hardware:**
  - **Alocação:** ~2.5GB de RAM (Sistema).
  - **Latência:** ~200ms na CPU (Aceitável para garantir a resposta correta).

---

## 2. Divisão de Responsabilidades (Quem faz o quê?)

Para viabilizar o uso do **Granite 1B (Modelo Pequeno)**, retiramos dele a responsabilidade de "saber" as coisas e deixamos apenas a responsabilidade de "raciocinar".

- **O Bibliotecário (Embedding - CPU):** Recebe o pedido do usuário, varre o banco vetorial e entrega o trecho exato do manual. Ele não interpreta a intenção, apenas a similaridade matemática.
- **O Intérprete (Granite - GPU):** Recebe o contexto "mastigado" pelo bibliotecário + o pedido do usuário. Sua função é deduzir a ação e formatar o JSON de saída.

**Fluxo de Dados:**
`Áudio (Whisper)` -> `Texto` -> `Embedding (bge-m3)` -> `Recuperação de Manual (ChromaDB)` -> `Injeção de Contexto` -> `Granite (Raciocínio)` -> `JSON` -> `Executor Python`.

---

## 3. Hierarquia de Memória (Estratégia L1/L2/L3)

Gerenciamento de recursos inspirado em cache de processadores para evitar estouro de VRAM (OOM) e garantir persistência.

### Nível L1: Contexto Imediato (VRAM - GPU)

- **Conteúdo:** KV Cache do Granite (A conversa atual e raciocínio instantâneo).
- **Limite:** Janela Deslizante (Sliding Window) de **2048 tokens**.
- **Comportamento:** Memória volátil. Se encher, descarta as mensagens mais antigas da sessão ativa.

### Nível L2: Memória de Trabalho (RAM - CPU)

- **Conteúdo:** Índice Vetorial do ChromaDB (HNSW) + Modelos Carregados (`bge-m3`, `Whisper`).
- **Alocação:** Até **8GB** reservados para o sistema (em máquinas de 32GB, isso deixa ampla margem).
- **Comportamento:** Carregado do disco no Boot para garantir buscas em milissegundos.

### Nível L3: Persistência (SSD - Disco)

- **Conteúdo:** Arquivos Markdown originais, Banco de Dados Vetorial (`chroma.sqlite3`) e Logs de Execução.
- **Comportamento:** Persistente. Novos manuais adicionados são vetorizados e salvos aqui. O sistema sobrevive a reinicializações sem perder conhecimento.

---

## 4. Definição de Limites (Resource Budget)

Para a PoC no hardware específico (Ryzen 7 + GTX 1650), definimos o perfil **"High Performance"**:

1.  **CPU:** Prioridade de processo elevada para o _Pipeline de Áudio_.
2.  **GPU:** Teto de 3.5GB de VRAM para o Granite (deixando 0.5GB para o OS).
3.  **Segurança:** Caso o sistema detecte hardware inferior no futuro (MVP), o código terá "flags" para reduzir a qualidade do Embedding e o tamanho do contexto automaticamente.
```

---

**Próximo Passo:**
Documento devidamente registrado!

Agora, podemos abordar os **"outros pontos cegos"** que você mencionou. O que mais precisamos definir antes de colocar a mão na massa? (Talvez o **VAD/Detecção de Silêncio** ou a **Gestão dos Downloads**?)
