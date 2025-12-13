#!/usr/bin/env python3
"""
CLI entry point for running the Cipherlink proxy client.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import Config
from common.logging_config import setup_logging
from client.proxy import ProxyClient


async def main():
    """Main entry point for client."""
    parser = argparse.ArgumentParser(
        description='Run Cipherlink proxy client'
    )
    parser.add_argument(
        '--server-host',
        type=str,
        default=None,
        help='Server hostname or IP (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--server-port',
        type=int,
        default=None,
        help='Server port (default: 8888)'
    )
    parser.add_argument(
        '--key-file',
        type=str,
        default=None,
        help='Path to encryption key file (default: keys/shared_key.key)'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default=None,
        help='Path to log file (optional)'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_file = Path(args.log_file) if args.log_file else None
    logger = setup_logging(level=args.log_level, log_file=log_file)
    
    # Load configuration
    config = Config(
        key_file=Path(args.key_file) if args.key_file else None,
        server_host=args.server_host,
        server_port=args.server_port,
    )
    
    # Verify key exists
    try:
        key = config.load_key()
        logger.info(f"Loaded encryption key from {config.key_file}")
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid key file: {e}")
        sys.exit(1)
    
    # Create and start client
    server_host = args.server_host or config.client_host
    server_port = args.server_port or config.server_port
    
    client = ProxyClient(server_host=server_host, server_port=server_port)
    logger.info(f"Connecting to Cipherlink server at {server_host}:{server_port}")
    
    try:
        await client.connect()
    except KeyboardInterrupt:
        logger.info("Client stopped by user")
    except Exception as e:
        logger.error(f"Client error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

