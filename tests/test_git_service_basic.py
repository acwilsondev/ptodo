import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pygit2
import pytest
from pytest import CaptureFixture

from ptodo.git_service import GitService


class TestGitServiceBasic:
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

    def test_is_repo_when_repository_exists(
        self, mock_discover_repository: MagicMock
    ) -> None:
        """Test is_repo when a repository exists."""
        # Arrange
        repo_path = Path("/path/to/repo")
        mock_discover_repository.return_value = str(repo_path / ".git")
        git_service = GitService(repo_dir=repo_path)

        # Act
        result = git_service.is_repo()

        # Assert
        assert result is True
        mock_discover_repository.assert_called_once_with(str(repo_path))

    def test_is_repo_when_repository_does_not_exist(
        self, mock_discover_repository: MagicMock
    ) -> None:
        """Test is_repo when a repository doesn't exist."""
        # Arrange
        repo_path = Path("/path/to/not/a/repo")
        mock_discover_repository.return_value = None
        git_service = GitService(repo_dir=repo_path)

        # Act
        result = git_service.is_repo()

        # Assert
        assert result is False
        mock_discover_repository.assert_called_once_with(str(repo_path))

    def test_is_repo_with_exception(self, mock_discover_repository: MagicMock) -> None:
        """Test is_repo when pygit2 raises an exception."""
        # Arrange
        repo_path = Path("/invalid/path")
        mock_discover_repository.side_effect = pygit2.errors.GitError(
            "Not a git repository"
        )
        git_service = GitService(repo_dir=repo_path)

        # Act
        result = git_service.is_repo()

        # Assert
        assert result is False
        mock_discover_repository.assert_called_once_with(str(repo_path))

    def test_init_repository_success(
        self, temp_dir: Path, mock_discover_repository: MagicMock
    ) -> None:
        """Test successful repository initialization."""
        # Arrange
        # First check returns False (not a repo) then True (after init)
        mock_discover_repository.side_effect = [None, str(temp_dir / ".git")]
        git_service = GitService(repo_dir=temp_dir)

        # Mock the pygit2.init_repository function
        with patch("pygit2.init_repository") as mock_init:
            mock_init.return_value = MagicMock()  # Return a mock repository object

            # Act
            result = git_service.init()

            # Assert
            assert result is True
            mock_init.assert_called_once_with(str(temp_dir))

    def test_init_when_repository_already_exists(
        self, mock_discover_repository: MagicMock
    ) -> None:
        """Test init when repository already exists."""
        # Arrange
        repo_path = Path("/existing/repo")
        mock_discover_repository.return_value = str(repo_path / ".git")
        git_service = GitService(repo_dir=repo_path)

        # Act
        with patch("builtins.print") as mock_print:
            result = git_service.init()

        # Assert
        assert result is True
        mock_print.assert_called_once_with(
            f"Git repository already exists at {repo_path}"
        )
        # Verify no initialization was attempted
        mock_discover_repository.assert_called_once()

    def test_init_handles_errors(self, mock_discover_repository: MagicMock) -> None:
        """Test init handles errors during repository initialization."""
        # Arrange
        repo_path = Path("/problematic/path")
        mock_discover_repository.return_value = None  # Not a repo initially
        git_service = GitService(repo_dir=repo_path)

        # Act
        with patch("pygit2.init_repository") as mock_init:
            mock_init.side_effect = pygit2.errors.GitError(
                "Failed to initialize repository"
            )
            with patch("builtins.print") as mock_print:
                result = git_service.init()

        # Assert
        assert result is False
        mock_print.assert_called_once_with(
            "Failed to initialize git repository: Failed to initialize repository"
        )

    def test_init_with_real_directory(self, temp_dir: Path) -> None:
        """Integration test for repository initialization with a real directory."""
        # Arrange
        git_service = GitService(repo_dir=temp_dir)

        # Act
        result = git_service.init()

        # Assert
        assert result is True
        # Verify the .git directory was created
        assert (temp_dir / ".git").exists()
        assert (temp_dir / ".git").is_dir()
