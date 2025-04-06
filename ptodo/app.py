import argparse
import sys
from typing import List, Optional

from .commands.config_commands import cmd_config
from .commands.git_commands import cmd_git_init, cmd_git_remote, cmd_git_sync
from .commands.organization_commands import (
    cmd_archive,
    cmd_contexts,
    cmd_project_mv,
    cmd_project_pri,
    cmd_project_rm,
    cmd_projects,
)
from .commands.task_commands import (
    cmd_add,
    cmd_await,
    cmd_done,
    cmd_due,
    cmd_edit,
    cmd_list,
    cmd_next,
    cmd_pri,
    cmd_rm,
    cmd_show,
    cmd_sort,
)
from .utils.deprecation import warn_deprecated_command

VERSION = "1.3.0"


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the ptodo application.

    Args:
        args: Command line arguments. Defaults to sys.argv[1:].

    Returns:
        Integer exit code.
    """
    if args is None:
        args = sys.argv[1:]

    # Create the top-level parser
    parser = argparse.ArgumentParser(description="Plain-text task management")
    parser.add_argument("--version", "-v", action="version", version=f"ptodo {VERSION}")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress informational output"
    )
    # Create subparsers for each command
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create tasks subparser with its own subcommands
    tasks_parser = subparsers.add_parser("tasks", help="Task operations")
    tasks_subparsers = tasks_parser.add_subparsers(
        dest="task_command", help="Task command to run"
    )

    # Add task subcommands
    # Tasks list command
    tasks_list_parser = tasks_subparsers.add_parser("list", help="List tasks")
    tasks_list_parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Show all tasks, including completed ones",
    )
    tasks_list_parser.add_argument(
        "--completed", "-c", action="store_true", help="Show only completed tasks"
    )
    tasks_list_parser.add_argument("--project", "-p", help="Filter by project")
    tasks_list_parser.add_argument("--context", "-@", help="Filter by context")
    tasks_list_parser.add_argument("--priority", help="Filter by priority (A-Z)")
    tasks_list_parser.add_argument(
        "--top",
        "-t",
        type=int,
        help="Limit display to the top N tasks after filtering",
    )

    # Tasks add command
    tasks_add_parser = tasks_subparsers.add_parser("add", help="Add a task")
    tasks_add_parser.add_argument("text", help="Task text")

    # Tasks done command
    tasks_done_parser = tasks_subparsers.add_parser("done", help="Mark tasks as done")
    tasks_done_parser.add_argument("task_ids", type=int, nargs="+", help="Task ID(s)")

    # Tasks remove command
    tasks_rm_parser = tasks_subparsers.add_parser(
        "rm", help="Remove a task without archiving"
    )
    tasks_rm_parser.add_argument("task_id", type=int, help="Task ID")

    # Tasks priority command
    tasks_pri_parser = tasks_subparsers.add_parser("pri", help="Set task priority")
    tasks_pri_parser.add_argument("task_id", type=int, help="Task ID")
    tasks_pri_parser.add_argument("priority", help="Priority (A-Z, or - to remove)")

    # Tasks show command
    tasks_show_parser = tasks_subparsers.add_parser("show", help="Show a task")
    tasks_show_parser.add_argument("task_id", type=int, help="Task ID")

    # Tasks sort command
    tasks_subparsers.add_parser("sort", help="Sort tasks by priority")

    # Tasks next command
    tasks_next_parser = tasks_subparsers.add_parser(
        "next", help="Show highest priority task"
    )
    tasks_next_parser.add_argument(
        "filters",
        nargs="*",
        help="Optional filters (+project or @context)"
    )

    # Tasks await command
    tasks_await_parser = tasks_subparsers.add_parser(
        "await", help="Add a waiting-for task with required due date"
    )
    tasks_await_parser.add_argument("description", help="Task description")
    tasks_await_parser.add_argument("due_date", help="Due date in YYYY-MM-DD format")
    tasks_await_parser.add_argument("--priority", "-p", help="Task priority (A-Z)")

    # Tasks edit command
    tasks_edit_parser = tasks_subparsers.add_parser(
        "edit", help="Open the todo file in your default editor"
    )
    tasks_edit_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational output"
    )

    # Tasks due command
    tasks_due_parser = tasks_subparsers.add_parser(
        "due", help="Show tasks due today or earlier"
    )
    tasks_due_parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress informational output",
    )
    tasks_due_parser.add_argument(
        "--soon",
        "-s",
        type=int,
        metavar="DAYS",
        help="Show tasks due within the specified number of days",
    )

    # List command (backward compatibility)
    list_parser = subparsers.add_parser("list", help="List tasks")
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
    list_parser.add_argument(
        "--top",
        "-t",
        type=int,
        help="Limit display to the top N tasks after filtering",
    )

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("text", help="Task text")

    # Done command
    done_parser = subparsers.add_parser("done", help="Mark tasks as done")
    done_parser.add_argument("task_ids", type=int, nargs="+", help="Task ID(s)")

    # Remove command
    rm_parser = subparsers.add_parser("rm", help="Remove a task without archiving")
    rm_parser.add_argument("task_id", type=int, help="Task ID")

    # Priority command
    pri_parser = subparsers.add_parser("pri", help="Set task priority")
    pri_parser.add_argument("task_id", type=int, help="Task ID")
    pri_parser.add_argument("priority", help="Priority (A-Z, or - to remove)")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show a task")
    show_parser.add_argument("task_id", type=int, help="Task ID")

    # Projects command
    subparsers.add_parser("projects", help="List projects")

    # Contexts command
    subparsers.add_parser("contexts", help="List contexts")

    # Archive command
    subparsers.add_parser("archive", help="Archive completed tasks")

    # Sort command
    subparsers.add_parser("sort", help="Sort tasks by priority")

    # Next command
    next_parser = subparsers.add_parser("next", help="Show highest priority task")
    next_parser.add_argument(
        "filters",
        nargs="*",
        help="Optional filters (+project or @context)"
    )

    # Await command
    await_parser = subparsers.add_parser(
        "await", help="Add a waiting-for task with required due date"
    )
    await_parser.add_argument("description", help="Task description")
    await_parser.add_argument("due_date", help="Due date in YYYY-MM-DD format")
    await_parser.add_argument("--priority", "-p", help="Task priority (A-Z)")
    # Due command
    due_parser = subparsers.add_parser("due", help="Show tasks due today or earlier")
    due_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational output"
    )
    due_parser.add_argument(
        "--soon", "-s",
        type=int,
        metavar="DAYS",
        help="Show tasks due within the specified number of days"
    )
    # Git commands
    git_parser = subparsers.add_parser("git", help="Git operations")
    git_subparsers = git_parser.add_subparsers(
        dest="git_command", help="Git command to run"
    )

    git_subparsers.add_parser("init", help="Initialize Git repository")

    git_remote_parser = git_subparsers.add_parser(
        "remote", help="Show or set Git remote"
    )
    git_remote_parser.add_argument(
        "url", nargs="?", help="Remote URL (if provided, sets/updates the remote)"
    )

    git_sync_parser = git_subparsers.add_parser("sync", help="Sync with Git remote")
    git_sync_parser.add_argument("--message", "-m", help="Commit message")
    # Project commands
    project_parser = subparsers.add_parser("project", help="Project operations")
    project_subparsers = project_parser.add_subparsers(
        dest="project_command", help="Project command to run"
    )

    project_mv_parser = project_subparsers.add_parser("mv", help="Rename a project")
    project_mv_parser.add_argument("old_name", help="Current project name")
    project_mv_parser.add_argument("new_name", help="New project name")

    project_rm_parser = project_subparsers.add_parser(
        "rm", help="Remove a project from all tasks"
    )
    project_rm_parser.add_argument("name", help="Project name to remove")

    project_pri_parser = project_subparsers.add_parser(
        "pri", help="Set same priority for all tasks in a project"
    )
    project_pri_parser.add_argument("name", help="Project name")
    project_pri_parser.add_argument("priority", help="Priority (A-Z, or - to remove)")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(
        dest="config_command", help="Config command to run"
    )

    config_subparsers.add_parser("show", help="Show all configuration")

    config_get_parser = config_subparsers.add_parser(
        "get", help="Get a configuration value"
    )
    config_get_parser.add_argument("key", help="Configuration key")

    config_set_parser = config_subparsers.add_parser(
        "set", help="Set a configuration value"
    )
    config_set_parser.add_argument("key", help="Configuration key")
    config_set_parser.add_argument("value", help="Configuration value")

    config_subparsers.add_parser("reset", help="Reset configuration to defaults")

    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Open the todo file in your default editor")
    edit_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational output"
    )

    # Help command
    subparsers.add_parser("help", help="Show this help message")

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Dispatch to the appropriate command
    if parsed_args.command == "tasks":
        # Handle new tasks subcommands
        if parsed_args.task_command == "list":
            return int(cmd_list(parsed_args))
        elif parsed_args.task_command == "add":
            return int(cmd_add(parsed_args))
        elif parsed_args.task_command == "done":
            return int(cmd_done(parsed_args))
        elif parsed_args.task_command == "rm":
            return int(cmd_rm(parsed_args))
        elif parsed_args.task_command == "pri":
            return int(cmd_pri(parsed_args))
        elif parsed_args.task_command == "show":
            return int(cmd_show(parsed_args))
        elif parsed_args.task_command == "sort":
            return int(cmd_sort(parsed_args))
        elif parsed_args.task_command == "next":
            return int(cmd_next(parsed_args))
        elif parsed_args.task_command == "await":
            return int(cmd_await(parsed_args))
        elif parsed_args.task_command == "edit":
            return int(cmd_edit(parsed_args))
        elif parsed_args.task_command == "due":
            return int(cmd_due(parsed_args))
        else:
            parser.print_help()
            return 1
    # Handle backward compatibility commands
    elif parsed_args.command == "list":
        warn_deprecated_command("ptodo list", "ptodo tasks list")
        return int(cmd_list(parsed_args))
    elif parsed_args.command == "add":
        warn_deprecated_command("ptodo add", "ptodo tasks add")
        return int(cmd_add(parsed_args))
    elif parsed_args.command == "done":
        warn_deprecated_command("ptodo done", "ptodo tasks done")
        return int(cmd_done(parsed_args))
    elif parsed_args.command == "rm":
        warn_deprecated_command("ptodo rm", "ptodo tasks rm")
        return int(cmd_rm(parsed_args))
    elif parsed_args.command == "pri":
        warn_deprecated_command("ptodo pri", "ptodo tasks pri")
        return int(cmd_pri(parsed_args))
    elif parsed_args.command == "show":
        warn_deprecated_command("ptodo show", "ptodo tasks show")
        return int(cmd_show(parsed_args))
    elif parsed_args.command == "projects":
        return int(cmd_projects(parsed_args))
    elif parsed_args.command == "contexts":
        return int(cmd_contexts(parsed_args))
    elif parsed_args.command == "archive":
        return int(cmd_archive(parsed_args))
    elif parsed_args.command == "sort":
        warn_deprecated_command("ptodo sort", "ptodo tasks sort")
        return int(cmd_sort(parsed_args))
    elif parsed_args.command == "git" and parsed_args.git_command == "init":
        return int(cmd_git_init(parsed_args))
    elif parsed_args.command == "git" and parsed_args.git_command == "remote":
        return int(cmd_git_remote(parsed_args))
    elif parsed_args.command == "git" and parsed_args.git_command == "sync":
        return int(cmd_git_sync(parsed_args))
    elif parsed_args.command == "next":
        warn_deprecated_command("ptodo next", "ptodo tasks next")
        return int(cmd_next(parsed_args))
    elif parsed_args.command == "await":
        warn_deprecated_command("ptodo await", "ptodo tasks await")
        return int(cmd_await(parsed_args))
    elif parsed_args.command == "due":
        warn_deprecated_command("ptodo due", "ptodo tasks due")
        return int(cmd_due(parsed_args))
    elif parsed_args.command == "config":
        return int(cmd_config(parsed_args))
    elif parsed_args.command == "project" and parsed_args.project_command == "mv":
        return int(cmd_project_mv(parsed_args))
    elif parsed_args.command == "project" and parsed_args.project_command == "rm":
        return int(cmd_project_rm(parsed_args))
    elif parsed_args.command == "project" and parsed_args.project_command == "pri":
        return int(cmd_project_pri(parsed_args))
    elif parsed_args.command == "edit":
        warn_deprecated_command("ptodo edit", "ptodo tasks edit")
        return int(cmd_edit(parsed_args))
    elif parsed_args.command == "help":
        parser.print_help()
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
