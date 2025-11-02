"""
Unit tests for crypto module.
"""

import pytest
from common.crypto import CryptoBox, KeyPair


def test_crypto_box_encrypt_decrypt():
    """Test that encryption and decryption work correctly."""
    key = b'0' * 32  # 32-byte key
    box = CryptoBox(key)
    
    plaintext = b"Hello, Cipherlink!"
    ciphertext = box.encrypt(plaintext)
    decrypted = box.decrypt(ciphertext)
    
    assert decrypted == plaintext
    assert ciphertext != plaintext


def test_crypto_box_invalid_key():
    """Test that invalid key size raises error."""
    with pytest.raises(ValueError):
        CryptoBox(b'too_short')


def test_key_pair_generation():
    """Test key pair generation."""
    kp = KeyPair()
    assert kp.public_key is not None
    assert len(kp.get_private_key_bytes()) == 32


def test_key_pair_shared_box():
    """Test shared box creation between two key pairs."""
    kp1 = KeyPair()
    kp2 = KeyPair()
    
    box1 = kp1.get_shared_box(kp2.public_key)
    box2 = kp2.get_shared_box(kp1.public_key)
    
    message = b"Shared secret message"
    # Box.encrypt() automatically handles nonces
    encrypted = box1.encrypt(message)
    decrypted = box2.decrypt(encrypted)
    
    assert decrypted == message

