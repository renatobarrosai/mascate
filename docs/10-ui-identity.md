# Mascate - Identidade Visual e Interface

**Versao:** 1.0  
**Status:** Aprovado para Implementacao

Este documento define a estrategia de identidade visual e interface (TUI).

---

## 1. Filosofia de Design: Futurismo Tropical

O objetivo e quebrar a frieza das ferramentas CLI tradicionais, evocando a energia das cores da cultura popular brasileira, especificamente inspiradas no **Frevo**.

### Por que TUI?

| Vantagem               | Descricao                                             |
| :--------------------- | :---------------------------------------------------- |
| **Contraste Perfeito** | Cores vibrantes funcionam como neon sobre fundo preto |
| **Identidade**         | Foge do padrao "Corporate Tech"                       |
| **Performance**        | Renderizacao de texto e muito mais leve que HTML/CSS  |

---

## 2. Stack de Interface

### 2.1. Telas de Configuracao (`Textual`)

- **Framework:** `Textual`
- **Uso:** Comando `mascate config` abre aplicacao de terminal completa
- **Funcionalidades:**
  - Navegacao por abas (Geral, Modelos, Voz)
  - Suporte a mouse (clicar, scroll)
  - Inputs de texto e checkboxes estilizados

### 2.2. HUD de Operacao (`Rich`)

- **Framework:** `Rich`
- **Uso:** Feedback visual durante execucao
- **Componentes:**
  - **Spinner:** Animacoes de carregamento
  - **Status:** "Ouvindo...", "Pensando..."
  - **Markdown:** Respostas formatadas

---

## 3. Paleta de Cores: O Codigo do Frevo

| Funcao UI             | Inspiracao            | Cor Hex   | Sensacao                |
| :-------------------- | :-------------------- | :-------- | :---------------------- |
| **Acao/Enfase**       | Vermelho da Sombrinha | `#FF0040` | Urgencia, Energia       |
| **Sucesso/Prompt**    | Verde da Mata         | `#00E676` | Positivo, Caminho Livre |
| **Aviso/Processando** | Amarelo do Sol        | `#FFEA00` | Atencao, Raciocinio     |
| **Informacao**        | Azul do Ceu           | `#2979FF` | Calma, Dados Tecnicos   |
| **Bordas/Detalhes**   | Roxo do Maracatu      | `#D500F9` | Contraste, Futurismo    |

**Nota:** Fundo sempre do terminal do usuario (geralmente escuro/transparente).

---

## 4. Componentes da Interface

### 4.1. Indicador de Estado

```python
from rich.console import Console
from rich.spinner import Spinner

console = Console()

def show_state(state: str):
    states = {
        "IDLE": ("[dim]Aguardando...[/dim]", None),
        "LISTENING": ("[green]Ouvindo...[/green]", "dots"),
        "PROCESSING": ("[yellow]Pensando...[/yellow]", "dots2"),
        "SPEAKING": ("[blue]Falando...[/blue]", None),
    }

    text, spinner_type = states.get(state, ("[red]???[/red]", None))

    if spinner_type:
        with console.status(text, spinner=spinner_type):
            # ... aguardar mudanca de estado
            pass
    else:
        console.print(text)
```

### 4.2. Indicador de Amplitude

```python
from rich.progress import Progress, BarColumn

def show_amplitude(level: float):
    """Mostra nivel de audio (0.0 a 1.0)."""
    bar = "█" * int(level * 20) + "░" * (20 - int(level * 20))
    color = "green" if level < 0.7 else "yellow" if level < 0.9 else "red"
    console.print(f"[{color}]{bar}[/{color}]", end="\r")
```

### 4.3. Log de Comandos

```python
from rich.panel import Panel
from rich.table import Table

def show_command_log(command: dict, result: str):
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Acao", command["action"])
    table.add_row("Alvo", command.get("target", "-"))
    table.add_row("Resultado", result)

    console.print(Panel(table, title="Comando Executado", border_style="green"))
```

---

## 5. Personalizacao de Wake Word

O sistema nao impoe nomes estrangeiros. Regionalidade e a chave.

### Feature: Treinamento Few-Shot Local

- **Ferramenta:** `openWakeWord` (Custom Verifier Model)
- **Fluxo UX:**
  1. Usuario acessa menu TUI: "Nova Palavra de Ativacao"
  2. Sistema pede: "Repita 4 vezes como voce quer chamar o computador"
  3. Exemplos: "E ai Man", "Ei Painho", "Fala ai"
  4. Sistema gera arquivo `.onnx` localmente

### Wake Words Planejados

| Wake Word    | Origem              | Status         |
| :----------- | :------------------ | :------------- |
| "Hey Jarvis" | Padrao ingles       | Modelo base    |
| "Ei Painho"  | Nordestino          | Planejado      |
| "Ariano"     | Referencia cultural | Planejado      |
| Custom       | Usuario             | Few-shot local |

---

## 6. Layout do HUD

```
+----------------------------------------------------------+
|  MASCATE v0.1.0                                [IDLE]    |
+----------------------------------------------------------+
|                                                          |
|  [████████████░░░░░░░░]  Amplitude                       |
|                                                          |
|  > Ultimo comando: "abre o firefox"                      |
|  > Resultado: OPEN_APP firefox (sucesso)                 |
|                                                          |
+----------------------------------------------------------+
|  [Q] Sair  [C] Config  [H] Historico                     |
+----------------------------------------------------------+
```

---

## 7. Implementacao Textual (Config)

```python
from textual.app import App
from textual.widgets import Header, Footer, TabbedContent, TabPane
from textual.widgets import Input, Switch, Button

class MascateConfig(App):
    CSS = """
    TabbedContent {
        background: $surface;
    }
    """

    def compose(self):
        yield Header()
        with TabbedContent():
            with TabPane("Geral"):
                yield Input(placeholder="Wake Word")
                yield Switch("Feedback por voz")
            with TabPane("Modelos"):
                # ... configuracoes de modelos
                pass
            with TabPane("Voz"):
                # ... configuracoes de TTS
                pass
        yield Footer()
```

---

## 8. Acessibilidade

- **Alto Contraste:** Cores vibrantes sobre fundo escuro
- **Tamanho de Fonte:** Respeita configuracao do terminal
- **Navegacao por Teclado:** Completa, sem depender de mouse
- **Feedback Sonoro:** TTS para todas as acoes

---

## Referencias

- [00-architecture-overview.md](./00-architecture-overview.md) - Arquitetura
- [02-pipeline-flow.md](./02-pipeline-flow.md) - Pipeline
