import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestSortCommand:
    """Tests for the sort command functionality of ptodo."""

    @pytest.fixture
    def temp_dir(self) -> Generator[str, None, None]:
        """Create a temporary directory for todo.txt files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def todo_file(self, temp_dir: str) -> Generator[str, None, None]:
        """Create a test todo.txt file with tasks in non-sorted order."""
        todo_file = os.path.join(temp_dir, "todo.txt")
        with open(todo_file, "w") as f:
            # Intentionally in non-sorted order
            f.write("No priority task first +project3 @context3\n")
            f.write("(B) Medium priority task +project2 @context2\n")
            f.write("(A) Highest priority task +project1 @context1\n")
            f.write("(C) Lower priority task +project1 @context2\n")
            f.write("x 2023-05-04 (D) Completed task\n")  # Should remain at its position
            f.write("Another no priority task +project4 @context4\n")
        # Set the environment variable to use our test file
        os.environ["TODO_FILE"] = todo_file
        yield todo_file
        # Clean up the environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

    @pytest.fixture
    def empty_todo_file(self, temp_dir: str) -> Generator[str, None, None]:
        """Create an empty todo.txt file for testing."""
        todo_file = os.path.join(temp_dir, "empty_todo.txt")
        with open(todo_file, "w") as f:
            pass  # Create an empty file
        yield todo_file

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_sort_command(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test that sort command correctly orders tasks by priority."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "sort"][idx]

        # Record the expected content after sorting
        expected_content = [
            "(A) Highest priority task +project1 @context1",
            "(B) Medium priority task +project2 @context2",
            "(C) Lower priority task +project1 @context2",
            "x 2023-05-04 (D) Completed task",  # Completed tasks usually maintain position
            "No priority task first +project3 @context3",
            "Another no priority task +project4 @context4"
        ]

        # Run the sort command
        result = main()
        captured = capsys.readouterr()

        # Check result
        assert result == 0
        assert "Sorted" in captured.out
        
        # Verify the file content is sorted correctly
        with open(todo_file, "r") as f:
            sorted_content = f.read().strip().split("\n")
        
        # Assert that all expected tasks are present
        for expected_line in expected_content:
            assert any(expected_line in line for line in sorted_content)
        
        # Check the priority order is correct
        priorities = []
        for line in sorted_content:
            if line.startswith("x"):
                continue  # Skip completed tasks
            if "(" in line and ")" in line and line.index("(") < line.index(")"):
                priorities.append(line[line.index("(")+1:line.index(")")])
            else:
                priorities.append("Z")  # No priority tasks should be after all prioritized tasks
                
        # Verify priorities are in correct order
        assert sorted(priorities) == priorities

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_sort_command_preserves_task_content(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test that sort command preserves task content while sorting."""
        mock_get_path.return_value = Path(todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "sort"][idx]

        # Get all the expected task content before sorting
        with open(todo_file, "r") as f:
            original_content = f.read().strip().split("\n")
        
        # Run the sort command
        result = main()
        captured = capsys.readouterr()

        # Verify the file content after sorting
        with open(todo_file, "r") as f:
            sorted_content = f.read().strip().split("\n")
        
        # Check that all tasks are preserved (just in different order)
        assert len(sorted_content) == len(original_content)
        
        # Each task from the original file should exist in sorted content, just in different order
        for task in original_content:
            assert task in sorted_content
            
        # Projects and contexts should be preserved
        projects_contexts_before = []
        for line in original_content:
            projects = [word for word in line.split() if word.startswith('+')]
            contexts = [word for word in line.split() if word.startswith('@')]
            projects_contexts_before.extend(projects + contexts)
            
        projects_contexts_after = []
        for line in sorted_content:
            projects = [word for word in line.split() if word.startswith('+')]
            contexts = [word for word in line.split() if word.startswith('@')]
            projects_contexts_after.extend(projects + contexts)
            
        assert sorted(projects_contexts_before) == sorted(projects_contexts_after)

    @patch("sys.argv")
    @patch("ptodo.core.get_todo_file_path")
    def test_sort_command_empty_file(
        self,
        mock_get_path: MagicMock,
        mock_argv: MagicMock,
        empty_todo_file: str,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test sort command with an empty todo file."""
        mock_get_path.return_value = Path(empty_todo_file)
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "sort"][idx]

        # Set the environment variable to use our empty test file
        os.environ["TODO_FILE"] = empty_todo_file

        # Run the sort command with an empty todo file
        result = main()
        captured = capsys.readouterr()

        # Clean up the environment variable
        if "TODO_FILE" in os.environ:
            del os.environ["TODO_FILE"]

        # Check result
        assert result == 0
        assert "No tasks found" in captured.out

