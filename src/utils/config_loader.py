
from pathlib import Path

import yaml


# Locate the project root directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Default validation configuration file.
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "validation_rules.yaml"


def load_config(config_path=DEFAULT_CONFIG_PATH):
    """
    Load and return configuration settings from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        A dictionary containing configuration settings.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the YAML content is empty or invalid.
    """

    config_path = Path(config_path)

    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

    except yaml.YAMLError as error:
        raise ValueError(
            f"Invalid YAML configuration: {error}"
        ) from error

    if not isinstance(config, dict) or not config:
        raise ValueError(
            "Configuration file is empty or must contain a YAML dictionary."
        )

    return config
