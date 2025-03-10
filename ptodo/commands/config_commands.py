#!/usr/bin/env python3
import argparse

from ..config import (
    DEFAULT_CONFIG,
    get_config,
    load_config,
    set_config,
    update_config,
)


def cmd_config(args: argparse.Namespace) -> int:
    """
    Handle configuration settings - show, get, set, or reset.

    Args:
        args: Command-line arguments with config_command (show, get, set, reset)
              and any other required parameters

    Returns:
        int: 0 for success, non-zero values for errors:
             1 - Configuration key not found
             2 - Configuration update error
             3 - Unknown configuration command
             4 - Unexpected error
    """
    try:
        if args.config_command == "show":
            # Show all configuration settings
            config = load_config()
            print("Current configuration settings:")
            for key, value in sorted(config.items()):
                print(f"  {key}: {value}")
            return 0

        elif args.config_command == "get":
            # Get a specific configuration setting
            key = args.key
            value = get_config(key)
            if value is not None:
                print(f"{key}: {value}")
                return 0
            else:
                print(f"No configuration setting found for '{key}'")
                return 1

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

            try:
                set_config(key, value)
                print(f"Configuration setting '{key}' has been set to '{value}'")
                return 0
            except Exception as e:
                print(f"Error setting configuration: {e}")
                return 2

        elif args.config_command == "reset":
            # Reset all configuration settings to defaults
            try:
                update_config(DEFAULT_CONFIG)
                print("Configuration has been reset to default values:")
                for key, value in sorted(DEFAULT_CONFIG.items()):
                    print(f"  {key}: {value}")
                return 0
            except Exception as e:
                print(f"Error resetting configuration: {e}")
                return 2
        else:
            print(f"Unknown configuration command: {args.config_command}")
            return 3
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 4
