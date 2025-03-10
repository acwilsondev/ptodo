import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ptodo.app import main


class TestApp:
    """Tests for the command-line functionality of ptodo."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for todo.txt files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def todo_file(self, temp_dir):
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
    def done_file(self, temp_dir):
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
    def test_list_command(self, mock_get_path, mock_argv, todo_file, capsys):
        """Test the list command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "list"][idx]

        main()
        captured = capsys.readouterr()

        assert "Test task" in captured.out
        assert "test task" in captured.out
        assert "test task with a context" in captured.out
        assert "(A)" in captured.out

    @patch("sys.argv")
    def test_add_command(self, mock_argv, temp_dir, capsys):
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

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_done_command(self, mock_get_path, mock_argv, todo_file, capsys):
        """Test the done command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "done", "1"][idx]

        main()
        captured = capsys.readouterr()

        with open(todo_file, "r") as f:
            content = f.read()

        assert "x " in content
        assert (
            "completed" in captured.out.lower()
            or "marked as done" in captured.out.lower()
        )

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_pri_command(self, mock_get_path, mock_argv, todo_file, capsys):
        """Test the pri (priority) command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "pri", "3", "A"][idx]

        main()
        captured = capsys.readouterr()

        with open(todo_file, "r") as f:
            content = f.read()

        assert "(A) test task with a context" in content
        assert "updated" in captured.out.lower()

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_projects_command(self, mock_get_path, mock_argv, todo_file, capsys):
        """Test the projects command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "projects"][idx]

        main()
        captured = capsys.readouterr()

        assert "test-project" in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_contexts_command(self, mock_get_path, mock_argv, todo_file, capsys):
        """Test the contexts command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "contexts"][idx]

        main()
        captured = capsys.readouterr()

        assert "home" in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_archive_command(
        self, mock_get_path, mock_argv, todo_file, done_file, capsys
    ):
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

    @patch("sys.argv")
    def test_help_command(self, mock_argv, capsys):
        """Test the help command."""
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "--help"][idx]

        # The main function would typically exit when showing help
        # We catch the SystemExit to continue the test
        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()

        # Check for common help text indicators
        assert "usage" in captured.out.lower()
        assert "commands" in captured.out.lower() or "options" in captured.out.lower()


if __name__ == "__main__":
    pytest.main()
