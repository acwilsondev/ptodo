import os
import sys
import unittest
from datetime import date, datetime, timedelta

# Add the parent directory to the path so we can import the ptodo package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Import our modules after path modification
from ptodo.core.serda import Task, parse_task, parse_date  # noqa: E402


class TestTask(unittest.TestCase):
    def test_task_initialization(self) -> None:
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

    def test_default_values(self) -> None:
        """Test that default values are set correctly."""
        task = Task(description="Simple task")

        self.assertEqual(task.description, "Simple task")
        self.assertIsNone(task.priority)
        self.assertIsNone(task.creation_date)
        self.assertFalse(task.completed)
        self.assertIsNone(task.completion_date)
        self.assertEqual(task.projects, set())
        self.assertEqual(task.contexts, set())

    def test_complete_task(self) -> None:
        """Test marking a task as complete."""
        task = Task(description="Write tests", priority="A")
        self.assertFalse(task.completed)

        # Priority should be included in the string representation before completion
        self.assertEqual(str(task), "(A) Write tests")
        self.assertEqual(task.priority, "A")

        # Mark as complete
        task.complete()
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completion_date)
        self.assertEqual(task.completion_date, date.today())

        # Priority should be removed when task is completed
        # Priority should be removed from priority field and stored in metadata
        self.assertIsNone(task.priority)
        self.assertEqual(
            task.metadata.get("pri"), "A"
        )  # Original priority preserved in metadata
        self.assertEqual(
            str(task), f"x {date.today().strftime('%Y-%m-%d')} Write tests pri:A"
        )

    def test_complete_task_removes_priority(self) -> None:
        """Test that priority is removed when a task is completed."""
        task = Task(
            description="Task with priority",
            priority="B",
            creation_date=date(2023, 1, 1),
        )

        # Check initial state
        self.assertEqual(task.priority, "B")
        self.assertFalse(task.completed)
        self.assertEqual(str(task), "(B) 2023-01-01 Task with priority")

        # Mark as complete
        task.complete()

        # Priority should be removed from priority field and stored in metadata
        self.assertIsNone(task.priority)
        self.assertTrue(task.completed)
        self.assertEqual(
            task.metadata.get("pri"), "B"
        )  # Original priority preserved in metadata

        # String representation should not contain priority prefix but should include metadata
        serialized = str(task)
        self.assertEqual(
            serialized,
            f"x {date.today().strftime('%Y-%m-%d')} 2023-01-01 Task with priority pri:B",
        )
        self.assertNotIn("(B)", serialized)

    def test_priority_removed_on_completion(self) -> None:
        """Test priority removal behavior when tasks are completed."""
        # Create two similar tasks
        task1 = Task(description="First task", priority="A")
        task2 = Task(description="Second task", priority="B")

        # Verify initial state
        self.assertEqual(task1.priority, "A")
        self.assertEqual(task2.priority, "B")
        self.assertEqual(str(task1), "(A) First task")
        self.assertEqual(str(task2), "(B) Second task")

        # Complete only task1
        task1.complete()

        # task1's priority should be None, task2's should remain unchanged
        # task1's priority should be None and stored in metadata, task2's should remain unchanged
        self.assertIsNone(task1.priority)
        self.assertEqual(
            task1.metadata.get("pri"), "A"
        )  # Original priority preserved in metadata
        self.assertEqual(task2.priority, "B")

        # Verify string representations
        self.assertEqual(
            str(task1), f"x {date.today().strftime('%Y-%m-%d')} First task pri:A"
        )
        self.assertEqual(str(task2), "(B) Second task")
        # Now complete task2
        # Now complete task2
        task2.complete()
        self.assertIsNone(task2.priority)
        self.assertEqual(
            task2.metadata.get("pri"), "B"
        )  # Original priority preserved in metadata
        self.assertEqual(
            str(task2), f"x {date.today().strftime('%Y-%m-%d')} Second task pri:B"
        )

    def test_complete_task_preserves_priority_in_metadata(self) -> None:
        """Test that priority is preserved in metadata when a task is completed."""
        # Create a task with priority
        task = Task(description="Important task", priority="A")

        # Verify initial state
        self.assertEqual(task.priority, "A")
        self.assertEqual(task.metadata, {})
        self.assertEqual(str(task), "(A) Important task")

        # Complete the task
        task.complete()

        # Verify priority is removed and stored in metadata
        self.assertIsNone(task.priority)
        self.assertEqual(task.metadata.get("pri"), "A")

        # Verify string representation includes the metadata
        serialized = str(task)
        self.assertEqual(
            serialized, f"x {date.today().strftime('%Y-%m-%d')} Important task pri:A"
        )
        self.assertNotIn("(A)", serialized)

    def test_recur_sets_due_date_correctly(self) -> None:
        """Test that recurring a task sets the due date correctly."""
        # Create a task with recurrence and due date
        today = date.today()
        due_date = today - timedelta(days=1)  # Yesterday
        recur_days = 7
        
        task = Task(
            description="Recurring task",
            priority="A",
            metadata={
                "due": due_date.strftime("%Y-%m-%d"),
                "recur": str(recur_days)
            }
        )
        
        # Call recur() to create a new recurring task
        new_task = task.recur()
        
        # Verify the new task is created
        self.assertIsNotNone(new_task)
        
        # Verify due date is set and calculated correctly
        self.assertIn("due", new_task.metadata)
        
        # Expected due date should be recur_days days from the original due date
        # Expected due date should be recur_days days from the original due date
        # but not earlier than tomorrow
        expected_due_date = due_date + timedelta(days=recur_days)
        while expected_due_date <= today:
            expected_due_date += timedelta(days=recur_days)
        actual_due_date = parse_date(new_task.metadata["due"])
        self.assertIsNotNone(actual_due_date)
        self.assertEqual(actual_due_date, expected_due_date)

    def test_recur_preserves_priority_format(self) -> None:
        """Test that recurring a completed task handles priority format correctly."""
        # Create a task with priority, recurrence and due date
        today = date.today()
        due_date = today - timedelta(days=1)  # Yesterday
        recur_days = 7
        
        task = Task(
            description="Priority recurring task",
            priority="A",
            metadata={
                "due": due_date.strftime("%Y-%m-%d"),
                "recur": str(recur_days)
            }
        )
        
        # Verify the original task has priority in (A) format
        self.assertEqual(task.priority, "A")
        self.assertNotIn("pri", task.metadata)
        self.assertIn("(A)", str(task))
        
        # Complete the task (which should store priority in metadata)
        task.complete()
        
        # Verify the completed task has priority in metadata
        self.assertIsNone(task.priority)
        self.assertEqual(task.metadata["pri"], "A")
        self.assertNotIn("(A)", str(task))
        self.assertIn("pri:A", str(task))
        
        # Call recur() to create a new recurring task
        new_task = task.recur()
        
        # Verify the new task is created
        self.assertIsNotNone(new_task)
        
        # Verify the new task has priority in (A) format, not in metadata
        self.assertEqual(new_task.priority, "A")
        self.assertNotIn("pri", new_task.metadata)
        self.assertIn("(A)", str(new_task))
        self.assertNotIn("pri:A", str(new_task))


class TestSerialization(unittest.TestCase):
    def test_serialize_simple_task(self) -> None:
        """Test serialization of a simple task."""
        task = Task(description="Simple task")
        serialized = str(task)
        self.assertEqual(serialized, "Simple task")

    def test_serialize_task_with_priority(self) -> None:
        """Test serialization of a task with priority."""
        task = Task(description="Task with priority", priority="A")
        serialized = str(task)
        self.assertEqual(serialized, "(A) Task with priority")

    def test_serialize_task_with_dates(self) -> None:
        """Test serialization of a task with creation date."""
        task = Task(description="Task with date", creation_date=date(2023, 1, 1))
        serialized = str(task)
        self.assertEqual(serialized, "2023-01-01 Task with date")

    def test_serialize_completed_task(self) -> None:
        """Test serialization of a completed task."""
        task = Task(
            description="Completed task",
            completed=True,
            completion_date=date(2023, 1, 15),
        )
        serialized = str(task)
        self.assertEqual(serialized, "x 2023-01-15 Completed task")

    def test_serialize_task_with_projects_and_contexts(self) -> None:
        """Test serialization of a task with projects and contexts."""
        task = Task(
            description="Task with metadata",
            projects={"work", "report"},
            contexts={"office", "computer"},
        )
        serialized = str(task)
        self.assertEqual(
            serialized, "Task with metadata +report +work @computer @office"
        )

    def test_serialize_complex_task(self) -> None:
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
        serialized = str(task)
        self.assertEqual(
            serialized, "x 2023-01-15 2023-01-01 Complex task +ptodo @coding"
        )


class TestParsing(unittest.TestCase):
    def test_parse_simple_task(self) -> None:
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

    def test_parse_task_with_priority(self) -> None:
        """Test parsing of a task with priority."""
        task_str = "(A) Task with priority"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Task with priority")
        self.assertEqual(task.priority, "A")

    def test_parse_task_with_dates(self) -> None:
        """Test parsing of a task with creation date."""
        task_str = "2023-01-01 Task with date"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Task with date")
        self.assertEqual(task.creation_date, date(2023, 1, 1))

    def test_parse_completed_task(self) -> None:
        """Test parsing of a completed task."""
        task_str = "x 2023-01-15 Completed task"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Completed task")
        self.assertTrue(task.completed)
        self.assertEqual(task.completion_date, date(2023, 1, 15))

    def test_parse_completed_task_with_creation_date(self) -> None:
        """Test parsing of a completed task with creation date."""
        task_str = "x 2023-01-15 2023-01-01 Completed task with creation date"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Completed task with creation date")
        self.assertTrue(task.completed)
        self.assertEqual(task.completion_date, date(2023, 1, 15))
        self.assertEqual(task.creation_date, date(2023, 1, 1))

    def test_parse_task_with_projects_and_contexts(self) -> None:
        """Test parsing of a task with projects and contexts."""
        task_str = "Task with metadata +work +report @office @computer"
        task = parse_task(task_str)

        self.assertEqual(task.description, "Task with metadata")
        self.assertEqual(task.projects, {"work", "report"})
        self.assertEqual(task.contexts, {"office", "computer"})

    def test_parse_complex_task(self) -> None:
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
