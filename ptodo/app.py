import argparse
import sys
from typing import List, Optional

from .commands.config_commands import cmd_config
from .commands.git_commands import cmd_git_init, cmd_git_remote, cmd_git_sync
from .commands.organization_commands import cmd_archive, cmd_contexts, cmd_projects
from .commands.task_commands import cmd_add, cmd_done, cmd_list, cmd_pri, cmd_show

VERSION = "0.2.0"


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
    parser.add_argument("--version", action="version", version=f"ptodo {VERSION}")

    # Create subparsers for each command
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
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

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("text", help="Task text")

    # Done command
    done_parser = subparsers.add_parser("done", help="Mark a task as done")
    done_parser.add_argument("task_id", type=int, help="Task ID")

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

    # Git commands
    subparsers.add_parser("git-init", help="Initialize Git repository")

    git_remote_parser = subparsers.add_parser("git-remote", help="Set Git remote")
    git_remote_parser.add_argument("url", help="Remote URL")

    git_sync_parser = subparsers.add_parser("git-sync", help="Sync with Git remote")
    git_sync_parser.add_argument("--message", "-m", help="Commit message")

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

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Dispatch to the appropriate command
    if parsed_args.command == "list":
        return cmd_list(parsed_args)
    elif parsed_args.command == "add":
        return cmd_add(parsed_args)
    elif parsed_args.command == "done":
        return cmd_done(parsed_args)
    elif parsed_args.command == "pri":
        return cmd_pri(parsed_args)
    elif parsed_args.command == "show":
        return cmd_show(parsed_args)
    elif parsed_args.command == "projects":
        return cmd_projects(parsed_args)
    elif parsed_args.command == "contexts":
        return cmd_contexts(parsed_args)
    elif parsed_args.command == "archive":
        return cmd_archive(parsed_args)
    elif parsed_args.command == "git-init":
        return cmd_git_init(parsed_args)
    elif parsed_args.command == "git-remote":
        return cmd_git_remote(parsed_args)
    elif parsed_args.command == "git-sync":
        return cmd_git_sync(parsed_args)
    elif parsed_args.command == "config":
        return cmd_config(parsed_args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
