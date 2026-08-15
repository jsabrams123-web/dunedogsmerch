#!/bin/zsh
set -e

cd "$(dirname "$0")"

if ! command -v gh >/dev/null 2>&1; then
  echo "Installing the GitHub command-line tool..."
  brew install gh
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "A browser window will open so you can authorize GitHub."
  gh auth login --web --git-protocol https
fi

gh auth setup-git
git push -u origin launch

echo ""
echo "Published the Dune Dogs launch branch to GitHub."
