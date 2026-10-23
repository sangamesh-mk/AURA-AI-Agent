
import json
from pathlib import Path
from datetime import datetime

TASK_FILE = Path(__file__).with_name("aura_tasks.json")


def load_tasks():
    """Load saved task history from disk."""
    if not TASK_FILE.exists():
        return []

    try:
        with TASK_FILE.open("r", encoding="utf-8") as file:
            tasks = json.load(file)
        return tasks if isinstance(tasks, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_task(task):
    """Append a task and persist the complete history."""
    tasks = load_tasks()
    tasks.append(task)

    with TASK_FILE.open("w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2, ensure_ascii=False)


def migrate_session_tasks(tasks):
    """Save existing session records that are not already persisted."""
    saved = load_tasks()
    known = {
        (task.get("goal"), task.get("created"))
        for task in saved
    }

    for task in tasks:
        key = (task.get("goal"), task.get("created"))
        if key not in known:
            saved.append(task)
            known.add(key)

    with TASK_FILE.open("w", encoding="utf-8") as file:
        json.dump(saved, file, indent=2, ensure_ascii=False)

    return saved
