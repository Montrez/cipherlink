#!/bin/bash
# Helper script to create feature branches following gitflow conventions
# Usage: ./scripts/create-feature-branch.sh phase-1-socks5
#        ./scripts/create-feature-branch.sh phase-2-tun-setup

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <branch-name>"
    echo ""
    echo "Examples:"
    echo "  $0 phase-1-socks5"
    echo "  $0 phase-1-client-connection"
    echo "  $0 phase-2-tun-setup"
    echo "  $0 keepalive-rekey"
    echo ""
    exit 1
fi

BRANCH_NAME="$1"

# Ensure we're on develop and it's up to date
echo "Checking out develop branch..."
git checkout develop || {
    echo "Error: Could not checkout develop. Does it exist?"
    exit 1
}

echo "Pulling latest changes from develop..."
git pull origin develop || echo "Warning: Could not pull from origin. Continuing..."

# Create feature branch
FEATURE_BRANCH="feature/${BRANCH_NAME}"
echo "Creating feature branch: ${FEATURE_BRANCH}..."
git checkout -b "${FEATURE_BRANCH}"

echo ""
echo "✓ Feature branch '${FEATURE_BRANCH}' created!"
echo ""
echo "Next steps:"
echo "  1. Make your changes"
echo "  2. Commit: git add . && git commit -m 'feat(${BRANCH_NAME}): <description>'"
echo "  3. Push: git push -u origin ${FEATURE_BRANCH}"
echo "  4. Create Pull Request: ${FEATURE_BRANCH} -> develop"
echo ""

