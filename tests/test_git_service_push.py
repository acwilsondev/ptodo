#!/usr/bin/env python3
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pygit2
import pytest

from ptodo.git_service import GitService
from ptodo.utils import get_ptodo_directory


class TestGitServicePush:
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

    # Tests for push method
    def test_push_success(self, mock_discover_repository, temp_dir):
        """Test successful push to remote."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with remote
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock remote
            mock_remote = MagicMock()
            mock_remote.name = "origin"
            mock_remote.url = "https://github.com/user/repo.git"

            # Mock successful push
            mock_remote.push.return_value = None

            # Set up remotes collection with our mock remote
            mock_repo.remotes = {"origin": mock_remote}

            # Act
            result = git_service.push()

            # Assert
            assert result is True
            mock_remote.push.assert_called_once()

    def test_push_no_remote(self, mock_discover_repository, temp_dir):
        """Test push when repository has no remotes."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with no remotes
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Empty remotes dictionary
            mock_repo.remotes = {}

            # Act
            result = git_service.push()

            # Assert
            assert result is False

    def test_push_authentication_error(self, mock_discover_repository, temp_dir):
        """Test push with authentication errors."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with remote
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock remote
            mock_remote = MagicMock()
            mock_remote.name = "origin"

            # Simulate authentication error during push
            mock_remote.push.side_effect = pygit2.GitError("Authentication failed")

            # Set up remotes collection with our mock remote
            mock_repo.remotes = {"origin": mock_remote}

            # Act
            result = git_service.push()

            # Assert
            assert result is False
            mock_remote.push.assert_called_once()

    def test_push_non_fast_forward(self, mock_discover_repository, temp_dir):
        """Test push with non-fast-forward errors."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with remote
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock remote
            mock_remote = MagicMock()
            mock_remote.name = "origin"

            # Simulate non-fast-forward error during push
            mock_remote.push.side_effect = pygit2.GitError(
                "non-fast-forward updates were rejected"
            )

            # Set up remotes collection with our mock remote
            mock_repo.remotes = {"origin": mock_remote}

            # Act
            result = git_service.push()

            # Assert
            assert result is False
            mock_remote.push.assert_called_once()

    def test_push_not_a_repository(self, mock_discover_repository):
        """Test push when not in a git repository."""
        # Arrange
        repo_path = Path("/not/a/repo")
        mock_discover_repository.return_value = None
        git_service = GitService(repo_dir=repo_path)

        # Act
        result = git_service.push()

        # Assert
        assert result is False
