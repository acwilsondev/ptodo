import os
import sys
import warnings
from functools import lru_cache

# Configuration constants
ENV_DEPRECATION_ENABLED = "PTODO_DEPRECATION_ENABLED"
ENV_DEPRECATION_WARNING_TYPE = "PTODO_DEPRECATION_WARNING_TYPE"

# Warning types
WARNING_TYPE_STDERR = "stderr"  # Print to stderr (default)
WARNING_TYPE_STDOUT = "stdout"  # Print to stdout
WARNING_TYPE_PYTHON = "python"  # Use Python's warning system
WARNING_TYPE_SILENT = "silent"  # No warnings

# Default configuration
DEFAULT_DEPRECATION_ENABLED = True
DEFAULT_WARNING_TYPE = WARNING_TYPE_STDERR


def get_config_value(env_var: str, default: str) -> str:
    """Get configuration value from environment variable with fallback to default."""
    value = os.environ.get(env_var)
    return value if value is not None else default


@lru_cache(maxsize=1)
def is_deprecation_enabled() -> bool:
    """
    Check if deprecation warnings are enabled.

    Controlled by PTODO_DEPRECATION_ENABLED environment variable.
    Set to "0", "false", or "no" to disable warnings.

    Returns:
        bool: True if deprecation warnings are enabled, False otherwise.
    """
    enabled_str = get_config_value(
        ENV_DEPRECATION_ENABLED, str(DEFAULT_DEPRECATION_ENABLED)
    )
    return enabled_str.lower() not in ("0", "false", "no", "off")


@lru_cache(maxsize=1)
def get_warning_type() -> str:
    """
    Get the type of warning to use.

    Controlled by PTODO_DEPRECATION_WARNING_TYPE environment variable.
    Valid values: "stderr", "stdout", "python", "silent"

    Returns:
        str: Warning type to use.
    """
    warning_type = get_config_value(ENV_DEPRECATION_WARNING_TYPE, DEFAULT_WARNING_TYPE)
    if warning_type not in (
        WARNING_TYPE_STDERR,
        WARNING_TYPE_STDOUT,
        WARNING_TYPE_PYTHON,
        WARNING_TYPE_SILENT,
    ):
        return DEFAULT_WARNING_TYPE
    return warning_type


def warn_deprecated_command(
    old_command: str, new_command: str, version: str = "2.0"
) -> None:
    """
    Show a deprecation warning for old commands.

    Args:
        old_command (str): The deprecated command that was used.
        new_command (str): The new recommended command format.
        version (str, optional): Version when the command will be removed. Defaults to "2.0".
    """
    if not is_deprecation_enabled():
        return

    message = (
        f"Warning: '{old_command}' is deprecated and will be removed in version {version}. "
        f"Please use '{new_command}' instead."
    )

    warning_type = get_warning_type()

    if warning_type == WARNING_TYPE_STDERR:
        print(message, file=sys.stderr)
    elif warning_type == WARNING_TYPE_STDOUT:
        print(message)
    elif warning_type == WARNING_TYPE_PYTHON:
        warnings.warn(message, DeprecationWarning, stacklevel=2)
    # Silent type does nothing
