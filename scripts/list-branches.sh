#!/bin/bash
# Helper script to list branches by type (feature, release, hotfix)
# Usage: ./scripts/list-branches.sh [feature|release|hotfix|all]

set -e

TYPE="${1:-all}"

case "$TYPE" in
    feature)
        echo "=== Feature Branches ==="
        git branch --list 'feature/*' | sed 's/^[* ] //'
        ;;
    release)
        echo "=== Release Branches ==="
        git branch --list 'release/*' | sed 's/^[* ] //'
        ;;
    hotfix)
        echo "=== Hotfix Branches ==="
        git branch --list 'hotfix/*' | sed 's/^[* ] //'
        ;;
    all|*)
        echo "=== All Branch Types ==="
        echo ""
        echo "Main branches:"
        git branch --list 'main' 'develop' | sed 's/^[* ] //' | sed 's/^/  /'
        echo ""
        echo "Feature branches:"
        git branch --list 'feature/*' | sed 's/^[* ] //' | sed 's/^/  /' || echo "  (none)"
        echo ""
        echo "Release branches:"
        git branch --list 'release/*' | sed 's/^[* ] //' | sed 's/^/  /' || echo "  (none)"
        echo ""
        echo "Hotfix branches:"
        git branch --list 'hotfix/*' | sed 's/^[* ] //' | sed 's/^/  /' || echo "  (none)"
        ;;
esac

