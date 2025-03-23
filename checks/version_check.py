#!/usr/bin/env python3
"""
Script to check if version in setup.py matches the VERSION in ptodo/app.py
"""
import re
import sys
from pathlib import Path


def extract_version_from_setup():
    """Extract version from setup.py file."""
    setup_path = Path(__file__).parent.parent / "setup.py"

    if not setup_path.exists():
        print(f"Error: Could not find setup.py at {setup_path}")
        sys.exit(1)

    with open(setup_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Look for version="X.X.X" pattern
    version_match = re.search(r'version="([^"]+)"', content)
    if version_match:
        return version_match.group(1)

    print("Error: Could not find version in setup.py")
    sys.exit(1)


def extract_version_from_app():
    """Extract VERSION from ptodo/app.py file."""
    app_path = Path(__file__).parent.parent / "ptodo" / "app.py"

    if not app_path.exists():
        print(f"Error: Could not find app.py at {app_path}")
        sys.exit(1)

    with open(app_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Look for VERSION="X.X.X" pattern
    version_match = re.search(r"VERSION\s*=\s*\"([^\"]+)\"", content)
    if version_match:
        return version_match.group(1)

    print("Error: Could not find VERSION in ptodo/app.py")
    sys.exit(1)


def main():
    """Main function to compare versions."""
    setup_version = extract_version_from_setup()
    app_version = extract_version_from_app()

    print(f"Version in setup.py: {setup_version}")
    print(f"Version in app.py: {app_version}")

    if setup_version == app_version:
        print("✓ Versions match!")
        return 0

    print("✗ Version mismatch!")
    print(f'  setup.py has version="{setup_version}"')
    print(f'  app.py has VERSION="{app_version}"')
    print("Please update the versions to match.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
