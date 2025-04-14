#!/usr/bin/env python3

import os
import re
import datetime
import math
import shutil
from dateutil import parser
from statistics import mean, median
from collections import defaultdict

def get_todo_file_path():
    """Get the todo file path from environment variable"""
    todo_file = os.environ.get('TODO_FILE')
    if not todo_file:
        raise ValueError("$TODO_FILE environment variable not set")
    return todo_file

def parse_task_date(line):
    """Extract the date from a task line using regex"""
    # Match YYYY-MM-DD format after priority marker
    date_match = re.search(r'\([A-Z]\)\s+(\d{4}-\d{2}-\d{2})', line)
    if date_match:
        date_str = date_match.group(1)
        try:
            return parser.parse(date_str).date()
        except ValueError:
            return None
    return None

def is_completed_task(line):
    """Check if a task is completed (starts with 'x')"""
    return line.strip().startswith('x')

def calculate_task_age(task_date, current_date):
    """Calculate task age in days"""
    delta = current_date - task_date
    return delta.days

def calculate_average_task_age():
    """Calculate the average age of all active tasks"""
    todo_file_path = get_todo_file_path()
    current_date = datetime.date.today()
    
    with open(todo_file_path, 'r') as f:
        lines = f.readlines()
    
    task_ages = []
    for line in lines:
        if not is_completed_task(line):
            task_date = parse_task_date(line)
            if task_date:
                age = calculate_task_age(task_date, current_date)
                task_ages.append(age)
    
    if not task_ages:
        return 0
    
    return mean(task_ages), median(task_ages) if task_ages else 0, task_ages

def create_age_histogram(task_ages, max_bins=15):
    """Create a terminal-based histogram of task ages"""
    if not task_ages:
        return "No tasks with dates found."
    
    # Get terminal width
    term_width, _ = shutil.get_terminal_size((80, 20))
    hist_width = min(term_width - 20, 60)  # Reserve space for labels
    
    # Filter out extreme outliers for better visualization
    regular_tasks = [age for age in task_ages if age < 365]  # Tasks less than a year old
    outliers = [age for age in task_ages if age >= 365]
    
    if not regular_tasks:
        return "All tasks are older than 1 year, can't create meaningful histogram."
    
    # Create bins based on regular tasks
    max_age = max(regular_tasks)
    min_age = min(regular_tasks)
    
    # Create reasonable bin sizes (7 days = weekly)
    bin_size = 7
    num_bins = min(max_bins, math.ceil((max_age - min_age) / bin_size) + 1)
    
    # Create bins
    bins = defaultdict(int)
    for age in regular_tasks:
        bin_index = math.floor((age - min_age) / bin_size)
        bins[bin_index] += 1
    
    # Find the max count for scaling
    max_count = max(bins.values()) if bins else 0
    
    # Generate histogram
    result = ["", "Task Age Distribution (last year):"]
    result.append("=" * (hist_width + 20))
    
    for i in range(num_bins):
        bin_start = min_age + (i * bin_size)
        bin_end = min_age + ((i + 1) * bin_size) - 1
        count = bins[i]
        
        # Scale the bar length to fit terminal width
        bar_length = int((count / max_count) * hist_width) if max_count > 0 else 0
        bar = "█" * bar_length
        
        # Format the bin label
        bin_label = f"{bin_start:3d}-{bin_end:<3d} days:"
        
        # Add the histogram bar with count
        result.append(f"{bin_label} {bar} {count:2d}")
    
    result.append("=" * (hist_width + 20))
    
    # Add information about outliers
    if outliers:
        result.append(f"Outliers: {len(outliers)} task(s) older than 1 year")
        oldest = max(task_ages)
        result.append(f"Oldest task: {oldest} days ({oldest//365} years, {oldest%365} days)")
    
    return "\n".join(result)
def main():
    try:
        avg_age, med_age, task_ages = calculate_average_task_age()
        print(f"Average age of tasks: {avg_age:.1f} days")
        print(f"Median age of tasks: {med_age:.1f} days")
        
        # Additional stats
        todo_file_path = get_todo_file_path()
        current_date = datetime.date.today()
        
        with open(todo_file_path, 'r') as f:
            lines = f.readlines()
        
        active_tasks = [line for line in lines if not is_completed_task(line)]
        completed_tasks = [line for line in lines if is_completed_task(line)]
        
        print(f"Total tasks: {len(lines)}")
        print(f"Active tasks: {len(active_tasks)}")
        print(f"Completed tasks: {len(completed_tasks)}")
        
        # Age distribution
        task_dates = []
        for line in active_tasks:
            task_date = parse_task_date(line)
            if task_date:
                task_dates.append(task_date)
        
        if task_dates:
            oldest_date = min(task_dates)
            newest_date = max(task_dates)
            oldest_age = calculate_task_age(oldest_date, current_date)
            newest_age = calculate_task_age(newest_date, current_date)
            
            print(f"Oldest task: {oldest_age} days old (from {oldest_date})")
            print(f"Newest task: {newest_age} days old (from {newest_date})")
            
            # Add histogram visualization
            print("\n" + create_age_histogram(task_ages))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
