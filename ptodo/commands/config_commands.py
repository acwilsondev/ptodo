#!/usr/bin/env python3
import argparse

from ..config import (
    DEFAULT_CONFIG,
    get_config,
    load_config,
    set_config,
    update_config,
)


def cmd_config(args: argparse.Namespace) -> None:
    """
    Handle configuration settings - show, get, set, or reset.

    Args:
        args: Command-line arguments with config_command (show, get, set, reset)
              and any other required parameters
    """
    if args.config_command == "show":
        # Show all configuration settings
        config = load_config()
        print("Current configuration settings:")
        for key, value in sorted(config.items()):
            print(f"  {key}: {value}")

    elif args.config_command == "get":
        # Get a specific configuration setting
        key = args.key
        value = get_config(key)
        if value is not None:
            print(f"{key}: {value}")
        else:
            print(f"No configuration setting found for '{key}'")

    elif args.config_command == "set":
        # Set a specific configuration setting
        key = args.key
        value = args.value

        # Try to convert value to appropriate type
        # If it looks like a boolean, convert it
        if value.lower() in ("true", "yes", "1"):
            value = True
        elif value.lower() in ("false", "no", "0"):
            value = False
        # If it looks like a number, convert it
        elif value.isdigit():
            value = int(value)
        elif value.replace(".", "", 1).isdigit() and value.count(".") <= 1:
            value = float(value)

        set_config(key, value)
        print(f"Configuration setting '{key}' has been set to '{value}'")

    elif args.config_command == "reset":
        # Reset all configuration settings to defaults
        update_config(DEFAULT_CONFIG)
        print("Configuration has been reset to default values:")
        for key, value in sorted(DEFAULT_CONFIG.items()):
            print(f"  {key}: {value}")
