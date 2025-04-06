import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pygit2
import pytest

from ptodo.git_service import GitService
from ptodo.utils import get_ptodo_directory


class TestGitServiceRemote:
    """Tests for the GitService class using pygit2."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_repo(self):
        """Mock the pygit2.Repository class."""
        with patch("pygit2.Repository") as mock_repo:
            yield mock_repo

    @pytest.fixture
    def mock_discover_repository(self):
        """Mock the pygit2.discover_repository function."""
        with patch("pygit2.discover_repository") as mock_discover:
            yield mock_discover

    # Tests for add_remote method
    def test_add_remote_new_success(self, mock_discover_repository, temp_dir):
        """Test adding a new remote successfully."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Mock Repository to avoid actual Git operations
        with patch("pygit2.Repository") as mock_repo_class:
            # Create a mock repository instance
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock remotes collection with proper methods
            remotes_mock = MagicMock()
            # Implement __contains__ to check if a name exists in remotes
            remotes_mock.__contains__ = lambda self, key: key in {}
            # Setup the create method
            remotes_mock.create = MagicMock(return_value=MagicMock())
            mock_repo.remotes = remotes_mock

            # Act
            with patch("builtins.print") as mock_print:
                result = git_service.add_remote(
                    "origin", "https://github.com/user/repo.git"
                )

            # Assert
            assert result is True
            mock_print.assert_called_once_with(
                "Added remote 'origin' at https://github.com/user/repo.git"
            )

    def test_add_remote_update_existing(self, mock_discover_repository, temp_dir):
        """Test updating an existing remote."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Mock Repository to avoid actual Git operations
        with patch("pygit2.Repository") as mock_repo_class:
            # Create a mock repository instance with existing remote
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Set up existing remote
            mock_remote = MagicMock()
            mock_remote.url = "https://github.com/user/old-repo.git"

            # Create a proper mock for remotes collection
            remotes_mock = MagicMock()
            # Setup the __contains__ method to return True for "origin"
            remotes_mock.__contains__ = lambda self, key: key == "origin"
            # Setup the __getitem__ method to return mock_remote for "origin"
            remotes_mock.__getitem__ = lambda self, key: (
                mock_remote if key == "origin" else None
            )
            # Setup the delete and create methods
            remotes_mock.delete = MagicMock()
            remotes_mock.create = MagicMock(return_value=MagicMock())
            mock_repo.remotes = remotes_mock

            # Act
            with patch("builtins.print") as mock_print:
                result = git_service.add_remote(
                    "origin", "https://github.com/user/new-repo.git"
                )

            # Assert
            assert result is True
            mock_print.assert_called_once_with(
                "Updated remote 'origin' to https://github.com/user/new-repo.git"
            )

    def test_add_remote_error_handling(self, mock_discover_repository, temp_dir):
        """Test handling errors in add_remote."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Mock Repository to throw an error
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo_class.side_effect = pygit2.GitError("Invalid remote URL")

            # Act
            with patch("builtins.print") as mock_print:
                result = git_service.add_remote("origin", "invalid://url")

            # Assert
            assert result is False
            mock_print.assert_called_once_with(
                "Failed to add remote: Invalid remote URL"
            )

    def test_add_remote_when_not_a_repository(self, mock_discover_repository):
        """Test add_remote when not in a git repository."""
        # Arrange
        repo_path = Path("/not/a/repo")
        mock_discover_repository.return_value = None
        git_service = GitService(repo_dir=repo_path)

        # Act
        with patch("builtins.print") as mock_print:
            result = git_service.add_remote(
                "origin", "https://github.com/user/repo.git"
            )

        # Assert
        assert result is False
        mock_print.assert_called_once_with(f"Not a git repository: {repo_path}")

    # Tests for has_remote method
    def test_has_remote_with_remotes(self, mock_discover_repository, temp_dir):
        """Test has_remote when repository has remotes."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Mock Repository with remotes
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Set up a remote
            mock_remote = MagicMock()
            mock_repo.remotes = {"origin": mock_remote}

            # Act
            result = git_service.has_remote()

            # Assert
            assert result is True

    def test_has_remote_without_remotes(self, mock_discover_repository, temp_dir):
        """Test has_remote when repository has no remotes."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Mock Repository without remotes
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Empty remotes dictionary
            mock_repo.remotes = {}

            # Act
            result = git_service.has_remote()

            # Assert
            assert result is False

    def test_has_remote_when_not_a_repository(self, mock_discover_repository):
        """Test has_remote when not in a git repository."""
        # Arrange
        repo_path = Path("/not/a/repo")
        mock_discover_repository.return_value = None
        git_service = GitService(repo_dir=repo_path)

        # Act
        result = git_service.has_remote()

        # Assert
        assert result is False

    def test_has_remote_error_handling(self, mock_discover_repository, temp_dir):
        """Test has_remote error handling."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Mock Repository to throw an error
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo_class.side_effect = pygit2.GitError("Repository access error")

            # Act
            result = git_service.has_remote()

            # Assert
            assert result is False
