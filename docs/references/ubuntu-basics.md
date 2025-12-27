# Referencia: Ubuntu/GNOME Basics

**Projeto:** Mascate
**Proposito:** Base de conhecimento para o RAG - comandos basicos Ubuntu/GNOME.
**Foco:** Cobertura de 80% do uso diario com 20% dos comandos.

---

## 1. Filosofia

### Divisao de Responsabilidades

- **Granite (Cerebro):** Interpreta pedido, consulta RAG, decide comando
- **Python (Guarda-Costas):** Valida RISCO (nao semantica), bloqueia comandos destrutivos

### Estrategia de Produto

Foco em **4 Pilares Universais** que cobrem 80% do uso:

1. Navegador
2. Midia
3. Arquivos
4. Ciclo de Vida de Apps

---

## 2. Pilar 1: Navegador

### Acoes Suportadas

| Acao              | Comando                                                     | Exemplo                        |
| ----------------- | ----------------------------------------------------------- | ------------------------------ |
| Abrir URL         | `xdg-open URL`                                              | `xdg-open https://youtube.com` |
| Pesquisar Google  | `xdg-open "https://google.com/search?q=TERMO"`              | Pesquisa web                   |
| Pesquisar YouTube | `xdg-open "https://youtube.com/results?search_query=TERMO"` | Busca videos                   |

### Exemplos de Intencao

| Usuario Diz                 | Granite Interpreta                              |
| --------------------------- | ----------------------------------------------- |
| "Entra no YouTube"          | `xdg-open https://youtube.com`                  |
| "Pesquisa Python no Google" | `xdg-open "https://google.com/search?q=Python"` |
| "Abre o G1"                 | `xdg-open https://g1.globo.com`                 |

---

## 3. Pilar 2: Midia

### Controle Universal (playerctl)

Funciona com qualquer player compativel com MPRIS (Spotify, VLC, Firefox, Chrome).

| Acao       | Comando                      |
| ---------- | ---------------------------- |
| Play/Pause | `playerctl play-pause`       |
| Proxima    | `playerctl next`             |
| Anterior   | `playerctl previous`         |
| Parar      | `playerctl stop`             |
| Volume     | `playerctl volume 0.5` (50%) |
| Mute       | `playerctl volume 0`         |

### Exemplos de Intencao

| Usuario Diz       | Granite Interpreta     |
| ----------------- | ---------------------- |
| "Toca musica"     | `playerctl play`       |
| "Pausa"           | `playerctl pause`      |
| "Pula essa"       | `playerctl next`       |
| "Abaixa o volume" | `playerctl volume 0.3` |

---

## 4. Pilar 3: Arquivos

### Navegacao

| Acao                   | Comando                   |
| ---------------------- | ------------------------- |
| Abrir pasta Home       | `xdg-open ~`              |
| Abrir Downloads        | `xdg-open ~/Downloads`    |
| Abrir Documentos       | `xdg-open ~/Documents`    |
| Abrir pasta especifica | `xdg-open /caminho/pasta` |

### Operacoes Basicas (Terminal)

| Acao              | Comando             | Nivel de Risco |
| ----------------- | ------------------- | -------------- |
| Listar            | `ls -la`            | Baixo          |
| Criar pasta       | `mkdir nome`        | Baixo          |
| Criar arquivo     | `touch arquivo.txt` | Baixo          |
| Copiar            | `cp origem destino` | Baixo          |
| Mover             | `mv origem destino` | Medio          |
| **Deletar**       | `rm arquivo`        | **ALTO**       |
| **Deletar pasta** | `rm -rf pasta`      | **CRITICO**    |

### Comandos que Requerem Confirmacao

**BLACKLIST (Guarda-Costas bloqueia):**

- `rm -rf`
- `rm -r`
- `dd`
- `mkfs`
- `format`
- Qualquer comando em `/etc`, `/boot`, `/sys`

---

## 5. Pilar 4: Ciclo de Vida de Apps

### Abrir Aplicativos

| Metodo   | Comando            | Uso                 |
| -------- | ------------------ | ------------------- |
| Generico | `gtk-launch nome`  | Usa .desktop file   |
| Direto   | `firefox`          | Executa binario     |
| xdg-open | `xdg-open arquivo` | Abre com app padrao |

### Fechar Aplicativos

| Metodo       | Comando                   | Notas              |
| ------------ | ------------------------- | ------------------ |
| Graceful     | `wmctrl -c "Nome Janela"` | Fecha janela       |
| Kill         | `pkill nome`              | Mata processo      |
| Kill forcado | `pkill -9 nome`           | Mata imediatamente |

### Gerenciamento de Janelas

| Acao             | Comando/Atalho                                            |
| ---------------- | --------------------------------------------------------- |
| Alternar janelas | `Alt+Tab` (simular via ydotool)                           |
| Minimizar        | `wmctrl -r :ACTIVE: -b add,hidden`                        |
| Maximizar        | `wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz` |

---

## 6. Comandos de Sistema

### Informacoes

| Acao           | Comando    |
| -------------- | ---------- |
| Info sistema   | `neofetch` |
| Uso de disco   | `df -h`    |
| Uso de memoria | `free -h`  |
| Processos      | `htop`     |

### Controle de Energia

| Acao          | Comando              | Risco    |
| ------------- | -------------------- | -------- |
| Suspender     | `systemctl suspend`  | Medio    |
| **Desligar**  | `systemctl poweroff` | **ALTO** |
| **Reiniciar** | `systemctl reboot`   | **ALTO** |

---

## 7. Ferramentas de Automacao

### ydotool (Simulacao de Input)

Para casos onde nao ha API direta:

```bash
# Simular tecla
ydotool key alt+tab
ydotool key ctrl+c

# Simular digitacao
ydotool type "texto aqui"

# Simular mouse
ydotool click 0x00  # Click esquerdo
```

**Nota:** Preferir APIs diretas (playerctl, wmctrl) quando disponiveis.

---

## 8. Escalabilidade

O sistema e **agnostico** - nao sabe usar nada a priori, mas aprende a usar qualquer coisa se tiver o manual.

**Adicionar novo software:**

1. Criar arquivo .md com comandos
2. Adicionar ao banco vetorial (RAG)
3. Granite consulta automaticamente

---

_Documento de referencia para consulta do RAG_
