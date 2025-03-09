# ptodo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

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

`ptodo` provides an intuitive command-line interface for managing your tasks:

```bash
# Add a new task
ptodo add "Call mom"

# Add a task with priority, project, and context
ptodo add "(A) Call mom about dinner +Family @Phone"

# List all tasks
ptodo list

# List tasks filtered by project or context
ptodo list +Family
ptodo list @Phone

# Mark a task as completed
ptodo do 1

# Remove a task
ptodo rm 2

# Show help
ptodo --help
```

By default, `ptodo` looks for `todo.txt` and `done.txt` files in the current directory, but you can customize the location using environment variables:

```bash
export TODO_FILE=/path/to/your/todo.txt
export DONE_FILE=/path/to/your/done.txt
```

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

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests on [GitHub](https://github.com/awilsoncs/ptodo).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

