#!/usr/bin/env python3

import argparse
import sys

from ptodo.commands.task_commands import cmd_list, cmd_add, cmd_done, cmd_pri, cmd_show
from ptodo.commands.organization_commands import cmd_projects, cmd_contexts, cmd_archive
from ptodo.commands.git_commands import cmd_git_init, cmd_git_remote, cmd_git_sync
from ptodo.commands.config_commands import cmd_config

VERSION = "0.1.0"

def main():
    parser = argparse.ArgumentParser(description='ptodo: A simple todo.txt manager')
    parser.add_argument('--version', action='version', version=f'ptodo {VERSION}')

    subparsers = parser.add_subparsers(dest='command', help='Commands')
    subparsers.required = True

    # List command
    list_parser = subparsers.add_parser('list', aliases=['ls'], help='List tasks')
    list_parser.add_argument('--project', '-p', help='Filter by project')
    list_parser.add_argument('--context', '-c', help='Filter by context')
    list_parser.add_argument('--priority', '-P', help='Filter by priority')
    list_parser.add_argument('--completed', '-C', action='store_true', help='Show only completed tasks')
    list_parser.add_argument('--all', '-a', action='store_true', help='Show all tasks, including completed ones')
    list_parser.set_defaults(func=cmd_list)

    # Add command
    add_parser = subparsers.add_parser('add', aliases=['a'], help='Add a task')
    add_parser.add_argument('task', help='Task description')
    add_parser.set_defaults(func=cmd_add)

    # Done command
    done_parser = subparsers.add_parser('done', aliases=['do'], help='Mark a task as done')
    done_parser.add_argument('task_num', type=int, help='Task number')
    done_parser.set_defaults(func=cmd_done)

    # Priority command
    pri_parser = subparsers.add_parser('pri', aliases=['p'], help='Set priority')
    pri_parser.add_argument('task_num', type=int, help='Task number')
    pri_parser.add_argument('priority', help='Priority (A-Z)')
    pri_parser.set_defaults(func=cmd_pri)

    # Show command
    show_parser = subparsers.add_parser('show', aliases=['s'], help='Show a task')
    show_parser.add_argument('task_num', type=int, help='Task number')
    show_parser.set_defaults(func=cmd_show)

    # Projects command
    projects_parser = subparsers.add_parser('projects', help='List projects')
    projects_parser.set_defaults(func=cmd_projects)

    # Contexts command
    contexts_parser = subparsers.add_parser('contexts', help='List contexts')
    contexts_parser.set_defaults(func=cmd_contexts)

    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Archive completed tasks')
    archive_parser.set_defaults(func=cmd_archive)

    # Git commands
    git_init_parser = subparsers.add_parser('git-init', help='Initialize a git repository')
    git_init_parser.set_defaults(func=cmd_git_init)

    git_remote_parser = subparsers.add_parser('git-remote', help='Set the git remote')
    git_remote_parser.add_argument('remote', help='Git remote URL')
    git_remote_parser.set_defaults(func=cmd_git_remote)

    git_sync_parser = subparsers.add_parser('git-sync', help='Sync with git remote')
    git_sync_parser.set_defaults(func=cmd_git_sync)

    # Config command
    config_parser = subparsers.add_parser('config', help='View or edit configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Config commands')
    config_subparsers.required = True

    # Config show command
    config_show_parser = config_subparsers.add_parser('show', help='Show all configuration')
    config_show_parser.set_defaults(func=cmd_config)

    # Config get command
    config_get_parser = config_subparsers.add_parser('get', help='Get a configuration value')
    config_get_parser.add_argument('key', help='Configuration key (e.g., todo_filename)')
    config_get_parser.set_defaults(func=cmd_config)

    # Config set command
    config_set_parser = config_subparsers.add_parser('set', help='Set a configuration value')
    config_set_parser.add_argument('key', help='Configuration key (e.g., todo_filename)')
    config_set_parser.add_argument('value', help='Configuration value')
    config_set_parser.set_defaults(func=cmd_config)

    # Config reset command
    config_reset_parser = config_subparsers.add_parser('reset', help='Reset configuration to defaults')
    config_reset_parser.set_defaults(func=cmd_config)

    args = parser.parse_args()

    try:
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\nOperation canceled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

