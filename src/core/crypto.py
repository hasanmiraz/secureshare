from dataclasses import dataclass
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, NoEncryption, PublicFormat, BestAvailableEncryption
)
import os

AES_KEY_BYTES = 32  # 256-bit AES key
NONCE_BYTES   = 12  # GCM nonce length

# Key generation
def gen_ecdsa_p256():
    return ec.generate_private_key(ec.SECP256R1())

def gen_rsa():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

# PEM (serialize/deserialize)
def pem_priv(priv, password: bytes | None = None):
    if password:
        enc = serialization.BestAvailableEncryption(password)
    else:
        enc = NoEncryption()
    return priv.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, enc)

def pem_pub(pub):
    return pub.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

def load_priv_pem(data: bytes, password: bytes | None = None):
    return serialization.load_pem_private_key(data, password=password)

def load_pub_pem(data: bytes):
    return serialization.load_pem_public_key(data)

# AES-GCM
def aes_encrypt(plaintext: bytes, aad: bytes = b""):
    key = os.urandom(AES_KEY_BYTES)
    nonce = os.urandom(NONCE_BYTES)
    aes = AESGCM(key)
    ct = aes.encrypt(nonce, plaintext, aad)
    return key, nonce, ct

def aes_decrypt(key: bytes, nonce: bytes, ct: bytes, aad: bytes = b""):
    aes = AESGCM(key)
    return aes.decrypt(nonce, ct, aad)

# ECDSA (SHA-256 prehash)
def sign_ecdsa(priv_key, message: bytes):
    h = hashes.SHA256()
    digest = hashes.Hash(h); digest.update(message); d = digest.finalize()
    return priv_key.sign(d, ec.ECDSA(Prehashed(h)))

def verify_ecdsa(pub_key, message: bytes, signature: bytes):
    h = hashes.SHA256()
    digest = hashes.Hash(h); digest.update(message); d = digest.finalize()
    pub_key.verify(signature, d, ec.ECDSA(Prehashed(h)))

# RSA-OAEP (SHA-256)
def rsa_wrap(pub_key, key_bytes: bytes) -> bytes:
    return pub_key.encrypt(
        key_bytes,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

def rsa_unwrap(priv_key, wrapped: bytes) -> bytes:
    return priv_key.decrypt(
        wrapped,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
