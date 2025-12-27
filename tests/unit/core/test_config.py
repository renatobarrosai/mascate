"""Unit tests for mascate.core.config module."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from mascate.core.config import (
    AudioConfig,
    Config,
    LLMConfig,
    SecurityConfig,
    _expand_path,
    get_config,
    reset_config,
    DEFAULT_CACHE_DIR,
    DEFAULT_DATA_DIR,
    DEFAULT_MODELS_DIR,
)
from mascate.core.exceptions import ConfigurationError

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(autouse=True)
def reset_config_fixture() -> Generator[None, None, None]:
    """Reset config singleton before and after each test."""
    reset_config()
    yield
    reset_config()


class TestAudioConfig:
    """Tests for AudioConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default audio config values."""
        config = AudioConfig()

        assert config.sample_rate == 16000
        assert config.channels == 1
        assert config.chunk_size == 1024
        assert config.vad_threshold == 0.5
        assert config.wake_word == "mascate"

    def test_custom_values(self) -> None:
        """Test custom audio config values."""
        config = AudioConfig(
            sample_rate=44100,
            channels=2,
            chunk_size=2048,
            vad_threshold=0.7,
            wake_word="hey_mascate",
        )

        assert config.sample_rate == 44100
        assert config.channels == 2
        assert config.chunk_size == 2048
        assert config.vad_threshold == 0.7
        assert config.wake_word == "hey_mascate"


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default LLM config values."""
        config = LLMConfig()

        assert config.model_path is None
        assert config.n_gpu_layers == -1
        assert config.n_ctx == 4096
        assert config.n_batch == 512
        assert config.temperature == 0.7
        assert config.max_tokens == 256

    def test_custom_values(self) -> None:
        """Test custom LLM config values."""
        model_path = Path("/models/granite.gguf")
        config = LLMConfig(
            model_path=model_path,
            n_gpu_layers=32,
            n_ctx=8192,
            n_batch=256,
            temperature=0.5,
            max_tokens=512,
        )

        assert config.model_path == model_path
        assert config.n_gpu_layers == 32
        assert config.n_ctx == 8192
        assert config.n_batch == 256
        assert config.temperature == 0.5
        assert config.max_tokens == 512


class TestSecurityConfig:
    """Tests for SecurityConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default security config values."""
        config = SecurityConfig()

        assert config.require_confirmation is True
        assert "rm -rf" in config.blacklist_commands
        assert "/etc" in config.protected_paths

    def test_custom_values(self) -> None:
        """Test custom security config values."""
        config = SecurityConfig(
            require_confirmation=False,
            blacklist_commands=["danger"],
            protected_paths=["/home"],
        )

        assert config.require_confirmation is False
        assert config.blacklist_commands == ["danger"]
        assert config.protected_paths == ["/home"]


class TestExpandPath:
    """Tests for _expand_path helper function."""

    def test_returns_default_when_none(self) -> None:
        """Test that default is returned when path_str is None."""
        default = Path("/default/path")
        result = _expand_path(None, default)

        assert result == default

    def test_expands_tilde(self) -> None:
        """Test that tilde is expanded to home directory."""
        result = _expand_path("~/test", Path("/default"))

        assert result == Path.home() / "test"
        assert result.is_absolute()

    def test_absolute_path_unchanged(self) -> None:
        """Test that absolute paths are preserved."""
        result = _expand_path("/absolute/path", Path("/default"))

        assert result == Path("/absolute/path")

    def test_relative_path_resolved(self) -> None:
        """Test that relative paths are resolved to absolute."""
        result = _expand_path("relative/path", Path("/default"))

        assert result.is_absolute()


class TestConfig:
    """Tests for Config dataclass."""

    def test_default_values(self) -> None:
        """Test default config values."""
        config = Config()

        assert isinstance(config.audio, AudioConfig)
        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.security, SecurityConfig)
        assert config.models_dir == DEFAULT_MODELS_DIR
        assert config.data_dir == DEFAULT_DATA_DIR
        assert config.cache_dir == DEFAULT_CACHE_DIR
        assert config.debug is False

    def test_validates_paths_on_init(self) -> None:
        """Test that paths are validated on initialization."""
        # Relative path should raise error
        with pytest.raises(ConfigurationError) as exc_info:
            Config(models_dir=Path("relative/path"))

        assert "must be absolute" in str(exc_info.value)

    def test_ensure_dirs_creates_directories(self, tmp_path: Path) -> None:
        """Test that ensure_dirs creates necessary directories."""
        models = tmp_path / "models"
        data = tmp_path / "data"
        cache = tmp_path / "cache"

        config = Config(
            models_dir=models,
            data_dir=data,
            cache_dir=cache,
        )

        # Directories should not exist yet
        assert not models.exists()
        assert not data.exists()
        assert not cache.exists()

        config.ensure_dirs()

        # Now they should exist
        assert models.exists()
        assert data.exists()
        assert cache.exists()


class TestConfigLoad:
    """Tests for Config.load() method."""

    def test_load_returns_defaults_when_file_not_exists(self) -> None:
        """Test that defaults are returned when config file doesn't exist."""
        config = Config.load(Path("/nonexistent/config.toml"))

        assert config.debug is False
        assert config.audio.sample_rate == 16000

    def test_load_from_valid_toml(self, tmp_path: Path) -> None:
        """Test loading config from valid TOML file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[general]
debug = true

[audio]
sample_rate = 44100
channels = 2
wake_word = "ola_mascate"

[llm]
model = "test-model.gguf"
n_gpu_layers = 16
temperature = 0.5

[security]
require_confirmation = false

[paths]
models_dir = "/tmp/models"
data_dir = "/tmp/data"
cache_dir = "/tmp/cache"
""")

        config = Config.load(config_file)

        assert config.debug is True
        assert config.audio.sample_rate == 44100
        assert config.audio.channels == 2
        assert config.audio.wake_word == "ola_mascate"
        assert config.llm.model_path == Path("test-model.gguf")
        assert config.llm.n_gpu_layers == 16
        assert config.llm.temperature == 0.5
        assert config.security.require_confirmation is False
        assert config.models_dir == Path("/tmp/models")
        assert config.data_dir == Path("/tmp/data")
        assert config.cache_dir == Path("/tmp/cache")

    def test_load_partial_config(self, tmp_path: Path) -> None:
        """Test loading config with only some values specified."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[general]
debug = true

[audio]
sample_rate = 22050
""")

        config = Config.load(config_file)

        # Specified values should be set
        assert config.debug is True
        assert config.audio.sample_rate == 22050

        # Unspecified values should use defaults
        assert config.audio.channels == 1
        assert config.llm.n_ctx == 4096

    def test_load_invalid_toml_raises_error(self, tmp_path: Path) -> None:
        """Test that invalid TOML raises ConfigurationError."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("this is not { valid toml [")

        with pytest.raises(ConfigurationError) as exc_info:
            Config.load(config_file)

        assert "Invalid TOML" in str(exc_info.value)

    def test_load_expands_tilde_in_paths(self, tmp_path: Path) -> None:
        """Test that tilde in paths is expanded."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[paths]
models_dir = "~/.mascate/models"
data_dir = "~/.mascate/data"
cache_dir = "~/.mascate/cache"
""")

        config = Config.load(config_file)

        assert config.models_dir == Path.home() / ".mascate" / "models"
        assert config.data_dir == Path.home() / ".mascate" / "data"
        assert config.cache_dir == Path.home() / ".mascate" / "cache"


class TestGetConfig:
    """Tests for get_config() singleton function."""

    def test_returns_config_instance(self) -> None:
        """Test that get_config returns a Config instance."""
        config = get_config()

        assert isinstance(config, Config)

    def test_returns_same_instance(self) -> None:
        """Test that get_config returns the same instance (singleton)."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_reset_clears_cache(self) -> None:
        """Test that reset_config clears the singleton cache."""
        config1 = get_config()
        reset_config()
        config2 = get_config()

        # Should be equal but not the same instance
        assert config1 is not config2
