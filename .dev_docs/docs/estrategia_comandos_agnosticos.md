# Estratégia Técnica: Comandos Agnósticos e Hierarquia de Execução

**Projeto:** Assistente de Controle Local (PoC)
**Módulo:** Executor / Camada de Sistema
**Data:** 21/12/2025

---

## 1. O Problema da Fragmentação

Para cumprir a promessa de um sistema rápido (< 1s) e expansível, não podemos depender de comandos específicos de aplicativos (ex: `firefox`, `gnome-calculator`) nem de simulação visual (mouse), que são lentos e frágeis.

O desafio é controlar o sistema operacional de forma que o código funcione independentemente da Interface Gráfica (Gnome, KDE, XFCE) ou, futuramente, do OS (Windows, Mac).

---

## 2. A Solução: Abstração via Standards (XDG & MPRIS)

Adotaremos o padrão de **Comandos de Intenção**. Em vez de dizer ao sistema _qual programa_ usar, dizemos _o que queremos fazer_, e deixamos o OS decidir a ferramenta padrão.

### Vantagens Técnicas:

1.  **Velocidade:** Execução direta no Kernel/API (< 5ms), sem depender da renderização gráfica.
2.  **Feedback:** Retorno de _Exit Codes_ (0 ou 1) permite ao assistente saber se o comando funcionou.
3.  **Portabilidade:** O mesmo comando lógico (`ABRIR_URL`) pode ser traduzido para `xdg-open` (Linux) ou `start` (Windows) sem mudar a inteligência do Granite.

---

## 3. Hierarquia de Execução (Ordem de Prioridade)

O Granite e o Python Executor devem buscar a solução nesta ordem:

### Nível 1: Comandos Nativos Agnósticos (Prioridade Máxima)

São "wrappers" universais do sistema. Devem cobrir 90% das ações da PoC.

| Ação                   | Comando Linux (Universal)     | Por que usar?                                                               |
| :--------------------- | :---------------------------- | :-------------------------------------------------------------------------- |
| **Abrir URL**          | `xdg-open [url]`              | Abre o navegador padrão (Chrome/Firefox/Edge) automaticamente.              |
| **Abrir Pasta**        | `xdg-open [caminho]`          | Abre o gerenciador de arquivos correto (Nautilus/Dolphin/Thunar).           |
| **Abrir Arquivo**      | `xdg-open [arquivo]`          | Abre o PDF/Imagem/Txt no app padrão do usuário.                             |
| **Mídia (Play/Pause)** | `playerctl play-pause`        | Controla Spotify, Chrome (YouTube), VLC ou qualquer player ativo via MPRIS. |
| **Mídia (Next/Prev)**  | `playerctl next` / `previous` | Funciona mesmo com o player minimizado.                                     |
| **Volume**             | `pactl` ou `wpctl`            | Controle direto no servidor de áudio (PulseAudio/PipeWire).                 |

### Nível 2: Atalhos de Teclado (Fallback)

Usados apenas quando não existe comando de terminal para a ação (ex: interagir _dentro_ de uma página web ou app proprietário fechado).

- **Ferramenta:** `ydotool` ou biblioteca Python `keyboard`.
- **Casos de Uso:**
  - Mudar de aba no navegador (`Ctrl + Tab`).
  - Mutar microfone no Google Meet (`Ctrl + D`).
  - Fechar janela (`Alt + F4`) - _se o comando de terminal falhar_.

### Nível 3: Visão e Mouse (Proibido na PoC)

- Descartado devido à alta latência e complexidade. O sistema não deve tentar "ver" botões para clicar.

---

## 4. Implementação na Base de Conhecimento (RAG)

Para que o Granite use essa estratégia, a documentação (`.md`) fornecida a ele não deve ensinar comandos específicos, mas sim os conceitos.

**Exemplo de Documentação Correta:**

> "Para abrir qualquer site ou arquivo, utilize a função de sistema 'OPEN'. Não tente adivinhar o nome do navegador."

**Tradução no Python (Executor):**

```python
if acao == "OPEN":
    subprocess.run(["xdg-open", alvo])
elif acao == "MEDIA_CONTROL":
    subprocess.run(["playerctl", alvo]) # alvo = play-pause, next, etc
```
