import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestArchiveCommand:
    """Tests for the archive command functionality of ptodo."""

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

    @pytest.fixture
    def done_file(self, temp_dir: str) -> Generator[str, None, None]:
        """Create a test done.txt file."""
        done_file = os.path.join(temp_dir, "done.txt")
        with open(done_file, "w") as f:
            f.write("x 2023-05-04 2023-05-01 Pay bills +Finance @Online\n")
        # Set the environment variable to use our test file
        os.environ["DONE_FILE"] = done_file
        yield done_file
        # Clean up the environment variable
        if "DONE_FILE" in os.environ:
            del os.environ["DONE_FILE"]

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_archive_command(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        done_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the archive command."""
        # First mark a task as done
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "done", "1"][idx]
        main()

        # Then archive completed tasks
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "archive"][idx]
        with patch("ptodo.core.get_done_file_path", return_value=Path(done_file)):
            main()

        captured = capsys.readouterr()

        with open(todo_file, "r") as f:
            todo_content = f.read()
        with open(done_file, "r") as f:
            done_content = f.read()

        assert "Test task" not in todo_content
        assert "Test task" in done_content
        assert "archived" in captured.out.lower() or "moved" in captured.out.lower()

