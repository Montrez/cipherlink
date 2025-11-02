# Quick Start Guide

This guide will help you get started with Cipherlink development.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate encryption keys:**
   ```bash
   python scripts/genkeys.py
   ```
   
   This creates a `keys/` directory with a `shared_key.key` file. **Never commit keys to version control!**

## Project Structure

```
cipherlink/
├── client/          # Client-side logic (proxy + TUN)
├── server/          # Server-side logic
├── common/          # Shared crypto and protocol helpers
│   ├── crypto.py    # Encryption/decryption utilities
│   └── protocol.py  # Packet structure and framing
├── scripts/         # Key generation and setup utilities
│   └── genkeys.py   # Key generation script
├── tests/           # Unit and integration tests
│   ├── test_crypto.py
│   └── test_protocol.py
├── requirements.txt # Python dependencies
├── setup.py         # Package configuration
└── README.md        # Project documentation
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_crypto.py
```

## Development Workflow

1. **Phase 1 - Encrypted Proxy (Current Focus):**
   - Basic encryption/decryption layer ✅
   - Key generation utility ✅
   - SOCKS5 protocol support (TODO)
   - Client/server connection handling (TODO)

2. **Phase 2 - TUN-Based VPN (Planned):**
   - TUN interface setup
   - Routing through TUN
   - Keepalive and rekey

3. **Phase 3 - Production Polish:**
   - Logging and monitoring
   - CI/CD setup
   - Docker integration

## Next Steps

1. Review the existing modules in `common/` to understand the crypto and protocol layers
2. Implement the client/server connection logic in `client/proxy.py` and `server/proxy.py`
3. Add unit tests as you develop new features
4. Check the README.md for detailed project goals and backlog

