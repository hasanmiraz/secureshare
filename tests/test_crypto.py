import os
import pytest
from src.core import crypto

def test_aes_gcm_roundtrip():
    # Encrypt and decrypt should return original plaintext
    msg = os.urandom(2048)
    aad = b"meta"
    key, nonce, ct = crypto.aes_encrypt(msg, aad=aad)
    pt = crypto.aes_decrypt(key, nonce, ct, aad=aad)
    assert pt == msg

def test_ecdsa_sign_verify():
    # Signature verification should succeed for original data
    priv = crypto.gen_ecdsa_p256()
    pub = priv.public_key()
    data = b"ciphertext-to-protect"
    sig = crypto.sign_ecdsa(priv, data)
    crypto.verify_ecdsa(pub, data, sig)  # no exception means success

def test_ecdsa_rejects_tamper():
    # Verification should fail if the message is altered
    priv = crypto.gen_ecdsa_p256()
    pub = priv.public_key()
    data = b"hello"
    sig = crypto.sign_ecdsa(priv, data)
    with pytest.raises(Exception):
        crypto.verify_ecdsa(pub, b"hello!", sig)

def test_rsa_wrap_unwrap():
    # RSA wrap/unwrap should recover the original key
    rsa_priv = crypto.gen_rsa()
    rsa_pub = rsa_priv.public_key()
    key = os.urandom(32)
    wrapped = crypto.rsa_wrap(rsa_pub, key)
    unwrapped = crypto.rsa_unwrap(rsa_priv, wrapped)
    assert key == unwrapped
