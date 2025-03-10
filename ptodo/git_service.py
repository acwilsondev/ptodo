#!/usr/bin/env python3
import subprocess
from pathlib import Path
from typing import Optional

# Import the get_ptodo_directory function from utils
from .utils import get_ptodo_directory


class GitService:
    """
    Service for git operations. Handles initialization, syncing, and remote management.
    """

    def __init__(self, repo_dir: Path = None):
        """
        Initialize the GitService for a specific directory.

        Args:
            repo_dir: The directory for the git repository. Defaults to ptodo directory.
        """
        self.repo_dir = repo_dir or get_ptodo_directory()

    def is_repo(self) -> bool:
        """
        Check if the current directory is a git repository.

        Returns:
            bool: True if the directory is a git repo, False otherwise.
        """
        git_dir = self.repo_dir / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def init(self) -> bool:
        """
        Initialize a git repository in the current directory.

        Returns:
            bool: True if successful, False otherwise.
        """
        if self.is_repo():
            print(f"Git repository already exists at {self.repo_dir}")
            return True

        try:
            subprocess.run(
                ["git", "init"],
                cwd=self.repo_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"Initialized git repository at {self.repo_dir}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to initialize git repository: {e.stderr}")
            return False

    def add_remote(self, name: str, url: str) -> bool:
        """
        Add a remote repository.

        Args:
            name: Name of the remote (e.g., 'origin')
            url: URL of the remote repository

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_repo():
            print(f"Not a git repository: {self.repo_dir}")
            return False

        try:
            # Check if remote already exists
            result = subprocess.run(
                ["git", "remote"],
                cwd=self.repo_dir,
                check=True,
                capture_output=True,
                text=True,
            )

            if name in result.stdout.split():
                # Update existing remote
                subprocess.run(
                    ["git", "remote", "set-url", name, url],
                    cwd=self.repo_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print(f"Updated remote '{name}' to {url}")
            else:
                # Add new remote
                subprocess.run(
                    ["git", "remote", "add", name, url],
                    cwd=self.repo_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print(f"Added remote '{name}' at {url}")

            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to add remote: {e.stderr}")
            return False

    def has_remote(self) -> bool:
        """
        Check if the repository has any remotes configured.

        Returns:
            bool: True if at least one remote exists, False otherwise.
        """
        if not self.is_repo():
            return False

        try:
            result = subprocess.run(
                ["git", "remote"],
                cwd=self.repo_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def stage_changes(self, file_path: Optional[Path] = None) -> bool:
        """
        Stage changes in the git repository.

        Args:
            file_path: Path to the file to stage. If None, stages all changes.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_repo():
            return False

        try:
            if file_path:
                subprocess.run(
                    ["git", "add", str(file_path)],
                    cwd=self.repo_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            else:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=self.repo_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            return True
        except subprocess.CalledProcessError:
            return False

    def commit(self, message: str) -> bool:
        """
        Commit staged changes with the given message.

        Args:
            message: Commit message

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_repo():
            return False

        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError:
            # No changes to commit or other error
            return False

    def pull(self) -> bool:
        """
        Pull changes from the remote repository.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_repo() or not self.has_remote():
            return False

        try:
            subprocess.run(
                ["git", "pull"],
                cwd=self.repo_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def push(self) -> bool:
        """
        Push changes to the remote repository.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_repo() or not self.has_remote():
            return False

        try:
            subprocess.run(
                ["git", "push"],
                cwd=self.repo_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def sync(
        self,
        file_path: Optional[Path] = None,
        commit_message: str = "Auto-sync changes",
    ) -> bool:
        """
        Sync changes with remote repository (pull, add, commit, push).

        Args:
            file_path: Path to the file to sync. If None, syncs all changes.
            commit_message: Message for the commit.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_repo():
            return False

        # Try to pull first if we have a remote
        if self.has_remote():
            self.pull()

        # Stage changes
        self.stage_changes(file_path)

        # Check if there are changes to commit
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.repo_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        if status.stdout.strip():
            # Commit changes
            self.commit(commit_message)

            # Push if we have a remote
            if self.has_remote():
                self.push()

            return True

        return False  # No changes to commit
