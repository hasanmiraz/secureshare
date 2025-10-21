import json
from typing import Any
from pathlib import Path

def read_json(path: str | Path, default: Any):
    p = Path(path)
    if not p.exists():
        return default
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str | Path, obj: Any, indent: int = 2):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent)
