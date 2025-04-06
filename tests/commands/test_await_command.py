import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestAwaitCommand:
    """Tests for the await command functionality of ptodo."""

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
            pass  # Create an empty file
        # Set the environment variable to use our test file
        os.environ["TODO_FILE"] = todo_file
        yield todo_file
        # Clean up the environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_await_command_basic(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the await command creates a task with waiting context and due date."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: [
            "ptodo",
            "await",
            "Waiting for response",
            "2023-12-31",
        ][idx]

        # Run the await command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Added waiting-for task" in captured.out

        # Verify the file content
        with open(todo_file, "r") as f:
            content = f.read()

        # Check task properties
        assert "Waiting for response" in content
        assert "@waiting" in content
        assert "due:2023-12-31" in content

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_await_command_with_priority(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the await command with a priority specified."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: [
            "ptodo",
            "await",
            "Waiting for urgent response",
            "2023-12-31",
            "-p",
            "A",
        ][idx]

        # Run the await command with priority
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Added waiting-for task" in captured.out

        # Verify the file content
        with open(todo_file, "r") as f:
            content = f.read()

        # Check task properties
        assert "Waiting for urgent response" in content
        assert "@waiting" in content
        assert "due:2023-12-31" in content
        assert "(A)" in content  # Priority should be set

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_await_command_invalid_date(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the await command with an invalid date format."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: [
            "ptodo",
            "await",
            "Waiting for response",
            "invalid-date",
        ][idx]

        # Run the await command with invalid date
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result != 0  # Should return error code
        assert "Error" in captured.out
        assert "Invalid date format" in captured.out

        # Verify no task was added
        with open(todo_file, "r") as f:
            content = f.read().strip()
        assert content == ""  # File should still be empty

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_await_command_future_date(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the await command with a future date."""
        mock_get_path.return_value = Path(todo_file)
        # Use a date far in the future to avoid test expiration
        mock_argv.__getitem__.side_effect = lambda idx: [
            "ptodo",
            "await",
            "Waiting for future response",
            "2030-12-31",
        ][idx]

        # Run the await command with future date
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Added waiting-for task" in captured.out

        # Verify the file content
        with open(todo_file, "r") as f:
            content = f.read()

        # Check task properties and metadata
        assert "Waiting for future response" in content
        assert "@waiting" in content
        assert "due:2030-12-31" in content

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_await_command_with_other_metadata(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the await command with a task that includes other metadata."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: [
            "ptodo",
            "await",
            "Waiting for response from John effort:3",
            "2023-12-31",
        ][idx]

        # Run the await command with a task that has additional metadata
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Added waiting-for task" in captured.out

        # Verify the file content
        with open(todo_file, "r") as f:
            content = f.read()

        # Check task properties and all metadata
        assert "Waiting for response from John" in content
        assert "@waiting" in content
        assert "due:2023-12-31" in content
        assert "effort:3" in content  # Should preserve the effort metadata
