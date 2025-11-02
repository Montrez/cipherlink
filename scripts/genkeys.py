#!/usr/bin/env python3
"""
Key generation utility for Cipherlink.
Generates symmetric encryption keys for client/server communication.
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import common modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from nacl.utils import random


def generate_key(key_size: int = 32) -> bytes:
    """
    Generate a random key of specified size.
    
    Args:
        key_size: Size of key in bytes (default: 32 for PyNaCl)
        
    Returns:
        Random bytes of specified size
    """
    return random(key_size)


def save_key(key: bytes, filepath: Path) -> None:
    """
    Save key to file in binary format.
    
    Args:
        key: Key bytes to save
        filepath: Path to save key file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(key)
    # Set restrictive permissions
    os.chmod(filepath, 0o600)
    print(f"✓ Key saved to {filepath}")


def main():
    """Main entry point for key generation script."""
    parser = argparse.ArgumentParser(
        description='Generate encryption keys for Cipherlink'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='keys',
        help='Directory to save keys (default: keys/)'
    )
    parser.add_argument(
        '--key-size',
        type=int,
        default=32,
        help='Key size in bytes (default: 32)'
    )
    parser.add_argument(
        '--name',
        type=str,
        default='shared_key',
        help='Key filename (without extension, default: shared_key)'
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    key_path = output_dir / f'{args.name}.key'
    
    print(f"Generating {args.key_size}-byte encryption key...")
    key = generate_key(args.key_size)
    save_key(key, key_path)
    
    # Print key as hex for verification (optional)
    print(f"Key (hex): {key.hex()}")
    print(f"\n⚠️  Keep this key secure and never commit it to version control!")


if __name__ == '__main__':
    main()

