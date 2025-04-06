import argparse
import unittest
from typing import Any, Callable, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest import CaptureFixture

from ptodo.commands.config_commands import cmd_config
from ptodo.config import DEFAULT_CONFIG


class TestConfigCommands:
    """Tests for the configuration commands in ptodo."""

    @pytest.fixture
    def mock_config_deps(self) -> Generator[Dict[str, MagicMock], None, None]:
        """Mock configuration dependencies."""
        with patch("ptodo.commands.config_commands.load_config") as mock_load, patch(
            "ptodo.commands.config_commands.get_config"
        ) as mock_get, patch(
            "ptodo.commands.config_commands.set_config"
        ) as mock_set, patch(
            "ptodo.commands.config_commands.update_config"
        ) as mock_update:

            # Set up mock return values
            mock_load.return_value = {
                "default_view": "all",
                "color_enabled": True,
                "priority_colors": {"A": "red", "B": "yellow", "C": "green"},
            }

            # Configure get_config to return values based on key
            def mock_get_config(key: str) -> Any:
                if key == "default_view":
                    return "all"
                elif key == "color_enabled":
                    return True
                elif key == "priority_colors":
                    return {"A": "red", "B": "yellow", "C": "green"}
                elif key == "unknown_key":
                    return None
                else:
                    return None

            mock_get.side_effect = mock_get_config

            yield {
                "load_config": mock_load,
                "get_config": mock_get,
                "set_config": mock_set,
                "update_config": mock_update,
            }

    def test_show_command(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'show' command."""
        # Create args
        args = argparse.Namespace(config_command="show")

        # Call the function
        result = cmd_config(args)

        # Check results
        mock_config_deps["load_config"].assert_called_once()
        captured = capsys.readouterr()
        assert result == 0
        assert "Current configuration settings:" in captured.out
        assert "default_view: all" in captured.out
        assert "color_enabled: True" in captured.out
        assert "priority_colors:" in captured.out

    def test_get_command_existing_key(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'get' command with an existing key."""
        # Create args
        args = argparse.Namespace(config_command="get", key="default_view")

        # Call the function
        result = cmd_config(args)

        # Check results
        mock_config_deps["get_config"].assert_called_once_with("default_view")
        captured = capsys.readouterr()
        assert result == 0
        assert "default_view: all" in captured.out

    def test_get_command_nonexistent_key(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'get' command with a nonexistent key."""
        # Create args
        args = argparse.Namespace(config_command="get", key="unknown_key")

        # Call the function
        result = cmd_config(args)

        # Check results
        mock_config_deps["get_config"].assert_called_once_with("unknown_key")
        captured = capsys.readouterr()
        assert result == 1
        assert "No configuration setting found" in captured.out

    def test_set_command_boolean_true(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'set' command with a boolean value (true)."""
        # Test different boolean representations
        boolean_values = ["true", "yes", "1", "True", "YES"]

        for value in boolean_values:
            # Create args
            args = argparse.Namespace(
                config_command="set", key="color_enabled", value=value
            )

            # Call the function
            result = cmd_config(args)

            # Check results
            mock_config_deps["set_config"].assert_called_with("color_enabled", True)
            captured = capsys.readouterr()
            assert result == 0
            assert "has been set to 'True'" in captured.out

    def test_set_command_boolean_false(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'set' command with a boolean value (false)."""
        # Test different boolean representations
        boolean_values = ["false", "no", "0", "False", "NO"]

        for value in boolean_values:
            # Create args
            args = argparse.Namespace(
                config_command="set", key="color_enabled", value=value
            )

            # Call the function
            result = cmd_config(args)

            # Check results
            mock_config_deps["set_config"].assert_called_with("color_enabled", False)
            captured = capsys.readouterr()
            assert result == 0
            assert "has been set to 'False'" in captured.out

    def test_set_command_integer(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'set' command with an integer value."""
        # Create args
        args = argparse.Namespace(config_command="set", key="max_tasks", value="42")

        # Call the function
        result = cmd_config(args)

        # Check results
        mock_config_deps["set_config"].assert_called_once_with("max_tasks", 42)
        captured = capsys.readouterr()
        assert result == 0
        assert "has been set to '42'" in captured.out

    def test_set_command_float(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'set' command with a float value."""
        # Create args
        args = argparse.Namespace(config_command="set", key="timeout", value="3.14")

        # Call the function
        result = cmd_config(args)

        # Check results
        mock_config_deps["set_config"].assert_called_once_with("timeout", 3.14)
        captured = capsys.readouterr()
        assert result == 0
        assert "has been set to '3.14'" in captured.out

    def test_set_command_string(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'set' command with a string value."""
        # Create args
        args = argparse.Namespace(config_command="set", key="editor", value="vim")

        # Call the function
        result = cmd_config(args)

        # Check results
        mock_config_deps["set_config"].assert_called_once_with("editor", "vim")
        captured = capsys.readouterr()
        assert result == 0
        assert "has been set to 'vim'" in captured.out

    def test_set_command_error(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'set' command with an error during setting."""
        # Setup mock to raise an exception
        mock_config_deps["set_config"].side_effect = ValueError("Invalid value")

        # Create args
        args = argparse.Namespace(
            config_command="set", key="invalid_key", value="invalid_value"
        )

        # Call the function
        result = cmd_config(args)

        # Check results
        mock_config_deps["set_config"].assert_called_once_with(
            "invalid_key", "invalid_value"
        )
        captured = capsys.readouterr()
        assert result == 2
        assert "Error setting configuration" in captured.out

    def test_reset_command(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'reset' command."""
        # Create args
        args = argparse.Namespace(config_command="reset")

        # Call the function
        result = cmd_config(args)

        # Check results
        mock_config_deps["update_config"].assert_called_once_with(DEFAULT_CONFIG)
        captured = capsys.readouterr()
        assert result == 0
        assert "Configuration has been reset to default values" in captured.out

    def test_reset_command_error(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test the 'reset' command with an error during update."""
        # Setup mock to raise an exception
        mock_config_deps["update_config"].side_effect = ValueError("Update error")

        # Create args
        args = argparse.Namespace(config_command="reset")

        # Call the function
        result = cmd_config(args)

        # Check results
        mock_config_deps["update_config"].assert_called_once_with(DEFAULT_CONFIG)
        captured = capsys.readouterr()
        assert result == 2
        assert "Error resetting configuration" in captured.out

    def test_unknown_command(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test an unknown configuration command."""
        # Create args
        args = argparse.Namespace(config_command="unknown_command")

        # Call the function
        result = cmd_config(args)

        # Check results
        captured = capsys.readouterr()
        assert result == 3
        assert "Unknown configuration command" in captured.out

    def test_unexpected_exception(
        self, mock_config_deps: Dict[str, MagicMock], capsys: CaptureFixture[str]
    ) -> None:
        """Test unexpected exception handling."""
        # Setup mocks to raise an exception
        mock_config_deps["load_config"].side_effect = Exception("Unexpected error")

        # Create args
        args = argparse.Namespace(config_command="show")

        # Call the function
        result = cmd_config(args)

        # Check results
        captured = capsys.readouterr()
        assert result == 4
        assert "Unexpected error" in captured.out


if __name__ == "__main__":
    pytest.main()
