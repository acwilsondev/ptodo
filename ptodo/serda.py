import datetime
import os
import re
from dataclasses import dataclass, field


@dataclass
class Task:
    """Represents a single task in todo.txt format."""

    completed: bool = False
    priority: str | None = None
    completion_date: datetime.date | None = None
    creation_date: datetime.date | None = None
    description: str = ""
    projects: set[str] = field(default_factory=set)
    contexts: set[str] = field(default_factory=set)
    metadata: dict[str, str] = field(default_factory=dict)
    effort: str | None = None

    def __post_init__(self) -> None:
        """Ensure priority is None for completed tasks."""
        if self.completed:
            self.priority = None

    def complete(self) -> None:
        """Mark the task as completed and set completion date to today."""
        # If there's a priority, store it in metadata before removing it
        if self.priority:
            self.metadata["pri"] = self.priority

        self.completed = True
        self.completion_date = datetime.date.today()
        self.priority = None

    def __str__(self) -> str:
        """Return the string representation in todo.txt format."""
        parts = []
        if self.completed:
            parts.append("x")
        if self.priority:
            parts.append(f"({self.priority})")
        if self.completed and self.completion_date:
            parts.append(self.completion_date.strftime("%Y-%m-%d"))
        if self.creation_date:
            parts.append(self.creation_date.strftime("%Y-%m-%d"))
        parts.append(self.description)
        parts.extend(f"+{p}" for p in sorted(self.projects))
        parts.extend(f"@{c}" for c in sorted(self.contexts))
        if self.effort:
            parts.append(f"effort:{self.effort}")
        for k, v in sorted(self.metadata.items()):
            parts.append(f"{k}:{v}")
        return " ".join(parts)

    def recur(self) -> "Task | None":
        """Create a recurring task."""
        if not self.validate_recurrence():
            return None
        due_date = parse_date(self.metadata["due"])
        # We know due_date is not None because validate_recurrence checks it
        assert due_date is not None, "Due date should be valid at this point"
        recur_days = int(self.metadata["recur"])
        next_due_date = due_date + datetime.timedelta(days=recur_days)
        while next_due_date <= datetime.date.today():
            next_due_date += datetime.timedelta(days=recur_days)
        return Task(
            completed=False,
            priority=self.priority,
            creation_date=datetime.date.today(),
            description=self.description,
            projects=self.projects.copy(),
            contexts=self.contexts.copy(),
            metadata=self.metadata.copy(),
            effort=self.effort,
        )

    def validate_recurrence(self) -> bool:
        """Validate the recurrence metadata."""
        # Return False early if there's no recurrence metadata
        if "recur" not in self.metadata:
            return False

        # Validate recurrence value is a positive digit
        if not self.metadata["recur"].isdigit():
            print(f"Invalid recur value: {self.metadata['recur']}")
            return False
        if int(self.metadata["recur"]) < 1:
            print(f"Invalid recur value: {self.metadata['recur']}")
            return False

        # Validate due date exists and is valid
        if "due" not in self.metadata:
            print(f"No due date found for the task: {self.description}")
            return False
        parsed_date = parse_date(self.metadata["due"])
        if parsed_date is None:
            print(f"Invalid due date format: {self.metadata['due']}")
            return False

        return True


def parse_date(date_str: str) -> datetime.date | None:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        if date_str and re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass
    return None


def serialize_date(date_obj: datetime.date | None) -> str:
    """Convert a date object to YYYY-MM-DD format."""
    if date_obj:
        return date_obj.strftime("%Y-%m-%d")
    return ""


def parse_task(line: str) -> Task:
    """Parse a todo.txt line into a Task object.

    Parse order:
    1. Completion status
    2. Priority
    3. Completion date (if completed)
    4. Creation date
    5. Description and metadata
    """
    # Initialize with default values
    task = Task()

    # Skip empty lines
    if not line.strip():
        return task

    # Check for completion
    if line.startswith("x "):
        task.completed = True
        line = line[2:]  # Remove the 'x ' prefix

    parts = line.strip().split(" ")

    # Parse priority if present (A) to (Z)
    if parts and re.match(r"^\([A-Z]\)$", parts[0]):
        task.priority = parts[0][1]  # Extract the letter
        parts.pop(0)

    # Parse dates in order: first completion date (if completed), then creation date
    remaining_parts_index = 0

    # If task is completed, first date might be completion date
    if task.completed and len(parts) >= 1 and parse_date(parts[0]):
        task.completion_date = parse_date(parts[0])
        remaining_parts_index = 1

    # Next possible date could be creation date
    if len(parts) > remaining_parts_index and parse_date(parts[remaining_parts_index]):
        task.creation_date = parse_date(parts[remaining_parts_index])
        remaining_parts_index += 1

    # Rest of the line is the description and metadata
    description_parts = []

    for part in parts[remaining_parts_index:]:
        # Parse projects
        if part.startswith("+") and len(part) > 1:
            task.projects.add(part[1:])
        # Parse contexts
        elif part.startswith("@") and len(part) > 1:
            task.contexts.add(part[1:])
        # Parse metadata (key:value)
        elif ":" in part and part.index(":") > 0:
            key, value = part.split(":", 1)
            # Handle effort as a dedicated field
            if key == "effort":
                task.effort = value
            else:
                task.metadata[key] = value
        else:
            description_parts.append(part)

    task.description = " ".join(description_parts).strip()

    return task


def read_tasks(filename: str) -> list[Task]:
    """Read tasks from a todo.txt file."""
    tasks: list[Task] = []

    if not os.path.exists(filename):
        return tasks

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                tasks.append(parse_task(line))

    return tasks


def append_task(filename: str, task: Task) -> None:
    """Append a task to a todo.txt file."""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{task}\n")


def today_string() -> str:
    """Return today's date in YYYY-MM-DD format."""
    return datetime.date.today().strftime("%Y-%m-%d")


def create_task(
    description: str,
    priority: str | None = None,
    add_creation_date: bool = True,
    projects: list[str] | None = None,
    contexts: list[str] | None = None,
    metadata: dict[str, str] | None = None,
    effort: str | None = None,
) -> Task:
    """Create a new task with the given parameters."""
    task = Task(
        completed=False,
        priority=priority,
        completion_date=None,
        creation_date=datetime.date.today() if add_creation_date else None,
        description=description,
        projects=set(projects) if projects else set(),
        contexts=set(contexts) if contexts else set(),
        metadata=metadata or {},
        effort=effort,
    )
    return task
