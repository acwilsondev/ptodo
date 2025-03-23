#!/usr/bin/env python3
import argparse

from ..core import get_todo_file_path, read_tasks, write_tasks
from ..git_service import GitService
from ..serda import Task, create_task, parse_date, serialize_task

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

    # Limit to top N tasks if specified
    if hasattr(args, "top") and args.top is not None and args.top > 0:
        indexed_tasks = indexed_tasks[: args.top]

    for _, (original_idx, task) in enumerate(indexed_tasks, 0):
        _show_task(original_idx, task)

        # Add a separator line between tasks for better readability
        print("")

    # Add a helpful note about task numbers
    print(
        f"{GRAY}Note: You can use task numbers with commands like 'done' and 'pri'.{RESET}"
    )
    print(f"{GRAY}      For example: 'ptodo done 3' or 'ptodo pri 2 A'{RESET}")
    return 0


def _show_task(original_idx, task):
    _show_main_line(original_idx, task)

        # Format additional information in indented blocks
    indent = "    "

    _show_projects(task, indent)

    _show_contexts(task, indent)

    if task.effort:
        print(f"{indent}Effort: {task.effort}")

    _show_metadata(task, indent)


def _show_main_line(original_idx, task):
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


def _show_projects(task, indent):
    if task.projects:
        project_list = " ".join(
                [f"{BLUE}+{project}{RESET}" for project in sorted(task.projects)]
            )
        print(f"{indent}Projects: {project_list}")


def _show_contexts(task, indent):
    if task.contexts:
        context_list = " ".join(
                [f"{CYAN}@{context}{RESET}" for context in sorted(task.contexts)]
            )
        print(f"{indent}Contexts: {context_list}")


def _show_metadata(task, indent):
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

    # Create a new task using the create_task utility which sets creation date by default
    task: Task = create_task(
        description=args.text,
        priority=getattr(args, "priority", None),
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
    git_service: GitService = GitService(todo_file.parent)
    tasks: list[Task] = read_tasks(todo_file, git_service)

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
    removed_task = serialize_task(task)
    tasks.pop(args.task_id - 1)
    write_tasks(tasks, todo_file, git_service)
    print(f"Removed: {removed_task}")
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
    original = serialize_task(task)
    task.priority = args.priority
    write_tasks(tasks, todo_file, git_service)
    print(f"Updated: {original} → {serialize_task(task)}")
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

    print(f"\nRaw format: {serialize_task(task)}")
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

    # Sort tasks by priority (A is highest, then B, etc.)
    # For tasks without priority, they come after tasks with priorities
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


def cmd_sort(_: argparse.Namespace) -> int:
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

    # Define priority sort key (A is highest, then B, etc.)
    # Tasks without priority come after tasks with priorities
    def priority_key(task: Task) -> str:
        if not task.priority:
            return "Z"  # Tasks without priority come last
        return task.priority

    # Sort tasks by priority
    tasks.sort(key=priority_key)

    # Write sorted tasks back to the file
    write_tasks(tasks, todo_file, git_service)
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
    print(f"Added waiting-for task: {serialize_task(task)}")
    return 0
