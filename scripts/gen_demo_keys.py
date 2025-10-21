"""
Generate demo keypairs for users to run the GUI without manual setup.

Usage:
  python scripts/gen_demo_keys.py owner1 requester1 alice bob
"""
import sys
from pathlib import Path
from config.settings import KEYS_DIR
from src.core.keystore import ensure_user_keys

def main():
    # Create keys for provided users (defaults if none specified)
    users = sys.argv[1:] or ["owner1", "requester1"]
    for u in users:
        ensure_user_keys(KEYS_DIR, u)
        print(f"[ok] keys for {u} at {KEYS_DIR/u}")

if __name__ == "__main__":
    # Entry point
    main()
