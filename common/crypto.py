"""
Cryptography utilities using PyNaCl for encryption/decryption.
"""

import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
from typing import Optional, Tuple


class CryptoBox:
    """
    Wrapper around PyNaCl's Box for symmetric encryption.
    Uses a shared secret key for encryption/decryption.
    """
    
    def __init__(self, key: bytes):
        """
        Initialize CryptoBox with a 32-byte secret key.
        
        Args:
            key: 32-byte secret key for encryption
        """
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes")
        self._box = nacl.secret.SecretBox(key)
    
    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt plaintext and return ciphertext with nonce prepended.
        
        Args:
            plaintext: Data to encrypt
            
        Returns:
            Ciphertext with nonce (24 bytes) + encrypted data
        """
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        ciphertext = self._box.encrypt(plaintext, nonce)
        return ciphertext
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt ciphertext (assumes nonce is prepended).
        
        Args:
            ciphertext: Encrypted data with nonce prepended
            
        Returns:
            Decrypted plaintext
        """
        return self._box.decrypt(ciphertext)


class KeyPair:
    """
    Wrapper for PyNaCl public/private key pair.
    Used for key exchange in future implementations.
    """
    
    def __init__(self):
        """Generate a new key pair."""
        self._private_key = PrivateKey.generate()
        self.public_key = self._private_key.public_key
    
    @classmethod
    def from_private_key(cls, private_key_bytes: bytes) -> 'KeyPair':
        """Create KeyPair from private key bytes."""
        instance = cls.__new__(cls)
        instance._private_key = PrivateKey(private_key_bytes)
        instance.public_key = instance._private_key.public_key
        return instance
    
    def get_shared_box(self, other_public_key: PublicKey) -> Box:
        """
        Create a Box for encryption with another party's public key.
        
        Args:
            other_public_key: The other party's public key
            
        Returns:
            Box instance for encryption/decryption
        """
        return Box(self._private_key, other_public_key)
    
    def get_private_key_bytes(self) -> bytes:
        """Get private key as bytes."""
        return bytes(self._private_key)

