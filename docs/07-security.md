# Mascate - Seguranca

**Versao:** 1.0  
**Status:** Aprovado para Implementacao

Este documento define a estrategia de seguranca do sistema ("Guarda-Costas").

---

## 1. Filosofia: Cerebro vs. Guarda-Costas

Ao contrario de abordagens que travam a IA em formularios rigidos, adotamos uma postura onde a IA tem liberdade interpretativa, controlada por uma camada de seguranca logica.

### O Cerebro (Granite LLM)

- **Funcao:** Interprete Soberano
- **Responsabilidade:** Receber pedido vago, consultar RAG, gerar comando exato
- **Limite:** NUNCA executa comandos diretamente

### O Guarda-Costas (Python)

- **Funcao:** Executor Cego e Blindagem
- **Responsabilidade:** Validar RISCO, nao semantica
- **Logica:** Nao julga _por que_ o usuario quer deletar. Julga _se_ deletar e perigoso.

---

## 2. Camadas de Protecao

### 2.1. Blacklist de Comandos Criticos

Comandos que sao **sempre** bloqueados sem excecao:

```python
BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "rm -rf ~",
    ":(){ :|:& };:",      # Fork bomb
    "mkfs",               # Formatar disco
    "dd if=/dev/zero",    # Sobrescrever disco
    "chmod 777 /",        # Permissoes globais
    "> /dev/sda",         # Escrever em disco raw
]
```

### 2.2. Lista de Confirmacao

Comandos que requerem confirmacao explicita:

```python
REQUIRES_CONFIRMATION = [
    "rm",           # Qualquer delecao
    "sudo",         # Qualquer elevacao
    "chmod",        # Alteracao de permissoes
    "chown",        # Alteracao de proprietario
    "mv",           # Mover arquivos
    "cp",           # Copiar (pode sobrescrever)
    "kill",         # Matar processos
    "pkill",        # Matar processos
    "shutdown",     # Desligar sistema
    "reboot",       # Reiniciar sistema
]
```

### 2.3. Comandos Seguros (Whitelist)

Comandos que executam diretamente:

```python
SAFE_ACTIONS = [
    "OPEN_APP",      # Abrir aplicativos
    "OPEN_URL",      # Abrir URLs
    "OPEN_FOLDER",   # Abrir pastas
    "VOLUME_UP",     # Aumentar volume
    "VOLUME_DOWN",   # Diminuir volume
    "VOLUME_MUTE",   # Mutar
    "MEDIA_PLAY_PAUSE",
    "MEDIA_NEXT",
    "MEDIA_PREV",
]
```

---

## 3. Fluxo de Validacao

```
JSON do LLM
      |
      v
+---------------------+
| 1. Esta na Blacklist? |
+---------------------+
      |
  Sim |         Nao
      v           |
  BLOCKED         v
            +---------------------+
            | 2. Requer Confirmacao? |
            +---------------------+
                  |
              Sim |         Nao
                  v           |
            CONFIRMING        v
                        +---------------------+
                        | 3. Requer Sudo?     |
                        +---------------------+
                              |
                          Sim |         Nao
                              v           |
                        REQUIRES_PASSWORD  v
                                      APPROVED
```

---

## 4. Implementacao

### 4.1. Verificador de Seguranca

```python
from dataclasses import dataclass
from enum import Enum

class SecurityStatus(Enum):
    APPROVED = "approved"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    REQUIRES_PASSWORD = "requires_password"
    BLOCKED = "blocked"

@dataclass
class SecurityResult:
    status: SecurityStatus
    reason: str | None = None

def check_security(command: dict) -> SecurityResult:
    action = command["action"]
    target = command.get("target", "")

    # 1. Verificar blacklist
    for pattern in BLOCKED_PATTERNS:
        if pattern in target:
            return SecurityResult(
                status=SecurityStatus.BLOCKED,
                reason=f"Comando bloqueado: {pattern}"
            )

    # 2. Verificar se requer confirmacao
    if action == "RUN_COMMAND":
        for cmd in REQUIRES_CONFIRMATION:
            if target.startswith(cmd):
                return SecurityResult(
                    status=SecurityStatus.REQUIRES_CONFIRMATION,
                    reason=f"Comando sensivel: {cmd}"
                )

    # 3. Verificar sudo
    if "sudo" in target:
        return SecurityResult(
            status=SecurityStatus.REQUIRES_PASSWORD,
            reason="Requer permissao de administrador"
        )

    # 4. Aprovado
    return SecurityResult(status=SecurityStatus.APPROVED)
```

### 4.2. Fluxo de Confirmacao

```python
async def handle_confirmation(command: dict, tts, input_handler):
    action = command["action"]
    target = command["target"]

    # Verbalizar risco
    tts.speak(f"Voce quer {action} {target}? Confirme com Y ou cancele com N.")

    # Aguardar input (teclado)
    response = await input_handler.wait_for_key(timeout=30)

    if response == "y":
        return True
    elif response == "n":
        tts.speak("Comando cancelado.")
        return False
    else:  # timeout
        tts.speak("Tempo esgotado, cancelando.")
        return False
```

---

## 5. Mensagens de Feedback

| Status                | Mensagem TTS                                             |
| :-------------------- | :------------------------------------------------------- |
| APPROVED              | (executa silenciosamente ou "Pronto, {acao} executado.") |
| REQUIRES_CONFIRMATION | "Voce quer {acao}? Confirme com Y ou cancele com N."     |
| REQUIRES_PASSWORD     | "Este comando precisa de permissao. Digite a senha."     |
| BLOCKED               | "Este comando nao e permitido por seguranca."            |

---

## 6. Isolamento de Usuario

- Sistema roda estritamente no nivel de permissao do usuario (`userspace`)
- Acesso `sudo` so permitido em modos avancados com dupla verificacao
- Nunca salvar senhas ou credenciais

---

## 7. Logging de Seguranca

Todos os comandos sensíveis sao logados:

```python
import logging

security_logger = logging.getLogger("mascate.security")

def log_security_event(command: dict, result: SecurityResult):
    security_logger.info(
        f"Command: {command['action']} {command.get('target', '')} "
        f"Status: {result.status.value} "
        f"Reason: {result.reason}"
    )
```

---

## 8. Configuracao

```toml
[security]
require_confirmation = ["rm", "sudo", "chmod", "chown", "mkfs", "dd", "kill"]
blocked_commands = ["rm -rf /", ":(){ :|:& };:", "mkfs", "dd if=/dev/zero"]
confirmation_timeout_seconds = 30
log_all_commands = true
```

---

## Referencias

- [00-architecture-overview.md](./00-architecture-overview.md) - Arquitetura
- [06-gbnf-strategy.md](./06-gbnf-strategy.md) - Gramaticas GBNF
- [08-commands-strategy.md](./08-commands-strategy.md) - Comandos agnosticos
