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
├── ptodo/            # Source code
│   ├── __init__.py
│   ├── cli.py        # Command-line interface
│   ├── serda.py      # Task serialization/deserialization
│   └── ...
├── tests/            # Test files
├── setup.py          # Package setup script
├── setup.cfg         # Configuration for tools
├── pytest.ini        # Pytest configuration
├── Makefile          # Build automation
├── README.md         # Project documentation
└── CONTRIBUTING.md   # This file
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
