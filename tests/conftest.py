import os
import tempfile
from datetime import date
import pytest
from pathlib import Path

from ptodo.serda import Task


@pytest.fixture
def temp_todo_file():
    """Create a temporary todo.txt file for testing."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    yield Path(path)
    # Cleanup after test
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def temp_done_file():
    """Create a temporary done.txt file for testing."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    yield Path(path)
    # Cleanup after test
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_tasks():
    """Return a list of sample Task objects for testing."""
    return [
        Task(description="Buy milk", priority="A"),
        Task(description="Call mom", creation_date=date.today()),
        Task(description="Write report", projects={"work"}, contexts={"office"}),
        Task(description="Go running", contexts={"health"}, completed=True),
        Task(
            description="Send email", 
            priority="B", 
            projects={"work", "communication"}, 
            contexts={"office"}
        ),
    ]


@pytest.fixture
def populated_todo_file(temp_todo_file, sample_tasks):
    """Create a todo.txt file populated with sample tasks."""
    with open(temp_todo_file, "w") as f:
        for task in sample_tasks:
            if not task.completed:
                f.write(f"{str(task)}\n")
    return temp_todo_file


@pytest.fixture
def populated_done_file(temp_done_file, sample_tasks):
    """Create a done.txt file populated with completed sample tasks."""
    with open(temp_done_file, "w") as f:
        for task in sample_tasks:
            if task.completed:
                f.write(f"{str(task)}\n")
    return temp_done_file


@pytest.fixture
def mock_user_input(monkeypatch):
    """Mock user input for testing interactive features."""
    inputs = []
    
    def mock_input(prompt=""):
        if not inputs:
            return ""
        return inputs.pop(0)
    
    def set_inputs(new_inputs):
        nonlocal inputs
        inputs = new_inputs.copy()
    
    monkeypatch.setattr("builtins.input", mock_input)
    return set_inputs


# Configure pytest to show more info on test failures
def pytest_configure(config):
    config.option.verbose = 2
    config.option.showlocals = True

