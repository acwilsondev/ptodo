"""
Command module for the ptodo CLI application.

This module organizes commands into logical groups and exposes them through a consistent namespace.
All commands can be imported directly from the commands module, e.g.:
from ptodo.commands import cmd_list, cmd_add, etc.
"""

# Configuration commands
from .config_commands import (
    cmd_config,
)

# Git integration commands
from .git_commands import (
    cmd_git_init,
    cmd_git_remote,
    cmd_git_sync,
)

# Organization commands
from .organization_commands import (
    cmd_archive,
    cmd_contexts,
    cmd_project_mv,
    cmd_project_pri,
    cmd_project_rm,
    cmd_projects,
)

# Task management commands
from .task_commands import (
    cmd_add,
    cmd_done,
    cmd_list,
    cmd_next,
    cmd_pri,
    cmd_rm,
    cmd_show,
)

# Export all commands for direct import from commands module
__all__ = [
    # Task management commands
    "cmd_list",
    "cmd_add",
    "cmd_done",
    "cmd_next",
    "cmd_pri",
    "cmd_rm",
    "cmd_show",
    # Organization commands
    "cmd_projects",
    "cmd_contexts",
    "cmd_archive",
    "cmd_project_pri",
    "cmd_project_mv",
    "cmd_project_rm",
    # Git commands
    "cmd_git_remote",
    "cmd_git_sync",
    "cmd_git_init",
    # Configuration commands
    "cmd_config",
]

# The above imports and __all__ declaration make all command functions
# directly available when importing from ptodo.commands, e.g.:
# from ptodo.commands import cmd_list, cmd_add
#
# This allows for a clean import interface while maintaining
# modular organization of the codebase.
