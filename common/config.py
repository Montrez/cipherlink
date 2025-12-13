"""
Configuration management for Cipherlink.
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration settings for Cipherlink."""
    
    # Default paths
    DEFAULT_KEYS_DIR = Path("keys")
    DEFAULT_KEY_FILE = DEFAULT_KEYS_DIR / "shared_key.key"
    
    # Network defaults
    DEFAULT_SERVER_HOST = "0.0.0.0"
    DEFAULT_SERVER_PORT = 8888
    DEFAULT_CLIENT_HOST = "127.0.0.1"
    
    # Protocol defaults
    DEFAULT_PROTOCOL_VERSION = 1
    
    def __init__(
        self,
        key_file: Optional[Path] = None,
        server_host: Optional[str] = None,
        server_port: Optional[int] = None,
        client_host: Optional[str] = None,
    ):
        """
        Initialize configuration.
        
        Args:
            key_file: Path to encryption key file (default: keys/shared_key.key)
            server_host: Server bind address (default: 0.0.0.0)
            server_port: Server bind port (default: 8888)
            client_host: Client server hostname (default: 127.0.0.1)
        """
        self.key_file = key_file or self.DEFAULT_KEY_FILE
        self.server_host = server_host or os.getenv("CIPHERLINK_SERVER_HOST", self.DEFAULT_SERVER_HOST)
        self.server_port = server_port or int(os.getenv("CIPHERLINK_SERVER_PORT", self.DEFAULT_SERVER_PORT))
        self.client_host = client_host or os.getenv("CIPHERLINK_CLIENT_HOST", self.DEFAULT_CLIENT_HOST)
    
    def load_key(self) -> bytes:
        """
        Load encryption key from file.
        
        Returns:
            Key bytes (32 bytes)
            
        Raises:
            FileNotFoundError: If key file doesn't exist
            ValueError: If key file is invalid
        """
        if not self.key_file.exists():
            raise FileNotFoundError(
                f"Key file not found: {self.key_file}\n"
                f"Generate keys with: python scripts/genkeys.py"
            )
        
        key = self.key_file.read_bytes()
        if len(key) != 32:
            raise ValueError(f"Invalid key size: expected 32 bytes, got {len(key)}")
        
        return key
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables."""
        key_file = os.getenv("CIPHERLINK_KEY_FILE")
        return cls(
            key_file=Path(key_file) if key_file else None,
        )

