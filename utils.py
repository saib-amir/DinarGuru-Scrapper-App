import json
import csv
import os
from pathlib import Path


def get_downloads_dir() -> str:
    """Get the OS downloads directory."""
    return str(Path.home() / "Downloads")


def download_json(posts: list[dict]) -> str:
    """
    Save a list of dictionaries as a JSON file.

    Args:
        posts: List of dictionaries with the same keys.

    Returns:
        The file path of the created JSON file.
    """
    downloads_dir = get_downloads_dir()
    os.makedirs(downloads_dir, exist_ok=True)

    file_path = os.path.join(downloads_dir, "posts.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4, ensure_ascii=False)

    return file_path


def download_csv(posts: list[dict]) -> str:
    """
    Save a list of dictionaries as a CSV file.

    Args:
        posts: List of dictionaries with the same keys.

    Returns:
        The file path of the created CSV file.
    """
    downloads_dir = get_downloads_dir()
    os.makedirs(downloads_dir, exist_ok=True)

    file_path = os.path.join(downloads_dir, "posts.csv")

    if not posts:
        with open(file_path, "w", encoding="utf-8") as f:
            pass
        return file_path

    fieldnames = list(posts[0].keys())

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)

    return file_path
