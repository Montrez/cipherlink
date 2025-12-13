#!/usr/bin/env python3
"""
CLI entry point for running the Cipherlink proxy server.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import Config
from common.logging_config import setup_logging
from server.proxy import ProxyServer


async def main():
    """Main entry point for server."""
    parser = argparse.ArgumentParser(
        description='Run Cipherlink proxy server'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='Server bind address (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Server bind port (default: 8888)'
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
        server_host=args.host,
        server_port=args.port,
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
    
    # Create and start server
    server = ProxyServer(host=config.server_host, port=config.server_port)
    logger.info(f"Starting Cipherlink server on {config.server_host}:{config.server_port}")
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

