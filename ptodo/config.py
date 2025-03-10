from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ptodo.utils import get_ptodo_directory

# Default configuration
DEFAULT_CONFIG = {
    "todo_file": "todo.txt",
    "done_file": "done.txt",
    "archive_completed": True,
    "default_priority": "C",
    "show_colors": True,
    "date_format": "%Y-%m-%d",
    "auto_commit": True,
    "auto_sync": True,
}

CONFIG_FILENAME = "config.yaml"


def get_config_file_path() -> Path:
    """
    Get the path to the configuration file.
    The configuration file is located at ~/.ptodo/config.yaml or $PTODO_DIRECTORY/config.yaml.

    Returns:
        Path: The path to the configuration file.
    """
    ptodo_dir = get_ptodo_directory()
    return ptodo_dir / CONFIG_FILENAME


def ensure_config_file_exists() -> None:
    """
    Ensure the configuration file exists.
    If the file doesn't exist, create it with default values.
    """
    config_path = get_config_file_path()
    if not config_path.exists():
        # Create the parent directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the default configuration
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)


def load_config() -> Dict[str, Any]:
    """
    Load the configuration from the file.
    If the file doesn't exist, create it with default values.

    Returns:
        Dict[str, Any]: The configuration dictionary.
    """
    ensure_config_file_exists()
    config_path = get_config_file_path()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Merge with defaults for any missing keys
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

        return config
    except (yaml.YAMLError, OSError) as e:
        print(f"Error loading config file: {e}")
        return DEFAULT_CONFIG.copy()


def get_config(key: str, default: Any = None) -> Any:
    """
    Get a configuration value.

    Args:
        key (str): The configuration key to get.
        default (Any, optional): The default value to return if the key doesn't exist.
            If not provided, the value from DEFAULT_CONFIG is used if available.

    Returns:
        Any: The configuration value.
    """
    config = load_config()
    if key in config:
        return config[key]

    # Use the provided default, or the default from DEFAULT_CONFIG
    if default is not None:
        return default
    return DEFAULT_CONFIG.get(key)


def set_config(key: str, value: Any) -> None:
    """
    Set a configuration value and save it to the file.

    Args:
        key (str): The configuration key to set.
        value (Any): The configuration value to set.
    """
    config = load_config()
    config[key] = value
    save_config(config)


def save_config(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Save the configuration to the file.

    Args:
        config (Optional[Dict[str, Any]], optional): The configuration to save.
            If not provided, the current configuration is loaded and saved.
    """
    if config is None:
        config = load_config()

    config_path = get_config_file_path()

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False)
    except (yaml.YAMLError, OSError) as e:
        print(f"Error saving config file: {e}")


def update_config(updates: Dict[str, Any]) -> None:
    """
    Update multiple configuration values at once and save.

    Args:
        updates (Dict[str, Any]): A dictionary of configuration updates.
    """
    config = load_config()
    config.update(updates)
    save_config(config)
