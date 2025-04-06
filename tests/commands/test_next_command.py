import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestNextCommand:
    """Tests for the next command functionality of ptodo."""

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for todo.txt files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def todo_file(self, temp_dir: str) -> Generator[str, None, None]:
        """Create a test todo.txt file with tasks of different priorities."""
        todo_file = os.path.join(temp_dir, "todo.txt")
        with open(todo_file, "w") as f:
            f.write("(A) Highest priority task +project1 @context1\n")
            f.write("(B) Medium priority task +project2 @context2\n")
            f.write("(C) Lower priority task +project1 @context2\n")
            f.write("No priority task +project3 @context3\n")
            f.write("x (A) Completed high priority task\n")  # Should be ignored
            f.write("(A) Another highest task +project4 @context1\n")
        # Set the environment variable to use our test file
        os.environ["TODO_FILE"] = todo_file
        yield todo_file
        # Clean up the environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

    @pytest.fixture
    def empty_todo_file(self, temp_dir: str) -> Generator[str, None, None]:
        """Create an empty todo.txt file for testing no tasks case."""
        todo_file = os.path.join(temp_dir, "empty_todo.txt")
        with open(todo_file, "w") as f:
            pass  # Create an empty file
        yield todo_file

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_next_command_highest_priority(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test that next command returns the highest priority task."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "next"][idx]

        # Run the next command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Highest priority task" in captured.out
        assert "(A)" in captured.out
        # Should not include completed tasks or lower priority tasks
        assert "Completed high priority" not in captured.out
        assert "(B) Medium priority" not in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_next_command_with_project_filter(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test next command with project filter."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "next", "+project2"][idx]

        # Run the next command with project filter
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Medium priority task" in captured.out
        assert "+project2" in captured.out
        # Should not include tasks from other projects
        assert "Highest priority task" not in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_next_command_with_context_filter(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test next command with context filter."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "next", "@context2"][idx]

        # Run the next command with context filter
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Medium priority task" in captured.out
        assert "@context2" in captured.out
        # Should not include tasks from other contexts
        assert "Highest priority task" not in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_next_command_no_matching_tasks(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test next command when no tasks match the filter."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "next", "+nonexistent-project"][idx]

        # Run the next command with a filter that matches no tasks
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "No matching tasks found" in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_next_command_empty_todo_file(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        empty_todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test next command with an empty todo file."""
        mock_get_path.return_value = Path(empty_todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "next"][idx]

        # Set the environment variable to use our empty test file
        os.environ["TODO_FILE"] = empty_todo_file

        # Run the next command with an empty todo file
        result = main()
        captured = capsys.readouterr()

        # Clean up the environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

        # Check result
        assert result == 0
        assert "No matching tasks found" in captured.out

