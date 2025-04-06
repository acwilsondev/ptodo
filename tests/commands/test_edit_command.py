import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestEditCommand:
    """Tests for the edit command functionality of ptodo."""

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for todo.txt files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def todo_file(self, temp_dir: str) -> Generator[str, None, None]:
        """Create an empty test todo.txt file."""
        todo_file = os.path.join(temp_dir, "todo.txt")
        with open(todo_file, "w") as f:
            f.write("Sample task for editing\n")
        # Set the environment variable to use our test file
        os.environ["TODO_FILE"] = todo_file
        yield todo_file
        # Clean up the environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    @patch("os.system")
    @patch.dict(os.environ, {"EDITOR": "test-editor"})
    def test_edit_command_with_editor_env(
        self,
        mock_system: MagicMock,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the edit command uses the EDITOR environment variable."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "edit"][idx]
        
        # Simulate successful editor execution
        mock_system.return_value = 0

        # Run the edit command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Edited" in captured.out
        
        # Verify the correct editor command was executed
        mock_system.assert_called_once()
        args = mock_system.call_args[0][0]
        assert "test-editor" in args
        assert todo_file in args

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    @patch("os.system")
    @patch.dict(os.environ, {}, clear=True)  # Clear environ to remove EDITOR
    def test_edit_command_without_editor_env(
        self,
        mock_system: MagicMock,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the edit command uses the default editor when EDITOR is not set."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "edit"][idx]
        
        # Need to set TODO_FILE since patch.dict clears the environment
        os.environ["TODO_FILE"] = todo_file
        
        # Simulate successful editor execution
        mock_system.return_value = 0

        # Run the edit command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Edited" in captured.out
        
        # Verify a default editor was used
        mock_system.assert_called_once()
        args = mock_system.call_args[0][0]
        assert "vi" in args  # Default editor should be vi
        assert todo_file in args

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    @patch("os.system")
    @patch.dict(os.environ, {"EDITOR": "test-editor"})
    def test_edit_command_with_editor_error(
        self,
        mock_system: MagicMock,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the edit command handles error from editor."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "edit"][idx]
        
        # Simulate editor failure with non-zero exit code
        mock_system.return_value = 1

        # Run the edit command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result != 0  # Should return error code
        assert "Error" in captured.out
        assert "exit code" in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    @patch("os.system")
    @patch.dict(os.environ, {"EDITOR": "test-editor"})
    def test_edit_command_quiet_mode(
        self,
        mock_system: MagicMock,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the edit command in quiet mode doesn't output success message."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "edit", "--quiet"][idx]
        
        # Simulate successful editor execution
        mock_system.return_value = 0

        # Run the edit command in quiet mode
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert captured.out == ""  # Should not output anything in quiet mode
        
        # Verify the editor was still called
        mock_system.assert_called_once()

