#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Set, TextIO

from .serda import Task, parse_task, serialize_task

DEFAULT_TODO_FILENAME = "todo.txt"
DEFAULT_DONE_FILENAME = "done.txt"


def get_todo_file_path() -> Path:
    """
    Get the path to the todo.txt file.
    
    First checks the TODO_FILE environment variable.
    If not set, uses the default (todo.txt in the current directory).
    
    Returns:
        Path: Path to the todo.txt file
    """
    todo_file = os.environ.get("TODO_FILE")
    if todo_file:
        return Path(todo_file)
    return Path.cwd() / DEFAULT_TODO_FILENAME


def get_done_file_path() -> Path:
    """
    Get the path to the done.txt file.
    
    First checks the DONE_FILE environment variable.
    If not set, uses the default (done.txt in the current directory).
    
    Returns:
        Path: Path to the done.txt file
    """
    done_file = os.environ.get("DONE_FILE")
    if done_file:
        return Path(done_file)
    return Path.cwd() / DEFAULT_DONE_FILENAME


def read_tasks(file_path: Path) -> List[Task]:
    """
    Read tasks from a file.
    
    Args:
        file_path: Path to the todo.txt file
        
    Returns:
        List of Task objects
    """
    tasks = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        task = parse_task(line)
                        tasks.append(task)
                    except ValueError as e:
                        print(f"Warning: Skipping invalid task: {line} ({e})", file=sys.stderr)
    except FileNotFoundError:
        # If the file doesn't exist, just return an empty list
        pass
        
    return tasks


def write_tasks(tasks: List[Task], file_path: Path) -> None:
    """
    Write tasks to a file.
    
    Args:
        tasks: List of Task objects
        file_path: Path to the output file
    """
    with open(file_path, 'w') as f:
        for task in tasks:
            f.write(serialize_task(task) + '\n')


def cmd_list(args: argparse.Namespace) -> None:
    """
    List tasks from the todo.txt file.
    
    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    tasks = read_tasks(todo_file)
    
    # Filter tasks
    if args.project:
        tasks = [t for t in tasks if args.project in t.projects]
    if args.context:
        tasks = [t for t in tasks if args.context in t.contexts]
    if args.priority:
        tasks = [t for t in tasks if t.priority == args.priority]
    if args.completed:
        tasks = [t for t in tasks if t.completed]
    elif not args.all:
        # By default, show only incomplete tasks
        tasks = [t for t in tasks if not t.completed]
    
    # Print tasks
    if not tasks:
        print("No matching tasks found.")
        return
        
    for i, task in enumerate(tasks, 1):
        priority_str = f"({task.priority}) " if task.priority else ""
        completion_str = "x " if task.completed else ""
        completion_date_str = f"{task.completion_date} " if task.completion_date else ""
        creation_date_str = f"{task.creation_date} " if task.creation_date else ""
        
        print(f"{i:3d}. {completion_str}{priority_str}{completion_date_str}{creation_date_str}{task.description}")


def cmd_add(args: argparse.Namespace) -> None:
    """
    Add a new task to the todo.txt file.
    
    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    tasks = read_tasks(todo_file)
    
    # Create a new task
    task = Task(
        description=args.text,
        priority=args.priority,
        creation_date=date.today() if args.date else None
    )
    
    tasks.append(task)
    write_tasks(tasks, todo_file)
    print(f"Added: {serialize_task(task)}")


def cmd_done(args: argparse.Namespace) -> None:
    """
    Mark a task as done.
    
    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    tasks = read_tasks(todo_file)
    
    if not tasks:
        print("No tasks found.")
        return
        
    if 1 <= args.task_number <= len(tasks):
        task = tasks[args.task_number - 1]
        task.complete()
        
        write_tasks(tasks, todo_file)
        print(f"Completed: {serialize_task(task)}")
    else:
        print(f"Error: Task number {args.task_number} out of range (1-{len(tasks)}).")


def cmd_pri(args: argparse.Namespace) -> None:
    """
    Set the priority of a task.
    
    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    tasks = read_tasks(todo_file)
    
    if not tasks:
        print("No tasks found.")
        return
        
    if 1 <= args.task_number <= len(tasks):
        task = tasks[args.task_number - 1]
        original = serialize_task(task)
        
        task.priority = args.priority
        
        write_tasks(tasks, todo_file)
        print(f"Updated: {original} → {serialize_task(task)}")
    else:
        print(f"Error: Task number {args.task_number} out of range (1-{len(tasks)}).")


def cmd_archive(args: argparse.Namespace) -> None:
    """
    Move completed tasks to the done.txt file.
    
    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    done_file = get_done_file_path()
    
    tasks = read_tasks(todo_file)
    done_tasks = read_tasks(done_file)
    
    # Find completed tasks
    completed_tasks = [t for t in tasks if t.completed]
    incomplete_tasks = [t for t in tasks if not t.completed]
    
    if not completed_tasks:
        print("No completed tasks to archive.")
        return
    
    # Add completed tasks to done.txt
    done_tasks.extend(completed_tasks)
    write_tasks(done_tasks, done_file)
    
    # Remove completed tasks from todo.txt
    write_tasks(incomplete_tasks, todo_file)
    
    print(f"Archived {len(completed_tasks)} completed task(s).")


def cmd_projects(args: argparse.Namespace) -> None:
    """
    List all projects in the todo.txt file.
    
    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    tasks = read_tasks(todo_file)
    
    # Get all projects
    all_projects: Set[str] = set()
    for task in tasks:
        all_projects.update(task.projects)
    
    # Print projects
    if not all_projects:
        print("No projects found.")
        return
        
    print("Projects:")
    for project in sorted(all_projects):
        print(f"  {project}")


def cmd_contexts(args: argparse.Namespace) -> None:
    """
    List all contexts in the todo.txt file.
    
    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    tasks = read_tasks(todo_file)
    
    # Get all contexts
    all_contexts: Set[str] = set()
    for task in tasks:
        all_contexts.update(task.contexts)
    
    # Print contexts
    if not all_contexts:
        print("No contexts found.")
        return
        
    print("Contexts:")
    for context in sorted(all_contexts):
        print(f"  {context}")


def main() -> None:
    """
    Main function for the todo.txt CLI.
    
    Parses command-line arguments and dispatches to the appropriate handler.
    """
    parser = argparse.ArgumentParser(description="Command-line todo.txt manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--all", "-a", action="store_true", help="Show all tasks, including completed ones")
    list_parser.add_argument("--completed", "-c", action="store_true", help="Show only completed tasks")
    list_parser.add_argument("--project", "-p", help="Filter by project")
    list_parser.add_argument("--context", "-@", help="Filter by context")
    list_parser.add_argument("--priority", help="Filter by priority (A-Z)")
    
    # add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("text", help="Task description")
    add_parser.add_argument("--priority", "-p", help="Task priority (A-Z)")
    add_parser.add_argument("--date", "-d", action="store_true", help="Add creation date")
    
    # done command
    done_parser = subparsers.add_parser("done", help="Mark a task as done")
    done_parser.add_argument("task_number", type=int, help="Task number to mark as done")
    
    # pri command
    pri_parser = subparsers.add_parser("pri", help="Set task priority")
    pri_parser.add_argument("task_number", type=int, help="Task number to prioritize")
    pri_parser.add_argument("priority", help="Priority (A-Z)")
    
    # archive command
    archive_parser = subparsers.add_parser("archive", help="Move completed tasks to done.txt")
    
    # projects command
    projects_parser = subparsers.add_parser("projects", help="List all projects")
    
    # contexts command
    contexts_parser = subparsers.add_parser("contexts", help="List all contexts")
    
    args = parser.parse_args()
    
    # Dispatch to the appropriate handler
    if args.command == "list":
        cmd_list(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "done":
        cmd_done(args)
    elif args.command == "pri":
        cmd_pri(args)
    elif args.command == "archive":
        cmd_archive(args)
    elif args.command == "projects":
        cmd_projects(args)
    elif args.command == "contexts":
        cmd_contexts(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

