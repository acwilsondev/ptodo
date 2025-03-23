#!/usr/bin/env python3
import argparse
import subprocess

from ..core import get_todo_file_path
from ..git_service import GitService


def cmd_git_init(_: argparse.Namespace) -> int:
    """
    Initialize a git repository in the current directory.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    git_service.init()
    return 0


def cmd_git_remote(args: argparse.Namespace) -> int:
    """
    Show remotes or add/update a git remote.

    When called without a URL, shows the configured remotes.
    When called with a URL, adds or updates the specified remote.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    if not git_service.is_repo():
        print("Not a git repository. Run 'ptodo git init' first.")
        return 1

    print(args)

    # If URL is provided, add or update the remote
    if hasattr(args, "url") and args.url:
        git_service.add_remote("origin", args.url)
        return 0

    # If no URL is provided, show the remotes
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=git_service.repo_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            print(result.stdout)
        else:
            print("No remotes configured.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to list remotes: {e.stderr}")
        return 1

    return 0


def cmd_git_sync(_: argparse.Namespace) -> int:
    """
    Sync changes with the remote repository.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    if not git_service.is_repo():
        print("Not a git repository. Run 'ptodo git init' first.")
        return 1

    if git_service.sync(commit_message="Manual sync of todo files"):
        print("Successfully synced changes with remote repository.")
        return 0
    else:
        print("No changes to sync or sync failed.")
        return 1
