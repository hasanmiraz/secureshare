import hashlib
from typing import Dict, Any, List
from pathlib import Path
from filelock import FileLock
from config.settings import LEDGER_DIR
from src.util.time import now_ts
from src.util.jsonio import read_json, write_json

LEDGER_FILE = LEDGER_DIR / "ledger.json"
LOCK_FILE   = LEDGER_DIR / "ledger.lock"

def _hash_block(block: Dict[str, Any]) -> str:
    # Compute SHA-256 hash of a block
    import json
    payload = {
        "ts": block["ts"],
        "prev": block["prev"],
        "event": block["event"],
    }
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()

class LocalChain:
    def __init__(self, ledger_path: Path = LEDGER_FILE, lock_path: Path = LOCK_FILE):
        self.ledger_path = Path(ledger_path)
        self.lock_path   = Path(lock_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.ledger_path.exists():
            write_json(self.ledger_path, [])

    def append_event(self, event: Dict[str, Any]) -> str:
        # Add an event to the ledger with file locking
        with FileLock(str(self.lock_path)):
            chain = read_json(self.ledger_path, default=[])
            prev_hash = chain[-1]["hash"] if chain else "GENESIS"
            block = {
                "ts": now_ts(),
                "prev": prev_hash,
                "event": event,
            }
            block["hash"] = _hash_block(block)
            chain.append(block)
            write_json(self.ledger_path, chain)
            return block["hash"]

    def get_events(self) -> List[Dict[str, Any]]:
        # Return all events from the ledger
        return read_json(self.ledger_path, default=[])

    def verify_chain(self) -> bool:
        # Verify integrity of the chain
        chain = self.get_events()
        prev = "GENESIS"
        for b in chain:
            if b.get("prev") != prev:
                return False
            if _hash_block(b) != b.get("hash"):
                return False
            prev = b["hash"]
        return True
