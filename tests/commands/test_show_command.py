import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestShowCommand:
    """Tests for the show command functionality of ptodo."""

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for todo.txt files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def todo_file(self, temp_dir: str) -> Generator[str, None, None]:
        """Create a test todo.txt file with rich content for show command testing."""
        todo_file = os.path.join(temp_dir, "todo.txt")
        with open(todo_file, "w") as f:
            f.write("(A) Test task with priority\n")
            f.write("test task +test-project @work due:2023-12-31\n")
            f.write(
                "test task with @multiple @contexts +and +multiple-projects effort:2\n"
            )
        # Set the environment variable to use our test file
        os.environ["TODO_FILE"] = todo_file
        yield todo_file
        # Clean up the environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_show_command_success(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the show command for displaying task details successfully."""
        mock_get_path.return_value = Path(todo_file)
        # Show the second task which has metadata
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "show", "2"][idx]

        # Run the show command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0

        # Verify task details are displayed
        output = captured.out
        assert "Task #2" in output
        assert "test task" in output
        assert "+test-project" in output
        assert "@work" in output
        assert "due:2023-12-31" in output or "due: 2023-12-31" in output
        assert "Projects:" in output
        assert "Contexts:" in output
        assert "Metadata:" in output

        # Verify raw format is also displayed
        assert "Raw format:" in output

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_show_command_with_multiple_attributes(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the show command for a task with multiple contexts, projects and effort metadata."""
        mock_get_path.return_value = Path(todo_file)
        # Show the third task which has multiple contexts and projects
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "show", "3"][idx]

        # Run the show command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0

        # Verify task details are displayed
        output = captured.out
        assert "Task #3" in output
        assert "test task with" in output
        assert "@multiple" in output
        assert "@contexts" in output
        assert "+and" in output
        assert "+multiple-projects" in output
        assert "effort:2" in output or "effort: 2" in output
        assert "Projects:" in output
        assert "Contexts:" in output
        assert "Effort:" in output

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_show_command_invalid_task_id(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the show command with an invalid task ID."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "show", "99"][idx]

        # Run the show command with an invalid task ID
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result != 0  # Should return non-zero exit code for error
        assert "Error" in captured.out
        assert "out of range" in captured.out
