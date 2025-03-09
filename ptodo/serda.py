import datetime
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, TextIO


@dataclass
class Task:
    """Represents a single task in todo.txt format."""

    description: str
    completed: bool = False
    priority: Optional[str] = None
    creation_date: Optional[datetime.date] = None
    completion_date: Optional[datetime.date] = None
    projects: Set[str] = None
    contexts: Set[str] = None
    metadata: Dict[str, str] = None

    def __post_init__(self):
        """Initialize default values for sets and dictionaries."""
        if self.projects is None:
            self.projects = set()
        if self.contexts is None:
            self.contexts = set()
        if self.metadata is None:
            self.metadata = {}

    def complete(self) -> None:
        """Mark the task as completed and set completion date to today."""
        self.completed = True
        self.completion_date = datetime.date.today()

    def __str__(self) -> str:
        """Return the string representation in todo.txt format."""
        return serialize_task(self)


def parse_date(date_str: str) -> Optional[datetime.date]:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        if date_str and re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass
    return None


def serialize_date(date_obj: Optional[datetime.date]) -> str:
    """Convert a date object to YYYY-MM-DD format."""
    if date_obj:
        return date_obj.strftime("%Y-%m-%d")
    return ""


def parse_task(line: str) -> Task:
    """Parse a todo.txt line into a Task object."""
    # Initialize with default values
    task = Task(description="")

    # Skip empty lines
    if not line.strip():
        return task

    # Check for completion
    if line.startswith("x "):
        task.completed = True
        line = line[2:]  # Remove the 'x ' prefix

    parts = line.strip().split(" ")
    remaining_parts = []

    # Parse priority if present (A) to (Z)
    if parts and re.match(r"^\([A-Z]\)$", parts[0]):
        task.priority = parts[0][1]  # Extract the letter
        parts.pop(0)

    # Parse dates
    date_index = 0

    # If task is completed, first date might be completion date
    if task.completed and len(parts) >= 1 and parse_date(parts[0]):
        task.completion_date = parse_date(parts[0])
        date_index = 1

    # Next possible date could be creation date
    if len(parts) > date_index and parse_date(parts[date_index]):
        task.creation_date = parse_date(parts[date_index])
        date_index += 1

    # Rest of the line is the description and metadata
    description_parts = []

    for part in parts[date_index:]:
        # Parse projects
        if part.startswith("+") and len(part) > 1:
            task.projects.add(part[1:])
        # Parse contexts
        elif part.startswith("@") and len(part) > 1:
            task.contexts.add(part[1:])
        # Parse metadata (key:value)
        elif ":" in part and part.index(":") > 0:
            key, value = part.split(":", 1)
            task.metadata[key] = value
        else:
            description_parts.append(part)

    task.description = " ".join(description_parts).strip()

    return task


def serialize_task(task: Task) -> str:
    """Convert a Task object to a todo.txt line."""
    parts = []

    # Add completion marker
    if task.completed:
        parts.append("x")

    # Add priority if present
    if task.priority:
        parts.append(f"({task.priority})")

    # Add completion date for completed tasks
    if task.completed and task.completion_date:
        parts.append(serialize_date(task.completion_date))

    # Add creation date if present
    if task.creation_date:
        parts.append(serialize_date(task.creation_date))

    # Add description
    parts.append(task.description)

    # Add projects
    for project in sorted(task.projects):
        parts.append(f"+{project}")

    # Add contexts
    for context in sorted(task.contexts):
        parts.append(f"@{context}")

    # Add metadata
    for key, value in sorted(task.metadata.items()):
        parts.append(f"{key}:{value}")

    return " ".join(parts)


def read_tasks(filename: str) -> List[Task]:
    """Read tasks from a todo.txt file."""
    tasks = []

    if not os.path.exists(filename):
        return tasks

    with open(filename, "r") as f:
        for line in f:
            if line.strip():
                tasks.append(parse_task(line))

    return tasks


def write_tasks(filename: str, tasks: List[Task]) -> None:
    """Write tasks to a todo.txt file."""
    with open(filename, "w") as f:
        for task in tasks:
            f.write(serialize_task(task) + "\n")


def append_task(filename: str, task: Task) -> None:
    """Append a task to a todo.txt file."""
    with open(filename, "a") as f:
        f.write(serialize_task(task) + "\n")


def today_string() -> str:
    """Return today's date in YYYY-MM-DD format."""
    return datetime.date.today().strftime("%Y-%m-%d")


def create_task(
    description: str,
    priority: Optional[str] = None,
    add_creation_date: bool = True,
    projects: List[str] = None,
    contexts: List[str] = None,
    metadata: Dict[str, str] = None,
) -> Task:
    """Create a new task with the given parameters."""
    task = Task(
        description=description,
        priority=priority,
        creation_date=datetime.date.today() if add_creation_date else None,
        projects=set(projects) if projects else set(),
        contexts=set(contexts) if contexts else set(),
        metadata=metadata or {},
    )
    return task
