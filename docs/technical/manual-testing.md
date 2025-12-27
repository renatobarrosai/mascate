# Mascate - Guia de Testes Manuais

Este documento descreve os testes manuais para validar o funcionamento do Mascate.

---

## Pre-requisitos

### 1. Ambiente

```bash
cd /home/renato/programacao/open-source/mascate-v2

# Sincronizar dependencias
uv sync --extra dev

# Verificar Python
uv run python --version  # Deve ser 3.12.x
```

### 2. Configuracao

Copie o arquivo de configuracao:

```bash
mkdir -p ~/.config/mascate
cp config.toml.example ~/.config/mascate/config.toml
```

Edite `~/.config/mascate/config.toml` conforme necessario:

```toml
[audio]
hotkey_enabled = true
hotkey = "ctrl+shift+m"
hotkey_only = true  # Recomendado para Python 3.12+

[general]
debug = true  # Para ver logs detalhados
```

### 3. Modelos (Opcional para testes iniciais)

Para testes completos, baixe os modelos:

```bash
uv run python scripts/download_models.py
```

**Nota**: Sem os modelos, alguns componentes operarao em modo mock.

---

## Testes por Componente

### Teste 1: Captura de Audio

**Objetivo**: Verificar se o microfone esta funcionando.

```bash
uv run python -c "
from mascate.audio.capture import AudioCapture, list_audio_devices

# Lista dispositivos
print('=== Dispositivos de Audio ===')
for dev in list_audio_devices():
    print(f'  [{dev[\"index\"]}] {dev[\"name\"]} (in: {dev[\"max_input_channels\"]})')

# Testa captura
print('\n=== Teste de Captura (3 segundos) ===')
capture = AudioCapture()
capture.start()

import time
chunks = []
for _ in range(30):  # ~3 segundos
    time.sleep(0.1)
    try:
        chunk = capture.get_chunk(timeout=0.1)
        chunks.append(chunk)
        print('.', end='', flush=True)
    except:
        pass

capture.stop()
print(f'\nCapturados {len(chunks)} chunks')
print('OK!' if len(chunks) > 20 else 'FALHA: Poucos chunks capturados')
"
```

**Resultado esperado**:

- Lista de dispositivos de audio
- ~30 chunks capturados em 3 segundos

---

### Teste 2: Hotkey Listener

**Objetivo**: Verificar se o atalho de teclado e detectado.

```bash
uv run python -c "
from mascate.audio.hotkey import HotkeyListener
import time

activated = False

def on_activate():
    global activated
    activated = True
    print('\n>>> HOTKEY DETECTADA! <<<')

print('=== Teste de Hotkey ===')
print('Pressione Ctrl+Shift+M nos proximos 10 segundos...')

listener = HotkeyListener(hotkey='ctrl+shift+m', on_activate=on_activate)
listener.start()

for i in range(10, 0, -1):
    print(f'  {i}...', end=' ', flush=True)
    time.sleep(1)
    if activated:
        break

listener.stop()
print('\nOK!' if activated else '\nFALHA: Hotkey nao detectada')
"
```

**Resultado esperado**:

- Ao pressionar `Ctrl+Shift+M`, deve aparecer ">>> HOTKEY DETECTADA! <<<"

**Troubleshooting**:

- Se nao funcionar, pode ser conflito com outro programa usando o mesmo atalho
- No Wayland, hotkeys globais podem requerer permissoes especiais

---

### Teste 3: VAD (Voice Activity Detection)

**Objetivo**: Verificar deteccao de voz vs silencio.

```bash
uv run python -c "
from mascate.audio.capture import AudioCapture
from mascate.audio.vad.processor import VADProcessor, VADState
import numpy as np

print('=== Teste de VAD ===')
print('Fale algo no microfone por 5 segundos...\n')

# Inicializa (usara modelo mock se nao encontrar o real)
capture = AudioCapture(chunk_size=512)
try:
    vad = VADProcessor(model_path='~/.local/share/mascate/models/silero_vad.onnx')
except:
    print('Modelo VAD nao encontrado, usando deteccao por energia')
    vad = None

capture.start()

import time
speech_detected = False
for i in range(50):  # ~5 segundos
    time.sleep(0.1)
    try:
        chunk = capture.get_chunk(timeout=0.1)
        if chunk.ndim > 1:
            chunk = chunk.flatten()

        # Deteccao simples por energia se nao tiver VAD
        if vad:
            state = vad.process(chunk[:512] if len(chunk) >= 512 else chunk)
            is_speech = state == VADState.SPEAKING
        else:
            energy = np.abs(chunk).mean()
            is_speech = energy > 0.01

        if is_speech:
            print('*', end='', flush=True)
            speech_detected = True
        else:
            print('.', end='', flush=True)
    except Exception as e:
        pass

capture.stop()
print('\n\nOK!' if speech_detected else '\nFALHA: Nenhuma fala detectada')
"
```

**Resultado esperado**:

- `.` = silencio, `*` = fala detectada
- Ao falar, deve mostrar asteriscos

---

### Teste 4: STT (Speech-to-Text)

**Objetivo**: Verificar transcricao de audio.

**Nota**: Requer modelo Whisper baixado.

```bash
uv run python -c "
from mascate.audio.capture import AudioCapture
from mascate.audio.stt.whisper import WhisperSTT
import numpy as np
import time

print('=== Teste de STT ===')

# Tenta carregar STT
try:
    stt = WhisperSTT(model_path='~/.local/share/mascate/models/ggml-large-v3-q5_0.bin')
    print('Modelo Whisper carregado!')
except Exception as e:
    print(f'Modelo nao encontrado: {e}')
    print('Execute: uv run python scripts/download_models.py')
    exit(1)

print('\nGrave uma frase de 3 segundos...')
print('Comecando em 2 segundos...')
time.sleep(2)

capture = AudioCapture()
capture.start()
print('GRAVANDO...')

audio_chunks = []
for _ in range(30):
    time.sleep(0.1)
    try:
        chunk = capture.get_chunk(timeout=0.1)
        audio_chunks.append(chunk.flatten() if chunk.ndim > 1 else chunk)
    except:
        pass

capture.stop()
print('Gravacao finalizada. Transcrevendo...')

audio = np.concatenate(audio_chunks)
text = stt.transcribe(audio)

print(f'\n=== Transcricao ===')
print(f'\"{text}\"')
print('\nOK!' if text and len(text) > 3 else '\nFALHA: Transcricao vazia ou muito curta')
"
```

**Resultado esperado**:

- Texto transcrito do que voce falou

---

### Teste 5: TTS (Text-to-Speech)

**Objetivo**: Verificar sintese de voz.

```bash
uv run python -c "
from mascate.audio.tts.piper import PiperTTS

print('=== Teste de TTS ===')

try:
    tts = PiperTTS(model_path='~/.local/share/mascate/models/pt_BR-faber-medium.onnx')
    print('Modelo Piper carregado!')
except Exception as e:
    print(f'Aviso: {e}')
    print('Usando modo mock (sem audio real)')
    tts = PiperTTS(model_path='ghost.onnx')

print('\nSintetizando e reproduzindo...')
tts.speak('Ola! Eu sou o Mascate, seu assistente de voz.', block=True)

print('\nOK! (Se ouviu a voz, o TTS esta funcionando)')
"
```

**Resultado esperado**:

- Ouvir a frase sintetizada pelo alto-falante

---

### Teste 6: Executor de Comandos

**Objetivo**: Verificar execucao de comandos do sistema.

```bash
uv run python -c "
from mascate.executor.executor import Executor
from mascate.core.config import Config

print('=== Teste do Executor ===')

config = Config()
executor = Executor(config)

# Teste 1: Abrir aplicativo (baixo risco)
print('\n1. Testando abertura de aplicativo...')
result = executor.execute_intent({
    'action': 'open_app',
    'target': 'gnome-calculator'
})
print(f'   Resultado: {result}')

import time
time.sleep(2)

# Teste 2: Abrir URL
print('\n2. Testando abertura de URL...')
result = executor.execute_intent({
    'action': 'open_url',
    'target': 'https://google.com'
})
print(f'   Resultado: {result}')

# Teste 3: Controle de midia (se tiver player aberto)
print('\n3. Testando controle de midia...')
result = executor.execute_intent({
    'action': 'media',
    'target': 'pause'
})
print(f'   Resultado: {result}')

print('\n=== Testes do Executor finalizados ===')
"
```

**Resultado esperado**:

- Calculadora abre
- Navegador abre com Google
- Player de midia pausa (se estiver tocando)

---

### Teste 7: Seguranca (Blacklist)

**Objetivo**: Verificar que comandos perigosos sao bloqueados.

```bash
uv run python -c "
from mascate.executor.security import SecurityGuard
from mascate.executor.models import Command, ActionType, RiskLevel
from mascate.core.config import Config

print('=== Teste de Seguranca ===')

config = Config()
guard = SecurityGuard(config)

# Teste 1: Comando seguro
print('\n1. Comando seguro (abrir firefox)...')
cmd = Command(action=ActionType.OPEN_APP, target='firefox', risk=RiskLevel.LOW)
try:
    guard.validate(cmd)
    print('   OK - Comando permitido')
except Exception as e:
    print(f'   BLOQUEADO: {e}')

# Teste 2: Comando na blacklist
print('\n2. Comando perigoso (rm -rf)...')
cmd = Command(action=ActionType.FILE_OP, target='rm -rf /tmp/test', risk=RiskLevel.HIGH)
try:
    guard.validate(cmd)
    print('   FALHA - Deveria ter bloqueado!')
except Exception as e:
    print(f'   OK - Bloqueado: {e}')

# Teste 3: Path protegido
print('\n3. Acesso a path protegido (/etc)...')
cmd = Command(action=ActionType.FILE_OP, target='/etc/passwd', risk=RiskLevel.HIGH)
try:
    guard.validate(cmd)
    print('   FALHA - Deveria ter bloqueado!')
except Exception as e:
    print(f'   OK - Bloqueado: {e}')

# Teste 4: Shell injection
print('\n4. Tentativa de shell injection...')
cmd = Command(action=ActionType.OPEN_APP, target='firefox; rm -rf /', risk=RiskLevel.LOW)
try:
    guard.validate(cmd)
    print('   FALHA - Deveria ter bloqueado!')
except Exception as e:
    print(f'   OK - Bloqueado: {e}')

print('\n=== Testes de Seguranca finalizados ===')
"
```

**Resultado esperado**:

- Comando 1: Permitido
- Comandos 2, 3, 4: Bloqueados

---

### Teste 8: Pipeline Completo (Integracao)

**Objetivo**: Testar o fluxo completo com hotkey.

```bash
uv run python -c "
from mascate.audio.capture import AudioCapture
from mascate.audio.hotkey import HotkeyListener
from mascate.audio.vad.processor import VADProcessor, VADState
from mascate.audio.pipeline import AudioPipeline
import numpy as np
import time

print('=== Teste de Pipeline Completo ===')
print('Este teste simula o fluxo: Hotkey -> Escuta -> VAD -> (STT mockado)')

# Mocks para STT e Wake (nao precisamos deles para este teste)
class MockSTT:
    def transcribe(self, audio):
        duration = len(audio) / 16000
        return f'[Audio de {duration:.1f}s transcrito]'

class MockWake:
    threshold = 0.5
    def process(self, chunk):
        return 0.0  # Nunca ativa (usamos hotkey)

# Inicializa componentes
capture = AudioCapture(chunk_size=1024)
hotkey = HotkeyListener(hotkey='ctrl+shift+m')

try:
    vad = VADProcessor(model_path='~/.local/share/mascate/models/silero_vad.onnx')
except:
    # VAD mock baseado em energia
    class MockVAD:
        _speaking = False
        _silence_count = 0
        def process(self, chunk):
            energy = np.abs(chunk).mean()
            if energy > 0.01:
                self._speaking = True
                self._silence_count = 0
                return VADState.SPEAKING
            elif self._speaking:
                self._silence_count += 1
                if self._silence_count > 10:
                    self._speaking = False
                    return VADState.END_OF_SPEECH
            return VADState.IDLE
        def confirm_end(self):
            self._speaking = False
            self._silence_count = 0
    vad = MockVAD()

stt = MockSTT()

# Cria pipeline
pipeline = AudioPipeline(
    capture=capture,
    wake_detector=MockWake(),
    vad_processor=vad,
    stt=stt,
    hotkey_listener=hotkey
)

# Callbacks
def on_activation():
    print('\\n>>> SISTEMA ATIVADO! Fale agora... <<<')

def on_transcription(text):
    print(f'\\n>>> TRANSCRICAO: {text} <<<')

pipeline.on_activation(on_activation)
pipeline.on_transcription(on_transcription)

# Inicia
print('\\nPressione Ctrl+Shift+M para ativar, depois fale algo.')
print('O sistema vai detectar quando voce parar de falar.')
print('Aguardando 15 segundos...\\n')

pipeline.start()
time.sleep(15)
pipeline.stop()

print('\\n=== Teste finalizado ===')
"
```

**Resultado esperado**:

1. Pressione `Ctrl+Shift+M` -> "SISTEMA ATIVADO!"
2. Fale algo por alguns segundos
3. Pare de falar -> Transcricao aparece

---

## Teste Final: Aplicacao Completa

```bash
# Com debug habilitado
uv run mascate run --debug
```

**Fluxo de teste**:

1. Pressione `Ctrl+Shift+M`
2. Diga: "Abra a calculadora"
3. Verifique se a calculadora abre
4. Pressione `Ctrl+Shift+M` novamente
5. Diga: "Pesquise no Google por clima hoje"
6. Verifique se o navegador abre com a pesquisa

**Comandos para testar**:

- "Abra o Firefox"
- "Pesquise por receitas de bolo"
- "Pause a musica"
- "Proxima musica"
- "Aumente o volume"

---

## Checklist de Validacao

| Componente       | Status | Notas         |
| :--------------- | :----: | :------------ |
| Captura de Audio |  [ ]   |               |
| Hotkey Listener  |  [ ]   |               |
| VAD              |  [ ]   |               |
| STT              |  [ ]   | Requer modelo |
| TTS              |  [ ]   | Requer modelo |
| Executor         |  [ ]   |               |
| Seguranca        |  [ ]   |               |
| Pipeline         |  [ ]   |               |
| App Completa     |  [ ]   |               |

---

## Problemas Comuns

### Hotkey nao funciona

1. **Conflito de atalho**: Outro programa pode estar usando `Ctrl+Shift+M`
   - Solucao: Mude para outro atalho em `config.toml`

2. **Wayland**: Hotkeys globais podem nao funcionar
   - Solucao: Use X11 ou configure permissoes do Wayland

3. **Permissoes**: `pynput` pode precisar de acesso ao `/dev/input`
   - Solucao: `sudo usermod -aG input $USER` e relogue

### Audio nao captura

1. **Dispositivo errado**: Verifique qual microfone esta selecionado
2. **Permissoes**: PulseAudio/PipeWire pode precisar de configuracao
3. **Volume**: Verifique se o microfone nao esta mutado

### Modelos nao encontrados

Execute o script de download:

```bash
uv run python scripts/download_models.py
```

Ou baixe manualmente e coloque em `~/.local/share/mascate/models/`
