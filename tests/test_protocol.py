"""
Unit tests for protocol module.
"""

import pytest
from common.protocol import Packet, PROTOCOL_VERSION, HEADER_SIZE


def test_packet_pack_unpack():
    """Test packet packing and unpacking."""
    # Simulate ciphertext (nonce + data)
    nonce = b'0' * 24
    data = b"encrypted_data"
    ciphertext = nonce + data
    
    packed = Packet.pack(PROTOCOL_VERSION, ciphertext)
    version, unpacked_ciphertext = Packet.unpack(packed)
    
    assert version == PROTOCOL_VERSION
    assert unpacked_ciphertext == ciphertext


def test_packet_unpack_insufficient_data():
    """Test unpacking with insufficient data."""
    result = Packet.unpack(b'short')
    assert result is None


def test_packet_unpack_invalid_header():
    """Test unpacking with invalid header."""
    # Invalid header (too short)
    result = Packet.unpack(b'\x01')
    assert result is None

