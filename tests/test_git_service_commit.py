#!/usr/bin/env python3
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple
from unittest.mock import MagicMock, PropertyMock, patch

import pygit2
import pytest
from pytest import CaptureFixture

from ptodo.git_service import GitService
from ptodo.utils import get_ptodo_directory


class TestGitServiceCommit:
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

    # Tests for commit method
    def test_commit_success(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test committing staged changes successfully."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)
        message = "Test commit message"

        # Create mock repository with index and other necessary objects
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock tree for commit
            mock_tree = MagicMock()
            mock_repo.index.write_tree.return_value = mock_tree

            # Mock signature creation
            with patch("pygit2.Signature") as mock_signature_class:
                mock_signature = MagicMock()
                mock_signature_class.return_value = mock_signature

                # Mock successful commit
                mock_repo.create_commit.return_value = "new-commit-sha"

                # Act
                result = git_service.commit(message)

                # Assert
                assert result is True
                # Check signature was created
                mock_signature_class.assert_called()
                # Check commit was created with right message
                mock_repo.create_commit.assert_called_once()
                # Verify message was passed to create_commit
                args, kwargs = mock_repo.create_commit.call_args
                # The message is passed as the 4th positional argument (index 3)
                assert message == args[3]

    def test_commit_verify_author_committer(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test that author and committer information is set correctly."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)
        message = "Test commit message"

        # Create mock repository
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.index.write_tree.return_value = MagicMock()

            # Mock config to return string values
            mock_config = MagicMock()
            mock_config.get_string.side_effect = lambda key: (
                "Test User" if key == "user.name" else "test@example.com"
            )
            mock_repo.config = mock_config

            # Track signature creation
            signature_args = []

            # Mock signature creation to capture arguments
            with patch("pygit2.Signature") as mock_signature_class:
                # Store the args used to create signatures
                def capture_signature_args(*args: Any, **kwargs: Any) -> MagicMock:
                    signature_args.append((args, kwargs))
                    return MagicMock()

                mock_signature_class.side_effect = capture_signature_args

                # Mock successful commit
                mock_repo.create_commit.return_value = "new-commit-sha"

                # Act
                result = git_service.commit(message)

                # Assert
                assert result is True
                # Check that we created exactly two signatures (author and committer)
                assert len(signature_args) == 2
                # Verify signature args contain expected name and email parameters
                for args, kwargs in signature_args:
                    assert len(args) >= 2  # Should have at least name and email
                    assert isinstance(args[0], str)  # Name
                    assert isinstance(args[1], str)  # Email

    def test_commit_no_staged_changes(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test committing when there are no staged changes."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with empty index
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Create a tree ID value to use for comparison
            test_tree_id = "test-tree-id-12345"

            # Create mock objects for the head reference chain
            mock_tree = MagicMock()
            mock_tree.id = test_tree_id

            mock_commit = MagicMock()
            mock_commit.tree = mock_tree

            # Configure head.peel() to return our mock commit
            mock_head = MagicMock()
            mock_head.peel.return_value = mock_commit

            # Set the head property on the repository
            type(mock_repo).head = PropertyMock(return_value=mock_head)

            # Simulate no staged changes by having write_tree return the same tree ID
            mock_repo.index.write_tree.return_value = test_tree_id

            # Act
            result = git_service.commit("No changes")

            # Assert
            assert result is False  # Should return False when no changes to commit

    def test_commit_empty_repository(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test committing in an empty repository (first commit)."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Simulate empty repository (no HEAD yet)
            # This will raise KeyError when accessing head reference
            type(mock_repo).head = PropertyMock(
                side_effect=KeyError("Reference 'refs/heads/master' not found")
            )
            mock_repo.index.write_tree.return_value = "tree-id"

            # Mock signature creation
            with patch("pygit2.Signature") as mock_signature_class:
                mock_signature_class.return_value = MagicMock()

                # Act
                result = git_service.commit("Initial commit")

                # Assert
                assert result is True
                # For initial commit, parent should be None or empty
                mock_repo.create_commit.assert_called_once()
                args, kwargs = mock_repo.create_commit.call_args
                # In this implementation, parents are passed as the 6th positional argument (index 5)
                assert args[5] == []  # Should be an empty list for initial commit

    def test_commit_empty_message(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test committing with an empty message."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.index.write_tree.return_value = MagicMock()

            # Mock signature creation
            with patch("pygit2.Signature") as mock_signature_class:
                mock_signature_class.return_value = MagicMock()

                # Act
                result = git_service.commit("")

                # Assert
                assert result is False  # Empty commit message should fail

    def test_commit_not_repo(self, mock_discover_repository: MagicMock) -> None:
        """Test committing when not in a git repository."""
        # Arrange
        repo_path = Path("/not/a/repo")
        mock_discover_repository.return_value = None
        git_service = GitService(repo_dir=repo_path)

        # Act
        result = git_service.commit("Test message")

        # Assert
        assert result is False

    def test_commit_repo_access_error(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test committing when repository access fails."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Mock Repository to raise exception
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo_class.side_effect = pygit2.GitError("Repository access error")

            # Act
            result = git_service.commit("Test message")

            # Assert
            assert result is False

    def test_commit_invalid_signature(
        self, mock_discover_repository: MagicMock, temp_dir: Path
    ) -> None:
        """Test committing with invalid signature information."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.index.write_tree.return_value = MagicMock()

            # Mock signature creation to raise an exception
            with patch("pygit2.Signature") as mock_signature_class:
                mock_signature_class.side_effect = ValueError(
                    "Invalid signature information"
                )

                # Act
                result = git_service.commit("Test message")

            # Assert
            assert result is False
