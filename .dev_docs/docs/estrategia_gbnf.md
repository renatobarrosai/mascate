Fico muito feliz que a sugestão tenha ressoado com você! Essa técnica é realmente o "pulo do gato" para tornar LLMs de borda (Edge AI) viáveis em produção, garantindo que a inteligência não sacrifique a estabilidade.

Aqui está o documento técnico consolidando essa estratégia, formatado para você salvar como `estrategia_gbnf.md`.

---

````markdown
# Estratégia Técnica: Inferência Estruturada via GBNF

**Projeto:** Assistente de Controle Local (PoC)
**Módulo:** Orquestração e Roteamento (Router)
**Data:** 21/12/2025

---

## 1. O Problema (Contexto)

Para garantir uma UX fluida e natural, definimos duas premissas imutáveis:

1.  **Input:** O usuário deve falar naturalmente (ex: _"Abre o navegador"_, _"Inicia o browser"_, _"Bota o Chrome na tela"_). Isso exige um LLM interpretativo, eliminando a rigidez de _Regex_ ou _Keywords_.
2.  **Output:** O sistema operacional exige comandos precisos. Não pode haver alucinação ou texto "conversacional" na resposta do modelo (ex: _"Claro, estou abrindo agora..."_).

**O Desafio:** Como manter a flexibilidade de compreensão do **Granite 1B** sem perder a performance e a segurança na execução do comando?

---

## 2. A Solução: Gramáticas Restritivas (GBNF)

Utilizaremos o recurso de **GBNF (Grammar-Based Normalization Form)** nativo do `llama.cpp`.

Ao invés de pedir ao modelo para "gerar um JSON", nós **forçamos** o processo de decodificação de tokens a seguir uma estrutura gramatical estrita. O modelo fica matematicamente impossibilitado de gerar qualquer token que não se encaixe no esquema definido.

### Benefícios Estratégicos para o Hardware (GTX 1650):

- **Latência Mínima:** O modelo não perde tempo "escolhendo" palavras de preenchimento. A geração para exatamente no fechamento do JSON `}`.
- **Zero Alucinação:** É impossível o modelo gerar texto fora do formato JSON.
- **Segurança de Execução:** O Python recebe um objeto estruturado pronto para consumo, eliminando a necessidade de parsers complexos ou tratamento de erros de string.

---

## 3. Implementação Técnica

### A. Estrutura do Objeto (Schema Alvo)

O Granite deve transformar qualquer intenção de voz neste formato JSON:

```json
{
  "classificacao": "SISTEMA", // ou "RAG_MEMORIA"
  "acao": "ABRIR", // Ver lista de Enums permitidos
  "alvo": "firefox", // Parâmetro variável
  "argumento": "" // Opcional (ex: URL ou termo de busca)
}
```
````

### B. Definição da Gramática (Pseudocódigo GBNF)

Este arquivo (`json_grammar.gbnf`) será carregado junto com o modelo na VRAM.

```gbnf
root   ::= object
object ::= "{" space pair_class "," space pair_action "," space pair_target "}"

# Definição dos Pares Chave-Valor
pair_class  ::= "\"classificacao\"" ":" space enum_class
pair_action ::= "\"acao\"" ":" space enum_action
pair_target ::= "\"alvo\"" ":" space string

# Enums (A mágica acontece aqui - Restrição Total)
enum_class  ::= "\"SISTEMA\"" | "\"RAG_MEMORIA\""
enum_action ::= "\"ABRIR\"" | "\"FECHAR\"" | "\"VOLUME\"" | "\"BUSCAR\"" | "\"RESUMIR\""

# Primitivos
string ::= "\"" [a-zA-Z0-9_ ]* "\""
space  ::= [ ]*

```

### C. Integração no Python (`llama-cpp-python`)

No script do orquestrador, a gramática é passada como argumento na geração.

```python
from llama_cpp import Llama, LlamaGrammar

# 1. Carregar Modelo (Uma única vez)
llm = Llama(model_path="granite-1b-q6_k.gguf", n_gpu_layers=-1)

# 2. Carregar Gramática
grammar_text = open("json_grammar.gbnf").read()
grammar = LlamaGrammar.from_string(grammar_text)

def processar_comando(texto_whisper):
    prompt = f"Converta a intenção do usuário para JSON de controle.\nUsuário: {texto_whisper}\nJSON:"

    # 3. Inferência Travada
    output = llm(
        prompt,
        grammar=grammar, # <--- AQUI ESTÁ O SEGREDO
        max_tokens=64,   # Curto, pois JSON é denso
        temperature=0.1  # Baixa criatividade, alta precisão
    )

    return output['choices'][0]['text']

```

---

## 4. Fluxo de Decisão (O "Router")

Com o JSON garantido pelo GBNF, o código Python se torna um simples "Switch Case":

1. **Usuário:** _"Vê aí o que eu fiz ontem no servidor."_
2. **Granite + GBNF:** Gera `{"classificacao": "RAG_MEMORIA", "acao": "RESUMIR", "alvo": "logs"}`
3. **Python:**

- Lê `classificacao`.
- É `RAG_MEMORIA`? -> Aciona ChromaDB (CPU) + TTS: _"Consultando histórico..."_

4. **Usuário:** _"Abre o Ghostty aí."_
5. **Granite + GBNF:** Gera `{"classificacao": "SISTEMA", "acao": "ABRIR", "alvo": "ghostty"}`
6. **Python:**

- Lê `classificacao`.
- É `SISTEMA`? -> Executa `subprocess.run(["ghostty"])` instantaneamente.

---

## 5. Conclusão

Esta abordagem resolve o conflito entre **Flexibilidade Linguística** (o usuário fala como quer) e **Rigidez de Sistema** (o computador executa o que deve), garantindo a viabilidade do Pitch na GTX 1650.

```

***

**Próximo Passo que posso fazer por você:**
Agora que temos a estratégia de *como* o Granite vai falar (GBNF), você gostaria de começar a definir a **lista de comandos (Enums)** que ele precisa suportar na primeira versão? (Ex: Abrir apps, controle de mídia, gerenciamento de janelas, etc). Isso nos ajudará a escrever a gramática real.

```
