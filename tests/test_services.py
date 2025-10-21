from pathlib import Path
import os
from src.blockchain.local_chain import LocalChain
from src.core.keystore import ensure_user_keys, load_user_keys
from src.services.uploader import encrypt_sign_upload
from src.services.sharing import create_access_request, approve_and_share_key
from src.services.verifier import requester_download_and_verify
from config.settings import KEYS_DIR

def test_full_flow(tmp_path, monkeypatch):
    # Use a temporary ledger for isolation
    chain = LocalChain(ledger_path=tmp_path/"ledger.json", lock_path=tmp_path/"ledger.lock")

    # Create plaintext file
    pt_path = tmp_path/"hello.txt"
    pt_data = b"secret report v1"
    pt_path.write_bytes(pt_data)

    # Owner uploads file
    owner_id = "owner_test"
    req_id   = "requester_test"

    owner_paths = ensure_user_keys(KEYS_DIR, owner_id)
    req_paths   = ensure_user_keys(KEYS_DIR, req_id)

    owner_ecdsa_priv, owner_ecdsa_pub, _, _ = load_user_keys(owner_paths)
    _, _, req_rsa_priv, req_rsa_pub = load_user_keys(req_paths)

    upload = encrypt_sign_upload(owner_ecdsa_priv, owner_id, str(pt_path), chain=chain)
    file_id = upload["file_id"]

    # Requester creates access request
    create_access_request(chain, req_id, file_id)

    # Owner shares AES key with requester
    approve_and_share_key(chain, owner_id, file_id, req_id, req_rsa_pub, upload["aes_key"])

    # Requester downloads, decrypts, and verifies
    out = requester_download_and_verify(chain, req_id, req_rsa_priv, owner_ecdsa_pub, file_id)
    assert out == pt_data
