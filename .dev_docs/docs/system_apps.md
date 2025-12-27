Você tem **toda a razão**. Peço desculpas se fui "técnico demais" na solução anterior e acabei matando a alma do projeto.

Se travarmos o Granite apenas para preencher lacunas pré-definidas, ele vira um "Google Assistant" glorificado de 2016. O diferencial dele — e a razão dele ocupar quase 1GB da sua VRAM — é a capacidade de **inferir contexto**.

Se você diz "Roda o htop", o Granite tem que ter a "sacada" de que `htop` roda no terminal. Se você diz "Entra no G1", ele tem que saber que isso exige um navegador. Se programarmos `if "htop": open_terminal()`, perdemos a IA.

Vamos ajustar a rota para o que você propôs: **Granite Proativo com Suporte de RAG (Busca Semântica)**.

Aqui está o alinhamento do conceito baseado no seu feedback:

---

### 1. A Nova Lógica: RAG como "Córtex", Granite como "Executor"

A grande sacada que você trouxe é: **Não hardcodar o conhecimento, mas disponibilizá-lo.**

Em vez de ensinar ao Granite (via código ou gramática rígida) o que é cada coisa, nós damos a ele acesso a uma "colinha" (Manuais/Docs) via Busca Vetorial.

**O Fluxo Realista (Cenário do `htop`):**

1. **Usuário:** _"Abre o htop aí."_
2. **Sistema (Busca Semântica/RAG):**

- O sistema busca "htop" no banco vetorial (ChromaDB na RAM).
- **Retorno:** _"htop: visualizador de processos interativo em modo texto (CLI)."_

3. **Granite (Raciocínio):**

- _Prompt dinâmico:_ "O usuário quer 'htop'. O manual diz que é CLI. Logo, preciso do emulador de terminal."
- _Decisão:_ Gera o comando para o Ghostty rodar o htop.

4. **Ação:** Executa `ghostty -e htop`.

Isso elimina o `If/Else` infinito. Se amanhã você instalar o `btop` ou o `cmatrix` e colocar o manual no banco, o Granite já sabe o que fazer sem mudar uma linha de código.

---

### 2. O Escopo da PoC (Pés no Chão)

Concordo 100% em definir limites claros. Não dá para abraçar o mundo. Vamos focar no "Kit de Sobrevivência do Dev" e no "Uso Doméstico".

**O que entra na Base de Conhecimento (Docs .md para o RAG):**

#### A. O Básico (Navegação e Sistema)

- **Navegador:** Comandos para abrir URL, buscar no Google/YouTube.
- _Exemplo:_ "Entra no Youtube" -> `firefox https://youtube.com`

- **Gerenciador de Arquivos:** Abrir pastas (Home, Downloads, Projetos).
- **Janelas (Hyprland):** Fechar, mover, focar, tela cheia.

#### B. A Ferramenta de Trabalho (Dev)

- **Bash/Terminal:** Comandos essenciais (`ls`, `cd`, `mkdir`, `touch`, `cp`, `rm`).
- **Git:** Como você disse, é fácil. Jogamos a doc básica (`status`, `push`, `pull`, `commit`, `checkout`).
- **Stack Web:** Comandos de execução (`npm start`, `python main.py`, `docker-compose up`).

**O que fica DE FORA (por enquanto):**

- Edição de código complexa via voz ("Crie uma função em Python que faz X..."). Isso é para uma IDE, não para um OS Controller.
- Configuração profunda de sistema (mexer em drivers, kernels).

---

### 3. Ajuste Técnico: GBNF apenas para Sintaxe, não para Conteúdo

Só para clarificar: ainda usaremos o GBNF (aquela gramática), mas **apenas** para garantir que o Granite não esqueça de fechar uma aspas ou uma chave `{ }`. Não usaremos para limitar o vocabulário dele.

- **Antes (Errado):** `acao ::= "ABRIR" | "FECHAR"` (Limitava a inteligência).
- **Agora (Certo):** `acao ::= string` (O Granite escreve o que ele deduziu ser o certo baseada no RAG).

---

### Próximo Passo: Estruturar a "Memória"

Já que a estratégia agora é **Busca Semântica**, o nosso trabalho principal antes de codar é definir como entregamos a informação para ele.

Você mencionou "toda a documentação do git em .md". Isso é ótimo.

**Minha proposta de ação imediata:**
Podemos criar a estrutura de pastas da **Base de Conhecimento** que o sistema vai ler ao iniciar. Algo assim:

```text
/conhecimento
  /sistema
     hyprland_controls.md  (Como mover janelas, workspaces)
     system_apps.md        (Lista: Firefox é browser, Ghostty é terminal, Thunar é arquivos)
  /dev
     git_cheat_sheet.md    (Comandos git básicos)
     bash_basics.md        (Comandos unix básicos)
     web_stack.md          (npm, python, pip)

```

O que acha dessa estrutura? Se estiver de acordo, posso gerar um exemplo de como seria o conteúdo do `system_apps.md` para garantir que o Granite entenda a diferença entre "Terminal" e "Interface Gráfica" sem a gente precisar programar isso.
