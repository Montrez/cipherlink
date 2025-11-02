# Cipherlink

**Lightweight peer-to-peer VPN** built in Python using modern cryptography and TUN networking.

Cipherlink is a learning-focused project that blends computer networking, cryptography, and systems design.  
The goal is to understand how secure tunnels actually work — not just use them.

---

## 🧭 Overview

Cipherlink creates a private, encrypted link between two devices.  
It starts as an encrypted proxy (Phase 1), then evolves into a real VPN using a TUN interface (Phase 2).

Key features planned:
- Modern encryption using [PyNaCl](https://pynacl.readthedocs.io/)
- Async I/O networking with Python’s `asyncio`
- Layered packet structure (versioning, nonces, ciphertext)
- Configurable client/server roles
- Eventual Docker + CI/CD setup for reproducible testing

---

## 🧰 Tech Stack

| Component | Purpose |
|------------|----------|
| Python 3.11+ | Core runtime |
| PyNaCl | Encryption |
| asyncio | Async network communication |
| Docker | Containerization (planned) |
| GitHub Actions | Continuous Integration (planned) |

---

---

## 🌿 Git Workflow

Cipherlink uses **Git Flow** optimized for phased development:

- **`main`**: Production-ready, stable code
- **`develop`**: Integration branch for ongoing development
- **`feature/phase-{N}-*`**: Feature branches (e.g., `feature/phase-1-socks5`)
- **`release/v*`**: Release preparation branches
- **`hotfix/*`**: Critical security/bug fixes

📖 **Full workflow documentation**: See [CONTRIBUTING.md](CONTRIBUTING.md)

### Quick Branch Creation

```bash
# Create a feature branch (automatically from develop)
./scripts/create-feature-branch.sh phase-1-socks5
```

---

## ⚙️ Quick Start (Phase 1 – Encrypted Proxy)

Generate keys:
```bash
python scripts/genkeys.py
