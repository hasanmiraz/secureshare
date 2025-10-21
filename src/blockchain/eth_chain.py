"""
Ethereum-backed Chain adapter.

Requires:
- Running Ethereum node (e.g., Ganache/Hardhat) at ETH_RPC_URL
- Deployed ChainLogger contract (address via CHAINLOGGER_ADDR or constructor)
- ABI file at contracts/ChainLogger.abi.json

Notes:
- verify_chain() always returns True (immutability handled by consensus).
- Returned events match LocalChain format.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List
from web3 import Web3
from config.settings import ETH_RPC_URL
from src.util.time import now_ts

ABI_PATH = Path("contracts/ChainLogger.abi.json")

class EthChain:
    def __init__(self, contract_address: str | None = None, abi_path: Path = ABI_PATH, rpc_url: str = ETH_RPC_URL):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise RuntimeError(f"Cannot connect to ETH node at {rpc_url}")

        self.contract_addr = Web3.to_checksum_address(
            contract_address or os.getenv("CHAINLOGGER_ADDR", "")
        )
        if not self.contract_addr:
            raise RuntimeError("Missing ChainLogger contract address")

        abi = json.loads(Path(abi_path).read_text(encoding="utf-8"))
        self.contract = self.w3.eth.contract(address=self.contract_addr, abi=abi)
        # Use first available account (common for Ganache/Hardhat)
        self.account = self.w3.eth.accounts[0]

    def append_event(self, event: Dict[str, Any]) -> str:
        # Encode event as JSON and send to contract
        payload = json.dumps(event, sort_keys=True, separators=(",", ":"))
        tx = self.contract.functions.append(payload).build_transaction({
            "from": self.account,
            "nonce": self.w3.eth.get_transaction_count(self.account),
            "gas": 100_000,
        })
        tx_hash = self.w3.eth.send_transaction(tx)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash.hex()

    def get_events(self) -> List[Dict[str, Any]]:
        # Read all events from contract storage
        items = self.contract.functions.getAll().call()
        out = []
        for s in items:
            try:
                ev = json.loads(s)
            except json.JSONDecodeError:
                continue
            out.append({
                "ts": now_ts(),
                "prev": "",
                "hash": "",
                "event": ev
            })
        return out

    def verify_chain(self) -> bool:
        # Trust Ethereum consensus for integrity
        return True
