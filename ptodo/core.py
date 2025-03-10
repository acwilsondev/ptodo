#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from .config import get_config
from .git_service import GitService
from .serda import Task, parse_task, serialize_task
from .utils import get_ptodo_directory


def get_todo_file_path() -> Path:
    """
    Get the path to the todo.txt file.

    First checks the TODO_FILE environment variable.
    If not set, uses the value from the configuration file.
    The ptodo directory is either ~/.ptodo or $PTODO_DIRECTORY if set.

    Returns:
        Path: Path to the todo.txt file
    """
    todo_file = os.environ.get("TODO_FILE")
    if todo_file:
        return Path(todo_file)
    return get_ptodo_directory() / get_config("todo_file")


def get_done_file_path() -> Path:
    """
    Get the path to the done.txt file.

    First checks the DONE_FILE environment variable.
    If not set, uses the value from the configuration file.
    The ptodo directory is either ~/.ptodo or $PTODO_DIRECTORY if set.

    Returns:
        Path: Path to the done.txt file
    """
    done_file = os.environ.get("DONE_FILE")
    if done_file:
        return Path(done_file)
    return get_ptodo_directory() / get_config("done_file")


def read_tasks(file_path: Path, git_service: GitService = None) -> list[Task]:
    """
    Read tasks from a file.

    Args:
        file_path: Path to the todo.txt file
        git_service: Optional GitService for syncing changes

    Returns:
        List of Task objects
    """
    tasks = []

    # Pull the latest changes if git is configured
    if git_service and git_service.is_repo() and git_service.has_remote():
        git_service.pull()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        task = parse_task(line)
                        tasks.append(task)
                    except ValueError as e:
                        print(
                            f"Warning: Skipping invalid task: {line} ({e})",
                            file=sys.stderr,
                        )
    except FileNotFoundError:
        # If the file doesn't exist, just return an empty list
        pass

    return tasks


def write_tasks(
    tasks: list[Task], file_path: Path, git_service: GitService = None
) -> None:
    """
    Write tasks to a file.

    Args:
        tasks: List of Task objects
        file_path: Path to the output file
        git_service: Optional GitService for syncing changes
    """
    with open(file_path, "w", encoding="utf-8") as f:
        for task in tasks:
            f.write(serialize_task(task) + "\n")

    # Auto-sync changes if git is configured
    if git_service and git_service.is_repo():
        git_service.sync(file_path, f"Update {file_path.name}")
