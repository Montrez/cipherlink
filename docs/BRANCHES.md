# Branch Management Guide

This document explains the branch structure and management for Cipherlink.

## Current Branch Structure

### Main Branches

- **`main`**: Production-ready, stable code. Only updated via release branches.
- **`develop`**: Integration branch for ongoing development. All features merge here first.

### Feature Branches (Phase 1 - Active)

Currently created feature branches for Phase 1 tasks:

1. **`feature/phase-1-socks5`** - SOCKS5 protocol support
2. **`feature/phase-1-client-connection`** - Client/server connection handling
3. **`feature/phase-1-timeout-handling`** - Connection timeout handling
4. **`feature/phase-1-multiple-clients`** - Support for multiple concurrent clients

### Future Branch Types

These branches will be created as needed:

#### Release Branches
- **Format**: `release/v{version}`
- **Example**: `release/v0.1.0`
- **When**: When Phase 1 is complete and ready for release
- **Purpose**: Final testing, version bumps, release notes

#### Hotfix Branches
- **Format**: `hotfix/{description}`
- **Example**: `hotfix/crypto-vulnerability`
- **When**: Critical security bugs or production issues
- **Purpose**: Emergency fixes that need immediate deployment

## Branch Commands

### List Branches by Type

```bash
# List all branches
./scripts/list-branches.sh all

# List only feature branches
./scripts/list-branches.sh feature

# List only release branches
./scripts/list-branches.sh release

# List only hotfix branches
./scripts/list-branches.sh hotfix
```

### Create Feature Branch

```bash
./scripts/create-feature-branch.sh phase-1-socks5
```

### Switch Between Branches

```bash
# Switch to develop
git checkout develop

# Switch to a feature branch
git checkout feature/phase-1-socks5

# Switch and track remote branch
git checkout -b feature/phase-1-socks5 origin/feature/phase-1-socks5
```

### Clean Up Merged Branches

```bash
# Delete merged feature branches locally
git branch --merged develop | grep 'feature/' | xargs git branch -d

# Delete merged branches remotely (after confirmation)
git branch -r --merged develop | grep 'feature/' | sed 's/origin\///' | xargs -n 1 git push origin --delete
```

## Branch Lifecycle

### Feature Branch Lifecycle

1. **Create**: `./scripts/create-feature-branch.sh phase-1-socks5`
2. **Develop**: Make changes, commit regularly
3. **Push**: `git push -u origin feature/phase-1-socks5`
4. **Pull Request**: Create PR from feature branch → develop
5. **Review**: Code review, tests pass
6. **Merge**: Merge to develop (squash merge recommended)
7. **Delete**: Delete local and remote branches after merge

### Release Branch Lifecycle

1. **Create**: `git checkout -b release/v0.1.0 develop`
2. **Prepare**: Version bumps, changelog, final tests
3. **Merge**: Merge to both `main` and `develop`
4. **Tag**: `git tag v0.1.0` on main
5. **Delete**: Clean up release branch after merge

### Hotfix Branch Lifecycle

1. **Create**: `git checkout -b hotfix/security-patch main`
2. **Fix**: Apply critical fix
3. **Merge**: Merge to both `main` and `develop`
4. **Tag**: `git tag v0.1.1` on main (patch version)
5. **Delete**: Clean up hotfix branch after merge

## Branch Naming Conventions

### Feature Branches
- **Phase 1**: `feature/phase-1-{description}`
- **Phase 2**: `feature/phase-2-{description}`
- **Phase 3**: `feature/phase-3-{description}`
- **General**: `feature/{description}`

**Good examples:**
- `feature/phase-1-socks5`
- `feature/phase-2-tun-setup`
- `feature/keepalive-rekey`

**Bad examples:**
- `fix-socks` (use `feature/phase-1-socks5-fix`)
- `socks5` (missing `feature/` prefix)
- `phase1` (missing `feature/` prefix and hyphen)

### Release Branches
- Always: `release/v{version}`
- Examples: `release/v0.1.0`, `release/v0.2.0`

### Hotfix Branches
- Format: `hotfix/{short-description}`
- Examples: `hotfix/crypto-vulnerability`, `hotfix/connection-crash`

## Best Practices

1. **Always start from develop**: Feature branches should branch from `develop`
2. **Keep branches focused**: One feature per branch
3. **Regular commits**: Commit small, logical changes
4. **Descriptive names**: Branch names should clearly indicate purpose
5. **Clean up**: Delete merged branches to keep repo clean
6. **Protect main**: Never push directly to `main`
7. **Hotfixes from main**: Hotfix branches branch from `main` (not develop)

## Phase-Based Development

### Phase 1 (Current)
- Focus: Encrypted Proxy
- Active branches: `feature/phase-1-*`
- Target: Basic encrypted proxy functionality

### Phase 2 (Planned)
- Focus: TUN-Based VPN
- Branches: `feature/phase-2-*`
- Target: Full VPN with TUN interface

### Phase 3 (Future)
- Focus: Production Polish
- Branches: `feature/phase-3-*`
- Target: CI/CD, Docker, documentation

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Full gitflow workflow documentation
- [README.md](../README.md) - Project overview and quick start

