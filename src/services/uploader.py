import binascii
from pathlib import Path
from src.core.crypto import aes_encrypt, sign_ecdsa
from src.storage.cloud import put_blob
from src.blockchain.local_chain import LocalChain
from src.core.ids import new_id

def encrypt_sign_upload(owner_ecdsa_priv, owner_id: str, file_path: str, chain=None):
    # Encrypt file with AES, sign ciphertext, upload to cloud, and log event
    chain = chain or LocalChain()
    data = Path(file_path).read_bytes()

    aes_key, nonce, ct = aes_encrypt(data)
    signature = sign_ecdsa(owner_ecdsa_priv, ct)

    file_id = new_id()
    put_blob(file_id, ct, filename=Path(file_path).name)

    record = {
        "type": "UPLOAD",
        "file_id": file_id,
        "owner_id": owner_id,
        "filename": Path(file_path).name,
        "aes_nonce": binascii.hexlify(nonce).decode(),
        "sig": binascii.hexlify(signature).decode(),
        "size": len(ct),
    }
    chain.append_event(record)

    return {
        "file_id": file_id,
        "aes_key": aes_key,
        "nonce": nonce,
        "signature": signature,
        "size": len(ct),
    }
