import os
import shutil
import tempfile
from unittest.mock import patch
from pathlib import Path

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
            f.write("(A) 2023-05-01 Call mom +Family @Phone\n")
            f.write("(B) 2023-05-02 Buy groceries +Shopping @Errands\n")
            f.write("2023-05-03 Finish report +Work @Computer\n")
        return todo_file

    @pytest.fixture
    def done_file(self, temp_dir):
        """Create a test done.txt file."""
        done_file = os.path.join(temp_dir, "done.txt")
        with open(done_file, "w") as f:
            f.write("x 2023-05-04 2023-05-01 Pay bills +Finance @Online\n")
        return done_file

    @patch("sys.argv")
    @patch("ptodo.app.get_todo_file_path")
    def test_list_command(self, mock_get_path, mock_argv, todo_file, capsys):
        """Test the list command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "list"][idx]

        main()
        captured = capsys.readouterr()

        assert "Call mom" in captured.out
        assert "Buy groceries" in captured.out
        assert "Finish report" in captured.out
        assert "(A)" in captured.out
        assert "(B)" in captured.out

    @patch("sys.argv")
    @patch("ptodo.app.get_todo_file_path")
    def test_add_command(self, mock_get_path, mock_argv, temp_dir, capsys):
        """Test the add command."""
        todo_file = os.path.join(temp_dir, "todo.txt")
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: [
            "ptodo",
            "add",
            "Test task +Test @CLI",
        ][idx]

        main()
        captured = capsys.readouterr()

        with open(todo_file, "r") as f:
            content = f.read()

        assert "Test task +Test @CLI" in content
        assert "Task added" in captured.out or "Added:" in captured.out

    @patch("sys.argv")
    @patch("ptodo.app.get_todo_file_path")
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
    @patch("ptodo.app.get_todo_file_path")
    def test_pri_command(self, mock_get_path, mock_argv, todo_file, capsys):
        """Test the pri (priority) command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "pri", "3", "A"][idx]

        main()
        captured = capsys.readouterr()

        with open(todo_file, "r") as f:
            content = f.read()

        assert "(A) 2023-05-03 Finish report" in content
        assert "updated" in captured.out.lower()

    @patch("sys.argv")
    @patch("ptodo.app.get_todo_file_path")
    def test_projects_command(self, mock_get_path, mock_argv, todo_file, capsys):
        """Test the projects command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "projects"][idx]

        main()
        captured = capsys.readouterr()

        assert "Family" in captured.out
        assert "Shopping" in captured.out
        assert "Work" in captured.out

    @patch("sys.argv")
    @patch("ptodo.app.get_todo_file_path")
    def test_contexts_command(self, mock_get_path, mock_argv, todo_file, capsys):
        """Test the contexts command."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "contexts"][idx]

        main()
        captured = capsys.readouterr()

        assert "Phone" in captured.out
        assert "Errands" in captured.out
        assert "Computer" in captured.out

    @patch("sys.argv")
    @patch("ptodo.app.get_todo_file_path")
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
        with patch("ptodo.app.get_done_file_path", return_value=Path(done_file)):
            main()

        captured = capsys.readouterr()

        with open(todo_file, "r") as f:
            todo_content = f.read()
        with open(done_file, "r") as f:
            done_content = f.read()

        assert "Call mom" not in todo_content
        assert "Call mom" in done_content
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
