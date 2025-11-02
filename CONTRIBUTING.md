# Contributing to Cipherlink

Thank you for contributing to Cipherlink! This document outlines our git workflow and development practices.

## Git Workflow

Cipherlink uses a **Git Flow** workflow optimized for phased development and security-sensitive features.

### Branch Structure

```
main
  ├── develop (integration branch)
  │   ├── feature/phase-1-socks5
  │   ├── feature/phase-2-tun-setup
  │   ├── feature/client-connection
  │   └── ...
  ├── release/v0.1.0 (preparing releases)
  └── hotfix/critical-bug-fix (emergency fixes)
```

### Branch Types

#### 1. **main** (Production/Stable)
- **Purpose**: Production-ready, stable code
- **Protection**: Only merged via `release/` branches
- **Who merges**: Project maintainers
- **When**: Only when a release is ready

#### 2. **develop** (Integration)
- **Purpose**: Integration branch for ongoing development
- **Protection**: Merged from `feature/` branches only
- **Who merges**: After code review and tests pass
- **Always**: Keep this branch in a working state

#### 3. **feature/** (Feature Development)
- **Naming**: `feature/phase-{N}-{description}` or `feature/{description}`
- **Examples**:
  - `feature/phase-1-socks5`
  - `feature/phase-1-client-connection`
  - `feature/phase-2-tun-setup`
  - `feature/keepalive-rekey`
- **Purpose**: Develop specific features from the backlog
- **Base**: Always branch from `develop`
- **Merge**: Back to `develop` when complete
- **Lifecycle**: Delete after merge

#### 4. **release/** (Release Preparation)
- **Naming**: `release/v{version}`
- **Examples**: `release/v0.1.0`, `release/v0.2.0`
- **Purpose**: Prepare releases, version bumps, final testing
- **Base**: Branch from `develop`
- **Merge**: Back to both `develop` and `main`
- **Lifecycle**: Delete after merge

#### 5. **hotfix/** (Critical Fixes)
- **Naming**: `hotfix/{description}`
- **Examples**: `hotfix/crypto-vulnerability`, `hotfix/connection-crash`
- **Purpose**: Fix critical bugs in production
- **Base**: Branch from `main`
- **Merge**: Back to both `main` and `develop`
- **Priority**: Highest priority, security issues first

### Workflow Examples

#### Starting a New Feature (Phase 1: SOCKS5 Support)

```bash
# 1. Ensure develop is up to date
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/phase-1-socks5

# 3. Develop feature
# ... make changes ...
git add .
git commit -m "feat: add SOCKS5 protocol support"

# 4. Push and create PR
git push -u origin feature/phase-1-socks5
# Create Pull Request: feature/phase-1-socks5 -> develop
```

#### Preparing a Release (v0.1.0)

```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v0.1.0

# 2. Update version numbers
# ... update setup.py, __init__.py, etc. ...
git commit -m "chore: bump version to 0.1.0"

# 3. Final testing
# ... run tests, integration tests ...

# 4. Merge to main and develop
git checkout main
git merge release/v0.1.0
git tag v0.1.0
git push origin main --tags

git checkout develop
git merge release/v0.1.0
git push origin develop

# 5. Delete release branch
git branch -d release/v0.1.0
git push origin --delete release/v0.1.0
```

#### Critical Hotfix

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/security-patch

# 2. Fix the issue
# ... make changes ...
git commit -m "fix: patch security vulnerability in crypto layer"

# 3. Merge to main
git checkout main
git merge hotfix/security-patch
git tag v0.1.1
git push origin main --tags

# 4. Merge to develop
git checkout develop
git merge hotfix/security-patch
git push origin develop

# 5. Delete hotfix branch
git branch -d hotfix/security-patch
git push origin --delete hotfix/security-patch
```

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature (Phase 1/2/3 tasks)
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (deps, config, etc.)
- `perf`: Performance improvements
- `security`: Security patches

### Examples

```
feat(phase-1): add SOCKS5 protocol support
fix(crypto): handle decryption errors gracefully
test(protocol): add packet fragmentation tests
docs(readme): update Phase 2 requirements
chore(deps): update PyNaCl to 1.6.0
security(crypto): patch nonce reuse vulnerability
```

## Code Review Process

1. **Create Pull Request**: From `feature/` → `develop`
2. **Review Checklist**:
   - [ ] Code follows project style
   - [ ] Tests pass (`pytest`)
   - [ ] New features have tests
   - [ ] Documentation updated if needed
   - [ ] No sensitive data (keys, passwords) in commits
   - [ ] Security implications considered for crypto/networking code
3. **Approval**: At least one review required
4. **Merge**: Use "Squash and merge" to keep history clean

## Phase-Based Development

### Phase 1: Encrypted Proxy
- Branch prefix: `feature/phase-1-*`
- Features: SOCKS5, client/server connection, timeout handling

### Phase 2: TUN-Based VPN
- Branch prefix: `feature/phase-2-*`
- Features: TUN setup, routing, keepalive, rekey

### Phase 3: Production Polish
- Branch prefix: `feature/phase-3-*`
- Features: Logging, CI/CD, Docker, documentation

## Security Considerations

Since Cipherlink handles cryptography and networking:

1. **Never commit keys or secrets** (`.gitignore` handles this)
2. **Review security implications** for crypto/networking changes
3. **Hotfix branch** should be used for security patches
4. **Tag releases** for security tracking
5. **Document breaking changes** in protocol/crypto layers

## Development Environment Setup

See [QUICKSTART.md](QUICKSTART.md) for environment setup instructions.

## Questions?

If you have questions about the workflow, please open an issue or reach out to the maintainers.

