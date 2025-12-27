# Mascate (v2) Context for Gemini

## Project Overview

**Mascate** is a local-first, privacy-focused Voice Assistant for Linux (Edge AI), designed with a Brazilian cultural identity ("Futurismo Tropical").

*   **Goal:** Provide a low-latency (<500ms), offline voice assistant that runs on consumer hardware (specifically optimized for NVIDIA GTX 1650 4GB).
*   **Architecture Pattern:** "Brain vs. Bodyguard".
    *   **Brain (LLM):** IBM Granite 4.0 Hybrid 1B. Interprets intent and generates structured JSON commands. **NEVER** executes code.
    *   **Bodyguard (Executor):** Python logic. Validates the JSON against security rules (blacklist) and executes system commands via subprocesses.
*   **Key Features:**
    *   **100% Local:** No cloud dependencies.
    *   **Hybrid Memory:** Uses "VRAM Tetris" strategy to balance GPU (LLM) and CPU/RAM (Audio/RAG) usage.
    *   **Interface:** CLI/TUI using `rich` and `textual`.

## Tech Stack

*   **Language:** Python 3.12+
*   **Dependency Manager:** `uv`
*   **Core Libraries:** `rich`, `textual`, `sounddevice`, `numpy`, `scipy`.
*   **AI/ML:**
    *   **LLM:** `llama-cpp-python` (IBM Granite 4.0 Hybrid 1B Q8_0).
    *   **STT:** Whisper Large v3 (via `whisper.cpp` logic/bindings).
    *   **TTS:** Piper (VITS).
    *   **RAG:** `qdrant-client` (Vector DB), `sentence-transformers` (BGE-M3 Embeddings).
    *   **VAD:** Silero VAD v5.

## Architecture Structure (`src/mascate/`)

| Directory | Purpose | Key Components |
| :--- | :--- | :--- |
| `audio/` | Ears & Voice (CPU) | STT (Whisper), TTS (Piper), VAD (Silero), Wake Word. |
| `intelligence/` | Brain (GPU/RAM) | LLM (Granite), RAG (Qdrant/BGE-M3), GBNF Grammars. |
| `executor/` | Bodyguard (CPU) | Command parsing, security validation (blacklist), execution. |
| `core/` | Infrastructure | Configuration, Logging, Exceptions. |
| `interface/` | UI | CLI entry points, TUI (Textual). |

## Development Workflow

### 1. Environment Setup
The project uses `uv` for dependency management.

```bash
# Sync Python dependencies
uv sync

# Install system dependencies (e.g., ffmpeg, portaudio)
uv run python scripts/install_deps.py

# Download required AI models
uv run python scripts/download_models.py
```

### 2. Building and Running
*   **Run Application:** `uv run mascate run`
*   **Run CLI:** `uv run mascate --help`

### 3. Testing & Quality
*   **Test Runner:** `pytest`
*   **Linting:** `ruff check .`
*   **Formatting:** `ruff format .`
*   **Type Checking:** `mypy .` (Strict mode enabled)

### 4. Key Conventions
*   **Strict Separation:** The `intelligence` module (LLM) must never import `executor` logic directly. Communication is via structured data (JSON).
*   **VRAM Conservation:** GPU is exclusively for the LLM. All other models (Audio, RAG) must run on CPU/RAM.
*   **Async:** The core pipeline is likely asynchronous (`asyncio`) to handle audio streaming and model inference concurrently.
*   **Docstrings:** Google-style or NumPy-style docstrings preferred.

## Documentation References
*   `docs/00-architecture-overview.md`: High-level system design.
*   `docs/01-models-spec.md`: Specifics on model versions and quantization.
*   `docs/07-security.md`: Security protocols for the Executor.
