from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .crypto import (
    gen_ecdsa_p256, gen_rsa, pem_priv, pem_pub,
    load_priv_pem, load_pub_pem
)

@dataclass
class KeyPairPaths:
    # File paths for user key pairs
    ecdsa_priv: Path
    ecdsa_pub:  Path
    rsa_priv:   Path
    rsa_pub:    Path

def user_key_paths(keys_dir: Path, user_id: str) -> KeyPairPaths:
    # Return paths to a user's key files
    udir = keys_dir / user_id
    return KeyPairPaths(
        ecdsa_priv=udir / "ecdsa_priv.pem",
        ecdsa_pub =udir / "ecdsa_pub.pem",
        rsa_priv  =udir / "rsa_priv.pem",
        rsa_pub   =udir / "rsa_pub.pem",
    )

def ensure_user_keys(keys_dir: Path, user_id: str, password: Optional[bytes]=None) -> KeyPairPaths:
    # Create keys for a user if they do not already exist
    paths = user_key_paths(keys_dir, user_id)
    paths.ecdsa_priv.parent.mkdir(parents=True, exist_ok=True)

    if not paths.ecdsa_priv.exists():
        ecdsa = gen_ecdsa_p256()
        paths.ecdsa_priv.write_bytes(pem_priv(ecdsa, password))
        paths.ecdsa_pub.write_bytes(pem_pub(ecdsa.public_key()))

    if not paths.rsa_priv.exists():
        rsa = gen_rsa()
        paths.rsa_priv.write_bytes(pem_priv(rsa, password))
        paths.rsa_pub.write_bytes(pem_pub(rsa.public_key()))

    return paths

def load_user_keys(paths: KeyPairPaths, password: Optional[bytes]=None):
    # Load keys from disk
    ecdsa_priv = load_priv_pem(paths.ecdsa_priv.read_bytes(), password=password)
    ecdsa_pub  = load_pub_pem(paths.ecdsa_pub.read_bytes())
    rsa_priv   = load_priv_pem(paths.rsa_priv.read_bytes(), password=password)
    rsa_pub    = load_pub_pem(paths.rsa_pub.read_bytes())
    return ecdsa_priv, ecdsa_pub, rsa_priv, rsa_pub
