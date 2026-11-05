
import pytest

from src.utils.config_loader import load_config


def test_default_config_loads_successfully():
    config = load_config()

    assert isinstance(config, dict)
    assert config["age"]["max"] == 120
    assert "required_columns" in config


def test_custom_config_loads_successfully(tmp_path):
    config_file = tmp_path / "custom.yaml"
    config_file.write_text(
        "age:\n  min: 18\n  max: 65\n",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config["age"]["min"] == 18
    assert config["age"]["max"] == 65


def test_missing_config_file_raises_error(tmp_path):
    config_file = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        load_config(config_file)


def test_invalid_yaml_raises_error(tmp_path):
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text(
        "age: [0, 120",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid YAML"):
        load_config(config_file)


def test_empty_config_raises_error(tmp_path):
    config_file = tmp_path / "empty.yaml"
    config_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        load_config(config_file)
