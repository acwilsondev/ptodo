"""
Command module for the ptodo CLI application.

This module organizes commands into logical groups and exposes them through a consistent namespace.
All commands can be imported directly from the commands module, e.g.:
from ptodo.commands import cmd_list, cmd_add, etc.
"""

# Task management commands
from .task_commands import (
    cmd_list,
    cmd_add,
    cmd_done,
    cmd_pri,
    cmd_show,
)

# Organization commands
from .organization_commands import (
    cmd_projects,
    cmd_contexts,
    cmd_archive,
)

# Git integration commands
from .git_commands import (
    cmd_git_init,
    cmd_git_remote,
    cmd_git_sync,
)

# Configuration commands
from .config_commands import (
    cmd_config,
)

# Export all commands for direct import from commands module
__all__ = [
    # Task management commands
    'cmd_list',
    'cmd_add',
    'cmd_done',
    'cmd_pri',
    'cmd_show',
    
    # Organization commands
    'cmd_projects',
    'cmd_contexts',
    'cmd_archive',
    
    # Git integration commands
    'cmd_git_init',
    'cmd_git_remote',
    'cmd_git_sync',
    
    # Configuration commands
    'cmd_config',
]

# The above imports and __all__ declaration make all command functions
# directly available when importing from ptodo.commands, e.g.:
# from ptodo.commands import cmd_list, cmd_add
#
# This allows for a clean import interface while maintaining 
# modular organization of the codebase.

