"""Excecoes customizadas do Mascate."""

from __future__ import annotations


class MascateError(Exception):
    """Excecao base do Mascate."""

    pass


# Audio Errors
class AudioError(MascateError):
    """Erro relacionado ao modulo de audio."""

    pass


class AudioInitError(AudioError):
    """Erro ao inicializar dispositivo de audio."""

    pass


class STTError(AudioError):
    """Erro no Speech-to-Text."""

    pass


class TTSError(AudioError):
    """Erro no Text-to-Speech."""

    pass


class VADError(AudioError):
    """Erro no Voice Activity Detection."""

    pass


class WakeWordError(AudioError):
    """Erro na deteccao de wake word."""

    pass


# Intelligence Errors
class IntelligenceError(MascateError):
    """Erro relacionado ao modulo de inteligencia."""

    pass


class LLMError(IntelligenceError):
    """Erro no LLM."""

    pass


class LLMLoadError(LLMError):
    """Erro ao carregar modelo LLM."""

    pass


class LLMInferenceError(LLMError):
    """Erro durante inferencia do LLM."""

    pass


class RAGError(IntelligenceError):
    """Erro no sistema RAG."""

    pass


# Executor Errors
class ExecutorError(MascateError):
    """Erro relacionado ao modulo executor."""

    pass


class CommandParseError(ExecutorError):
    """Erro ao parsear comando."""

    pass


class SecurityError(ExecutorError):
    """Erro de seguranca - comando bloqueado."""

    pass


class CommandExecutionError(ExecutorError):
    """Erro ao executar comando."""

    pass


# Model Errors
class ModelError(MascateError):
    """Erro relacionado a modelos."""

    pass


class ModelNotFoundError(ModelError):
    """Modelo nao encontrado."""

    pass


class ModelDownloadError(ModelError):
    """Erro ao baixar modelo."""

    pass


class ModelValidationError(ModelError):
    """Erro ao validar modelo (hash incorreto)."""

    pass


# Config Errors
class ConfigError(MascateError):
    """Erro relacionado a configuracao."""

    pass


class ConfigurationError(ConfigError):
    """Erro generico de configuracao."""

    pass


class ConfigLoadError(ConfigError):
    """Erro ao carregar arquivo de configuracao."""

    pass


class ConfigValidationError(ConfigError):
    """Erro ao validar configuracao."""

    pass
