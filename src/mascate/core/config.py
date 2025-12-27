"""Configuracao do Mascate.

Carrega configuracoes do arquivo config.toml e variaveis de ambiente.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli

from mascate.core.exceptions import ConfigurationError

# Diretorios padrao
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "mascate"
DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "mascate"
DEFAULT_MODELS_DIR = DEFAULT_DATA_DIR / "models"
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "mascate"

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuracao de um modelo."""

    name: str
    repo_id: str
    filename: str
    quantization: str = "Q8_0"
    device: str = "cpu"  # cpu, cuda, rocm


@dataclass
class AudioConfig:
    """Configuracao do modulo de audio."""

    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    vad_threshold: float = 0.5
    wake_word: str = "mascate"
    # Ativacao via hotkey (alternativa ao wake word)
    hotkey_enabled: bool = True
    hotkey: str = "ctrl+shift+m"
    # Se True, desabilita wake word e usa apenas hotkey
    hotkey_only: bool = False


@dataclass
class LLMConfig:
    """Configuracao do LLM."""

    model_path: Path | None = None
    n_gpu_layers: int = -1  # -1 = all layers on GPU
    n_ctx: int = 4096
    n_batch: int = 512
    temperature: float = 0.7
    max_tokens: int = 256


@dataclass
class SecurityConfig:
    """Configuracao de seguranca (Guarda-Costas)."""

    require_confirmation: bool = True
    blacklist_commands: list[str] = field(
        default_factory=lambda: [
            "rm -rf",
            "rm -r",
            "dd",
            "mkfs",
            "format",
            "> /dev/",
        ]
    )
    protected_paths: list[str] = field(
        default_factory=lambda: [
            "/etc",
            "/boot",
            "/sys",
            "/proc",
            "/dev",
        ]
    )


def _expand_path(path_str: str | None, default: Path) -> Path:
    """Expande path com ~ e variaveis de ambiente.

    Args:
        path_str: String do path (pode conter ~ ou $VAR).
        default: Valor padrao se path_str for None.

    Returns:
        Path absoluto e expandido.
    """
    if path_str is None:
        return default

    expanded = Path(path_str).expanduser()
    if not expanded.is_absolute():
        expanded = expanded.resolve()
    return expanded


@dataclass
class Config:
    """Configuracao principal do Mascate."""

    audio: AudioConfig = field(default_factory=AudioConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    models_dir: Path = DEFAULT_MODELS_DIR
    data_dir: Path = DEFAULT_DATA_DIR
    cache_dir: Path = DEFAULT_CACHE_DIR
    debug: bool = False

    def __post_init__(self) -> None:
        """Valida a configuracao apos inicializacao."""
        self._validate_paths()

    def _validate_paths(self) -> None:
        """Valida que os paths sao absolutos e expandidos.

        Raises:
            ConfigurationError: Se algum path for invalido.
        """
        for attr_name in ("models_dir", "data_dir", "cache_dir"):
            path = getattr(self, attr_name)
            if not path.is_absolute():
                raise ConfigurationError(
                    f"Path '{attr_name}' must be absolute, got: {path}"
                )

    @classmethod
    def load(cls, config_path: Path | None = None) -> Config:
        """Carrega configuracao do arquivo TOML.

        Args:
            config_path: Caminho para o arquivo config.toml.
                         Se None, usa o padrao em ~/.config/mascate/config.toml.

        Returns:
            Instancia de Config com valores carregados.

        Raises:
            ConfigurationError: Se o arquivo existir mas for invalido.
        """
        if config_path is None:
            config_path = DEFAULT_CONFIG_DIR / "config.toml"

        if not config_path.exists():
            logger.debug("Config file not found at %s, using defaults", config_path)
            return cls()

        try:
            with config_path.open("rb") as f:
                data = tomli.load(f)
        except tomli.TOMLDecodeError as e:
            raise ConfigurationError(f"Invalid TOML in {config_path}: {e}") from e

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> Config:
        """Cria instancia de Config a partir de dicionario.

        Args:
            data: Dicionario com dados do TOML.

        Returns:
            Instancia de Config.
        """
        # Parse audio config
        audio_data = data.get("audio", {})
        audio = AudioConfig(
            sample_rate=audio_data.get("sample_rate", 16000),
            channels=audio_data.get("channels", 1),
            chunk_size=audio_data.get("chunk_size", 1024),
            vad_threshold=audio_data.get("vad_threshold", 0.5),
            wake_word=audio_data.get("wake_word", "mascate"),
            hotkey_enabled=audio_data.get("hotkey_enabled", True),
            hotkey=audio_data.get("hotkey", "ctrl+shift+m"),
            hotkey_only=audio_data.get("hotkey_only", False),
        )

        # Parse LLM config
        llm_data = data.get("llm", {})
        model_path = llm_data.get("model")
        llm = LLMConfig(
            model_path=Path(model_path) if model_path else None,
            n_gpu_layers=llm_data.get("n_gpu_layers", -1),
            n_ctx=llm_data.get("n_ctx", 4096),
            n_batch=llm_data.get("n_batch", 512),
            temperature=llm_data.get("temperature", 0.7),
            max_tokens=llm_data.get("max_tokens", 256),
        )

        # Parse security config
        security_data = data.get("security", {})
        security = SecurityConfig(
            require_confirmation=security_data.get("require_confirmation", True),
            blacklist_commands=security_data.get(
                "blacklist_commands",
                SecurityConfig().blacklist_commands,
            ),
            protected_paths=security_data.get(
                "protected_paths",
                SecurityConfig().protected_paths,
            ),
        )

        # Parse paths
        paths_data = data.get("paths", {})
        models_dir = _expand_path(paths_data.get("models_dir"), DEFAULT_MODELS_DIR)
        data_dir = _expand_path(paths_data.get("data_dir"), DEFAULT_DATA_DIR)
        cache_dir = _expand_path(paths_data.get("cache_dir"), DEFAULT_CACHE_DIR)

        # Parse general config
        general_data = data.get("general", {})
        debug = general_data.get("debug", False)

        return cls(
            audio=audio,
            llm=llm,
            security=security,
            models_dir=models_dir,
            data_dir=data_dir,
            cache_dir=cache_dir,
            debug=debug,
        )

    def ensure_dirs(self) -> None:
        """Cria diretorios necessarios se nao existirem."""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


def get_config() -> Config:
    """Obtem a configuracao global (singleton).

    Returns:
        Instancia de Config carregada do arquivo ou defaults.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.load()
    return _config_instance


def reset_config() -> None:
    """Reseta o cache de configuracao.

    Util para testes ou recarregar configuracao.
    """
    global _config_instance
    _config_instance = None


# Cache global da configuracao
_config_instance: Config | None = None
