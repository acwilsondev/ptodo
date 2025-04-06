#!/usr/bin/env python3
import argparse
import subprocess
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, call, patch

import pytest

from ptodo.commands.git_commands import cmd_git_init, cmd_git_remote, cmd_git_sync


class TestGitCommands:
    """Tests for the git commands in ptodo."""

    @pytest.fixture
    def mock_git_service(self) -> Generator[Dict[str, MagicMock], None, None]:
        """Mock GitService class."""
        with patch("ptodo.commands.git_commands.GitService") as mock_service_class:
            # Create a mock instance that will be returned when GitService is instantiated
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            # Return both the class and instance for flexibility in tests
            yield {"class": mock_service_class, "instance": mock_service}

    @pytest.fixture
    def mock_todo_file_path(self) -> Generator[MagicMock, None, None]:
        """Mock get_todo_file_path function."""
        with patch("ptodo.commands.git_commands.get_todo_file_path") as mock_get_path:
            # Mock a Path object with a parent attribute
            mock_path = MagicMock()
            mock_path.parent = "/mock/path"
            mock_get_path.return_value = mock_path
            yield mock_get_path

    # Tests for cmd_git_init
    def test_git_init_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test successful git initialization."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.init.return_value = True
        args = argparse.Namespace()

        # Act
        result = cmd_git_init(args)

        # Assert
        mock_git_service["class"].assert_called_once_with(
            mock_todo_file_path.return_value.parent
        )
        mock_service.init.assert_called_once()
        assert result == 0

    def test_git_init_failure(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test failed git initialization."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.init.return_value = False
        args = argparse.Namespace()

        # Act
        result = cmd_git_init(args)

        # Assert
        mock_git_service["class"].assert_called_once_with(
            mock_todo_file_path.return_value.parent
        )
        mock_service.init.assert_called_once()
        # The function still returns 0 even if initialization fails
        # This matches the current implementation
        assert result == 0

    # Tests for cmd_git_remote
    def test_git_remote_show_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test successfully showing git remotes."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.is_repo.return_value = True
        args = argparse.Namespace(url=None)

        # Mock subprocess.run to return a successful result with remote info
        mock_result = MagicMock()
        mock_result.stdout = "origin\thttps://github.com/user/repo.git (fetch)\norigin\thttps://github.com/user/repo.git (push)\n"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            # Act
            result = cmd_git_remote(args)

            # Assert
            mock_git_service["class"].assert_called_once_with(
                mock_todo_file_path.return_value.parent
            )
            mock_service.is_repo.assert_called_once()
            mock_run.assert_called_once()
            captured = capsys.readouterr()
            assert mock_result.stdout in captured.out
            assert result == 0

    def test_git_remote_show_no_remotes(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test showing git remotes when none exist."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.is_repo.return_value = True
        args = argparse.Namespace(url=None)

        # Mock subprocess.run to return a successful result with no remote info
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            # Act
            result = cmd_git_remote(args)

            # Assert
            mock_service.is_repo.assert_called_once()
            mock_run.assert_called_once()
            captured = capsys.readouterr()
            assert "No remotes configured" in captured.out
            assert result == 0

    def test_git_remote_show_failure(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test failure when showing git remotes."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.is_repo.return_value = True
        args = argparse.Namespace(url=None)

        # Mock subprocess.run to raise a CalledProcessError
        error = subprocess.CalledProcessError(
            1, "git remote -v", stderr="Command failed"
        )

        with patch("subprocess.run", side_effect=error) as mock_run:
            # Act
            result = cmd_git_remote(args)

            # Assert
            mock_service.is_repo.assert_called_once()
            mock_run.assert_called_once()
            captured = capsys.readouterr()
            assert "Failed to list remotes" in captured.out
            assert result == 1

    def test_git_remote_add_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test adding a git remote successfully."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.is_repo.return_value = True
        mock_service.add_remote.return_value = True
        args = argparse.Namespace(url="https://github.com/user/repo.git")

        # Act
        result = cmd_git_remote(args)

        # Assert
        mock_service.is_repo.assert_called_once()
        mock_service.add_remote.assert_called_once_with(
            "origin", "https://github.com/user/repo.git"
        )
        assert result == 0

    def test_git_remote_not_a_repo(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test git remote command when not in a git repository."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.is_repo.return_value = False
        args = argparse.Namespace(url=None)

        # Act
        result = cmd_git_remote(args)

        # Assert
        mock_service.is_repo.assert_called_once()
        captured = capsys.readouterr()
        assert "Not a git repository" in captured.out
        assert result == 1

    # Tests for cmd_git_sync
    def test_git_sync_success(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test successful git sync."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.is_repo.return_value = True
        mock_service.sync.return_value = True
        args = argparse.Namespace()

        # Act
        result = cmd_git_sync(args)

        # Assert
        mock_git_service["class"].assert_called_once_with(
            mock_todo_file_path.return_value.parent
        )
        mock_service.is_repo.assert_called_once()
        mock_service.sync.assert_called_once_with(
            commit_message="Manual sync of todo files"
        )
        captured = capsys.readouterr()
        assert "Successfully synced changes" in captured.out
        assert result == 0

    def test_git_sync_failure(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test failed git sync."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.is_repo.return_value = True
        mock_service.sync.return_value = False
        args = argparse.Namespace()

        # Act
        result = cmd_git_sync(args)

        # Assert
        mock_service.is_repo.assert_called_once()
        mock_service.sync.assert_called_once_with(
            commit_message="Manual sync of todo files"
        )
        captured = capsys.readouterr()
        assert "No changes to sync or sync failed" in captured.out
        assert result == 1

    def test_git_sync_not_a_repo(
        self,
        mock_git_service: Dict[str, MagicMock],
        mock_todo_file_path: MagicMock,
        capsys: Any,
    ) -> None:
        """Test git sync when not in a git repository."""
        # Arrange
        mock_service = mock_git_service["instance"]
        mock_service.is_repo.return_value = False
        args = argparse.Namespace()

        # Act
        result = cmd_git_sync(args)

        # Assert
        mock_service.is_repo.assert_called_once()
        captured = capsys.readouterr()
        assert "Not a git repository" in captured.out
        assert result == 1


if __name__ == "__main__":
    pytest.main()
