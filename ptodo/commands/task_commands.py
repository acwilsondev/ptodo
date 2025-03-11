#!/usr/bin/env python3
import argparse
from datetime import date

from ..core import get_todo_file_path, read_tasks, write_tasks
from ..git_service import GitService
from ..serda import Task, serialize_task


def cmd_list(args: argparse.Namespace) -> int:
    """
    List tasks from the todo.txt file.

    Args:
        args: Command-line arguments
    """
    # ANSI color codes for formatting
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"
    # RED = "\033[31m"
    MAGENTA = "\033[35m"

    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    all_tasks = read_tasks(todo_file, git_service)

    # Create a list of (index, task) tuples to track original positions
    indexed_tasks = list(enumerate(all_tasks))

    # Filter tasks but keep track of original indices
    if args.project:
        indexed_tasks = [(i, t) for i, t in indexed_tasks if args.project in t.projects]
    if args.context:
        indexed_tasks = [(i, t) for i, t in indexed_tasks if args.context in t.contexts]
    if args.priority:
        indexed_tasks = [
            (i, t) for i, t in indexed_tasks if t.priority == args.priority
        ]
    if args.completed:
        indexed_tasks = [(i, t) for i, t in indexed_tasks if t.completed]
    elif not args.all:
        # By default, show only incomplete tasks
        indexed_tasks = [(i, t) for i, t in indexed_tasks if not t.completed]

    # Print tasks
    if not indexed_tasks:
        print("No matching tasks found.")
        return 0

    # Limit to top N tasks if specified
    if hasattr(args, 'top') and args.top is not None and args.top > 0:
        indexed_tasks = indexed_tasks[:args.top]

    for idx, (original_idx, task) in enumerate(indexed_tasks, 0):
        # Format basic task information using the original (1-based) index
        task_num = f"{BOLD}[{original_idx + 1}]{RESET}"
        priority_str = f"{YELLOW}({task.priority}){RESET} " if task.priority else ""
        completion_str = f"{GREEN}x{RESET} " if task.completed else ""
        completion_date_str = (
            f"{GRAY}{task.completion_date}{RESET} " if task.completion_date else ""
        )
        creation_date_str = (
            f"{GRAY}{task.creation_date}{RESET} " if task.creation_date else ""
        )

        # Format the main task line with basic information
        main_line = (
            f"{task_num} {completion_str}{priority_str}{completion_date_str}"
            f"{creation_date_str}{task.description}"
        )
        print(main_line)

        # Format additional information in indented blocks
        indent = "    "

        # Show projects if any
        if task.projects:
            project_list = " ".join(
                [f"{BLUE}+{project}{RESET}" for project in sorted(task.projects)]
            )
            print(f"{indent}Projects: {project_list}")

        # Show contexts if any
        if task.contexts:
            context_list = " ".join(
                [f"{CYAN}@{context}{RESET}" for context in sorted(task.contexts)]
            )
            print(f"{indent}Contexts: {context_list}")

        # Show metadata if any
        if task.metadata:
            print(f"{indent}Metadata:")
            for key, value in sorted(task.metadata.items()):
                print(f"{indent}  {MAGENTA}{key}{RESET}: {value}")

        # Add a separator line between tasks for better readability
        print("")

    # Add a helpful note about task numbers
    print(
        f"{GRAY}Note: You can use task numbers with commands like 'done' and 'pri'.{RESET}"
    )
    print(f"{GRAY}      For example: 'ptodo done 3' or 'ptodo pri 2 A'{RESET}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """
    Add a new task to the todo.txt file.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    tasks = read_tasks(todo_file, git_service)

    # Create a new task
    task = Task(
        description=args.text,
        priority=getattr(args, "priority", None),
        creation_date=date.today() if getattr(args, "date", False) else None,
    )

    tasks.append(task)
    write_tasks(tasks, todo_file, git_service)
    print(f"Added: {serialize_task(task)}")
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    """
    Mark a task as done.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    tasks = read_tasks(todo_file, git_service)

    if not tasks:
        print("No tasks found.")
        return 1

    if 1 <= args.task_id <= len(tasks):
        task = tasks[args.task_id - 1]
        task.complete()
        write_tasks(tasks, todo_file, git_service)
        print(f"Completed: {serialize_task(task)}")
        return 0
    else:
        print(f"Error: Task number {args.task_id} out of range (1-{len(tasks)}).")
        return 1


def cmd_pri(args: argparse.Namespace) -> int:
    """
    Set the priority of a task.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    tasks = read_tasks(todo_file, git_service)

    if not tasks:
        print("No tasks found.")
        return 1

    if 1 <= args.task_id <= len(tasks):
        task = tasks[args.task_id - 1]
        original = serialize_task(task)
        task.priority = args.priority
        write_tasks(tasks, todo_file, git_service)
        print(f"Updated: {original} → {serialize_task(task)}")
        return 0
    else:
        print(f"Error: Task number {args.task_id} out of range (1-{len(tasks)}).")
        return 1


def cmd_show(args: argparse.Namespace) -> int:
    """
    Show detailed information for a specific task.

    Args:
        args: Command-line arguments containing the task number
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    tasks = read_tasks(todo_file, git_service)

    if not tasks:
        print("No tasks found.")
        return 1

    if 1 <= args.task_id <= len(tasks):
        task = tasks[args.task_id - 1]

        # Build a detailed view of the task
        print(f"Task #{args.task_id}:")
        print(f"  Status: {'Completed' if task.completed else 'Pending'}")

        if task.priority:
            print(f"  Priority: {task.priority}")

        if task.creation_date:
            print(f"  Created: {task.creation_date}")

        if task.completion_date:
            print(f"  Completed: {task.completion_date}")

        print(f"  Description: {task.description}")

        if task.projects:
            print(f"  Projects: {', '.join(task.projects)}")

        if task.contexts:
            print(f"  Contexts: {', '.join(task.contexts)}")

        if task.metadata:
            print("  Metadata:")
            for key, value in task.metadata.items():
                print(f"    {key}: {value}")

        print(f"\nRaw format: {serialize_task(task)}")
        return 0
    else:
        print(f"Error: Task number {args.task_id} out of range (1-{len(tasks)}).")
        return 1
def cmd_next(args: argparse.Namespace) -> int:
    """
    Show the highest priority incomplete task.

    Args:
        args: Command-line arguments
    """
    # ANSI color codes for formatting
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"
    MAGENTA = "\033[35m"

    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    all_tasks = read_tasks(todo_file, git_service)

    # Create a list of (index, task) tuples to track original positions
    indexed_tasks = list(enumerate(all_tasks))

    # Filter tasks but keep track of original indices
    if args.project:
        indexed_tasks = [(i, t) for i, t in indexed_tasks if args.project in t.projects]
    if args.context:
        indexed_tasks = [(i, t) for i, t in indexed_tasks if args.context in t.contexts]
    
    # Always filter to show only incomplete tasks
    indexed_tasks = [(i, t) for i, t in indexed_tasks if not t.completed]

    # Sort tasks by priority (A is highest, then B, etc.)
    # For tasks without priority, they come after tasks with priorities
    def priority_key(item):
        task = item[1]
        if not task.priority:
            return 'Z'  # Tasks without priority come last
        return task.priority

    indexed_tasks.sort(key=priority_key)

    # Print the highest priority task, if any
    if not indexed_tasks:
        print("No matching tasks found.")
        return 0
    
    # Only show the top task
    original_idx, task = indexed_tasks[0]
    
    # Format basic task information using the original (1-based) index
    task_num = f"{BOLD}[{original_idx + 1}]{RESET}"
    priority_str = f"{YELLOW}({task.priority}){RESET} " if task.priority else ""
    creation_date_str = (
        f"{GRAY}{task.creation_date}{RESET} " if task.creation_date else ""
    )

    # Format the main task line with basic information
    main_line = (
        f"{task_num} {priority_str}{creation_date_str}{task.description}"
    )
    print(main_line)

    # Format additional information in indented blocks
    indent = "    "

    # Show projects if any
    if task.projects:
        project_list = " ".join(
            [f"{BLUE}+{project}{RESET}" for project in sorted(task.projects)]
        )
        print(f"{indent}Projects: {project_list}")

    # Show contexts if any
    if task.contexts:
        context_list = " ".join(
            [f"{CYAN}@{context}{RESET}" for context in sorted(task.contexts)]
        )
        print(f"{indent}Contexts: {context_list}")

    # Show metadata if any
    if task.metadata:
        print(f"{indent}Metadata:")
        for key, value in sorted(task.metadata.items()):
            print(f"{indent}  {MAGENTA}{key}{RESET}: {value}")

    return 0
