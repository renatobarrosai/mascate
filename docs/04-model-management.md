# Mascate - Gestao de Modelos

**Versao:** 1.0  
**Status:** Aprovado para Implementacao

Este documento define a estrategia de download, verificacao e organizacao dos modelos.

---

## 1. Principios

- **Fora do Git:** Pesos binarios (.gguf, .onnx) NAO sobem para o repositorio
- **Automatizado:** Script `download_models.py` baixa tudo automaticamente
- **Verificado:** Hash SHA256 garante integridade dos arquivos
- **Organizado:** Estrutura canonica em `models/`

---

## 2. Estrutura de Diretorios

```
models/
+-- llm/
|   +-- granite-4.0-hybrid-1b-instruct.Q8_0.gguf
+-- stt/
|   +-- ggml-large-v3-q5_k_m.bin
+-- tts/
|   +-- pt_BR-faber-medium.onnx
|   +-- pt_BR-faber-medium.onnx.json
+-- vad/
|   +-- silero_vad.onnx
+-- wake/
|   +-- hey_jarvis_v0.1.onnx
+-- embeddings/
    +-- bge-m3/
        +-- (diretorio completo do modelo)
```

---

## 3. Lista de Modelos

| Modelo           | Repositorio HF        | Arquivo                    | Destino            | Tamanho |
| :--------------- | :-------------------- | :------------------------- | :----------------- | :------ |
| Granite 4.0      | TBD (comunidade)      | `*q8_0.gguf`               | models/llm/        | ~1.3 GB |
| Whisper Large v3 | ggerganov/whisper.cpp | `ggml-large-v3-q5_k_m.bin` | models/stt/        | ~2.2 GB |
| Piper pt-BR      | rhasspy/piper-voices  | `pt_BR-faber-medium.onnx`  | models/tts/        | ~300 MB |
| Silero VAD       | snakers4/silero-vad   | `silero_vad.onnx`          | models/vad/        | ~50 MB  |
| openWakeWord     | dscripka/openwakeword | `hey_jarvis_v0.1.onnx`     | models/wake/       | ~150 MB |
| BGE-M3           | BAAI/bge-m3           | (diretorio completo)       | models/embeddings/ | ~1.5 GB |

**Total aproximado:** ~5.5 GB

---

## 4. Script de Download

### 4.1. Ferramenta

Utilizamos `huggingface_hub` para downloads do Hugging Face.

```python
from huggingface_hub import hf_hub_download, snapshot_download

# Para arquivos individuais
hf_hub_download(
    repo_id="ggerganov/whisper.cpp",
    filename="ggml-large-v3-q5_k_m.bin",
    local_dir="models/stt"
)

# Para diretorios completos (BGE-M3)
snapshot_download(
    repo_id="BAAI/bge-m3",
    local_dir="models/embeddings/bge-m3"
)
```

### 4.2. Verificacao de Hash

Apos download, verificar SHA256:

```python
import hashlib

def verify_hash(filepath: str, expected_hash: str) -> bool:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash
```

### 4.3. Progress Bar

Usar Rich para feedback visual:

```python
from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("Baixando Granite...", total=100)
    # ... logica de download com callbacks
```

---

## 5. Configuracao em config.toml

```toml
[models]
llm_path = "models/llm/granite-4.0-hybrid-1b-instruct.Q8_0.gguf"
stt_path = "models/stt/ggml-large-v3-q5_k_m.bin"
tts_path = "models/tts/pt_BR-faber-medium.onnx"
vad_path = "models/vad/silero_vad.onnx"
wake_path = "models/wake/hey_jarvis_v0.1.onnx"
embeddings_path = "models/embeddings/bge-m3"
```

---

## 6. .gitignore

Garantir que modelos nao subam para o Git:

```gitignore
# Modelos (binarios grandes)
models/
*.gguf
*.onnx
*.bin
*.safetensors
```

---

## 7. Pontos Pendentes (TBD)

| Item                          | Status   | Notas                                                    |
| :---------------------------- | :------- | :------------------------------------------------------- |
| URL exata do Granite 4.0 GGUF | PENDENTE | Buscar em repos da comunidade (Bartowski, MaziyarPanahi) |
| Formato final do BGE-M3       | PENDENTE | ONNX ou PyTorch?                                         |
| Hashes SHA256 de cada modelo  | PENDENTE | Coletar apos primeira execucao                           |

---

## 8. Fluxo de Uso

1. Usuario clona o repositorio
2. Executa `python scripts/download_models.py`
3. Script verifica se modelos ja existem
4. Baixa modelos faltantes do Hugging Face
5. Verifica integridade via SHA256
6. Reporta sucesso/falha

---

## Referencias

- [01-models-spec.md](./01-models-spec.md) - Especificacoes dos modelos
- [09-infrastructure.md](./09-infrastructure.md) - Infraestrutura geral
