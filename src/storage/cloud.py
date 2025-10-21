from pathlib import Path
from typing import List
from config.settings import CLOUD_DIR
from src.util.jsonio import read_json, write_json

BLOB_EXT = ".blob"
META_FILE = CLOUD_DIR / "meta.json"

def _meta():
    # Load metadata (create cloud dir if missing)
    CLOUD_DIR.mkdir(parents=True, exist_ok=True)
    return read_json(META_FILE, default={})

def _save_meta(m):
    # Save metadata back to disk
    write_json(META_FILE, m)

def put_blob(file_id: str, content: bytes, filename: str):
    # Store file content and update metadata
    CLOUD_DIR.mkdir(parents=True, exist_ok=True)
    path = CLOUD_DIR / f"{file_id}{BLOB_EXT}"
    path.write_bytes(content)
    meta = _meta()
    meta[file_id] = {"filename": filename, "size": len(content)}
    _save_meta(meta)
    return str(path)

def get_blob(file_id: str) -> bytes:
    # Retrieve stored file content
    path = CLOUD_DIR / f"{file_id}{BLOB_EXT}"
    return path.read_bytes()

def list_files() -> List[dict]:
    # List all stored files with metadata
    meta = _meta()
    out = []
    for fid, m in meta.items():
        out.append({"file_id": fid, "filename": m["filename"], "size": m["size"]})
    return out

def get_meta(file_id: str) -> dict | None:
    # Get metadata for a specific file
    return _meta().get(file_id)
