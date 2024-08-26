# utils.py

import json
from typing import List
from config import RECENT_FILES_PATH

def load_recent_files() -> List[str]:
    try:
        with open(RECENT_FILES_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_recent_files(recent_files: List[str]) -> None:
    with open(RECENT_FILES_PATH, 'w') as f:
        json.dump(recent_files, f)