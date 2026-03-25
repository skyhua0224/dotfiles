#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

assert_grep() {
  local pattern="$1"
  local file="$2"
  if ! grep -Eq "$pattern" "$file"; then
    fail "expected pattern [$pattern] in $file"
  fi
}

help_output="$("$REPO_ROOT/bin/install.sh" --help 2>&1 || true)"
if [[ "$help_output" != *"--auto"* ]]; then
  fail "install.sh should delegate to setup.py help output"
fi

assert_grep '^brew "tmux"$' "$REPO_ROOT/packages/Brewfile"
assert_grep '^brew "neovim"$' "$REPO_ROOT/packages/Brewfile"
assert_grep '^brew "libyaml"$' "$REPO_ROOT/packages/Brewfile"
assert_grep '^tmux$' "$REPO_ROOT/packages/cachyos-pacman.txt"
assert_grep '^neovim$' "$REPO_ROOT/packages/cachyos-pacman.txt"
assert_grep '^libyaml$' "$REPO_ROOT/packages/cachyos-pacman.txt"
assert_grep '^__pycache__/$' "$REPO_ROOT/.gitignore"
assert_grep '^\*\.pyc$' "$REPO_ROOT/.gitignore"
assert_grep 'mise activate zsh' "$REPO_ROOT/zsh/.zshrc"

if [[ -e "$REPO_ROOT/bin/__pycache__/setup.cpython-312.pyc" ]]; then
  fail "tracked Python bytecode cache should not live in the repo"
fi

dry_run_output="$(python3 "$REPO_ROOT/bin/setup.py" --auto --link-only --dry-run)"
if [[ "$dry_run_output" != *$'\n  zsh\n'* ]]; then
  fail "plain dry-run output should show module names"
fi

printf 'ok: repo smoke checks passed\n'
