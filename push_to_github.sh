#!/usr/bin/env bash
# ------------------------------------------------------------------
# push_to_github.sh
# Initializes a git repo (if needed) and pushes this project to GitHub.
#
# USAGE:
#   1. Create an empty repository on GitHub first (no README/license,
#      to avoid merge conflicts): https://github.com/new
#   2. Run this script from inside the project folder:
#        chmod +x push_to_github.sh
#        ./push_to_github.sh https://github.com/<your-username>/<your-repo>.git
# ------------------------------------------------------------------

set -e

REPO_URL="$1"
BRANCH="main"

if [ -z "$REPO_URL" ]; then
  echo "Usage: ./push_to_github.sh <github-repo-url>"
  echo "Example: ./push_to_github.sh https://github.com/yourname/astro-chatbot.git"
  exit 1
fi

# Safety check: make sure .env is not about to be committed
if git check-ignore -q .env 2>/dev/null; then
  echo "OK: .env is gitignored."
else
  if [ -f .env ]; then
    echo "WARNING: .env exists and does not appear to be gitignored."
    echo "Refusing to continue to avoid leaking secrets. Check your .gitignore."
    exit 1
  fi
fi

# Init git if this isn't already a repo
if [ ! -d ".git" ]; then
  git init
  git branch -M "$BRANCH"
fi

git add .

# Warn if .env somehow got staged
if git diff --cached --name-only | grep -qx ".env"; then
  echo "ERROR: .env is staged for commit. Aborting to protect your secrets."
  git reset .env
  exit 1
fi

git commit -m "Initial commit: Astro e-commerce RAG chatbot" || echo "Nothing new to commit."

# Add remote if not already set
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "$REPO_URL"
else
  git remote set-url origin "$REPO_URL"
fi

git push -u origin "$BRANCH"

echo "Done. Pushed to $REPO_URL"
