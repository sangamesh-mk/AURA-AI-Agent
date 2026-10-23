
import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "aura_memory.json"


def load_memories():
    """Load saved memories from the local JSON file."""
    if not MEMORY_FILE.exists():
        return {}

    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (json.JSONDecodeError, OSError):
        return {}


def save_memory(key: str, value: str):
    """Save or update one memory."""
    memories = load_memories()
    memories[key] = value

    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(memories, file, indent=4, ensure_ascii=False)

    return f"Saved memory: {key}"


def get_memory(key: str):
    """Retrieve one saved memory."""
    memories = load_memories()
    return memories.get(key, "No memory found for that key.")


def detect_memory_request(message: str):
    """Extract a memory from a simple 'remember that ...' instruction."""
    text = message.strip()

    prefixes = (
        "remember that ",
        "remember ",
    )

    for prefix in prefixes:
        if text.lower().startswith(prefix):
            statement = text[len(prefix):].strip().rstrip(".!?")
            break
    else:
        return None

    separators = (" is ", " are ", " = ")

    for separator in separators:
        if separator in statement.lower():
            index = statement.lower().find(separator)
            key = statement[:index].strip()
            value = statement[index + len(separator):].strip()

            if key and value:
                return key, value

    return None
