# Cipherlink

**Lightweight peer-to-peer VPN** built in Python using modern cryptography and TUN networking.

Cipherlink is a learning-focused project that blends computer networking, cryptography, and systems design.  
The goal is to understand how secure tunnels actually work — not just use them.

---

## 🧭 Overview

Cipherlink creates a private, encrypted link between two devices.  
It starts as an encrypted proxy (Phase 1), then evolves into a real VPN using a TUN interface (Phase 2).

Key features:
- ✅ Modern encryption using [PyNaCl](https://pynacl.readthedocs.io/)
- ✅ Async I/O networking with Python's `asyncio`
- ✅ Layered packet structure (versioning, nonces, ciphertext)
- ✅ Configurable client/server roles
- ✅ Docker + CI/CD setup for reproducible testing
- 🚧 SOCKS5 protocol support (in progress)
- 🚧 TUN interface support (planned)

---

## 🧰 Tech Stack

| Component | Purpose |
|------------|----------|
| Python 3.11+ | Core runtime |
| PyNaCl | Encryption |
| asyncio | Async network communication |
| Docker | Containerization |
| GitHub Actions | Continuous Integration |
| pytest | Testing framework |
| black | Code formatting |

---

## ⚙️ Quick Start (Phase 1 – Encrypted Proxy)

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or use make: make install
   ```

2. **Generate encryption keys:**
   ```bash
   python scripts/genkeys.py
   # or use make: make keys
   ```
   
   This creates a `keys/` directory with a `shared_key.key` file. **Never commit keys to version control!**

3. **Run tests:**
   ```bash
   pytest
   # or use make: make test
   ```

### Running the Application

**Start the server:**
```bash
python scripts/run_server.py --host 0.0.0.0 --port 8888
```

**Start the client:**
```bash
python scripts/run_client.py --server-host 127.0.0.1 --server-port 8888
```

### Using Docker

```bash
# Build and start services
make docker-build
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

---

## 📋 Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and [TASKS.md](TASKS.md) for available tasks.

### Available Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make test          # Run tests
make lint          # Run linters
make format        # Format code
make type-check    # Run type checker
make docker-build  # Build Docker images
make docker-up     # Start Docker containers
```

---

## 📁 Project Structure

```
cipherlink/
├── client/              # Client-side logic (proxy + TUN)
├── server/              # Server-side logic
├── common/              # Shared crypto and protocol helpers
│   ├── crypto.py        # Encryption/decryption utilities
│   ├── protocol.py      # Packet structure and framing
│   ├── config.py        # Configuration management
│   └── logging_config.py # Logging setup
├── scripts/             # CLI entry points and utilities
│   ├── genkeys.py       # Key generation script
│   ├── run_server.py    # Server CLI entry point
│   └── run_client.py    # Client CLI entry point
├── tests/               # Unit and integration tests
├── .github/workflows/   # CI/CD workflows
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
├── Makefile            # Development commands
├── TASKS.md            # Task tracking
└── CONTRIBUTING.md     # Contribution guidelines
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_crypto.py

# Run with coverage
make test-cov
```

---

## 📝 License

See [LICENSE](LICENSE) file for details.
