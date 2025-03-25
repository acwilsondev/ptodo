# ptodo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A powerful, lightweight command-line interface for managing your tasks in plaintext using the Todo.txt format.

## Introduction

`ptodo` is a Python-based CLI tool that helps you manage your to-do list using the simple and effective [Todo.txt](http://todotxt.org/) format. Keep your tasks in a plain text file that's portable, future-proof, and can be edited with any text editor, while still having powerful task management capabilities at your fingertips.

## Installation

```bash
# Install from PyPI
pip install ptodo

# Or install directly from GitHub
pip install git+https://github.com/awilsoncs/ptodo.git
```

## Usage

`ptodo` provides an intuitive command-line interface for managing your tasks. You can use either the traditional command style or the new subcommand structure:

```bash
# Add a new task (two equivalent ways)
ptodo add "Call mom"                                    # Traditional style
ptodo tasks add "Call mom"                              # New subcommand style

# Add a task with priority, project, and context (two equivalent ways)
ptodo add "(A) Call mom about dinner +Family @Phone"    # Traditional style
ptodo tasks add "(A) Call mom about dinner +Family @Phone"  # New subcommand style

# List all tasks (two equivalent ways)
ptodo list                                              # Traditional style
ptodo tasks list                                        # New subcommand style

# List tasks filtered by project or context (two equivalent ways)
ptodo list +Family                                      # Traditional style
ptodo tasks list +Family                                # New subcommand style

# Mark a task as completed (two equivalent ways)
ptodo do 1                                              # Traditional style
ptodo tasks done 1                                      # New subcommand style

# Remove a task (two equivalent ways)
ptodo rm 2                                              # Traditional style
ptodo tasks rm 2                                        # New subcommand style

# Open your todo file in your default editor (two equivalent ways)
ptodo edit                                              # Traditional style
ptodo tasks edit                                        # New subcommand style

# Configure ptodo settings
ptodo config set default_priority A
ptodo config get default_priority
ptodo config list

# Git integration
ptodo git commit "Updated tasks for project"
ptodo git push
ptodo git pull

# Show help
ptodo --help
ptodo tasks --help
```

### Command Structure

The new "tasks" command groups all task-related commands under a single namespace:

```
ptodo tasks <command> [options]
```

Available task commands:
- `add`: Add a new task
- `list`: List and filter tasks
- `done` (or `do`): Mark task(s) as completed
- `rm`: Remove task(s)
- `pri`: Set task priority
- `show`: Display detailed task information
- `edit`: Open tasks in your editor

### Backward Compatibility

For backward compatibility, all original command forms (e.g., `ptodo add`) continue to work alongside the new subcommand structure (`ptodo tasks add`). This allows you to gradually transition to the new command style without breaking existing scripts or workflows.

### Command Deprecation

While backward compatibility is maintained for now, the traditional command style (e.g., `ptodo add`) is deprecated and will display warnings when used. These commands will be removed in version 2.0, so it's recommended to transition to the new subcommand structure (e.g., `ptodo tasks add`).

You can control deprecation warnings using these environment variables:

| Variable | Description | Values |
|----------|-------------|--------|
| `PTODO_DEPRECATION_ENABLED` | Enable or disable deprecation warnings | `true` (default), `false`, `0`, `no`, `off` |
| `PTODO_DEPRECATION_WARNING_TYPE` | Control how deprecation warnings are displayed | `stderr` (default), `stdout`, `python`, `silent` |

Warning types:
- `stderr`: Display warnings to standard error (default)
- `stdout`: Display warnings to standard output
- `python`: Use Python's built-in warning system
- `silent`: Suppress all deprecation warnings

To disable deprecation warnings temporarily:

```bash
export PTODO_DEPRECATION_ENABLED=false
```

To disable them for a single command:

```bash
PTODO_DEPRECATION_ENABLED=false ptodo add "New task"
```

To change the warning type:

```bash
export PTODO_DEPRECATION_WARNING_TYPE=stdout
```

By default, `ptodo` looks for `todo.txt` and `done.txt` files in the current directory, but you can customize the location using environment variables:

```bash
export TODO_FILE=/path/to/your/todo.txt
export DONE_FILE=/path/to/your/done.txt
export PTODO_DIRECTORY=/path/to/your/todo/directory
```

The `PTODO_DIRECTORY` environment variable sets the base directory for all ptodo files when not explicitly specified with `TODO_FILE` or `DONE_FILE`.

## Features

- **Todo.txt Compatible**: Fully compatible with the Todo.txt format
- **Lightweight**: Minimal dependencies, fast performance
- **Task Properties**:
  - Priority levels (A-Z)
  - Creation and completion dates
  - Projects and contexts
  - Custom metadata
- **Powerful Filtering**: Filter tasks by priority, project, context, or completion status
- **Environment Variable Support**: Customize file locations via environment variables
- **Simple Plain Text Storage**: Tasks stored in human-readable text files
- **Editor Integration**: Open your todo files in your preferred editor
- **Git Integration**: Sync and manage your todo files with Git
- **Configuration System**: Customize ptodo behavior with persistent settings

## Todo.txt Format

The [Todo.txt](http://todotxt.org/) format is a simple, standards-based format for task management. Each task is a single line in a text file with the following optional components:

- `x` at the beginning marks a task as complete
- `(A)` sets a priority (can be A-Z)
- `2023-04-01` date format for creation and completion dates
- `+Project` adds a project tag
- `@Context` adds a context tag
- `key:value` adds metadata

Example:

```
x (A) 2023-04-01 2023-04-02 Complete the project documentation +Work @Computer due:2023-04-15
```

This represents a completed task with priority A, created on April 1, 2023, completed on April 2, 2023, with the project tag "Work", context tag "Computer", and a due date metadata.
88|

## Configuration

You can customize the behavior of `ptodo` using the built-in configuration system:

```bash
# Set a configuration value
ptodo config set default_priority A

# Get a configuration value
ptodo config get default_priority

# List all configuration settings
ptodo config list

# Reset a configuration value to default
ptodo config reset default_priority
```

Available configuration options include:

| Option | Description | Default |
|--------|-------------|---------|
| `default_priority` | Default priority for new tasks | None |
| `date_format` | Format for displaying dates | %Y-%m-%d |
| `auto_archive` | Automatically archive completed tasks | false |
| `editor` | Editor to use when editing tasks | $EDITOR or vi |
| `git_auto_commit` | Automatically commit changes | false |
| `git_auto_push` | Automatically push after commit | false |

## Git Integration

`ptodo` provides built-in Git integration to help you sync your tasks across multiple devices:

```bash
# Initialize Git repository in your todo directory
ptodo git init

# Commit changes with a message
ptodo git commit "Updated project tasks"

# Push changes to remote repository
ptodo git push

# Pull changes from remote repository
ptodo git pull

# View Git status
ptodo git status
```

The Git integration works with any Git remote, making it easy to synchronize your tasks using GitHub, GitLab, or any other Git hosting service.

## Advanced Usage

Here are some advanced examples of using `ptodo`:

```bash
# Filter tasks by multiple criteria (traditional and new style)
ptodo list +Project @Context due:today
ptodo tasks list +Project @Context due:today

# Add a task with a specific creation date (traditional and new style)
ptodo add "2023-05-01 Start new project +Work"
ptodo tasks add "2023-05-01 Start new project +Work"

# Add a task with custom metadata (traditional and new style)
ptodo add "Research API options +Dev due:2023-06-15 effort:medium"
ptodo tasks add "Research API options +Dev due:2023-06-15 effort:medium"

# Mark a task as completed and archive in one step (traditional and new style)
ptodo do 3 --archive
ptodo tasks done 3 --archive

# List tasks due today (traditional and new style)
ptodo list due:today
ptodo tasks list due:today

# List high priority tasks (traditional and new style)
ptodo list "(A)"
ptodo tasks list "(A)"

# Edit a specific task (traditional and new style)
ptodo edit 5
ptodo tasks edit 5

# Configure Git auto-sync
ptodo config set git_auto_commit true
ptodo config set git_auto_push true
```

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests on [GitHub](https://github.com/awilsoncs/ptodo).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

