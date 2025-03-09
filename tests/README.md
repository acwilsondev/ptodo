# Running Tests for ptodo

This directory contains tests for the `ptodo` application, a command-line tool for managing todo.txt files.

## Requirements

Before running tests, make sure you have the following installed:
- Python 3.6 or higher
- pytest
- pytest-cov (for code coverage reports)

## Running Tests

### Run all tests

From the project root directory:

```bash
pytest
```

### Run tests with verbose output

```bash
pytest -v
```

### Run specific test file

```bash
pytest tests/test_serda.py
```

### Run tests with coverage report

```bash
pytest --cov=ptodo
```

For HTML coverage report:

```bash
pytest --cov=ptodo --cov-report=html
```

The HTML report will be generated in the `htmlcov` directory.

## Test Structure

- `test_serda.py`: Tests for the serialization/deserialization functionality
- `test_app.py`: Tests for the command-line application functionality
- `conftest.py`: Common fixtures and test configurations

## Adding New Tests

When adding new tests:
1. Create a file named `test_*.py` in the tests directory
2. Import the modules you want to test
3. Write test functions prefixed with `test_`

Example:
```python
def test_something():
    assert True
```

## Continuous Integration

These tests are designed to be run in a CI/CD pipeline. Make sure all tests pass before submitting pull requests.

