from typing import Optional
import binascii
from src.core.crypto import rsa_unwrap, aes_decrypt, verify_ecdsa
from src.storage.cloud import get_blob
from src.blockchain.local_chain import LocalChain

def _find_upload(chain_events, file_id: str) -> Optional[dict]:
    # Find the upload event for a given file
    for e in chain_events:
        ev = e["event"]
        if ev.get("type") == "UPLOAD" and ev.get("file_id") == file_id:
            return ev
    return None

def _find_keyshare(chain_events, file_id: str, requester_id: str) -> Optional[dict]:
    # Get the most recent KEY_SHARE for a file and requester
    ks = [e["event"] for e in chain_events if e["event"].get("type")=="KEY_SHARE"
          and e["event"].get("file_id")==file_id
          and e["event"].get("requester_id")==requester_id]
    return ks[-1] if ks else None

def requester_download_and_verify(chain: LocalChain, requester_id: str, requester_rsa_priv, owner_ecdsa_pub, file_id: str) -> bytes:
    # Download file from cloud, unwrap AES key, decrypt, and verify signature
    events = chain.get_events()
    upload_ev  = _find_upload(events, file_id)
    if not upload_ev:
        raise ValueError("No upload event for file")

    keyshare_ev = _find_keyshare(events, file_id, requester_id)
    if not keyshare_ev:
        raise ValueError("Key not shared to this requester")

    wrapped = bytes.fromhex(keyshare_ev["wrapped_key"])
    aes_key = rsa_unwrap(requester_rsa_priv, wrapped)

    nonce = bytes.fromhex(upload_ev["aes_nonce"])
    sig   = bytes.fromhex(upload_ev["sig"])

    ct = get_blob(file_id)
    pt = aes_decrypt(aes_key, nonce, ct)

    # Verify owner’s ECDSA signature over ciphertext
    verify_ecdsa(owner_ecdsa_pub, ct, sig)
    return pt
