#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

from ..config import get_config
from ..git_service import GitService
from .serda import Task, parse_task
from ..utils import get_ptodo_directory


def sort_tasks(tasks: list[Task]) -> list[Task]:
    """
    Sort tasks by priority (A is highest, then B, etc.).
    Tasks without priority come after tasks with priorities.

    Args:
        tasks: List of Task objects to be sorted

    Returns:
        A new list with the tasks sorted by priority
    """

    # Define priority sort key (A is highest, then B, etc.)
    # Tasks without priority come after tasks with priorities
    def priority_key(task: Task) -> str:
        if not task.priority:
            return "Z"  # Tasks without priority come last
        return task.priority

    # Create a copy of the tasks list and sort it
    sorted_tasks = sorted(tasks, key=priority_key)
    return sorted_tasks


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
    todo_file_name = str(get_config("todo_file"))  # Ensure string type
    return get_ptodo_directory() / todo_file_name


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
    done_file_name = str(get_config("done_file"))  # Ensure string type
    return get_ptodo_directory() / done_file_name


def read_tasks(file_path: Path, git_service: GitService | None = None) -> list[Task]:
    """
    Read tasks from a file.

    Args:
        file_path: Path to the todo.txt file
        git_service: Optional GitService for syncing changes

    Returns:
        List of Task objects
    """
    tasks: list[Task] = []

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
    tasks: list[Task],
    file_path: Path,
    git_service: GitService | None = None,
) -> None:
    """
    Write tasks to a file.

    Args:
        tasks: List of Task objects
        file_path: Path to the output file
        git_service: Optional GitService for syncing changes
    """
    # Check if auto_sort is enabled in the configuration
    auto_sort = get_config("auto_sort", True)

    # If auto_sort is enabled, sort the tasks by priority
    if auto_sort:
        tasks_to_write = sort_tasks(tasks)
    else:
        tasks_to_write = tasks

    with open(file_path, "w", encoding="utf-8") as f:
        for task in tasks_to_write:
            f.write(f"{task}\n")

    if not git_service or not git_service.is_repo():
        # nothing to commit if git is not configured
        return

    auto_commit = get_config("auto_commit", True)
    auto_sync = get_config("auto_sync", True)

    if not auto_commit:
        # nothing to commit if auto_commit is disabled
        return

    # Stage changes
    git_service.stage_changes(file_path)

    # Check if there are changes to commit
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=git_service.repo_dir,
        check=True,
        capture_output=True,
        text=True,
    )

    if status.stdout.strip():
        git_service.commit(f"Update {file_path.name}")

        if auto_sync and git_service.has_remote():
            git_service.push()
