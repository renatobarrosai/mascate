# Mascate - Comandos Agnosticos

**Versao:** 1.0  
**Status:** Aprovado para Implementacao

Este documento define a estrategia de comandos agnosticos e hierarquia de execucao.

---

## 1. O Problema da Fragmentacao

Para cumprir a promessa de sistema rapido (<500ms) e expansivel, nao podemos depender de:

- Comandos especificos de aplicativos (ex: `firefox`, `gnome-calculator`)
- Simulacao visual (mouse), que e lenta e fragil

**Desafio:** Controlar o SO de forma que o codigo funcione independente da interface grafica (Gnome, KDE, XFCE) ou, futuramente, do OS.

---

## 2. A Solucao: Abstracão via Standards

Adotamos **Comandos de Intencao**. Em vez de dizer ao sistema _qual programa_ usar, dizemos _o que queremos fazer_, e deixamos o OS decidir a ferramenta padrao.

### Vantagens

| Vantagem          | Descricao                                           |
| :---------------- | :-------------------------------------------------- |
| **Velocidade**    | Execucao direta no Kernel/API (<5ms)                |
| **Feedback**      | Exit Codes (0 ou 1) indicam sucesso/falha           |
| **Portabilidade** | Mesmo comando logico funciona em diferentes distros |

---

## 3. Hierarquia de Execucao

### Nivel 1: Comandos Nativos Agnosticos (Prioridade Maxima)

Sao "wrappers" universais do sistema. Devem cobrir 90% das acoes da PoC.

| Acao                 | Comando Linux             | Por que usar?                          |
| :------------------- | :------------------------ | :------------------------------------- |
| **Abrir URL**        | `xdg-open [url]`          | Abre o navegador padrao                |
| **Abrir Pasta**      | `xdg-open [caminho]`      | Abre o gerenciador de arquivos correto |
| **Abrir Arquivo**    | `xdg-open [arquivo]`      | Abre no app padrao do usuario          |
| **Midia Play/Pause** | `playerctl play-pause`    | Controla qualquer player via MPRIS     |
| **Midia Next/Prev**  | `playerctl next/previous` | Funciona mesmo minimizado              |
| **Volume**           | `pactl` ou `wpctl`        | Controle direto no servidor de audio   |

### Nivel 2: Atalhos de Teclado (Fallback)

Usados apenas quando nao existe comando de terminal.

- **Ferramenta:** `ydotool`
- **Casos de Uso:**
  - Mudar de aba no navegador (`Ctrl + Tab`)
  - Mutar microfone no Google Meet (`Ctrl + D`)
  - Fechar janela (`Alt + F4`)

### Nivel 3: Visao e Mouse (Proibido na PoC)

Descartado devido a alta latencia e complexidade.

---

## 4. Mapeamento de Comandos

### 4.1. Aplicativos e Navegacao

```python
def execute_open_app(target: str) -> int:
    """Abre um aplicativo pelo nome."""
    return subprocess.run([target]).returncode

def execute_open_url(url: str) -> int:
    """Abre uma URL no navegador padrao."""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return subprocess.run(["xdg-open", url]).returncode

def execute_open_folder(path: str) -> int:
    """Abre uma pasta no gerenciador de arquivos."""
    path = os.path.expanduser(path)
    return subprocess.run(["xdg-open", path]).returncode
```

### 4.2. Controle de Midia

```python
def execute_media_play_pause() -> int:
    return subprocess.run(["playerctl", "play-pause"]).returncode

def execute_media_next() -> int:
    return subprocess.run(["playerctl", "next"]).returncode

def execute_media_prev() -> int:
    return subprocess.run(["playerctl", "previous"]).returncode
```

### 4.3. Controle de Volume

```python
def execute_volume_up(percent: int = 5) -> int:
    return subprocess.run([
        "pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{percent}%"
    ]).returncode

def execute_volume_down(percent: int = 5) -> int:
    return subprocess.run([
        "pactl", "set-sink-volume", "@DEFAULT_SINK@", f"-{percent}%"
    ]).returncode

def execute_volume_mute() -> int:
    return subprocess.run([
        "pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"
    ]).returncode
```

### 4.4. Simulacao de Teclado

```python
def execute_key_press(keys: str) -> int:
    """Simula pressionamento de teclas via ydotool.

    Args:
        keys: Combinacao de teclas (ex: "ctrl+c", "alt+tab")
    """
    # Converter para formato ydotool
    key_map = {
        "ctrl": "29",  # KEY_LEFTCTRL
        "alt": "56",   # KEY_LEFTALT
        "shift": "42", # KEY_LEFTSHIFT
        # ... mais mapeamentos
    }
    return subprocess.run(["ydotool", "key", keys]).returncode
```

---

## 5. Dispatcher Central

```python
def dispatch(command: dict) -> tuple[bool, str]:
    """Despacha comando para o executor apropriado.

    Returns:
        Tuple de (sucesso, mensagem)
    """
    action = command["action"]
    target = command.get("target", "")

    executors = {
        "OPEN_APP": lambda: execute_open_app(target),
        "OPEN_URL": lambda: execute_open_url(target),
        "OPEN_FOLDER": lambda: execute_open_folder(target),
        "MEDIA_PLAY_PAUSE": execute_media_play_pause,
        "MEDIA_NEXT": execute_media_next,
        "MEDIA_PREV": execute_media_prev,
        "VOLUME_UP": execute_volume_up,
        "VOLUME_DOWN": execute_volume_down,
        "VOLUME_MUTE": execute_volume_mute,
        "KEY_PRESS": lambda: execute_key_press(target),
    }

    executor = executors.get(action)
    if not executor:
        return False, f"Acao desconhecida: {action}"

    exit_code = executor()

    if exit_code == 0:
        return True, f"{action} executado com sucesso"
    else:
        return False, f"{action} falhou (exit code: {exit_code})"
```

---

## 6. Dependencias de Sistema

| Pacote           | Arch (pacman) | Ubuntu (apt)       | Funcao               |
| :--------------- | :------------ | :----------------- | :------------------- |
| xdg-utils        | `xdg-utils`   | `xdg-utils`        | Abrir URLs/arquivos  |
| playerctl        | `playerctl`   | `playerctl`        | Controle de midia    |
| pulseaudio-utils | `pulseaudio`  | `pulseaudio-utils` | Controle de volume   |
| ydotool          | `ydotool`     | `ydotool`          | Simulacao de teclado |

---

## 7. Tratamento de Erros

```python
def handle_execution_result(success: bool, message: str, tts):
    if success:
        # Feedback positivo (opcional - pode ser silencioso)
        tts.speak("Pronto.")
    else:
        # Feedback de erro
        tts.speak(f"Nao consegui executar. {message}")
```

---

## Referencias

- [00-architecture-overview.md](./00-architecture-overview.md) - Arquitetura
- [07-security.md](./07-security.md) - Seguranca
- [02-pipeline-flow.md](./02-pipeline-flow.md) - Pipeline
