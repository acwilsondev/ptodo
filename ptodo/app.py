#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import date
from pathlib import Path

from .serda import Task, parse_task, serialize_task
from .git_service import GitService
from .utils import get_ptodo_directory

VERSION = "0.1.0"
DEFAULT_TODO_FILENAME = "todo.txt"
DEFAULT_DONE_FILENAME = "done.txt"



def get_todo_file_path() -> Path:
    """
    Get the path to the todo.txt file.

    First checks the TODO_FILE environment variable.
    If not set, uses the default (todo.txt in the ptodo directory).
    The ptodo directory is either ~/.ptodo or $PTODO_DIRECTORY if set.

    Returns:
        Path: Path to the todo.txt file
    """
    todo_file = os.environ.get("TODO_FILE")
    if todo_file:
        return Path(todo_file)
    return get_ptodo_directory() / DEFAULT_TODO_FILENAME


def get_done_file_path() -> Path:
    """
    Get the path to the done.txt file.

    First checks the DONE_FILE environment variable.
    If not set, uses the default (done.txt in the ptodo directory).
    The ptodo directory is either ~/.ptodo or $PTODO_DIRECTORY if set.

    Returns:
        Path: Path to the done.txt file
    """
    done_file = os.environ.get("DONE_FILE")
    if done_file:
        return Path(done_file)
    return get_ptodo_directory() / DEFAULT_DONE_FILENAME


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


def write_tasks(tasks: list[Task], file_path: Path, git_service: GitService = None) -> None:
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


def cmd_list(args: argparse.Namespace) -> None:
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
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    tasks = read_tasks(todo_file, git_service)

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
        # Format basic task information
        task_num = f"{BOLD}[Task {i}]{RESET}"
        priority_str = f"{YELLOW}({task.priority}){RESET} " if task.priority else ""
        completion_str = f"{GREEN}x{RESET} " if task.completed else ""
        completion_date_str = f"{GRAY}{task.completion_date}{RESET} " if task.completion_date else ""
        creation_date_str = f"{GRAY}{task.creation_date}{RESET} " if task.creation_date else ""
        
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
            project_list = " ".join([f"{BLUE}+{project}{RESET}" for project in sorted(task.projects)])
            print(f"{indent}Projects: {project_list}")
            
        # Show contexts if any
        if task.contexts:
            context_list = " ".join([f"{CYAN}@{context}{RESET}" for context in sorted(task.contexts)])
            print(f"{indent}Contexts: {context_list}")
            
        # Show metadata if any
        if task.metadata:
            print(f"{indent}Metadata:")
            for key, value in sorted(task.metadata.items()):
                print(f"{indent}  {MAGENTA}{key}{RESET}: {value}")
                
        # Add a separator line between tasks for better readability
        print("")

    # Add a helpful note about task numbers
    print(f"{GRAY}Note: You can use task numbers with commands like 'done' and 'pri'.{RESET}")
    print(f"{GRAY}      For example: 'ptodo done 3' or 'ptodo pri 2 A'{RESET}")


def cmd_add(args: argparse.Namespace) -> None:
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
        priority=args.priority,
        creation_date=date.today() if args.date else None,
    )

    tasks.append(task)
    write_tasks(tasks, todo_file, git_service)
    print(f"Added: {serialize_task(task)}")


def cmd_done(args: argparse.Namespace) -> None:
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
        return

    if 1 <= args.task_number <= len(tasks):
        task = tasks[args.task_number - 1]
        task.complete()

        write_tasks(tasks, todo_file, git_service)
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
    git_service = GitService(todo_file.parent)
    tasks = read_tasks(todo_file, git_service)

    if not tasks:
        print("No tasks found.")
        return

    if 1 <= args.task_number <= len(tasks):
        task = tasks[args.task_number - 1]
        original = serialize_task(task)
        task.priority = args.priority

        write_tasks(tasks, todo_file, git_service)
        print(f"Updated: {original} → {serialize_task(task)}")
    else:
        print(f"Error: Task number {args.task_number} out of range (1-{len(tasks)}).")


def cmd_archive(_: argparse.Namespace) -> None:
    """
    Move completed tasks to the done.txt file.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    done_file = get_done_file_path()

    tasks = read_tasks(todo_file, git_service)
    done_tasks = read_tasks(done_file, git_service)

    # Find completed tasks
    completed_tasks = [t for t in tasks if t.completed]
    incomplete_tasks = [t for t in tasks if not t.completed]

    if not completed_tasks:
        print("No completed tasks to archive.")
        return

    # Add completed tasks to done.txt
    done_tasks.extend(completed_tasks)
    write_tasks(done_tasks, done_file, git_service)

    # Remove completed tasks from todo.txt
    write_tasks(incomplete_tasks, todo_file, git_service)

    print(f"Archived {len(completed_tasks)} completed task(s).")


def cmd_projects(_: argparse.Namespace) -> None:
    """
    List all projects in the todo.txt file.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    tasks = read_tasks(todo_file, git_service)

    # Get all projects
    all_projects: set[str] = set()
    for task in tasks:
        all_projects.update(task.projects)

    # Print projects
    if not all_projects:
        print("No projects found.")
        return

    print("Projects:")
    for project in sorted(all_projects):
        print(f"  {project}")


def cmd_contexts(_: argparse.Namespace) -> None:
    """
    List all contexts in the todo.txt file.

    Args:
        _: (Unused) Command-line arguments
    """
    todo_file = get_todo_file_path()
    git_service = GitService(todo_file.parent)
    tasks = read_tasks(todo_file, git_service)

    # Get all contexts
    all_contexts: set[str] = set()
    for task in tasks:
        all_contexts.update(task.contexts)

    # Print contexts
    if not all_contexts:
        print("No contexts found.")
        return

    print("Contexts:")
    for context in sorted(all_contexts):
        print(f"  {context}")


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

    done_file = get_done_file_path()
    
    if git_service.sync(commit_message="Manual sync of todo files"):
        print("Successfully synced changes with remote repository.")
    else:
        print("No changes to sync or sync failed.")


def cmd_show(args: argparse.Namespace) -> None:
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
        return

    if 1 <= args.task_number <= len(tasks):
        task = tasks[args.task_number - 1]
        
        # Build a detailed view of the task
        print(f"Task #{args.task_number}:")
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
    else:
        print(f"Error: Task number {args.task_number} out of range (1-{len(tasks)}).")



def main() -> None:
    """
    Main function for the todo.txt CLI.

    Parses command-line arguments and dispatches to the appropriate handler.
    """
    parser = argparse.ArgumentParser(
        description=f"Command-line todo.txt manager v{VERSION}",
        epilog="""
Examples:\n
  ptodo list                    # List all incomplete tasks\n
  ptodo add "Buy groceries"     # Add a new task\n
  ptodo done 1                  # Mark task #1 as complete\n
  ptodo show 2                  # Show details for task #2\n
\n
Environment Variables:\n
  PTODO_DIRECTORY               # Directory for todo files (default: ~/.ptodo)\n
  TODO_FILE                     # Path to todo.txt file (default: ~/.ptodo/todo.txt)\n
  DONE_FILE                     # Path to done.txt file (default: ~/.ptodo/done.txt)\n
""",
    )
    # Add version flag
    parser.add_argument('--version', '-v', action='version', version=f'ptodo {VERSION}',
                        help='Show the version number and exit')
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list command
    list_parser = subparsers.add_parser(
        "list",
        help="List tasks",
        description="List and filter tasks from your todo.txt file",
        epilog="""
Examples:
  ptodo list                    # List all incomplete tasks
  ptodo list --all              # List all tasks (including completed)
  ptodo list --completed        # List only completed tasks
  ptodo list --project home     # List tasks for project 'home' (+home)
  ptodo list --context phone    # List tasks with context 'phone' (@phone)
  ptodo list --priority A       # List tasks with priority A
""",
    )
    list_parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Show all tasks, including completed ones",
    )
    list_parser.add_argument(
        "--completed", "-c", action="store_true", help="Show only completed tasks"
    )
    list_parser.add_argument("--project", "-p", help="Filter by project")
    list_parser.add_argument("--context", "-@", help="Filter by context")
    list_parser.add_argument("--priority", help="Filter by priority (A-Z)")

    # add command
    add_parser = subparsers.add_parser(
        "add",
        help="Add a new task",
        description="Add a new task to your todo.txt file",
        epilog="""
Examples:
  ptodo add "Buy groceries"                      # Add a simple task
  ptodo add "Buy milk @store +shopping"          # Add task with context and project
  ptodo add "Call mom" --priority A              # Add high priority task
  ptodo add "Submit report" --date               # Add task with creation date
  ptodo add "Email client @work +project"        # Add task with context and project
""",
    )
    add_parser.add_argument("text", help="Task description")
    add_parser.add_argument("--priority", "-p", help="Task priority (A-Z)")
    add_parser.add_argument(
        "--date", "-d", action="store_true", help="Add creation date"
    )

    # done command
    done_parser = subparsers.add_parser(
        "done",
        help="Mark a task as done",
        description="Mark a task as completed by its number",
        epilog="""
Examples:
  ptodo done 1                  # Mark task #1 as complete
Note: Task numbers are shown when listing tasks with 'ptodo list'
""",
    )
    done_parser.add_argument(
        "task_number", type=int, help="Task number to mark as done"
    )

    # pri command
    pri_parser = subparsers.add_parser(
        "pri",
        help="Set task priority",
        description="Set or change the priority of a task",
        epilog="""
Examples:
  ptodo pri 2 A                 # Set task #2 to priority A
  ptodo pri 3 C                 # Set task #3 to priority C
Note: Priorities range from A (highest) to Z (lowest)
""",
    )
    pri_parser.add_argument("task_number", type=int, help="Task number to prioritize")
    pri_parser.add_argument("priority", help="Priority (A-Z)")

    # archive command
    subparsers.add_parser(
        "archive",
        help="Move completed tasks to done.txt",
        description="Move all completed tasks from todo.txt to done.txt",
        epilog="""
Examples:
  ptodo archive                 # Move all completed tasks to done.txt
Note: This is useful for cleaning up your todo.txt file after completing tasks
""",
    )

    # projects command
    subparsers.add_parser(
        "projects",
        help="List all projects",
        description="List all projects (+project) found in your tasks",
        epilog="""
Examples:
  ptodo projects                # List all projects in todo.txt
Note: Projects in todo.txt format are words prefixed with '+' like +home
""",
    )

    # contexts command
    subparsers.add_parser(
        "contexts",
        help="List all contexts",
        description="List all contexts (@context) found in your tasks",
        epilog="""
Examples:
  ptodo contexts                # List all contexts in todo.txt
Note: Contexts in todo.txt format are words prefixed with '@' like @phone
""",
    )

    # show command
    show_parser = subparsers.add_parser(
        "show",
        help="Show detailed information for a task",
        description="Show detailed information for a task by its number",
        epilog="""
Examples:
  ptodo show 2                  # Show detailed information for task #2
Note: Task numbers are shown when listing tasks with 'ptodo list'
""",
    )
    show_parser.add_argument(
        "task_number", type=int, help="Task number to show details for"
    )

    # git commands
    git_parser = subparsers.add_parser(
        "git",
        help="Git operations for synchronizing tasks",
        description="Git operations for synchronizing tasks across devices",
    )
    git_subparsers = git_parser.add_subparsers(dest="git_command", help="Git command to run")
    
    # git init command
    git_subparsers.add_parser(
        "init",
        help="Initialize a git repository",
        description="Initialize a git repository in the ptodo directory for task synchronization",
    )
    
    # git remote command
    git_remote_parser = git_subparsers.add_parser(
        "remote",
        help="Add or update a git remote",
        description="Add or update a git remote for task synchronization",
    )
    git_remote_parser.add_argument("name", help="Remote name (e.g., 'origin')")
    git_remote_parser.add_argument("url", help="Remote URL (e.g., 'https://github.com/user/repo.git')")
    
    # git sync command
    git_subparsers.add_parser(
        "sync",
        help="Sync changes with the remote repository",
        description="Pull changes from the remote repository, then push local changes",
    )

    # Parse command-line arguments
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
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "git":
        if args.git_command == "init":
            cmd_git_init(args)
        elif args.git_command == "remote":
            cmd_git_remote(args)
        elif args.git_command == "sync":
            cmd_git_sync(args)
        else:
            parser.parse_args(["git", "-h"])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
