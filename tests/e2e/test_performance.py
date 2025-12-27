"""Testes de Performance E2E para o Mascate.

Mede latência crítica e uso de recursos.
"""

import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from mascate.audio.stt.whisper import WhisperSTT
from mascate.audio.wake.detector import WakeWordDetector
from mascate.intelligence.brain import Brain
from mascate.intelligence.llm.granite import GraniteLLM


@pytest.mark.benchmark
def test_latency_wake_word():
    """Mede a latência de processamento da Wake Word."""
    with patch("mascate.audio.wake.detector.Model") as MockModel:
        # Mock do modelo interno
        mock_instance = MagicMock()
        mock_instance.models = {"hey_mascate": {}}
        mock_instance.prediction_buffer = {"hey_mascate": [0.0]}
        MockModel.return_value = mock_instance

        detector = WakeWordDetector(threshold=0.5)

        chunk = np.zeros(1280, dtype=np.float32)

        # Warmup
        detector.process(chunk)

        start_time = time.perf_counter()
        detector.process(chunk)
        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000
        print(f"\nWake Word Wrapper Overhead: {latency_ms:.2f}ms")

        assert latency_ms < 50


@pytest.mark.benchmark
def test_latency_stt_mock():
    """Mede a latência do STT (Mockado para referência de overhead)."""
    with patch("mascate.audio.stt.whisper.whisper") as mock_whisper:
        with patch("pathlib.Path.exists", return_value=True):
            stt = WhisperSTT(model_path="dummy.bin")
            audio = np.zeros(16000 * 3, dtype=np.float32)

            start_time = time.perf_counter()
            stt.transcribe(audio)
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000
            print(f"\nSTT Wrapper Overhead: {latency_ms:.2f}ms")

            assert latency_ms < 50


@pytest.mark.benchmark
def test_latency_llm_generation_mock():
    """Mede a latência de geração do LLM (Mockado)."""
    # Novamente, teste real precisa de GPU.
    # Medimos overhead do prompt building e grammar loading.
    with patch("mascate.intelligence.llm.granite.Llama") as MockLlama:
        with patch("mascate.intelligence.llm.granite.LlamaGrammar"):
            mock_instance = MagicMock()
            mock_instance.return_value = {"choices": [{"text": "{}"}]}
            MockLlama.return_value = mock_instance

            with patch("pathlib.Path.exists", return_value=True):
                llm = GraniteLLM(model_path="model.gguf")

                start_time = time.perf_counter()
                llm.generate("Teste de performance")
                end_time = time.perf_counter()

                latency_ms = (end_time - start_time) * 1000
                print(f"\nLLM Wrapper Latency: {latency_ms:.2f}ms")

                # Overhead de prompt + grammar deve ser baixo
                assert latency_ms < 100


@pytest.mark.benchmark
def test_latency_total_pipeline_mock():
    """Simula latência total do sistema com componentes mockados."""
    # Este teste valida se a orquestração adiciona delay significativo
    retriever = MagicMock()
    retriever.search.return_value = []
    retriever.format_context.return_value = ""

    llm = MagicMock()
    llm.generate.return_value = '{"action": "test"}'

    brain = Brain(llm, retriever)

    start_time = time.perf_counter()
    brain.process("Comando de teste")
    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000
    print(f"\nTotal System Overhead: {latency_ms:.2f}ms")

    assert latency_ms < 50
