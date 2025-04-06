#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock, call, patch

import pytest
from pytest import CaptureFixture

from ptodo.commands.organization_commands import (
    cmd_archive,
    cmd_contexts,
    cmd_project_mv,
    cmd_project_pri,
    cmd_project_rm,
    cmd_projects,
)
from ptodo.serda import Task


class TestOrganizationCommands:
    """Tests for the organization commands in ptodo."""

    @pytest.fixture
    def mock_git_service(self) -> Generator[Dict[str, MagicMock], None, None]:
        """Mock GitService class."""
        with patch(
            "ptodo.commands.organization_commands.GitService"
        ) as mock_service_class:
            # Create a mock instance that will be returned when GitService is instantiated
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            # Return both the class and instance for flexibility in tests
            yield {"class": mock_service_class, "instance": mock_service}

    @pytest.fixture
    def mock_todo_file_path(self) -> Generator[MagicMock, None, None]:
        """Mock get_todo_file_path function."""
        with patch(
            "ptodo.commands.organization_commands.get_todo_file_path"
        ) as mock_get_path:
            # Mock a Path object with a parent attribute
            mock_path = MagicMock(spec=Path)
            mock_path.parent = Path("/mock/path")
            mock_get_path.return_value = mock_path
            yield mock_get_path

    @pytest.fixture
    def mock_done_file_path(self) -> Generator[MagicMock, None, None]:
        """Mock get_done_file_path function."""
        with patch(
            "ptodo.commands.organization_commands.get_done_file_path"
        ) as mock_get_path:
            # Mock a Path object with a parent attribute
            mock_path = MagicMock(spec=Path)
            mock_path.parent = Path("/mock/path")
            mock_get_path.return_value = mock_path
            yield mock_get_path

    @pytest.fixture
    def mock_read_tasks(self) -> Generator[MagicMock, None, None]:
        """Mock read_tasks function."""
        with patch("ptodo.commands.organization_commands.read_tasks") as mock_read:
            yield mock_read

    @pytest.fixture
    def mock_write_tasks(self) -> Generator[MagicMock, None, None]:
        """Mock write_tasks function."""
        with patch("ptodo.commands.organization_commands.write_tasks") as mock_write:
            yield mock_write

    @pytest.fixture
    def sample_tasks(self) -> List[Task]:
        """Create sample tasks for testing."""
        task1 = Task(
            description="Sample task 1",
            projects={"project1", "project2"},
            contexts={"context1"},
        )
        task2 = Task(
            description="Sample task 2",
            completed=True,
            projects={"project1"},
            contexts={"context2"},
        )
        task3 = Task(
            description="Sample task 3",
            priority="A",
            projects={"project3"},
            contexts={"context1"},
        )
        return [task1, task2, task3]

    # Tests for cmd_archive
    def test_archive_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_done_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        mock_write_tasks: MagicMock,
        sample_tasks: List[Task],
        capsys: CaptureFixture[str],
    ) -> None:
        """Test successful archiving of completed tasks."""
        # Arrange
        todo_path = mock_todo_file_path.return_value
        done_path = mock_done_file_path.return_value

        # Configure mocks
        mock_read_tasks.side_effect = [
            sample_tasks,  # First call for todo file
            [],  # Second call for done file (empty)
        ]

        # Act
        result = cmd_archive(argparse.Namespace())

        # Assert
        mock_git_service["class"].assert_called_once_with(todo_path.parent)
        mock_read_tasks.assert_has_calls(
            [
                call(todo_path, mock_git_service["instance"]),
                call(done_path, mock_git_service["instance"]),
            ]
        )

        # Check that write_tasks was called with completed tasks for done file
        # and incomplete tasks for todo file
        completed_tasks = [t for t in sample_tasks if t.completed]
        incomplete_tasks = [t for t in sample_tasks if not t.completed]
        mock_write_tasks.assert_has_calls(
            [
                call(completed_tasks, done_path, mock_git_service["instance"]),
                call(incomplete_tasks, todo_path, mock_git_service["instance"]),
            ]
        )

        # Check output
        captured = capsys.readouterr()
        assert "Archived 1 completed task(s)" in captured.out
        assert result == 0

    def test_archive_no_completed_tasks(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_done_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        mock_write_tasks: MagicMock,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test archiving when there are no completed tasks."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Create tasks with no completed tasks
        tasks = [
            Task(description="Task 1", completed=False),
            Task(description="Task 2", completed=False),
        ]

        # Configure mocks
        mock_read_tasks.side_effect = [
            tasks,  # First call for todo file
            [],  # Second call for done file (empty)
        ]

        # Act
        result = cmd_archive(argparse.Namespace())

        # Assert
        mock_read_tasks.assert_has_calls(
            [
                call(todo_path, mock_git_service["instance"]),
                call(mock_done_file_path.return_value, mock_git_service["instance"]),
            ]
        )

        # Check that write_tasks was not called
        mock_write_tasks.assert_not_called()

        # Check output
        captured = capsys.readouterr()
        assert "No completed tasks to archive" in captured.out
        assert result == 0

    # Tests for cmd_projects
    def test_projects_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        sample_tasks: List[Task],
        capsys: CaptureFixture[str],
    ) -> None:
        """Test successfully listing projects."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Act
        result = cmd_projects(argparse.Namespace())

        # Assert
        mock_git_service["class"].assert_called_once_with(todo_path.parent)
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])

        # Check output
        captured = capsys.readouterr()
        assert "Projects:" in captured.out
        assert "project1" in captured.out
        assert "project2" in captured.out
        assert "project3" in captured.out
        assert result == 0

    def test_projects_no_projects(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test listing projects when there are none."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Create tasks with no projects
        tasks = [
            Task(description="Task 1"),
            Task(description="Task 2"),
        ]

        # Configure mocks
        mock_read_tasks.return_value = tasks

        # Act
        result = cmd_projects(argparse.Namespace())

        # Assert
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])

        # Check output
        captured = capsys.readouterr()
        assert "No projects found" in captured.out
        assert result == 0

    # Tests for cmd_contexts
    def test_contexts_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        sample_tasks: List[Task],
        capsys: CaptureFixture[str],
    ) -> None:
        """Test successfully listing contexts."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Act
        result = cmd_contexts(argparse.Namespace())

        # Assert
        mock_git_service["class"].assert_called_once_with(todo_path.parent)
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])

        # Check output
        captured = capsys.readouterr()
        assert "Contexts:" in captured.out
        assert "context1" in captured.out
        assert "context2" in captured.out
        assert result == 0

    def test_contexts_no_contexts(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        capsys: CaptureFixture[str],
    ) -> None:
        """Test listing contexts when there are none."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Create tasks with no contexts
        tasks = [
            Task(description="Task 1"),
            Task(description="Task 2"),
        ]

        # Configure mocks
        mock_read_tasks.return_value = tasks

        # Act
        result = cmd_contexts(argparse.Namespace())

        # Assert
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])

        # Check output
        captured = capsys.readouterr()
        assert "No contexts found" in captured.out
        assert result == 0

    # Tests for cmd_project_mv
    def test_project_mv_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        mock_write_tasks: MagicMock,
        sample_tasks: List[Task],
        capsys: CaptureFixture[str],
    ) -> None:
        """Test successfully renaming a project."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Create args
        args = argparse.Namespace(old_name="project1", new_name="new_project")

        # Act
        result = cmd_project_mv(args)

        # Assert
        mock_git_service["class"].assert_called_once_with(todo_path.parent)
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])

        # Check that the projects were updated correctly in the tasks
        # We need to check what's passed to write_tasks
        args, kwargs = mock_write_tasks.call_args
        modified_tasks = args[0]

        # Check if the project names were updated correctly
        for task in modified_tasks:
            assert "project1" not in task.projects
            if (
                "new_project" in task.projects
                or "project2" in task.projects
                or "project3" in task.projects
            ):
                pass  # This is expected

        # Check output
        captured = capsys.readouterr()
        assert "Renamed project +project1 to +new_project in 2 task(s)" in captured.out
        assert result == 0

    def test_project_mv_project_not_found(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        mock_write_tasks: MagicMock,
        sample_tasks: List[Task],
        capsys: CaptureFixture[str],
    ) -> None:
        """Test project rename when the old project doesn't exist."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Create args
        args = argparse.Namespace(old_name="nonexistent", new_name="new_project")

        # Act
        result = cmd_project_mv(args)

        # Assert
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])
        mock_write_tasks.assert_not_called()

        # Check output
        captured = capsys.readouterr()
        assert "No tasks found with project +nonexistent" in captured.out
        assert result == 1

    # Tests for cmd_project_rm
    def test_project_rm_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        mock_write_tasks: MagicMock,
        sample_tasks: List[Task],
        capsys: CaptureFixture[str],
    ) -> None:
        """Test successfully removing tasks with a specific project."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Create args
        args = argparse.Namespace(name="project1")

        # Act
        result = cmd_project_rm(args)

        # Assert
        mock_git_service["class"].assert_called_once_with(todo_path.parent)
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])

        # Check that tasks with project1 were removed
        args, kwargs = mock_write_tasks.call_args
        remaining_tasks = args[0]

        # There should be only one task left (the one with project3)
        assert len(remaining_tasks) == 1
        assert "project3" in remaining_tasks[0].projects

        # Check output
        captured = capsys.readouterr()
        assert "Removed 2 task(s) with project +project1" in captured.out
        assert result == 0

    def test_project_rm_project_not_found(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        mock_write_tasks: MagicMock,
        sample_tasks: List[Task],
        capsys: CaptureFixture[str],
    ) -> None:
        """Test project removal when the project doesn't exist."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Create args
        args = argparse.Namespace(name="nonexistent")

        # Act
        result = cmd_project_rm(args)

        # Assert
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])
        mock_write_tasks.assert_not_called()

        # Check output
        captured = capsys.readouterr()
        assert "No tasks found with project +nonexistent" in captured.out
        assert result == 1

    # Tests for cmd_project_pri
    def test_project_pri_set_priority_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        mock_write_tasks: MagicMock,
        sample_tasks: List[Task],
        capsys: CaptureFixture[str],
    ) -> None:
        """Test successfully setting priority for all tasks in a project."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Create args
        # Create args
        args = argparse.Namespace(name="project1", priority="B")

        # Act
        result = cmd_project_pri(args)

        # Assert
        mock_git_service["class"].assert_called_once_with(todo_path.parent)
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])

        # Check that the priorities were updated correctly
        args, kwargs = mock_write_tasks.call_args
        modified_tasks = args[0]

        # Check if the priorities were set correctly for tasks with project1
        for task in modified_tasks:
            if "project1" in task.projects:
                assert task.priority == "B"

        # Check output
        captured = capsys.readouterr()
        assert "Set priority (B) for 2 task(s) in project +project1" in captured.out
        assert result == 0

    def test_project_pri_remove_priority_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        mock_read_tasks: MagicMock,
        mock_write_tasks: MagicMock,
        sample_tasks: List[Task],
        capsys: CaptureFixture[str],
    ):
        """Test successfully removing priority from all tasks in a project."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Create args
        args = argparse.Namespace(name="project3", priority="-")

        # Act
        result = cmd_project_pri(args)

        # Assert
        mock_git_service["class"].assert_called_once_with(todo_path.parent)
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])

        # Check that the priorities were removed correctly
        args, kwargs = mock_write_tasks.call_args
        modified_tasks = args[0]

        # Check if the priorities were removed for tasks with project3
        for task in modified_tasks:
            if "project3" in task.projects:
                assert task.priority is None

        # Check output
        captured = capsys.readouterr()
        assert "Removed priority from 1 task(s) in project +project3" in captured.out
        assert result == 0

    def test_project_pri_invalid_priority(
        self,
        mock_git_service,
        mock_todo_file_path,
        mock_read_tasks,
        mock_write_tasks,
        sample_tasks,
        capsys,
    ):
        """Test setting an invalid priority for tasks in a project."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Create args with invalid priority (must be A-Z or -)
        args = argparse.Namespace(name="project1", priority="a")

        # Act
        result = cmd_project_pri(args)

        # Assert
        mock_read_tasks.assert_not_called()
        mock_write_tasks.assert_not_called()

        # Check output
        captured = capsys.readouterr()
        assert "Error: Priority must be a capital letter (A-Z) or '-'" in captured.out
        assert result == 1

    def test_project_pri_project_not_found(
        self,
        mock_git_service,
        mock_todo_file_path,
        mock_read_tasks,
        mock_write_tasks,
        sample_tasks,
        capsys,
    ):
        """Test setting priority when the project doesn't exist."""
        # Arrange
        todo_path = mock_todo_file_path.return_value

        # Configure mocks
        mock_read_tasks.return_value = sample_tasks

        # Create args
        args = argparse.Namespace(name="nonexistent", priority="A")

        # Act
        result = cmd_project_pri(args)

        # Assert
        mock_read_tasks.assert_called_once_with(todo_path, mock_git_service["instance"])
        mock_write_tasks.assert_not_called()

        # Check output
        captured = capsys.readouterr()
        assert "No tasks found with project +nonexistent" in captured.out
        assert result == 1
