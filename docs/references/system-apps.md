# Referencia: Aplicativos do Sistema

**Projeto:** Mascate
**Proposito:** Base de conhecimento para o RAG - mapeamento de aplicativos e suas categorias.

---

## 1. Conceito

Este documento serve como "colinha" para o Granite via busca semantica (RAG). Em vez de hardcodar conhecimento, disponibilizamos informacao estruturada que o LLM consulta para tomar decisoes.

**Fluxo:**

1. Usuario: "Abre o htop"
2. RAG busca "htop" no banco vetorial
3. Retorno: "htop: visualizador de processos interativo em modo texto (CLI)"
4. Granite raciocina: "CLI = preciso do terminal"
5. Acao: `ghostty -e htop` (ou terminal padrao)

---

## 2. Categorias de Aplicativos

### 2.1. Navegadores Web (GUI)

| App           | Comando         | Notas                        |
| ------------- | --------------- | ---------------------------- |
| Firefox       | `firefox`       | Navegador padrao Ubuntu      |
| Google Chrome | `google-chrome` | Alternativa popular          |
| Chromium      | `chromium`      | Versao open-source do Chrome |

**Acoes Comuns:**

- Abrir URL: `firefox https://example.com`
- Pesquisar: `firefox https://google.com/search?q=termo`

### 2.2. Terminais (CLI Host)

| App            | Comando          | Notas                            |
| -------------- | ---------------- | -------------------------------- |
| GNOME Terminal | `gnome-terminal` | Padrao Ubuntu/GNOME              |
| Ghostty        | `ghostty`        | Terminal moderno GPU-accelerated |
| Alacritty      | `alacritty`      | Terminal GPU-accelerated         |
| Kitty          | `kitty`          | Terminal com recursos avancados  |

**Executar Comando:**

- `gnome-terminal -- comando`
- `ghostty -e comando`

### 2.3. Gerenciadores de Arquivos (GUI)

| App      | Comando    | Notas                  |
| -------- | ---------- | ---------------------- |
| Nautilus | `nautilus` | Padrao GNOME ("Files") |
| Thunar   | `thunar`   | Padrao XFCE, leve      |
| Dolphin  | `dolphin`  | Padrao KDE             |

**Abrir Pasta:**

- Generico: `xdg-open ~/Downloads`
- Especifico: `nautilus ~/Downloads`

### 2.4. Players de Midia

| App       | Comando     | Tipo        | Notas            |
| --------- | ----------- | ----------- | ---------------- |
| Spotify   | `spotify`   | Musica      | Streaming        |
| VLC       | `vlc`       | Video/Audio | Player universal |
| Rhythmbox | `rhythmbox` | Musica      | Padrao GNOME     |

**Controle Universal (playerctl):**

```bash
playerctl play-pause  # Toggle play/pause
playerctl next        # Proxima faixa
playerctl previous    # Faixa anterior
playerctl volume 0.5  # Volume 50%
```

### 2.5. Ferramentas CLI

| App      | Categoria | Descricao                            |
| -------- | --------- | ------------------------------------ |
| htop     | Monitor   | Visualizador de processos interativo |
| btop     | Monitor   | Alternativa moderna ao htop          |
| neofetch | Info      | Informacoes do sistema               |
| cmatrix  | Visual    | Efeito Matrix no terminal            |

**Regra:** Ferramentas CLI precisam de terminal para executar.

### 2.6. Editores de Texto/Codigo

| App     | Comando | Tipo                  |
| ------- | ------- | --------------------- |
| VS Code | `code`  | GUI                   |
| Neovim  | `nvim`  | CLI (requer terminal) |
| Vim     | `vim`   | CLI (requer terminal) |
| Gedit   | `gedit` | GUI                   |

---

## 3. Regras de Inferencia

O Granite deve inferir:

| Se o App e...   | Entao...                            |
| --------------- | ----------------------------------- |
| GUI             | Executar diretamente                |
| CLI             | Executar dentro do terminal         |
| Player de Midia | Preferir `playerctl` para controle  |
| Navegador       | Usar `xdg-open` para URLs genericas |

---

## 4. Comandos Universais

```bash
# Abrir qualquer arquivo/URL com app padrao
xdg-open arquivo.pdf
xdg-open https://google.com
xdg-open ~/Downloads

# Controle de midia (qualquer player)
playerctl play-pause
playerctl next
playerctl volume 0.8

# Abrir app pelo nome (freedesktop)
gtk-launch firefox
gio launch /usr/share/applications/firefox.desktop
```

---

_Documento de referencia para consulta do RAG_
