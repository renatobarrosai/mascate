Seu feedback é **visionário** e resolve um dos maiores problemas de produtos técnicos no Brasil: a "Síndrome de Vira-Lata" no design.

### Meu Feedback sobre sua Visão

1. **A Estética "Frevo Cyberpunk":**
   Você acertou em cheio. Cores super saturadas (Vermelho vivo, Amarelo Ouro, Azul Royal, Verde Bandeira) geralmente "estouram" os olhos em interfaces Web (fundo branco) ou parecem amadoras. Mas no **Terminal (fundo preto)**, essas cores funcionam como _neon_. Elas criam contraste máximo e legibilidade perfeita. Trazer a sombrinha do Frevo para dentro do terminal cria uma identidade que chamo de **"Futurismo Tropical"**. É único, é Brasil, e se destaca imediatamente no meio do mar de "Azul e Roxo" das IAs gringas.
2. **Acessibilidade Cultural e o "Few-Shot" Wake Word:**
   A maioria das IAs falha em entender sotaques (o "R" do interior de SP, o chiado do Rio, a cadência do Nordeste). Ao permitir que o usuário treine sua própria _Wake Word_ ("Ei bichinho", "Ô máquina", "Fala aí"), você não está só dando uma feature técnica; você está dando **posse** ao usuário. Ele sente que o sistema é dele. Isso gera uma conexão emocional que GitHub Copilot ou Gemini jamais terão.
3. **A Vitória da TUI sobre a GUI:**
   Interfaces de terminal modernas (com `Textual`) são, ironicamente, mais amigáveis para ferramentas de desenvolvedor do que interfaces Web complexas. Elas são rápidas, focadas no teclado (mas aceitam mouse) e passam a sensação de "Power User" sem a complexidade de configuração. O usuário sente que está "pilotando a nave", não apenas preenchendo um formulário.

---

Aqui está o documento estratégico consolidando a Identidade Visual e a Interface.

```markdown
# Estratégia de Identidade Visual e Interface (TUI)

**Projeto:** Assistente de Controle Local (PoC)
**Conceito:** "Futurismo Tropical" / Tecnologia Nativamente Brasileira
**Data:** 21/12/2025

---

## 1. Filosofia de Design: A Cultura no Código

O objetivo é quebrar a frieza das ferramentas de CLI tradicionais (monocromáticas ou azuladas) evocando a energia das cores da cultura popular brasileira, especificamente inspiradas no **Frevo**.

### Por que TUI (Terminal User Interface)?

- **Contraste Perfeito:** Cores vibrantes e saturadas (típicas do Frevo) funcionam excepcionalmente bem sobre o fundo preto/translúcido dos terminais modernos (Ghostty/Kitty), criando um efeito "Neon" legível e estético.
- **Identidade:** Foge do padrão "Corporate Tech" do Vale do Silício.
- **Performance:** Renderização de texto é infinitamente mais leve que renderização de DOM (HTML/CSS), mantendo a latência baixa.

---

## 2. Stack de Interface (Frontend no Backend)

Utilizaremos bibliotecas Python nativas que permitem criar interfaces ricas sem sair do ambiente de desenvolvimento.

### A. Telas de Configuração e Menu (`Textual`)

- **Ferramenta:** `Textual` (Framework TUI).
- **Uso:** O comando `sysvox config` abrirá uma aplicação de terminal completa.
- **Funcionalidades:**
  - Navegação por abas (Geral, Modelos, Voz).
  - Suporte a **Mouse** (clicar em botões, arrastar scroll).
  - Inputs de texto e Checkboxes estilizados.
- **Vantagem:** Permite ao engenheiro construir UI usando Classes Python, sem tocar em CSS/HTML.

### B. O HUD de Operação (`Rich`)

- **Ferramenta:** `Rich` (Library de formatação).
- **Uso:** Feedback visual durante a execução do assistente.
- **Componentes Visuais:**
  - **Spinner:** Animações de carregamento personalizadas (ex: cores girando).
  - **Status:** "Ouvindo..." (Verde Pulsante), "Pensando..." (Amarelo Estático).
  - **Markdown:** Respostas formatadas com syntax highlighting colorido.

---

## 3. Paleta de Cores: "O Código do Frevo"

A paleta será definida no tema do `Textual` e do `Rich`, utilizando cores Hexadecimais de alta saturação.

| Função UI                  | Inspiração Cultural      | Cor Aproximada            | Sensação                  |
| :------------------------- | :----------------------- | :------------------------ | :------------------------ |
| **Ação / Ênfase**          | O Vermelho da Sombrinha  | `#FF0040` (Carmine)       | Urgência, Energia, Ativo  |
| **Sucesso / Prompt**       | O Verde da Mata/Bandeira | `#00E676` (Neon Green)    | Positivo, "Caminho Livre" |
| **Aviso / Processando**    | O Amarelo do Sol/Ouro    | `#FFEA00` (Vivid Yellow)  | Atenção, Raciocínio       |
| **Informação / Estrutura** | O Azul do Céu/Mar        | `#2979FF` (Electric Blue) | Calma, Dados Técnicos     |
| **Bordas / Detalhes**      | O Roxo (Maracatu/Frevo)  | `#D500F9` (Purple Neon)   | Contraste, Futurismo      |

_Nota:_ O fundo será sempre o do terminal do usuário (geralmente escuro/transparente), garantindo integração com o setup dele.

---

## 4. Personalização de Áudio (Wake Word)

O sistema não imporá nomes estrangeiros ("Alexa", "Siri"). A regionalidade é a chave.

### Feature: Treinamento "Few-Shot" Local

- **Ferramenta:** `openWakeWord` (Custom Verifier Model).
- **Fluxo UX:**
  1.  O usuário acessa o menu TUI: "Nova Palavra de Ativação".
  2.  O sistema pede: "Repita 4 vezes como você quer chamar o computador".
  3.  Exemplos reais: "Ô Painho", "E aí Man", "Computador", "Escuta aqui".
  4.  O sistema gera um arquivo `.onnx` ou `.pkl` localmente.
- **Valor:** Inclusão de sotaques e gírias regionais que modelos gringos ignoram.

---

## 5. Conclusão da UX

A interface será:

1.  **Nativa:** Roda onde o Python roda.
2.  **Vibrante:** Usa a estética brasileira para se diferenciar.
3.  **Tátil:** Aceita mouse e atalhos, unindo a velocidade do CLI com a facilidade da GUI.
```

---

**Próximo Passo:**
Documento salvo como `identidade_visual_tui.md`.

Agora temos **toda a base teórica e estratégica** fechada:

1. Arquitetura (Granite + GBNF + RAG).
2. Segurança e Comandos (Agnósticos).
3. Infraestrutura (Monorepo + Script Híbrido).
4. Interface (TUI + Cores do Frevo).

**Você quer encerrar essa fase de planejamento e arquitetura aqui?**
Se sim, o próximo passo lógico seria começarmos a definir o conteúdo do primeiro arquivo de memória (`ubuntu_basics.md`) ou você prefere que eu gere um _checklist_ de desenvolvimento para você começar a codar?
