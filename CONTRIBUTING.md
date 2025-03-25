# Contributing to ptodo

Thank you for your interest in contributing to ptodo! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Contributing to ptodo](#contributing-to-ptodo)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [Getting Started](#getting-started)
    - [Setting Up Development Environment](#setting-up-development-environment)
    - [Project Structure](#project-structure)
  - [Development Workflow](#development-workflow)
    - [Making Changes](#making-changes)
    - [Testing](#testing)
      - [Requirements](#requirements)
      - [Running Tests](#running-tests)
      - [Test Structure](#test-structure)
      - [Adding New Tests](#adding-new-tests)
      - [Continuous Integration](#continuous-integration)
    - [Code Style](#code-style)
    - [Command Documentation](#command-documentation)
    - [Git Commit Messages](#git-commit-messages)
  - [Development Principles](#development-principles)
    - [Backward Compatibility](#backward-compatibility)
    - [Configuration System](#configuration-system)
    - [Error Handling](#error-handling)
    - [User Feedback](#user-feedback)
  - [Submitting Contributions](#submitting-contributions)
    - [Issues](#issues)
    - [Pull Requests](#pull-requests)
  - [Release Process](#release-process)
  - [Using the Makefile](#using-the-makefile)
    - [Available Make Commands](#available-make-commands)
  - [Community](#community)

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Be respectful and inclusive
- Be patient and welcoming
- Be thoughtful
- Be collaborative
- Be open-minded

## Getting Started

### Setting Up Development Environment

1. **Fork the repository**
   - Visit the [ptodo repository](https://github.com/awilsoncs/ptodo) and click the "Fork" button

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR-USERNAME/ptodo.git
   cd ptodo
   ```

3. **Set up a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**

   ```bash
   # Using the Makefile (recommended)
   make setup

   # Or manually:
   pip install -e ".[dev]"
   pip install -e ".[test]"
   ```

### Project Structure

```bash
ptodo/
├── ptodo/                   # Source code
│   ├── __init__.py
│   ├── app.py              # Main application entry point
│   ├── serda.py            # Task serialization/deserialization
│   ├── config.py           # Configuration management
│   ├── utils.py            # Utility functions
│   ├── commands/           # Command implementations
│   │   ├── __init__.py
│   │   ├── task_commands.py # Task-related commands (add, list, done, etc.)
│   │   ├── config_commands.py # Configuration commands
│   │   └── git_commands.py  # Git integration commands
│   └── ...
├── tests/                  # Test files
│   ├── test_app.py
│   ├── test_serda.py
│   ├── test_commands/      # Command tests
│   │   ├── test_task_commands.py
│   │   ├── test_config_commands.py
│   │   └── test_git_commands.py
│   └── conftest.py         # Test fixtures and configurations
├── setup.py                # Package setup script
├── setup.cfg               # Configuration for tools
├── pytest.ini              # Pytest configuration
├── Makefile                # Build automation
├── README.md               # Project documentation
└── CONTRIBUTING.md         # This file
```

## Development Workflow

### Making Changes

1. **Create a new branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, concise, and well-documented code
   - Follow the code style guidelines
   - Add or update tests as necessary

3. **Commit your changes**

   ```bash
   git commit -m "Description of the changes"
   ```

   - Use clear and descriptive commit messages
   - Reference issue numbers if applicable (#123)

### Testing

We use pytest for testing. All code contributions should include tests.

For command implementations:

1. Test both successful command execution and error cases
2. Include integration tests when commands interact with each other
3. Test with various configuration settings
4. For Git integration, use a temporary repository for testing

#### Requirements

Before running tests, make sure you have the following installed:

- Python 3.6 or higher
- pytest
- pytest-cov (for code coverage reports)

These are automatically installed when you set up the development environment as described above.

#### Running Tests

From the project root directory:

```bash
# Run all tests using the Makefile (recommended)
make test

# Run tests with coverage report
make coverage

# Run specific tests directly
pytest tests/test_serda.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=ptodo --cov-report=html
```

The HTML coverage report will be generated in the `htmlcov` directory.

#### Test Structure

- `tests/test_serda.py`: Tests for the serialization/deserialization functionality
- `tests/test_app.py`: Tests for the command-line application functionality
- `tests/conftest.py`: Common fixtures and test configurations

Tests should be placed in the `tests/` directory and should follow the same structure as the source code.

#### Adding New Tests

When adding new tests:

1. Create a file named `test_*.py` in the tests directory
2. Import the modules you want to test
3. Write test functions prefixed with `test_`

Example:

```python
def test_something():
    assert True
```

#### Continuous Integration

These tests are designed to be run in a CI/CD pipeline. Make sure all tests pass before submitting pull requests.

For Git integration testing, we use a special fixture that creates a temporary Git repository:

```python
@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary Git repository for testing."""
    repo_dir = tmp_path / "git_repo"
    repo_dir.mkdir()
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)
    # Return the path to the repo
    return repo_dir
```

### Code Style

We follow PEP 8 guidelines for Python code. Some specific points:

- Use 4 spaces for indentation (no tabs)
- Use snake_case for variables and function names
- Use CamelCase for class names
- Maximum line length is 88 characters
- Include docstrings for all public functions, classes, and modules

You can check and format your code style with:

```bash
# Check code style (flake8, isort, black)
make lint

# Auto-format code using black and isort
make format

# Type checking with mypy (if needed)
mypy ptodo
```

### Command Documentation

All commands should be well-documented:

1. Include a clear, concise description in the command's help text
2. Document all command parameters with meaningful help messages
3. Include examples in the docstring
4. Document return values and exit codes
5. Update the README.md when adding new commands

Example:

```python
def cmd_edit(args):
    """
    Open the todo file in the system's default editor.
    
    Uses the EDITOR environment variable if available, otherwise falls back to vi.
    
    Parameters:
        args: Command-line arguments (not used)
        
    Returns:
        int: 0 on success, non-zero on error
        
    Example:
        ptodo edit
    """
    # Implementation here
```

### Git Commit Messages

We follow a structured commit message format:

1. Use the imperative mood ("Add feature" not "Added feature")
2. First line is a summary (max 50 characters)
3. Followed by a blank line
4. Detailed description if necessary (wrap at 72 characters)
5. Reference issues and pull requests

Format:
```
<type>(<scope>): <summary>

<description>

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc; no code change
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding tests
- `chore`: Updating build tasks, package manager configs, etc

Example:
```
feat(commands): add edit command for opening todo file

Implement a new 'edit' command that opens the todo file in the user's
default editor using the EDITOR environment variable.

Closes #456
```

## Development Principles

### Backward Compatibility

When making changes, consider backward compatibility:

1. Avoid breaking changes to existing functionality whenever possible
2. If a breaking change is necessary:
   - Document it clearly in the changelog
   - Increment the major version number (X.y.z → X+1.0.0)
   - Provide migration instructions for users
3. Maintain compatibility with existing data formats and files
   - If the format needs to change, provide a migration path
4. Deprecate features before removing them:
   - Mark features as deprecated with warnings
   - Keep deprecated features for at least one release cycle

### Configuration System

The configuration system follows these principles:

1. Configuration should be layered:
   - System-wide defaults
   - User configuration file (~/.config/ptodo/config)
   - Project-specific configuration
   - Environment variables
   - Command-line arguments (highest precedence)
2. All settings should have sensible defaults
3. Configuration should be self-documenting
4. New settings must include:
   - Clear description
   - Default value
   - Validation logic
   - Type annotation

When adding new configuration options:
```python
def get_config_schema():
    return {
        "todo_file": {
            "type": "string",
            "default": "todo.txt",
            "description": "The file to store todo items",
        },
        "new_option": {
            "type": "string",
            "default": "default_value",
            "description": "Description of the new option",
        }
    }
```

### Error Handling

Guidelines for error handling:

1. Catch specific exceptions, not generic ones
2. Provide clear, actionable error messages
3. Log errors with appropriate context for debugging
4. Use appropriate exit codes for different error types
5. Handle user errors gracefully with helpful suggestions

Example:
```python
try:
    with open(get_todo_file_path(), "r") as f:
        content = f.read()
except FileNotFoundError:
    print(f"Todo file not found. Create one with 'ptodo add <task>'")
    return 1
except PermissionError:
    print(f"Permission denied when trying to read todo file.")
    print(f"Check file permissions and try again.")
    return 2
```

### User Feedback

Principles for providing good user feedback:

1. Success messages should be concise and confirmatory
2. Error messages should be clear and actionable
3. For long-running operations, provide progress indication
4. Use consistent formatting for similar types of output
5. Consider color coding for different message types (success, warning, error)
6. Give context when operations fail

Example:
```python
def cmd_add(args):
    # Implementation...
    if success:
        print(f"Added task: {task}")
        return 0
    else:
        print(f"Failed to add task. Reason: {reason}")
        print(f"Suggestion: {suggestion}")
        return 1
```

## Submitting Contributions

### Issues

- Search for existing issues before creating a new one
- Use a clear and descriptive title
- Include as much relevant information as possible
- For bug reports, include:
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Version information (OS, Python, ptodo)
  - If possible, a minimal code example

### Pull Requests

1. **Push your changes to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a pull request**
   - Go to the [ptodo repository](https://github.com/awilsoncs/ptodo)
   - Click "Pull Requests" > "New Pull Request"
   - Select "compare across forks"
   - Select your fork and branch
   - Click "Create Pull Request"

3. **Pull Request Guidelines**
   - Use a clear and descriptive title
   - Reference any related issues (#123)
   - Describe the changes and why they're needed
   - Ensure all tests pass
   - Make sure code follows style guidelines
   - Update documentation if necessary

4. **Code Review Process**
   - Maintainers will review your code
   - Address any requested changes
   - Once approved, a maintainer will merge your contribution

## Release Process

The maintainers will handle the release process, which includes:

1. Versioning (following [Semantic Versioning](https://semver.org/))
2. Creating release notes
3. Publishing to PyPI

## Using the Makefile

The project includes a Makefile to simplify common development tasks. Using the Makefile ensures consistency and reduces the chance of errors when running development commands.

To see all available commands:

```bash
make help
```

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install development dependencies |
| `make test` | Run tests with pytest |
| `make coverage` | Run tests with coverage report |
| `make format` | Format code using black and isort |
| `make build` | Build the package |
| `make install` | Install the package |
| `make uninstall` | Uninstall the package |
| `make lint` | Run linting checks (flake8, isort, black) |
| `make check` | Run both linting and tests to verify code quality |
| `make clean` | Clean up build artifacts |
| `make help` | Show help message with all available commands |

Using these Makefile commands instead of direct tool invocation ensures consistent behavior across different development environments.

## Community

- GitHub Issues: For bug reports, feature requests, and discussion
- Pull Requests: For contributing code and documentation

Thank you for contributing to ptodo!
