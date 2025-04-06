#!/usr/bin/env python3
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pygit2
import pytest

# Define pygit2 constants for type checking
# GIT_STATUS_WT_MODIFIED and GIT_STATUS_WT_NEW are used to mock the status of files
GIT_STATUS_WT_MODIFIED = 1 << 7  # 128
GIT_STATUS_WT_NEW = 1 << 2  # 4
from pytest import CaptureFixture

from ptodo.git_service import GitService
from ptodo.utils import get_ptodo_directory


class TestGitServiceStage:
    """Tests for the GitService class using pygit2."""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_repo(self) -> Generator[MagicMock, None, None]:
        """Mock the pygit2.Repository class."""
        with patch("pygit2.Repository") as mock_repo:
            yield mock_repo

    @pytest.fixture
    def mock_discover_repository(self) -> Generator[MagicMock, None, None]:
        """Mock the pygit2.discover_repository function."""
        with patch("pygit2.discover_repository") as mock_discover:
            yield mock_discover

    # Tests for stage_changes method
    def test_stage_specific_file_success(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test staging a specific file successfully."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)
        file_path = temp_dir / "test_file.txt"

        # Create mock repository with index
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_index = MagicMock()
            mock_repo.index = mock_index

            # Act
            result = git_service.stage_changes(file_path)

            # Assert
            assert result is True
            mock_index.add.assert_called_once_with(str(file_path.relative_to(temp_dir)))
            mock_index.write.assert_called_once()

    def test_stage_nonexistent_file(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test staging a file that doesn't exist."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Create mock repository with index
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_index = MagicMock()
            mock_repo.index = mock_index

            # Simulate error when adding non-existent file
            mock_index.add.side_effect = pygit2.GitError("Path not found")

            # Act
            result = git_service.stage_changes(nonexistent_file)

            # Assert
            assert result is False
            mock_index.add.assert_called_once_with(
                str(nonexistent_file.relative_to(temp_dir))
            )

    def test_stage_path_outside_repository(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test staging a path outside the repository."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)
        external_file = Path("/some/external/file.txt")

        # Act with patch to avoid actual file system operations
        with patch("pygit2.Repository") as mock_repo_class:
            # Act & Assert - should raise ValueError due to path being outside repo
            with pytest.raises(ValueError):
                git_service.stage_changes(external_file)

    def test_stage_all_changes_success(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test staging all changes successfully."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with index
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_index = MagicMock()
            mock_repo.index = mock_index

            # Act
            result = git_service.stage_changes()

            # Assert
            assert result is True
            # Should call add_all to stage everything
            mock_index.add_all.assert_called_once()
            mock_index.write.assert_called_once()

    def test_stage_no_changes(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test staging when there are no changes."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with index
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_index = MagicMock()
            mock_repo.index = mock_index

            # Simulate no changes by returning empty status
            mock_repo.status.return_value = {}

            # Act
            result = git_service.stage_changes()

            # Assert
            assert result is True  # Should still return True even with no changes

    def test_stage_dirty_working_directory(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test staging with a dirty working directory."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with index and dirty status
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_index = MagicMock()
            mock_repo.index = mock_index

            # Simulate dirty working directory
            mock_repo.status.return_value = {
                "file1.txt": GIT_STATUS_WT_MODIFIED,
                "file2.txt": GIT_STATUS_WT_NEW,
            }

            # Act
            result = git_service.stage_changes()

            # Assert
            assert result is True
            mock_index.add_all.assert_called_once()
            mock_index.write.assert_called_once()

    def test_stage_changes_not_repo(self, mock_discover_repository: MagicMock) -> None:
        """Test stage_changes when not in a git repository."""
        # Arrange
        repo_path = Path("/not/a/repo")
        mock_discover_repository.return_value = None
        git_service = GitService(repo_dir=repo_path)

        # Act
        result = git_service.stage_changes()

        # Assert
        assert result is False

    def test_stage_changes_repo_access_error(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test stage_changes when repository access fails."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Mock Repository to raise exception
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo_class.side_effect = pygit2.GitError("Repository access error")

            # Act
            result = git_service.stage_changes()

            # Assert
            assert result is False

    def test_stage_changes_invalid_path_type(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test stage_changes with invalid path type."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)
        invalid_path = 123  # Not a Path object

        # Act & Assert
        with pytest.raises(TypeError):
            git_service.stage_changes(invalid_path)  # type: ignore
