"""AES/CBC/PKCS7 helper for the Wema Merchant Payout API.

Wema encrypts every business request/response body with
``AES/CBC/PKCS5Padding`` (PKCS5 == PKCS7 for AES's 16-byte block), base64
encoded, using a static key + IV (raw UTF-8 bytes) supplied by the bank.
"""

from __future__ import annotations

import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

_BLOCK_BITS = 128  # AES block size


class AesCipher:
    """Encrypt/decrypt strings exactly as the Wema gateway expects."""

    def __init__(self, key: str, iv: str) -> None:
        self._key = key.encode("utf-8")
        self._iv = iv.encode("utf-8")
        if len(self._key) not in (16, 24, 32):
            raise ValueError("AES key must be 16, 24 or 32 bytes")
        if len(self._iv) != 16:
            raise ValueError("AES IV must be 16 bytes")

    def encrypt(self, plaintext: str) -> str:
        padder = PKCS7(_BLOCK_BITS).padder()
        padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()
        encryptor = Cipher(algorithms.AES(self._key), modes.CBC(self._iv)).encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(ciphertext).decode("ascii")

    def decrypt(self, b64_ciphertext: str) -> str:
        ciphertext = base64.b64decode(b64_ciphertext)
        decryptor = Cipher(algorithms.AES(self._key), modes.CBC(self._iv)).decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = PKCS7(_BLOCK_BITS).unpadder()
        return (unpadder.update(padded) + unpadder.finalize()).decode("utf-8")
