#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Optional

from ..core import (
    Task,
    get_done_file_path,
    get_todo_file_path,
    read_tasks,
    write_tasks,
)
from ..git_service import GitService

def cmd_archive(_: argparse.Namespace) -> int:
    """
    Move completed tasks to the done.txt file.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file: Path = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    done_file: Path = get_done_file_path()

    tasks: list[Task] = read_tasks(todo_file, git_service)
    done_tasks: list[Task] = read_tasks(done_file, git_service)

    # Find completed tasks
    completed_tasks: list[Task] = [t for t in tasks if t.completed]
    incomplete_tasks: list[Task] = [t for t in tasks if not t.completed]

    if not completed_tasks:
        print("No completed tasks to archive.")
        return 0

    # Add completed tasks to done.txt
    done_tasks.extend(completed_tasks)
    write_tasks(done_tasks, done_file, git_service)

    # Remove completed tasks from todo.txt
    write_tasks(incomplete_tasks, todo_file, git_service)

    print(f"Archived {len(completed_tasks)} completed task(s).")
    return 0


def cmd_projects(_: argparse.Namespace) -> int:
    """
    List all projects in the todo.txt file.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file: Path = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    # Get all projects
    all_projects: set[str] = set()
    for task in tasks:
        all_projects.update(task.projects)

    # Print projects
    if not all_projects:
        print("No projects found.")
        return 0

    print("Projects:")
    for project in sorted(all_projects):
        print(f"  {project}")
    return 0


def cmd_contexts(_: argparse.Namespace) -> int:
    """
    List all contexts in the todo.txt file.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file: Path = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    # Get all contexts
    all_contexts: set[str] = set()
    for task in tasks:
        all_contexts.update(task.contexts)

    # Print contexts
    if not all_contexts:
        print("No contexts found.")
        return 0

    print("Contexts:")
    for context in sorted(all_contexts):
        print(f"  {context}")
    return 0


def cmd_project_mv(args: argparse.Namespace) -> int:
    """
    Rename a project from old_name to new_name.

    Args:
        args: Command-line arguments containing old_name and new_name
    """
    old_name: str = args.old_name
    new_name: str = args.new_name

    todo_file: Path = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    # Count tasks with the old project
    affected_tasks: list[Task] = [t for t in tasks if old_name in t.projects]

    if not affected_tasks:
        print(f"No tasks found with project +{old_name}")
        return 1

    # Update project names
    for task in affected_tasks:
        task.projects.remove(old_name)
        task.projects.add(new_name)

    # Write updated tasks back to file
    write_tasks(tasks, todo_file, git_service)

    print(
        f"Renamed project +{old_name} to +{new_name} in {len(affected_tasks)} task(s)"
    )
    return 0


def cmd_project_rm(args: argparse.Namespace) -> int:
    """
    Remove all tasks with the specified project.

    Args:
        args: Command-line arguments containing the project name
    """
    project_name: str = args.name

    todo_file: Path = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    # Count tasks with the specified project
    affected_tasks: list[Task] = [t for t in tasks if project_name in t.projects]

    if not affected_tasks:
        print(f"No tasks found with project +{project_name}")
        return 1

    # Remove tasks with the specified project
    remaining_tasks: list[Task] = [t for t in tasks if t not in affected_tasks]

    # Write remaining tasks back to file
    write_tasks(remaining_tasks, todo_file, git_service)

    print(f"Removed {len(affected_tasks)} task(s) with project +{project_name}")
    return 0


def cmd_project_pri(args: argparse.Namespace) -> int:
    """
    Assign the same priority to all tasks in a project.

    Args:
        args: Command-line arguments containing the project name and priority
    """
    project_name: str = args.name
    priority: str = args.priority

    # Validate priority
    if priority != "-" and (len(priority) != 1 or not "A" <= priority <= "Z"):
        print(
            "Error: Priority must be a capital letter (A-Z) or '-' to remove priority"
        )
        return 1

    todo_file: Path = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    # Find tasks with the specified project
    affected_tasks: list[Task] = [t for t in tasks if project_name in t.projects]

    if not affected_tasks:
        print(f"No tasks found with project +{project_name}")
        return 1

    # Update priority for all tasks in the project
    for task in affected_tasks:
        if priority == "-":
            task.priority = None
        else:
            task.priority = priority

    # Write updated tasks back to file
    write_tasks(tasks, todo_file, git_service)

    if priority == "-":
        print(
            f"Removed priority from {len(affected_tasks)} task(s) in project +{project_name}"
        )
    else:
        print(
            f"Set priority ({priority}) for {len(affected_tasks)} task(s) in "
            f"project +{project_name}"
        )
    return 0
