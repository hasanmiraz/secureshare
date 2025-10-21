from pathlib import Path
import shutil
import json
from src.blockchain.local_chain import LocalChain, LEDGER_FILE
from src.util.jsonio import read_json, write_json

def _fresh_ledger(tmp_path: Path):
    # Create a LocalChain instance with a temporary ledger file
    ledger = tmp_path / "ledger.json"
    lock   = tmp_path / "ledger.lock"
    return LocalChain(ledger_path=ledger, lock_path=lock), ledger

def test_append_and_verify(tmp_path):
    # Appending events should maintain a valid chain
    chain, ledger = _fresh_ledger(tmp_path)
    h1 = chain.append_event({"type":"UPLOAD","file_id":"f1"})
    h2 = chain.append_event({"type":"ACCESS_REQUEST","file_id":"f1","requester_id":"r1"})
    assert chain.verify_chain()
    evs = chain.get_events()
    assert len(evs) == 2
    assert evs[0]["hash"] == h1
    assert evs[1]["hash"] == h2

def test_detect_tamper(tmp_path):
    # Modifying a block should cause chain verification to fail
    chain, ledger = _fresh_ledger(tmp_path)
    chain.append_event({"type":"A"})
    chain.append_event({"type":"B"})
    data = read_json(ledger, [])
    data[1]["event"]["type"] = "X"  # tamper with payload
    write_json(ledger, data)
    assert chain.verify_chain() is False
