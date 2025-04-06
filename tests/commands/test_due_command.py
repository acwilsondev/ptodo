import os
import shutil
import tempfile
from datetime import date, timedelta
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestDueCommand:
    """Tests for the due command functionality of ptodo."""

    # Mock a fixed date as "today" for consistent testing
    MOCK_TODAY = date(2023, 5, 15)  # Use a fixed date as "today"

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for todo.txt files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def todo_file(self, temp_dir: str) -> Generator[str, None, None]:
        """Create a test todo.txt file with tasks having different due dates."""
        todo_file = os.path.join(temp_dir, "todo.txt")
        with open(todo_file, "w") as f:
            # Task due yesterday (overdue)
            yesterday = (self.MOCK_TODAY - timedelta(days=1)).strftime("%Y-%m-%d")
            f.write(f"Overdue task due:{yesterday}\n")
            
            # Task due today
            today = self.MOCK_TODAY.strftime("%Y-%m-%d")
            f.write(f"Task due today due:{today}\n")
            
            # Task due tomorrow
            tomorrow = (self.MOCK_TODAY + timedelta(days=1)).strftime("%Y-%m-%d")
            f.write(f"Task due tomorrow due:{tomorrow}\n")
            
            # Task due in 3 days
            in_three_days = (self.MOCK_TODAY + timedelta(days=3)).strftime("%Y-%m-%d")
            f.write(f"Task due in 3 days due:{in_three_days}\n")
            
            # Task due in 7 days
            in_week = (self.MOCK_TODAY + timedelta(days=7)).strftime("%Y-%m-%d")
            f.write(f"Task due in a week due:{in_week}\n")
            
            # Task with no due date
            f.write("Task with no due date\n")
            
            # Completed task with due date (should be ignored)
            f.write(f"x 2023-05-14 Completed task due:{today}\n")
            
            # Task overdue by 10 days (for testing overdue duration)
            very_overdue = (self.MOCK_TODAY - timedelta(days=10)).strftime("%Y-%m-%d")
            f.write(f"Very overdue task due:{very_overdue}\n")
        
        # Set the environment variable to use our test file
        os.environ["TODO_FILE"] = todo_file
        yield todo_file
        # Clean up the environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    @patch("datetime.date")
    def test_due_command_today(
        self,
        mock_date: MagicMock,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the due command shows tasks due today or earlier."""
        mock_date.today.return_value = self.MOCK_TODAY
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "due"][idx]

        # Run the due command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        
        # Should include today and overdue tasks
        assert "Task due today" in captured.out
        assert "Overdue task" in captured.out
        assert "Very overdue task" in captured.out
        
        # Should not include future tasks
        assert "Task due tomorrow" not in captured.out
        assert "Task due in 3 days" not in captured.out
        assert "Task due in a week" not in captured.out
        
        # Should not include completed tasks
        assert "Completed task" not in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    @patch("datetime.date")
    def test_due_command_with_soon_option(
        self,
        mock_date: MagicMock,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the due command with --soon option shows tasks due within specified days."""
        mock_date.today.return_value = self.MOCK_TODAY
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "due", "--soon", "3"][idx]

        # Run the due command with --soon 3
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        
        # Should include today, tomorrow, and overdue tasks
        assert "Task due today" in captured.out
        assert "Overdue task" in captured.out
        assert "Task due tomorrow" in captured.out
        assert "Task due in 3 days" in captured.out
        
        # Should not include tasks due further in the future
        assert "Task due in a week" not in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    @patch("datetime.date")
    def test_due_command_sorting(
        self,
        mock_date: MagicMock,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the due command sorts tasks by due date."""
        mock_date.today.return_value = self.MOCK_TODAY
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "due", "--soon", "10"][idx]

        # Run the due command with --soon 10 to include all test tasks
        result = main()
        captured = capsys.readouterr()
        output = captured.out

        # Check result
        assert result == 0
        
        # Verify sorting order:
        # 1. Most overdue tasks should appear first
        # 2. Tasks due today
        # 3. Future tasks in chronological order
        
        # Check the relative positions in the output text
        very_overdue_pos = output.find("Very overdue task")
        overdue_pos = output.find("Overdue task")
        today_pos = output.find("Task due today")
        tomorrow_pos = output.find("Task due tomorrow")
        three_days_pos = output.find("Task due in 3 days")
        week_pos = output.find("Task due in a week")
        
        # Verify all tasks were found
        assert very_overdue_pos >= 0
        assert overdue_pos >= 0
        assert today_pos >= 0
        assert tomorrow_pos >= 0
        assert three_days_pos >= 0
        assert week_pos >= 0
        
        # Verify sorting order
        assert very_overdue_pos < overdue_pos < today_pos < tomorrow_pos < three_days_pos < week_pos

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    @patch("datetime.date")
    def test_due_command_overdue_duration(
        self,
        mock_date: MagicMock,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test that due command shows the overdue duration for overdue tasks."""
        mock_date.today.return_value = self.MOCK_TODAY
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "due"][idx]

        # Run the due command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        
        # Check overdue indicators
        assert "OVERDUE" in captured.out
        
        # Very overdue task should show 10 days overdue
        assert "10 days overdue" in captured.out
        
        # Task overdue by 1 day should show 1 day overdue
        assert "1 day overdue" in captured.out

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    @patch("datetime.date")
    def test_due_command_with_no_matching_tasks(
        self,
        mock_date: MagicMock,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test the due command when there are no matching tasks."""
        # Set today to a date far in the past so no tasks are due yet
        mock_date.today.return_value = date(2000, 1, 1)
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "due"][idx]

        # Run the due command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert result == 0
        assert "No due tasks found" in captured.out
