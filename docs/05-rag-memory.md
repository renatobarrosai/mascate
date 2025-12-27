# Mascate - Arquitetura RAG e Memoria

**Versao:** 1.0  
**Status:** Aprovado para Implementacao

Este documento define a estrategia de memoria e busca semantica (RAG).

---

## 1. Visao Geral

O sistema RAG permite que o Granite "aprenda" a usar ferramentas atraves de documentacao, sem precisar de fine-tuning.

### Divisao de Responsabilidades

- **Bibliotecario (Embedding - CPU):** Recebe a query, varre o banco vetorial, entrega o trecho exato do manual
- **Interprete (Granite - GPU):** Recebe o contexto "mastigado" + pedido do usuario, deduz a acao e gera JSON

---

## 2. Modelo de Embedding: BGE-M3

### Por que BGE-M3?

| Caracteristica            | Beneficio                                 |
| :------------------------ | :---------------------------------------- |
| **Janela de 8192 tokens** | Le manuais inteiros sem chunking complexo |
| **Busca Hibrida**         | Densa (semantica) + Esparsa (keywords)    |
| **Multilingual**          | Suporte nativo PT-BR                      |
| **SOTA**                  | Estado da arte em embeddings              |

### Especificacoes

| Propriedade    | Valor           |
| :------------- | :-------------- |
| Modelo         | BAAI/bge-m3     |
| Dimensao Densa | 1024            |
| Formato        | ONNX ou PyTorch |
| Alocacao       | CPU/RAM         |
| Consumo        | ~1.5 GB RAM     |
| Latencia       | ~200ms (CPU)    |

---

## 3. Banco Vetorial: Qdrant

### Por que Qdrant?

| Caracteristica           | Beneficio                                |
| :----------------------- | :--------------------------------------- |
| **Busca Hibrida Nativa** | Suporta saida do BGE-M3 diretamente      |
| **Local Mode**           | Roda sem Docker, como biblioteca Python  |
| **Rust Backend**         | Extremamente rapido                      |
| **Persistencia**         | Salva em SSD, sobrevive reinicializacoes |

### Especificacoes

| Propriedade  | Valor                |
| :----------- | :------------------- |
| Modo         | Local (in-process)   |
| Persistencia | `~/.mascate/qdrant/` |
| Indice       | HNSW + Sparse        |
| Collection   | `knowledge_base`     |

---

## 4. Hierarquia de Memoria (L1/L2/L3)

Gerenciamento inspirado em cache de CPUs para evitar OOM.

### L1: Contexto Imediato (VRAM - GPU)

- **Conteudo:** KV Cache do Granite (conversa atual)
- **Limite:** Janela deslizante de 2048 tokens
- **Comportamento:** Volatil, descarta mensagens antigas

### L2: Memoria de Trabalho (RAM - CPU)

- **Conteudo:** Indice Qdrant + Modelos (BGE-M3, Whisper)
- **Alocacao:** Ate 8GB reservados
- **Comportamento:** Carregado no boot para buscas instantaneas

### L3: Persistencia (SSD - Disco)

- **Conteudo:** Markdown originais, banco vetorial, logs
- **Comportamento:** Persistente, sobrevive reinicializacoes

---

## 5. Fluxo de Dados

```
Audio (Whisper)
      |
      v
    Texto
      |
      v
Embedding (BGE-M3)
      |
      v
Busca Vetorial (Qdrant)
      |
      v
Contexto Recuperado
      |
      v
Injeta no Prompt
      |
      v
Granite (Raciocinio)
      |
      v
    JSON
      |
      v
Executor Python
```

---

## 6. Integracao

### 6.1. Indexacao de Documentos

```python
from qdrant_client import QdrantClient
from FlagEmbedding import BGEM3FlagModel

# Inicializar
model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
client = QdrantClient(path="~/.mascate/qdrant")

# Processar documento
text = open("knowledge_base/ubuntu_basics.md").read()
embeddings = model.encode([text], return_dense=True, return_sparse=True)

# Indexar
client.upsert(
    collection_name="knowledge_base",
    points=[{
        "id": 1,
        "vector": {
            "dense": embeddings["dense"][0],
            "sparse": embeddings["sparse"][0]
        },
        "payload": {"text": text, "source": "ubuntu_basics.md"}
    }]
)
```

### 6.2. Busca Hibrida

```python
def search(query: str, top_k: int = 3):
    query_embedding = model.encode([query], return_dense=True, return_sparse=True)

    results = client.search(
        collection_name="knowledge_base",
        query_vector=query_embedding["dense"][0],
        sparse_vector=query_embedding["sparse"][0],
        limit=top_k
    )

    return [r.payload["text"] for r in results]
```

---

## 7. Base de Conhecimento

### Estrutura

```
knowledge_base/
+-- sistema/
|   +-- ubuntu_basics.md
|   +-- gnome_shortcuts.md
+-- apps/
|   +-- firefox.md
|   +-- spotify.md
+-- comandos/
    +-- navegacao.md
    +-- midia.md
```

### Formato dos Documentos

Documentos devem ensinar **conceitos**, nao comandos especificos:

```markdown
# Abrir URLs e Arquivos

Para abrir qualquer site ou arquivo, utilize a funcao de sistema 'OPEN'.
Nao tente adivinhar o nome do navegador.

## Exemplos

- "Abre o G1" -> OPEN_URL g1.com.br
- "Abre meus downloads" -> OPEN_FOLDER ~/Downloads
```

---

## 8. Escalabilidade

Para adicionar suporte a novas ferramentas:

1. Criar documento Markdown com comandos/atalhos
2. Executar script de ingestao
3. Sistema passa a suportar a ferramenta via busca semantica

**Exemplo:** Inserir `git_cheatsheet.md` -> Usuario pede "da um push ai" -> Granite busca, acha `git push`, executa.

---

## Referencias

- [00-architecture-overview.md](./00-architecture-overview.md) - Arquitetura geral
- [01-models-spec.md](./01-models-spec.md) - Especificacoes BGE-M3
- [06-gbnf-strategy.md](./06-gbnf-strategy.md) - Gramaticas GBNF
