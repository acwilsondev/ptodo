import os
import shutil
import tempfile
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestAddCommand:
    """Tests for the add command functionality of ptodo."""

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for todo.txt files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @patch("sys.argv")
    def test_add_command(
        self, mock_argv: MagicMock, temp_dir: str, capsys: CaptureFixture[str]
    ) -> None:
        """Test the add command."""
        todo_file = os.path.join(temp_dir, "todo.txt")
        # Create an empty todo.txt file if it doesn't exist
        if not os.path.exists(todo_file):
            with open(todo_file, "w") as f:
                pass  # Create an empty file

        # Set environment variable to use our test file
        os.environ["TODO_FILE"] = todo_file
        mock_argv.__getitem__.side_effect = lambda idx: [
            "ptodo",
            "add",
            "Test task +Test @CLI",
        ][idx]

        main()
        captured = capsys.readouterr()

        # Clean up environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

        with open(todo_file, "r") as f:
            content = f.read()

        assert "Test task +Test @CLI" in content
        assert "Task added" in captured.out or "Added:" in captured.out

