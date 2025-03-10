import os
from pathlib import Path


def get_ptodo_directory():
    """
    Get the directory where ptodo files are stored.
    Uses $PTODO_DIRECTORY environment variable if set, otherwise defaults to ~/.ptodo
    """
    ptodo_dir = os.environ.get("PTODO_DIRECTORY")
    if ptodo_dir:
        directory = Path(ptodo_dir)
    else:
        directory = Path.home() / ".ptodo"

    # Ensure the directory exists
    directory.mkdir(exist_ok=True)

    return directory
