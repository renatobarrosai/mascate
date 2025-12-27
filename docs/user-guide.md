# Guia do Usuario

Este guia apresenta todas as funcionalidades do Mascate e como usa-las.

---

## Indice

1. [Como Usar](#1-como-usar)
2. [Comandos por Categoria](#2-comandos-por-categoria)
3. [Sistema de Seguranca](#3-sistema-de-seguranca)
4. [Dicas de Uso](#4-dicas-de-uso)

---

## 1. Como Usar

### 1.1 Ativar o Mascate

O Mascate fica em modo de espera ate ser ativado. Ha duas formas:

**Atalho de Teclado (Recomendado)**

- Pressione `Ctrl+Shift+M`
- O status muda de `IDLE` para `LISTENING`
- Fale seu comando

**Palavra de Ativacao (Wake Word)**

- Diga "Mascate" (ou a palavra configurada)
- Requer Python < 3.12 e configuracao adicional

### 1.2 Falar Comandos

Apos ativar:

1. Aguarde o status mudar para `LISTENING`
2. Fale seu comando de forma clara
3. Faca uma pausa breve no final
4. O sistema detecta automaticamente quando voce parou de falar

### 1.3 Ciclo de Uso

```
IDLE → [Hotkey] → LISTENING → [Fala] → PROCESSING → EXECUTING → IDLE
```

### 1.4 Interface Visual

```
╭─────────────────────────────────────╮
│         MASCATE v0.1.0              │
├─────────────────────────────────────┤
│ Status: LISTENING                   │
│ Audio:  ████████░░░░░░░░  52%       │
├─────────────────────────────────────┤
│ > Aguardando comando...             │
│ > [14:32:01] Volume aumentado       │
│ > [14:31:45] Firefox aberto         │
╰─────────────────────────────────────╯
```

**Estados:**

- `IDLE` - Aguardando ativacao
- `LISTENING` - Ouvindo seu comando
- `PROCESSING` - Interpretando com IA
- `EXECUTING` - Executando acao
- `SPEAKING` - Respondendo por voz

---

## 2. Comandos por Categoria

### 2.1 Aplicativos

Abre aplicativos instalados no sistema.

| Comando                          | Acao                        |
| -------------------------------- | --------------------------- |
| "Abre o Firefox"                 | Abre o navegador Firefox    |
| "Abre o VS Code"                 | Abre o Visual Studio Code   |
| "Abre a calculadora"             | Abre a calculadora          |
| "Abre o terminal"                | Abre o emulador de terminal |
| "Abre o gerenciador de arquivos" | Abre o Nautilus/Dolphin     |

**Variacoes aceitas:**

- "Abre o...", "Inicia o...", "Executa o..."
- O nome do aplicativo pode ser o nome do executavel ou nome comum

**Requisitos:** O aplicativo deve estar instalado e no PATH.

---

### 2.2 Navegacao Web

Abre URLs e faz pesquisas no navegador padrao.

| Comando                     | Acao                        |
| --------------------------- | --------------------------- |
| "Abre o YouTube"            | Abre youtube.com            |
| "Abre github.com"           | Abre a URL especificada     |
| "Pesquisa Python no Google" | Pesquisa "Python" no Google |
| "Busca receita de bolo"     | Pesquisa no Google          |
| "Abre o Google Maps"        | Abre maps.google.com        |

**Como funciona:**

- URLs reconhecidas sao abertas diretamente
- Outros termos sao pesquisados no Google

**Requisitos:** `xdg-open` (instalado por padrao no Linux)

---

### 2.3 Controle de Midia

Controla players compativeis com MPRIS (Spotify, VLC, Firefox, etc.).

| Comando       | Acao                 |
| ------------- | -------------------- |
| "Toca musica" | Play/Pause (alterna) |
| "Play"        | Inicia reproducao    |
| "Pausa"       | Pausa reproducao     |
| "Proxima"     | Proxima faixa        |
| "Anterior"    | Faixa anterior       |
| "Para"        | Para reproducao      |

**Variacoes aceitas:**

- "Proxima faixa", "Proxima musica", "Pula"
- "Pausa a musica", "Pausa isso"

**Requisitos:**

- `playerctl` instalado
- Um player de midia aberto e tocando

**Verificar players ativos:**

```bash
playerctl -l
```

---

### 2.4 Controle de Volume

Ajusta o volume do sistema.

| Comando            | Acao                    |
| ------------------ | ----------------------- |
| "Aumenta o volume" | +5% volume              |
| "Diminui o volume" | -5% volume              |
| "Volume em 50%"    | Define volume para 50%  |
| "Muta o som"       | Silencia audio          |
| "Desmuta"          | Reativa audio           |
| "Volume maximo"    | Define volume para 100% |

**Requisitos:** PulseAudio ou PipeWire (instalado por padrao)

---

### 2.5 Controle de Brilho

Ajusta o brilho da tela.

| Comando            | Acao                    |
| ------------------ | ----------------------- |
| "Aumenta o brilho" | +10% brilho             |
| "Diminui o brilho" | -10% brilho             |
| "Brilho em 80%"    | Define brilho para 80%  |
| "Brilho maximo"    | Define brilho para 100% |
| "Brilho minimo"    | Define brilho para 10%  |

**Requisitos:**

```bash
sudo apt install brightnessctl  # Ubuntu/Debian
```

---

### 2.6 Operacoes de Arquivo

Gerencia arquivos e diretorios.

| Comando                              | Acao                     |
| ------------------------------------ | ------------------------ |
| "Abre o arquivo relatorio.pdf"       | Abre com app padrao      |
| "Lista a pasta Downloads"            | Mostra conteudo          |
| "Cria a pasta Projetos"              | Cria novo diretorio      |
| "Copia arquivo.txt para Backup"      | Copia arquivo            |
| "Move documento.pdf para Documentos" | Move arquivo             |
| "Deleta arquivo.tmp"                 | Deleta (com confirmacao) |

**Seguranca:**

- Operacoes de delecao sempre pedem confirmacao
- Caminhos do sistema sao protegidos (veja secao 3)

---

### 2.7 Controle de Energia

| Comando                 | Acao                       |
| ----------------------- | -------------------------- |
| "Bloqueia a tela"       | Bloqueia a sessao          |
| "Suspende"              | Entra em modo suspensao    |
| "Reinicia o computador" | Reinicia (com confirmacao) |
| "Desliga o computador"  | Desliga (com confirmacao)  |

**Atencao:** Reiniciar e desligar sempre pedem confirmacao por voz.

---

### 2.8 Conectividade

| Comando               | Acao               |
| --------------------- | ------------------ |
| "Liga o WiFi"         | Ativa WiFi         |
| "Desliga o WiFi"      | Desativa WiFi      |
| "Liga o Bluetooth"    | Ativa Bluetooth    |
| "Desliga o Bluetooth" | Desativa Bluetooth |

**Requisitos:**

- WiFi: NetworkManager (`nmcli`)
- Bluetooth: BlueZ (`bluetoothctl`)

---

### 2.9 Notificacoes

| Comando                          | Acao                      |
| -------------------------------- | ------------------------- |
| "Notifica que a tarefa terminou" | Envia notificacao desktop |
| "Mostra notificacao: teste"      | Notificacao customizada   |

---

## 3. Sistema de Seguranca

O Mascate possui multiplas camadas de protecao.

### 3.1 Niveis de Risco

| Nivel    | Comportamento             | Exemplos              |
| -------- | ------------------------- | --------------------- |
| LOW      | Executa automaticamente   | Abrir apps, pesquisar |
| MEDIUM   | Executa com log de aviso  | Listar arquivos       |
| HIGH     | Pede confirmacao por voz  | Deletar, desligar     |
| CRITICAL | Bloqueado permanentemente | rm -rf, format        |

### 3.2 Confirmacao por Voz

Para acoes de alto risco, o Mascate pergunta:

```
Mascate: "Voce tem certeza que deseja deletar arquivo.txt?"
Voce: "Sim" ou "Confirma"
```

Respostas aceitas para confirmar: "sim", "confirma", "pode", "ok"
Respostas para cancelar: "nao", "cancela", "para"

### 3.3 Comandos Bloqueados

Estes padroes sao sempre bloqueados:

| Padrao       | Motivo                    |
| ------------ | ------------------------- |
| `rm -rf`     | Delecao recursiva forcada |
| `dd if=`     | Acesso direto a disco     |
| `mkfs`       | Formatacao de disco       |
| `chmod 777`  | Permissoes inseguras      |
| `curl \| sh` | Execucao remota           |

### 3.4 Diretorios Protegidos

Acesso a estes diretorios e bloqueado ou requer confirmacao:

- `/etc`, `/boot`, `/sys`, `/proc`
- `/dev`, `/root`, `/var`
- Diretorios do sistema operacional

### 3.5 Protecao contra Injecao

O sistema detecta e bloqueia tentativas de injecao de shell:

```
# Bloqueado:
"Abre firefox; rm -rf /"
"Abre $(cat /etc/passwd)"
```

---

## 4. Dicas de Uso

### 4.1 Fale com Clareza

- Fale em ritmo normal, nao muito rapido
- Pronuncie as palavras completamente
- Ambiente silencioso melhora a precisao

### 4.2 Comandos Diretos

Seja direto nos comandos:

| Bom                | Evite                                |
| ------------------ | ------------------------------------ |
| "Abre o Firefox"   | "Sera que voce pode abrir o Firefox" |
| "Aumenta o volume" | "O volume esta baixo"                |
| "Pesquisa clima"   | "Quero saber sobre o clima"          |

### 4.3 Nomes de Aplicativos

Use o nome real do executavel quando possivel:

| Funciona           | Pode nao funcionar   |
| ------------------ | -------------------- |
| "firefox"          | "navegador"          |
| "code"             | "visual studio"      |
| "gnome-calculator" | "calculadora padrao" |

### 4.4 Modo Debug

Para ver detalhes do processamento:

```bash
uv run mascate run --debug
```

Mostra:

- Texto transcrito pelo STT
- Intent detectado pelo LLM
- Comando executado

---

## Resumo Rapido

```
ATIVACAO
  Ctrl+Shift+M

COMANDOS COMUNS
  "Abre o [app]"
  "Pesquisa [termo]"
  "Toca/Pausa musica"
  "Aumenta/Diminui volume"
  "Bloqueia a tela"

CONFIRMACAO
  "Sim" / "Nao"
```

---

[Voltar ao README](../README.md) | [Anterior: Instalacao](getting-started.md) | [Proximo: Configuracao](configuration.md)
