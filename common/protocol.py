"""
Protocol definitions for packet structure and framing.
"""

import struct
from typing import Optional, Tuple


# Protocol constants
PROTOCOL_VERSION = 1
HEADER_SIZE = 9  # version (1) + nonce_size (4) + data_size (4)


class Packet:
    """
    Packet structure:
    - Version (1 byte): Protocol version
    - Nonce size (4 bytes): Size of nonce in ciphertext
    - Data size (4 bytes): Size of encrypted data
    - Ciphertext: Nonce + encrypted data (variable length)
    """
    
    @staticmethod
    def pack(version: int, ciphertext: bytes) -> bytes:
        """
        Pack a packet with version and ciphertext.
        
        Args:
            version: Protocol version
            ciphertext: Encrypted data (assumes nonce is prepended)
            
        Returns:
            Packed packet bytes
        """
        nonce_size = 24  # PyNaCl nonce size
        data_size = len(ciphertext) - nonce_size
        
        header = struct.pack('!BII', version, nonce_size, data_size)
        return header + ciphertext
    
    @staticmethod
    def unpack(data: bytes) -> Optional[Tuple[int, bytes]]:
        """
        Unpack packet header and return version + ciphertext.
        
        Args:
            data: Raw packet bytes
            
        Returns:
            Tuple of (version, ciphertext) or None if invalid
        """
        if len(data) < HEADER_SIZE:
            return None
        
        try:
            version, nonce_size, data_size = struct.unpack('!BII', data[:HEADER_SIZE])
            total_size = HEADER_SIZE + nonce_size + data_size
            
            if len(data) < total_size:
                return None
            
            ciphertext = data[HEADER_SIZE:total_size]
            return (version, ciphertext)
        except struct.error:
            return None

