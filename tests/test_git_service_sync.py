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


class TestGitServiceSync:
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

    # Tests for improved sync method
    def test_sync_no_changes(self, mock_discover_repository, temp_dir):
        """Test sync when there are no changes to commit."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with empty status (no changes)
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock empty status (no changes)
            mock_repo.status.return_value = {}

            # Setup pull and stage success
            with patch.object(git_service, "pull", return_value=True), patch.object(
                git_service, "stage_changes", return_value=True
            ):

                # Act
                result = git_service.sync()

                # Assert
                assert (
                    result is True
                )  # Sync should be considered successful with no changes
                # Verify commit was not called (no changes to commit)
                assert (
                    not mock_repo.create_commit.called
                    if hasattr(mock_repo, "create_commit")
                    else True
                )

    def test_sync_auto_commit_false(self, mock_discover_repository, temp_dir):
        """Test sync with auto_commit=False (should stage but not commit)."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with changes to commit
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock status with changes
            mock_repo.status.return_value = {"file.txt": pygit2.GIT_STATUS_WT_MODIFIED}

            # Setup pull and stage success
            with patch.object(git_service, "pull", return_value=True), patch.object(
                git_service, "stage_changes", return_value=True
            ), patch.object(git_service, "commit") as mock_commit:

                # Act
                result = git_service.sync(auto_commit=False)

                # Assert
                assert result is True  # Sync should be considered successful
                # Verify commit was not called since auto_commit=False
                mock_commit.assert_not_called()

    def test_sync_changes_no_remote(self, mock_discover_repository, temp_dir):
        """Test sync with changes but no remote (should commit but not push)."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with changes to commit
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock status with changes
            mock_repo.status.return_value = {"file.txt": pygit2.GIT_STATUS_WT_MODIFIED}

            # Setup has_remote, stage, and commit success
            with patch.object(
                git_service, "has_remote", return_value=False
            ), patch.object(
                git_service, "stage_changes", return_value=True
            ), patch.object(
                git_service, "commit", return_value=True
            ), patch.object(
                git_service, "push"
            ) as mock_push:

                # Act
                result = git_service.sync()

                # Assert
                assert result is True  # Sync should be considered successful
                # Verify push was not called since no remote
                mock_push.assert_not_called()

    def test_sync_failed_stage(self, mock_discover_repository, temp_dir):
        """Test sync when staging changes fails."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Setup pull success but stage failure
        with patch.object(git_service, "pull", return_value=True), patch.object(
            git_service, "stage_changes", return_value=False
        ), patch.object(git_service, "commit") as mock_commit:

            # Act
            result = git_service.sync()

            # Assert
            assert result is False  # Sync should fail if staging fails
            # Verify commit was not called after staging failure
            mock_commit.assert_not_called()

    def test_sync_failed_commit(self, mock_discover_repository, temp_dir):
        """Test sync when commit fails."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with changes to commit
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock status with changes
            mock_repo.status.return_value = {"file.txt": pygit2.GIT_STATUS_WT_MODIFIED}

            # Setup pull and stage success but commit failure
            with patch.object(git_service, "pull", return_value=True), patch.object(
                git_service, "stage_changes", return_value=True
            ), patch.object(git_service, "commit", return_value=False), patch.object(
                git_service, "push"
            ) as mock_push:

                # Act
                result = git_service.sync()

                # Assert
                assert result is False  # Sync should fail if commit fails
                # Verify push was not called after commit failure
                mock_push.assert_not_called()

    def test_sync_failed_push(self, mock_discover_repository, temp_dir):
        """Test sync when push fails but commit succeeds."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with changes to commit
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock status with changes
            mock_repo.status.return_value = {"file.txt": pygit2.GIT_STATUS_WT_MODIFIED}

            # Setup has_remote, pull, stage, and commit success but push failure
            with patch.object(
                git_service, "has_remote", return_value=True
            ), patch.object(git_service, "pull", return_value=True), patch.object(
                git_service, "stage_changes", return_value=True
            ), patch.object(
                git_service, "commit", return_value=True
            ), patch.object(
                git_service, "push", return_value=False
            ):

                # Act
                result = git_service.sync()

                # Assert
                assert (
                    result is True
                )  # Sync should be considered successful even if push fails

    def test_sync_full_workflow(self, mock_discover_repository, temp_dir):
        """Test full sync workflow (pull, stage, commit, push)."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with changes to commit
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock status with changes
            mock_repo.status.return_value = {"file.txt": pygit2.GIT_STATUS_WT_MODIFIED}

            # Setup mocks for tracking method calls
            pull_mock = MagicMock(return_value=True)
            stage_mock = MagicMock(return_value=True)
            commit_mock = MagicMock(return_value=True)
            push_mock = MagicMock(return_value=True)
            has_remote_mock = MagicMock(return_value=True)

            # Apply mocks
            with patch.object(git_service, "has_remote", has_remote_mock), patch.object(
                git_service, "pull", pull_mock
            ), patch.object(git_service, "stage_changes", stage_mock), patch.object(
                git_service, "commit", commit_mock
            ), patch.object(
                git_service, "push", push_mock
            ):

                # Act
                result = git_service.sync(commit_message="Test sync")

                # Assert
                assert result is True  # Full sync should succeed

                # Verify correct sequence of calls
                has_remote_mock.assert_called_once()
                pull_mock.assert_called_once()
                stage_mock.assert_called_once()
                commit_mock.assert_called_once_with("Test sync")
                push_mock.assert_called_once()

    def test_sync_merge_conflicts(self, mock_discover_repository, temp_dir):
        """Test sync with merge conflicts during pull."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with changes to commit
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock status with changes
            mock_repo.status.return_value = {"file.txt": pygit2.GIT_STATUS_WT_MODIFIED}

            # Setup pull failure due to merge conflicts but successful stage and commit
            with patch.object(
                git_service, "has_remote", return_value=True
            ), patch.object(git_service, "pull", return_value=False), patch.object(
                git_service, "stage_changes", return_value=True
            ), patch.object(
                git_service, "commit", return_value=True
            ), patch.object(
                git_service, "push"
            ) as mock_push:

                # Act
                result = git_service.sync()

                # Assert
                assert result is True  # Sync should succeed despite pull issues
                # Push should still be called after commit succeeds
                mock_push.assert_called_once()

    def test_sync_non_fast_forward(self, mock_discover_repository, temp_dir):
        """Test sync with non-fast-forward errors during push."""
        # Arrange
        mock_discover_repository.return_value = str(temp_dir / ".git")
        git_service = GitService(repo_dir=temp_dir)

        # Create mock repository with changes to commit
        with patch("pygit2.Repository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            # Mock status with changes
            mock_repo.status.return_value = {"file.txt": pygit2.GIT_STATUS_WT_MODIFIED}

            # Setup mocks for tracking method calls
            pull_mock = MagicMock(return_value=True)
            stage_mock = MagicMock(return_value=True)
            commit_mock = MagicMock(return_value=True)
            # Simulate non-fast-forward push error
            push_mock = MagicMock(return_value=False)
            has_remote_mock = MagicMock(return_value=True)

            # Apply mocks
            with patch.object(git_service, "has_remote", has_remote_mock), patch.object(
                git_service, "pull", pull_mock
            ), patch.object(git_service, "stage_changes", stage_mock), patch.object(
                git_service, "commit", commit_mock
            ), patch.object(
                git_service, "push", push_mock
            ):

                # Act
                result = git_service.sync()

                # Assert
                assert (
                    result is True
                )  # Sync should be considered successful even if push fails

                # Verify correct sequence of calls
                has_remote_mock.assert_called_once()
                pull_mock.assert_called_once()
                stage_mock.assert_called_once()
                commit_mock.assert_called_once()
                push_mock.assert_called_once()
