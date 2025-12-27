# Mascate - Estrategia GBNF

**Versao:** 1.0  
**Status:** Aprovado para Implementacao

Este documento define a estrategia de inferencia estruturada via gramaticas GBNF.

---

## 1. O Problema

Para garantir UX fluida, temos duas premissas imutaveis:

1. **Input Flexivel:** Usuario fala naturalmente ("Abre o navegador", "Inicia o browser", "Bota o Chrome na tela")
2. **Output Rigido:** Sistema exige comandos precisos, sem alucinacoes ("Claro, estou abrindo agora...")

**Desafio:** Como manter flexibilidade de compreensao do Granite sem perder seguranca na execucao?

---

## 2. A Solucao: Gramaticas GBNF

Utilizamos **GBNF (Grammar-Based Normalization Form)** nativo do `llama.cpp`.

Ao inves de pedir ao modelo para "gerar um JSON", **forcamos** o processo de decodificacao a seguir uma estrutura gramatical estrita. O modelo fica matematicamente impossibilitado de gerar tokens fora do esquema.

### Beneficios

| Beneficio           | Descricao                                                                |
| :------------------ | :----------------------------------------------------------------------- |
| **Latencia Minima** | Modelo nao perde tempo "escolhendo" palavras. Para no fechamento do JSON |
| **Zero Alucinacao** | Impossivel gerar texto fora do formato                                   |
| **Seguranca**       | Python recebe objeto estruturado, sem parsers complexos                  |

---

## 3. Estrutura do JSON Alvo

O Granite deve transformar qualquer intencao de voz neste formato:

```json
{
  "action": "OPEN_APP",
  "target": "firefox",
  "args": null,
  "confidence": 0.95,
  "requires_confirmation": false
}
```

### Campos

| Campo                   | Tipo        | Descricao                                  |
| :---------------------- | :---------- | :----------------------------------------- |
| `action`                | Enum        | Acao a executar (OPEN_APP, VOLUME_UP, etc) |
| `target`                | String      | Alvo da acao (nome do app, URL, etc)       |
| `args`                  | String/null | Argumentos adicionais                      |
| `confidence`            | Float       | Confianca do modelo (0.0 a 1.0)            |
| `requires_confirmation` | Bool        | Se precisa confirmacao do usuario          |

---

## 4. Definicao da Gramatica GBNF

Arquivo `json_grammar.gbnf`:

```gbnf
root   ::= object
object ::= "{" space pairs "}"
pairs  ::= pair_action "," space pair_target "," space pair_args "," space pair_conf "," space pair_req

# Pares Chave-Valor
pair_action ::= "\"action\"" ":" space enum_action
pair_target ::= "\"target\"" ":" space string
pair_args   ::= "\"args\"" ":" space (string | "null")
pair_conf   ::= "\"confidence\"" ":" space number
pair_req    ::= "\"requires_confirmation\"" ":" space boolean

# Enums (Restricao Total)
enum_action ::= "\"OPEN_APP\""
             | "\"OPEN_URL\""
             | "\"OPEN_FOLDER\""
             | "\"VOLUME_UP\""
             | "\"VOLUME_DOWN\""
             | "\"VOLUME_MUTE\""
             | "\"MEDIA_PLAY_PAUSE\""
             | "\"MEDIA_NEXT\""
             | "\"MEDIA_PREV\""
             | "\"RUN_COMMAND\""
             | "\"KEY_PRESS\""
             | "\"UNKNOWN\""

# Primitivos
string  ::= "\"" [a-zA-Z0-9_./\-: ]* "\""
number  ::= [0-9] "." [0-9]+
boolean ::= "true" | "false"
space   ::= [ ]*
```

---

## 5. Integracao Python

```python
from llama_cpp import Llama, LlamaGrammar

# Carregar modelo (uma vez)
llm = Llama(
    model_path="models/llm/granite-4.0-hybrid-1b-instruct.Q8_0.gguf",
    n_gpu_layers=-1
)

# Carregar gramatica
grammar_text = open("grammars/json_grammar.gbnf").read()
grammar = LlamaGrammar.from_string(grammar_text)

def processar_comando(texto_whisper: str, contexto_rag: str) -> dict:
    prompt = f"""Voce e um assistente de sistema Linux.

## Contexto:
{contexto_rag}

## Pedido do Usuario:
{texto_whisper}

## Responda com JSON:
"""

    output = llm(
        prompt,
        grammar=grammar,  # <-- GBNF ativa
        max_tokens=64,
        temperature=0.1
    )

    import json
    return json.loads(output['choices'][0]['text'])
```

---

## 6. Fluxo de Decisao (Router)

Com JSON garantido pelo GBNF, o Python se torna um simples switch:

```python
def executar(comando: dict):
    action = comando["action"]
    target = comando["target"]

    if action == "OPEN_APP":
        subprocess.run([target])
    elif action == "OPEN_URL":
        subprocess.run(["xdg-open", f"https://{target}"])
    elif action == "MEDIA_PLAY_PAUSE":
        subprocess.run(["playerctl", "play-pause"])
    elif action == "VOLUME_UP":
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
    # ... etc
```

---

## 7. Lista de Acoes Suportadas

### Aplicativos

| Acao        | Descricao                  | Exemplo                 |
| :---------- | :------------------------- | :---------------------- |
| OPEN_APP    | Abrir aplicativo           | firefox, code, nautilus |
| OPEN_URL    | Abrir URL no navegador     | g1.com.br, youtube.com  |
| OPEN_FOLDER | Abrir pasta no gerenciador | ~/Downloads             |

### Midia

| Acao             | Descricao       | Traducao             |
| :--------------- | :-------------- | :------------------- |
| MEDIA_PLAY_PAUSE | Play/Pause      | playerctl play-pause |
| MEDIA_NEXT       | Proxima musica  | playerctl next       |
| MEDIA_PREV       | Musica anterior | playerctl previous   |

### Volume

| Acao        | Descricao       | Traducao     |
| :---------- | :-------------- | :----------- |
| VOLUME_UP   | Aumentar volume | pactl +5%    |
| VOLUME_DOWN | Diminuir volume | pactl -5%    |
| VOLUME_MUTE | Mutar/desmutar  | pactl toggle |

### Sistema

| Acao        | Descricao        | Exemplo         |
| :---------- | :--------------- | :-------------- |
| RUN_COMMAND | Executar comando | ls, git status  |
| KEY_PRESS   | Simular tecla    | ctrl+c, alt+tab |
| UNKNOWN     | Nao reconhecido  | -               |

---

## 8. Tratamento de UNKNOWN

Quando o modelo nao consegue classificar a intencao:

```python
if comando["action"] == "UNKNOWN":
    tts.speak("Nao entendi o que voce quer fazer. Pode repetir?")
    return
```

---

## Referencias

- [00-architecture-overview.md](./00-architecture-overview.md) - Arquitetura
- [01-models-spec.md](./01-models-spec.md) - Especificacoes Granite
- [07-security.md](./07-security.md) - Seguranca
