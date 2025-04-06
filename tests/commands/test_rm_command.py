import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestRmCommand:
    """Tests for the rm command functionality of ptodo."""

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
    def test_rm_command_success(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the rm command for successful task removal."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "rm", "2"][idx]

        # Verify initial content
        with open(todo_file, "r") as f:
            initial_content = f.read()
        assert "test task +test-project" in initial_content

        # Run the rm command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Removed" in captured.out

        # Verify the task was removed
        with open(todo_file, "r") as f:
            final_content = f.read()
        assert "test task +test-project" not in final_content
        assert "(A) Test task" in final_content
        assert "test task with a context @home" in final_content

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_rm_command_invalid_task_id(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the rm command with an invalid task ID."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "rm", "99"][idx]

        # Verify initial content
        with open(todo_file, "r") as f:
            initial_content = f.read()

        # Run the rm command with an invalid task ID
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result != 0  # Should return non-zero exit code for error
        assert "Error" in captured.out
        assert "out of range" in captured.out

        # Verify no tasks were removed
        with open(todo_file, "r") as f:
            final_content = f.read()
        assert final_content == initial_content

