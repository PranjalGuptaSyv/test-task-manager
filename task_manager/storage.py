import json
from pathlib import Path
from typing import List

from task_manager.models import Task

STORAGE_FILE = Path.home() / ".task_manager_data.json"


def load_tasks() -> List[Task]:
    if not STORAGE_FILE.exists():
        return []
    with open(STORAGE_FILE) as f:
        return [Task.from_dict(d) for d in json.load(f)]


def save_tasks(tasks: List[Task]) -> None:
    with open(STORAGE_FILE, "w") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)


def next_id(tasks: List[Task]) -> int:
    return max((t.id for t in tasks), default=0) + 1
