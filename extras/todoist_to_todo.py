#!/usr/bin/env python3
"""
Todoist to Todo.txt Converter

This script converts Todoist CSV backup files to todo.txt format and adds them
to your todo.txt file using the 'ptodo' command-line tool.

Purpose:
    - Imports tasks from Todoist CSV backup files into todo.txt format
    - Preserves project structure, priority levels, and context tags
    - Provides detailed logs of the conversion process

Usage:
    python todoist_to_todo.py PATH_TO_BACKUP_DIRECTORY

    Where PATH_TO_BACKUP_DIRECTORY is the folder containing your Todoist
    CSV backup files (e.g., ~/Downloads/Todoist_Backup_2023-01-01).

Requirements:
    - Python 3.6+
    - ptodo command-line tool installed and accessible in your PATH

Conversion Details:
    - Todoist priorities (1-4) are converted to todo.txt priorities (A-D)
    - Project names are extracted from CSV filenames and added as +project_tag
    - Context tags (@home, @work, etc.) are preserved
    - Completed tasks are included in the conversion process
    - Provides a detailed summary of processed and skipped items

Output:
    The script will print detailed logs of the conversion process, including:
    - CSV headers and sample rows for debugging
    - Each task's conversion details
    - A summary of total rows processed, skipped, and tasks added
    - Potential issues if no tasks were added
"""

import os
import csv
import re
import subprocess
import argparse
from pathlib import Path


def extract_project_name(filename):
    """Extract project name from the CSV filename."""
    # Pattern matches "Project Name [RANDOM_ID].csv"
    match = re.match(r'(.*?)\s*\[[^\]]+\]\.csv$', filename)
    if match:
        return match.group(1).strip()
    return os.path.splitext(filename)[0]  # Fallback to filename without extension


def convert_priority(todoist_priority):
    """Convert Todoist priority (4-1) to todo.txt priority (A-D)."""
    try:
        priority = int(todoist_priority)
        # Todoist: 1=highest, 4=lowest
        # todo.txt: A=highest, D=lowest
        priorities = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
        return priorities.get(priority, None)
    except (ValueError, TypeError):
        return None


def process_csv_files(backup_dir):
    """Process all CSV files in the backup directory."""
    backup_path = Path(backup_dir).expanduser()
    
    if not backup_path.exists():
        print(f"Error: Directory not found: {backup_path}")
        return
    
    csv_files = [f for f in backup_path.glob('*.csv')]
    if not csv_files:
        print(f"No CSV files found in {backup_path}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    
    tasks_added = 0
    rows_processed = 0
    rows_skipped = 0
    for csv_file in csv_files:
        project_name = extract_project_name(csv_file.name)
        print(f"Processing project: {project_name}")
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Print header for debugging
            fieldnames = reader.fieldnames
            print(f"\nCSV Headers for {csv_file.name}:")
            print(", ".join(fieldnames if fieldnames else ["No headers found"]))
            
            sample_row_printed = False
            
            for row in reader:
                rows_processed += 1
                
                # Print a sample row for debugging (just the first row)
                if not sample_row_printed:
                    print(f"\nSample row from {csv_file.name}:")
                    for key, value in row.items():
                        print(f"  {key}: {value}")
                    sample_row_printed = True
                
                # Debug info about current row
                row_type = row.get('TYPE', 'unknown')
                checked_status = row.get('CHECKED', 'unknown')
                print(f"\nProcessing row {rows_processed}: TYPE={row_type}, CHECKED={checked_status}")
                
                # Removed the skip condition for debugging
                # (Original code would skip if TYPE != 'task' or CHECKED == 'yes')
                
                content = row.get('CONTENT', '')
                if not content:
                    print(f"  Skipping row {rows_processed}: Empty content")
                    rows_skipped += 1
                    continue
                
                # Convert priority
                raw_priority = row.get('PRIORITY', '4')
                priority = convert_priority(raw_priority)
                print(f"  Priority: Todoist={raw_priority}, todo.txt={priority if priority else 'None'}")
                
                # Extract existing context tags from content (like @computer, @home)
                context_tags = re.findall(r'@[^\s]+', content)
                print(f"  Content: {content}")
                print(f"  Context tags: {context_tags if context_tags else 'None'}")
                
                # Clean the content (remove context tags)
                clean_content = re.sub(r'@[^\s]+', '', content).strip()
                print(f"  Clean content: {clean_content}")
                
                # Build the todo.txt task
                todo_task = []
                
                # Add priority if available
                if priority:
                    todo_task.append(f"({priority})")
                
                # Add content
                todo_task.append(clean_content)
                # Add project tag based on CSV filename
                project_tag = f"+{project_name.replace(' ', '_')}"
                todo_task.append(project_tag)
                print(f"  Project tag: {project_tag}")
                todo_task.append(f"+{project_name.replace(' ', '_')}")
                
                # Add context tags
                todo_task.extend(context_tags)
                
                # Build the final task string
                task_str = " ".join(todo_task)
                print(f"  Final task: {task_str}")
                
                # Add task using ptodo command
                try:
                    result = subprocess.run(
                        ["ptodo", "add", task_str],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    tasks_added += 1
                    print(f"  Added: {task_str}")
                except subprocess.CalledProcessError as e:
                    print(f"  Error adding task: {task_str}")
                    print(f"  {e.stderr.strip()}")
    
    print(f"\nSummary:")
    print(f"  Total rows processed: {rows_processed}")
    print(f"  Total rows skipped: {rows_skipped}")
    print(f"  Total tasks added: {tasks_added}")
    
    if tasks_added == 0:
        print("\nPossible issues why no tasks were added:")
        print("1. The CSV files might not have the expected structure or column names")
        print("2. All tasks might be having empty content")
        print("3. There might be an issue with the 'ptodo add' command")
        print("Check the debugging output above for more details.")


def main():
    parser = argparse.ArgumentParser(description="Convert Todoist backup CSV files to todo.txt format")
    parser.add_argument(
        "backup_dir", 
        help="Path to the Todoist backup directory containing CSV files"
    )
    args = parser.parse_args()
    
    process_csv_files(args.backup_dir)


if __name__ == "__main__":
    main()

