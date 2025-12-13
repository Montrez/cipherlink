# Contributing to Cipherlink

Thank you for your interest in contributing to Cipherlink! This guide will help you get started.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd cipherlink
   ```

2. **Set up your development environment:**
   ```bash
   # Create a virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   make install
   # or: pip install -r requirements.txt
   
   # Generate encryption keys
   make keys
   # or: python scripts/genkeys.py
   ```

3. **Run tests to verify setup:**
   ```bash
   make test
   # or: pytest
   ```

## Development Workflow

### 1. Pick a Task

Check `TASKS.md` for available tasks. Pick one that's marked as "Available" and update it with your name:
```markdown
- [ ] **Task 1.1**: Implement basic TCP server
  - **Assigned to**: Your Name
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/task-1.1
# or: git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Write code following the existing style
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_your_file.py

# Check code formatting
make format-check

# Run linters
make lint
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:
```bash
git add .
git commit -m "feat: implement basic TCP server in ProxyServer"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/task-1.1
```

Then create a pull request on GitHub.

## Code Style

- Follow PEP 8 style guidelines
- Use `black` for code formatting (run `make format`)
- Maximum line length: 127 characters
- Use type hints where appropriate
- Write docstrings for all public functions and classes

## Testing Guidelines

- Write tests for all new features
- Aim for good test coverage
- Use descriptive test names: `test_function_name_scenario`
- Mark slow tests with `@pytest.mark.slow`
- Mark integration tests with `@pytest.mark.integration`

## Project Structure

```
cipherlink/
├── client/          # Client-side logic
├── server/          # Server-side logic
├── common/          # Shared utilities
│   ├── crypto.py    # Encryption/decryption
│   ├── protocol.py  # Packet structure
│   ├── config.py    # Configuration management
│   └── logging_config.py  # Logging setup
├── scripts/         # CLI entry points and utilities
├── tests/           # Test suite
└── TASKS.md         # Task tracking
```

## Running the Application

### Server

```bash
# Using the script directly
python scripts/run_server.py --host 0.0.0.0 --port 8888

# Using make (if installed via setup.py)
cipherlink-server --host 0.0.0.0 --port 8888
```

### Client

```bash
# Using the script directly
python scripts/run_client.py --server-host 127.0.0.1 --server-port 8888

# Using make (if installed via setup.py)
cipherlink-client --server-host 127.0.0.1 --server-port 8888
```

## Docker Development

```bash
# Build images
make docker-build

# Start services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

## Getting Help

- Check `TASKS.md` for current tasks
- Review `README.md` and `QUICKSTART.md` for project overview
- Ask questions in pull requests or issues

## Commit Message Guidelines

Use conventional commit format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Example:
```
feat: implement SOCKS5 handshake in ProxyServer

- Add SOCKS5 authentication method negotiation
- Implement CONNECT command handling
- Add tests for SOCKS5 protocol
```

Happy coding! 🚀

