import binascii
from src.core.crypto import rsa_wrap
from src.blockchain.local_chain import LocalChain

def create_access_request(chain, requester_id: str, file_id: str):
    # Log an access request event
    chain.append_event({
        "type": "ACCESS_REQUEST",
        "file_id": file_id,
        "requester_id": requester_id,
    })

def approve_and_share_key(chain, owner_id: str, file_id: str, requester_id: str, requester_rsa_pub, aes_key: bytes):
    # Wrap AES key with requester's RSA public key and log share event
    wrapped = rsa_wrap(requester_rsa_pub, aes_key)
    chain.append_event({
        "type": "KEY_SHARE",
        "file_id": file_id,
        "owner_id": owner_id,
        "requester_id": requester_id,
        "wrapped_key": binascii.hexlify(wrapped).decode(),
    })
    return wrapped
