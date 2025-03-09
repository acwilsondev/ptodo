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
    - [Code Style](#code-style)
  - [Submitting Contributions](#submitting-contributions)
    - [Issues](#issues)
    - [Pull Requests](#pull-requests)
  - [Release Process](#release-process)
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
   pip install -e ".[dev]"
   # If the above doesn't work, try:
   pip install -e .
   pip install pytest pytest-cov flake8 mypy
   ```

### Project Structure

```
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

We use pytest for testing. All code contributions should include tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=ptodo

# Run a specific test file
pytest tests/test_specific_file.py
```

Tests should be placed in the `tests/` directory and should follow the same structure as the source code.

### Code Style

We follow PEP 8 guidelines for Python code. Some specific points:

- Use 4 spaces for indentation (no tabs)
- Use snake_case for variables and function names
- Use CamelCase for class names
- Maximum line length is 88 characters
- Include docstrings for all public functions, classes, and modules

You can check your code style with:

```bash
# Check code style with flake8
flake8 ptodo tests

# Type checking with mypy
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

## Community

- GitHub Issues: For bug reports, feature requests, and discussion
- Pull Requests: For contributing code and documentation

Thank you for contributing to ptodo!
