import os
import sys
import unittest
from datetime import date

# Add the parent directory to the path so we can import the ptodo package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Import our modules after path modification
from ptodo.serda import Task, parse_task, serialize_task  # noqa: E402


class TestTask(unittest.TestCase):
    def test_task_initialization(self):
        """Test that a Task object can be created with various properties."""
        task = Task(
            description="Buy milk",
            priority="A",
            creation_date=date(2023, 1, 1),
            completed=False,
            completion_date=None,
            projects={"grocery"},
            contexts={"errands"},
        )

        self.assertEqual(task.description, "Buy milk")
        self.assertEqual(task.priority, "A")
        self.assertEqual(task.creation_date, date(2023, 1, 1))
        self.assertFalse(task.completed)
        self.assertIsNone(task.completion_date)
        self.assertEqual(task.projects, {"grocery"})
        self.assertEqual(task.contexts, {"errands"})

    def test_default_values(self):
        """Test that default values are set correctly."""
        task = Task(description="Simple task")

        self.assertEqual(task.description, "Simple task")
        self.assertIsNone(task.priority)
        self.assertIsNone(task.creation_date)
        self.assertFalse(task.completed)
        self.assertIsNone(task.completion_date)
        self.assertEqual(task.projects, set())
        self.assertEqual(task.contexts, set())

    def test_complete_task(self):
        """Test marking a task as complete."""
        task = Task(description="Write tests")
        self.assertFalse(task.completed)

        # Mark as complete
        task.complete()
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completion_date)
        self.assertEqual(task.completion_date, date.today())


class TestSerialization(unittest.TestCase):
    def test_serialize_simple_task(self):
        """Test serialization of a simple task."""
        task = Task(description="Simple task")
        serialized = serialize_task(task)
        self.assertEqual(serialized, "Simple task")

    def test_serialize_task_with_priority(self):
        """Test serialization of a task with priority."""
        task = Task(description="Task with priority", priority="A")
        serialized = serialize_task(task)
        self.assertEqual(serialized, "(A) Task with priority")

    def test_serialize_task_with_dates(self):
        """Test serialization of a task with creation date."""
        task = Task(description="Task with date", creation_date=date(2023, 1, 1))
        serialized = serialize_task(task)
        self.assertEqual(serialized, "2023-01-01 Task with date")

    def test_serialize_completed_task(self):
        """Test serialization of a completed task."""
        task = Task(
            description="Completed task",
            completed=True,
            completion_date=date(2023, 1, 15),
        )
        serialized = serialize_task(task)
        self.assertEqual(serialized, "x 2023-01-15 Completed task")

    def test_serialize_task_with_projects_and_contexts(self):
        """Test serialization of a task with projects and contexts."""
        task = Task(
            description="Task with metadata",
            projects={"work", "report"},
            contexts={"office", "computer"},
        )
        serialized = serialize_task(task)
        self.assertEqual(
            serialized, "Task with metadata +report +work @computer @office"
        )

    def test_serialize_complex_task(self):
        """Test serialization of a complex task with all attributes."""
        task = Task(
            description="Complex task",
            priority="B",
            creation_date=date(2023, 1, 1),
            completed=True,
            completion_date=date(2023, 1, 15),
            projects={"ptodo"},
            contexts={"coding"},
        )
        serialized = serialize_task(task)
        self.assertEqual(
            serialized, "x (B) 2023-01-15 2023-01-01 Complex task +ptodo @coding"
        )


class TestParsing(unittest.TestCase):
    def test_parse_simple_task(self):
        """Test parsing of a simple task."""
        task_str = "Simple task"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Simple task")
        self.assertIsNone(task.priority)
        self.assertIsNone(task.creation_date)
        self.assertFalse(task.completed)
        self.assertIsNone(task.completion_date)
        self.assertEqual(task.projects, set())
        self.assertEqual(task.contexts, set())

    def test_parse_task_with_priority(self):
        """Test parsing of a task with priority."""
        task_str = "(A) Task with priority"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Task with priority")
        self.assertEqual(task.priority, "A")

    def test_parse_task_with_dates(self):
        """Test parsing of a task with creation date."""
        task_str = "2023-01-01 Task with date"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Task with date")
        self.assertEqual(task.creation_date, date(2023, 1, 1))

    def test_parse_completed_task(self):
        """Test parsing of a completed task."""
        task_str = "x 2023-01-15 Completed task"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Completed task")
        self.assertTrue(task.completed)
        self.assertEqual(task.completion_date, date(2023, 1, 15))

    def test_parse_completed_task_with_creation_date(self):
        """Test parsing of a completed task with creation date."""
        task_str = "x 2023-01-15 2023-01-01 Completed task with creation date"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Completed task with creation date")
        self.assertTrue(task.completed)
        self.assertEqual(task.completion_date, date(2023, 1, 15))
        self.assertEqual(task.creation_date, date(2023, 1, 1))

    def test_parse_task_with_projects_and_contexts(self):
        """Test parsing of a task with projects and contexts."""
        task_str = "Task with metadata +work +report @office @computer"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Task with metadata")
        self.assertEqual(task.projects, {"work", "report"})
        self.assertEqual(task.contexts, {"office", "computer"})

    def test_parse_complex_task(self):
        """Test parsing of a complex task with all attributes."""
        task_str = "x (B) 2023-01-15 2023-01-01 Complex task +ptodo @coding"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Complex task")
        self.assertEqual(task.priority, "B")
        self.assertEqual(task.creation_date, date(2023, 1, 1))
        self.assertTrue(task.completed)
        self.assertEqual(task.completion_date, date(2023, 1, 15))
        self.assertEqual(task.projects, {"ptodo"})
        self.assertEqual(task.contexts, {"coding"})


if __name__ == "__main__":
    unittest.main()
