#!/usr/bin/env python3
import argparse
import datetime
import os
from operator import itemgetter

from ..config import get_config
from ..core import (
    get_done_file_path,
    get_todo_file_path,
    read_tasks,
    sort_tasks,
    write_tasks,
)
from ..git_service import GitService
from ..serda import Task, create_task, parse_date, parse_task, today_string

# ANSI color codes for formatting
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
GRAY = "\033[90m"
RED = "\033[31m"
MAGENTA = "\033[35m"


def cmd_list(args: argparse.Namespace) -> int:
    """
    List tasks from the todo.txt file.

    Args:
        args: Command-line arguments
    """

    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    all_tasks = read_tasks(todo_file, git_service)

    # Create a list of (index, task) tuples to track original positions
    indexed_tasks: list[tuple[int, Task]] = list(enumerate(all_tasks))

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

    # Get any explicit top count from args
    list_count = getattr(args, "top", None)
    # If not explicitly set and not showing all tasks, try to get from config
    if list_count is None and not args.all:
        list_count = get_config("default_list_count")
    # Limit to top N tasks if count is specified
    if list_count is not None and list_count > 0:
        indexed_tasks = indexed_tasks[:list_count]

    for _, (original_idx, task) in enumerate(indexed_tasks, 0):
        _show_task(original_idx, task)

        # Add a separator line between tasks for better readability
        print("")

    if not hasattr(args, "quiet") or not args.quiet:
        print(f"{GRAY}Showing {len(indexed_tasks)} of {len(all_tasks)} tasks.{RESET}")
        print("")

        # Add a helpful note about task numbers
        print(
            f"{GRAY}Note: You can use task numbers with commands like 'done' and 'pri'.{RESET}"
        )
        print(f"{GRAY}      For example: 'ptodo done 3' or 'ptodo pri 2 A'{RESET}")
    return 0


def _show_task(original_idx: int, task: Task) -> None:
    _show_main_line(original_idx, task)

    # Format additional information in indented blocks
    indent = "    "

    _show_projects(task, indent)

    _show_contexts(task, indent)

    if task.effort:
        print(f"{indent}Effort: {task.effort}")

    _show_metadata(task, indent)


def _show_main_line(original_idx: int, task: Task) -> None:
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


def _show_projects(task: Task, indent: str) -> None:
    if task.projects:
        project_list = " ".join(
            [f"{BLUE}+{project}{RESET}" for project in sorted(task.projects)]
        )
        print(f"{indent}Projects: {project_list}")


def _show_contexts(task: Task, indent: str) -> None:
    if task.contexts:
        context_list = " ".join(
            [f"{CYAN}@{context}{RESET}" for context in sorted(task.contexts)]
        )
        print(f"{indent}Contexts: {context_list}")


def _show_metadata(task: Task, indent: str) -> None:
    if task.metadata:
        print(f"{indent}Metadata:")
        for key, value in sorted(task.metadata.items()):
            print(f"{indent}  {MAGENTA}{key}{RESET}: {value}")


def cmd_add(args: argparse.Namespace) -> int:
    """
    Add a new task to the todo.txt file.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    # Step 1: Parse the input text first to extract all components
    parsed_task = parse_task(args.text)

    # Use the priority from the parsed task or from args
    priority = parsed_task.priority or getattr(args, "priority", None)

    task: Task = create_task(
        description=parsed_task.description,
        priority=priority,
        add_creation_date=True,  # Changed from datetime.date.today()
        projects=list(parsed_task.projects) if parsed_task.projects else None,
        contexts=list(parsed_task.contexts) if parsed_task.contexts else None,
        metadata=parsed_task.metadata if parsed_task.metadata else None,
        effort=parsed_task.effort,
    )

    tasks.append(task)
    write_tasks(tasks, todo_file, git_service)
    if not hasattr(args, "quiet") or not args.quiet:
        print(f"Added: {task}")
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    """
    Mark one or more tasks as done.

    Args:
        args: Command-line arguments containing task_ids
    """
    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    if not tasks:
        print("No tasks found.")
        return 1

    all_successful = True
    completed_tasks = []

    for task_id in args.task_ids:
        if 1 <= task_id <= len(tasks):
            task = tasks[task_id - 1]
            task.complete()
            completed_tasks.append(task)
            if not hasattr(args, "quiet") or not args.quiet:
                print(f"Completed: {task}")
        else:
            print(f"Error: Task number {task_id} out of range (1-{len(tasks)}).")
            all_successful = False

    if completed_tasks:
        # check completed tasks metadata for recur:[days] and create new instance if needed
        for task in completed_tasks:
            if recurrence := task.recur():
                tasks.append(recurrence)

        if get_config("archive_completed"):
            if not hasattr(args, "quiet") or not args.quiet:
                print(f"Archiving: {len(completed_tasks)} task(s)")
            done_file = get_done_file_path()
            incomplete_tasks = [t for t in tasks if not t.completed]
            write_tasks(completed_tasks, done_file, git_service)
            write_tasks(incomplete_tasks, todo_file, git_service)
        else:
            write_tasks(tasks, todo_file, git_service)
    return 0 if all_successful else 1


def cmd_rm(args: argparse.Namespace) -> int:
    """
    Remove a task without archiving.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    if not tasks:
        print("No tasks found.")
        return 1

    if args.task_id < 1 or args.task_id > len(tasks):
        print(f"Error: Task number {args.task_id} out of range (1-{len(tasks)}).")
        return 1

    task = tasks[args.task_id - 1]
    tasks.pop(args.task_id - 1)
    write_tasks(tasks, todo_file, git_service)
    if not hasattr(args, "quiet") or not args.quiet:
        print(f"Removed: {task}")
    return 0


def cmd_pri(args: argparse.Namespace) -> int:
    """
    Set the priority of a task.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    if not tasks:
        print("No tasks found.")
        return 1

    if args.task_id < 1 or args.task_id > len(tasks):
        print(f"Error: Task number {args.task_id} out of range (1-{len(tasks)}).")
        return 1

    task = tasks[args.task_id - 1]
    original = str(task)
    task.priority = args.priority
    write_tasks(tasks, todo_file, git_service)
    if not hasattr(args, "quiet") or not args.quiet:
        print(f"Updated: {original} → {task}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """
    Show detailed information for a specific task.

    Args:
        args: Command-line arguments containing the task number
    """
    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    if not tasks:
        print("No tasks found.")
        return 1

    if args.task_id < 1 or args.task_id > len(tasks):
        print(f"Error: Task number {args.task_id} out of range (1-{len(tasks)}).")
        return 1

    task = tasks[args.task_id - 1]

    # Build a detailed view of the task
    print(f"Task #{args.task_id}:")
    _show_task(args.task_id - 1, task)

    if not hasattr(args, "quiet") or not args.quiet:
        print(f"\nRaw format: {task}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    """
    Show the highest priority incomplete task.

    Args:
        args: Command-line arguments
    """

    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    all_tasks: list[Task] = read_tasks(todo_file, git_service)

    # Create a list of (index, task) tuples to track original positions
    indexed_tasks: list[tuple[int, Task]] = list(enumerate(all_tasks))

    # Filter tasks but keep track of original indices
    if args.project:
        indexed_tasks = [(i, t) for i, t in indexed_tasks if args.project in t.projects]
    if args.context:
        indexed_tasks = [(i, t) for i, t in indexed_tasks if args.context in t.contexts]

    # Always filter to show only incomplete tasks
    indexed_tasks = [(i, t) for i, t in indexed_tasks if not t.completed]

    # Use a key function adapted for indexed_tasks that uses the same
    # sorting logic as the sort_tasks function in core.py
    def priority_key(item: tuple[int, Task]) -> str:
        task = item[1]
        if not task.priority:
            return "Z"  # Tasks without priority come last
        return task.priority

    indexed_tasks.sort(key=priority_key)

    # Print the highest priority task, if any
    if not indexed_tasks:
        print("No matching tasks found.")
        return 0

    # Only show the top task
    original_idx: int
    task: Task
    original_idx, task = indexed_tasks[0]

    _show_task(original_idx, task)

    return 0


def cmd_sort(args: argparse.Namespace) -> int:
    """
    Sort tasks in the todo.txt file by priority.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    if not tasks:
        print("No tasks found.")
        return 0

    # Sort tasks by priority using the shared sort_tasks function
    sorted_tasks = sort_tasks(tasks)

    # Write sorted tasks back to the file
    # Note: We're passing the sorted list directly since write_tasks will handle
    # auto_sort based on configuration
    write_tasks(sorted_tasks, todo_file, git_service)
    if not hasattr(args, "quiet") or not args.quiet:
        print(f"Sorted {len(tasks)} tasks by priority.")
    return 0


def cmd_await(args: argparse.Namespace) -> int:
    """
    Add a new waiting-for task with required due date to the todo.txt file.

    Args:
        args: Command-line arguments containing description and due_date
    """
    # Validate the due date format before proceeding
    due_date = parse_date(args.due_date)
    if due_date is None:
        print(
            f"Error: Invalid date format '{args.due_date}'. Please use YYYY-MM-DD format."
        )
        return 1

    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    # Create a new task using the create_task utility which sets creation date by default
    task: Task = create_task(
        description=args.description,
        priority=getattr(args, "priority", None),
    )

    # Add @waiting-for context
    if not task.contexts:
        task.contexts = set()
    task.contexts.add("waiting")

    # Add due date to metadata
    if not task.metadata:
        task.metadata = {}
    task.metadata["due"] = due_date.strftime("%Y-%m-%d")

    tasks.append(task)
    write_tasks(tasks, todo_file, git_service)
    if not hasattr(args, "quiet") or not args.quiet:
        print(f"Added waiting-for task: {task}")
    return 0


def cmd_edit(args: argparse.Namespace) -> int:
    """
    Open the todo.txt file in the system's default editor.

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()

    # Get the editor from environment variable or use a fallback
    editor = os.environ.get("EDITOR", "vi")

    # Open the file in the editor
    exit_code = os.system(f'{editor} "{todo_file}"')

    if exit_code != 0:
        print(f"Error: Editor returned exit code {exit_code}")
        return 1

    if not hasattr(args, "quiet") or not args.quiet:
        print(f"Edited: {todo_file}")

    return 0


def cmd_due(args: argparse.Namespace) -> int:
    """
    Show tasks that are due today or earlier, or within a specified number of days.

    Lists all incomplete tasks that have a due date of today or earlier,
    or if --soon is specified, tasks due within the given number of days,
    sorted by due date (oldest first).

    Args:
        args: Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

    # Filter incomplete tasks with due date metadata
    due_tasks = []
    today = datetime.date.today()

    # Calculate the future date if --soon is specified
    soon_days = getattr(args, "soon", None)
    future_date = None
    if soon_days is not None:
        future_date = today + datetime.timedelta(days=soon_days)

    for idx, task in enumerate(tasks):
        # Skip completed tasks
        if task.completed:
            continue

        # Skip tasks without due date
        if "due" not in task.metadata:
            continue

        # Parse the due date
        due_date = parse_date(task.metadata["due"])
        if due_date is None:
            continue  # Skip tasks with invalid due date

        # Include tasks due today or earlier, or within the specified number of days
        if due_date <= today or (future_date is not None and due_date <= future_date):
            due_tasks.append((idx, task, due_date))

    # Sort by due date (oldest first)
    due_tasks.sort(key=itemgetter(2))

    # Print tasks
    if not due_tasks:
        if future_date is not None:
            print(
                f"No tasks due within the next {soon_days} day{'s' if soon_days != 1 else ''}."
            )
        else:
            print("No tasks due today or earlier.")
        return 0

    for _, (original_idx, task, due_date) in enumerate(due_tasks, 1):
        _show_task(original_idx, task)
        # Add a separator line between tasks for better readability
        print("")

    if not hasattr(args, "quiet") or not args.quiet:
        if future_date is not None:
            print(
                f"{GRAY}Showing {len(due_tasks)} task(s) due within the next {soon_days} day{'s' if soon_days != 1 else ''}.{RESET}"
            )
        else:
            print(
                f"{GRAY}Showing {len(due_tasks)} task(s) due today or earlier.{RESET}"
            )

        # Show overdue tasks
        days_past = {
            (datetime.date.today() - due_date).days
            for _, _, due_date in due_tasks
            if (datetime.date.today() - due_date).days > 0
        }
        if days_past:
            overdue_str = ", ".join(
                f"{days} day{'s' if days > 1 else ''}" for days in sorted(days_past)
            )
            print(f"{RED}Tasks overdue by: {overdue_str}{RESET}")

        # Show future tasks if --soon is specified
        if future_date is not None:
            days_future = {
                (due_date - datetime.date.today()).days
                for _, _, due_date in due_tasks
                if due_date > datetime.date.today()
            }
            if days_future:
                future_str = ", ".join(
                    f"{days} day{'s' if days > 1 else ''}"
                    for days in sorted(days_future)
                )
                print(f"{GREEN}Tasks due in: {future_str}{RESET}")

        print("")

    return 0
