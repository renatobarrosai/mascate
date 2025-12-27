Com certeza. Este documento é fundamental porque define a **filosofia do produto** e a **arquitetura de segurança**, separando o que é responsabilidade da IA do que é regra de negócio.

Aqui está o documento consolidado, pronto para ser salvo como `estrategia_produto_seguranca.md`.

---

```markdown
# Documento de Estratégia de Produto e Segurança (PoC)

**Projeto:** Assistente de Controle Local (PoC)
**Foco:** Definição de Escopo, Responsabilidades da IA e Segurança Operacional.
**Data:** 21/12/2025

---

## 1. Filosofia de Arquitetura: Cérebro vs. Guarda-Costas

Ao contrário da abordagem anterior (onde travávamos a IA em formulários rígidos), adotamos uma postura onde a IA tem liberdade interpretativa, controlada por uma camada de segurança lógica.

### A. O Papel do Granite (O Cérebro Proativo)

- **Função:** Intérprete Soberano.
- **Responsabilidade:** Receber o pedido vago do usuário, consultar a base de conhecimento (RAG) para entender o contexto técnico e gerar o comando exato.
- **Diferencial:** Não hardcodamos "if/else" para cada programa. O Granite deve deduzir que "Quero ver meus processos" significa "Abrir o terminal e rodar htop", baseado na documentação que ele leu.

### B. O Papel do Python (O Guarda-Costas / Firewall)

- **Função:** Executor Cego e Blindagem.
- **Responsabilidade:** Receber o comando gerado pelo Granite e validar **RISCO**, não semântica.
- **Lógica:** O Python não julga _por que_ o usuário quer deletar uma pasta. Ele julga _se_ deletar uma pasta é perigoso. Se for, ele bloqueia e exige confirmação explícita (física ou verbal).

---

## 2. Escopo da PoC: A Estratégia de Pareto (80/20)

Para a Prova de Conceito, abandonamos nichos específicos (Arch/Hyprland) para focar no padrão de mercado (Ubuntu/Gnome), visando cobrir 80% do uso diário com 20% de esforço de mapeamento.

### Os 4 Pilares Universais

O sistema deve dominar estas quatro áreas sem falhas:

1.  **Navegador (A Janela do Mundo):**
    - _Apps:_ Chrome, Firefox.
    - _Ações:_ Abrir URL, Pesquisar (Google/YouTube), Gerenciar Abas, Histórico.
    - _Meta:_ "Abre o G1" ou "Pesquisa receita de bolo" deve ser instantâneo.

2.  **Mídia (Controle Global):**
    - _Apps:_ Spotify, YouTube Music, VLC.
    - _Ações:_ Play, Pause, Próximo, Anterior, Volume (Up/Down/Mute).
    - _Estratégia:_ Mapear teclas globais de mídia (`XF86AudioPlay`), tornando o controle agnóstico ao player que está rodando.

3.  **Gestão de Arquivos (Básico):**
    - _Apps:_ Nautilus (Gnome Files).
    - _Ações:_ Navegar entre pastas (Home, Downloads), Copiar, Mover, Abrir Arquivos.
    - _Limite:_ Operações complexas de sistema de arquivos ficam para o terminal, se solicitadas.

4.  **Ciclo de Vida de Apps:**
    - _Ações:_ Lançar aplicativos, Fechar janelas, Alternar foco (`Alt+Tab`).

---

## 3. Escalabilidade: Ingestão de Conhecimento (RAG)

Para evitar que o desenvolvimento se torne infinito (mapear cada software do mundo), o sistema será projetado para **aprender via documentação**.

- **O Mecanismo:** O sistema não "sabe" usar o Git ou o Photoshop nativamente. Ele sabe "ler manuais".
- **A Feature:** O usuário (ou nós, no setup) fornece arquivos Markdown/PDF com a lista de atalhos ou comandos de uma ferramenta nova.
- **O Resultado:** O Granite ingere isso no Banco Vetorial (ChromaDB) e passa a suportar a ferramenta imediatamente via busca semântica.
  - _Exemplo:_ Inserimos `git_cheat_sheet.md`. O usuário pede: "Dá um push aí". O Granite busca no vetor, acha `git push`, e executa.

---

## 4. Protocolo de Segurança (Anti-Alucinação)

Para garantir que a "Inteligência" não destrua o sistema do usuário, estabelecemos as seguintes travas no código Python executor:

1.  **Blacklist de Comandos Críticos:**
    - Comandos que envolvem deleção recursiva (`rm -rf`), formatação (`mkfs`, `fdisk`), sobrescrita de disco (`dd`) ou alteração de permissões globais (`chmod 777 /`).
2.  **Confirmação Explícita:**
    - Qualquer comando que caia na Blacklist **pára a execução**.
    - O sistema verbaliza o risco: _"Este comando vai apagar arquivos permanentemente. Confirma?"_
    - Exige input positivo (Voz: "Sim, confirmo" ou Teclado).
3.  **Isolamento de Usuário:**
    - O sistema roda estritamente no nível de permissão do usuário (`user space`). Acesso `sudo` só será permitido em modos avançados com dupla verificação.

---

## 5. Resumo do Valor para o Investidor

Com esta estratégia, o Pitch muda:

- **Não vendemos:** Um assistente que sabe abrir o Chrome.
- **Vendemos:** Um orquestrador seguro que aprende a usar qualquer ferramenta que você documentar, rodando 100% local, protegendo seus dados e seu sistema.
```

---

**Próximo Passo:**
Documento salvo! Agora temos a base estratégica. Quando você quiser retomar o desenvolvimento prático, o próximo passo lógico será criarmos o primeiro arquivo de conhecimento (`ubuntu_basics.md`) para testar se o Granite consegue ler esse manual e entender os comandos dos "4 Pilares".
