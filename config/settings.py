import os
from pathlib import Path

# Project root directory (two levels up from this file)
ROOT = Path(__file__).resolve().parents[1]

# Chain mode (default: local)
CHAIN_MODE = os.getenv("CHAIN_MODE", "local")

# Data directories (can be overridden via environment variables)
DATA_DIR   = Path(os.getenv("DATA_DIR", ROOT / "data"))
CLOUD_DIR  = Path(os.getenv("CLOUD_DIR", DATA_DIR / "cloud"))
LEDGER_DIR = Path(os.getenv("LEDGER_DIR", DATA_DIR / "ledger"))
KEYS_DIR   = Path(os.getenv("KEYS_DIR", DATA_DIR / "keys"))

# Ethereum RPC endpoint
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "http://127.0.0.1:8545")

# Create required directories if they don’t exist
for p in [DATA_DIR, CLOUD_DIR, LEDGER_DIR, KEYS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# GUI settings
APP_TITLE = "SecureShare | CSIT953"
APP_SIZE  = "1000x680"
