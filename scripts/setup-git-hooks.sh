#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

git config core.hooksPath .githooks

echo "Git hooks path configured: .githooks"
echo "pre-commit hook will run automatically on each commit."
echo "Run 'git commit' now to verify."

