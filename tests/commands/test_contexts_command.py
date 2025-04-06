import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestContextsCommand:
    """Tests for the contexts command functionality of ptodo."""

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for todo.txt files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def todo_file(self, temp_dir: str) -> Generator[str, None, None]:
        """Create a test todo.txt file."""
        todo_file = os.path.join(temp_dir, "todo.txt")
        with open(todo_file, "w") as f:
            f.write("(A) Test task\n")
            f.write("test task +test-project\n")
            f.write("test task with a context @home\n")
        # Set the environment variable to use our test file
        os.environ["TODO_FILE"] = todo_file
        yield todo_file
        # Clean up the environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_contexts_command(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the contexts command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "contexts"][idx]

        main()
        captured = capsys.readouterr()

        assert "home" in captured.out

