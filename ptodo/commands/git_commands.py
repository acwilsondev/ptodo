#!/usr/bin/env python3
import argparse

from ..core import get_todo_file_path
from ..git_service import GitService


def cmd_git_init(_: argparse.Namespace) -> None:
    """
    Initialize a git repository in the current directory.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    git_service.init()


def cmd_git_remote(args: argparse.Namespace) -> None:
    """
    Add or update a git remote.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    if not git_service.is_repo():
        print("Not a git repository. Run 'ptodo git init' first.")
        return

    git_service.add_remote(args.name, args.url)


def cmd_git_sync(_: argparse.Namespace) -> None:
    """
    Sync changes with the remote repository.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    if not git_service.is_repo():
        print("Not a git repository. Run 'ptodo git init' first.")
        return

    if git_service.sync(commit_message="Manual sync of todo files"):
        print("Successfully synced changes with remote repository.")
    else:
        print("No changes to sync or sync failed.")

