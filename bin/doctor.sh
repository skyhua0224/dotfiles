#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANAGED_FILES=(
  ".zshrc"
  ".zprofile"
  ".gitconfig"
  ".tool-versions"
  ".config/starship.toml"
  ".config/atuin/config.toml"
  ".config/mise/config.toml"
)
REQUIRED_COMMANDS=(
  zsh
  git
  rg
  eza
  starship
  atuin
  zoxide
)

printf 'Managed files\n'
for rel in "${MANAGED_FILES[@]}"; do
  dest="${HOME}/${rel}"
  if [[ -L "$dest" ]]; then
    printf '  ok   %s -> %s\n' "$rel" "$(readlink "$dest")"
  elif [[ -e "$dest" ]]; then
    printf '  warn %s exists but is not symlinked\n' "$rel"
  else
    printf '  miss %s\n' "$rel"
  fi
done

printf '\nCommands\n'
for cmd in "${REQUIRED_COMMANDS[@]}"; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '  ok   %s\n' "$cmd"
  else
    printf '  miss %s\n' "$cmd"
  fi
done

printf '\nRuntime manager\n'
if command -v mise >/dev/null 2>&1; then
  printf '  ok   mise\n'
elif command -v asdf >/dev/null 2>&1; then
  printf '  ok   asdf\n'
else
  printf '  miss asdf/mise\n'
fi

printf '\nLocal overrides\n'
for file in \
  "${HOME}/.gitconfig.local" \
  "${HOME}/.config/dotfiles/local.zsh" \
  "${HOME}/.config/dotfiles/local.zprofile"; do
  if [[ -e "$file" ]]; then
    printf '  ok   %s\n' "$file"
  else
    printf '  miss %s\n' "$file"
  fi
done

printf '\nRepo root: %s\n' "$REPO_ROOT"
