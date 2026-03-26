#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OS="$(uname -s)"
APPLY=0

usage() {
  cat <<'EOF'
Usage: ./bin/bootstrap.sh [--apply]

Without --apply:
  Show what this machine should install.

With --apply:
  Install packages on supported systems.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      APPLY=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

print_file_list() {
  local file="$1"
  grep -vE '^\s*#|^\s*$' "$file"
}

pick_aur_helper() {
  if [[ -n "${DOTFILES_AUR_HELPER:-}" ]] && command -v "${DOTFILES_AUR_HELPER}" >/dev/null 2>&1; then
    command -v "${DOTFILES_AUR_HELPER}"
    return 0
  fi
  if command -v paru >/dev/null 2>&1; then
    command -v paru
    return 0
  fi
  if command -v yay >/dev/null 2>&1; then
    command -v yay
    return 0
  fi
  return 1
}

if [[ "$OS" == "Darwin" ]]; then
  echo "Platform: macOS"
  echo "Package source: Homebrew"
  echo
  echo "Brew bundle file:"
  echo "  ${REPO_ROOT}/packages/Brewfile"

  if [[ "$APPLY" -eq 1 ]]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "Homebrew is not installed."
      echo "Visit: https://brew.sh/"
      exit 1
    fi
    brew bundle --file="${REPO_ROOT}/packages/Brewfile"
  fi
  exit 0
fi

if [[ "$OS" == "Linux" ]] && command -v pacman >/dev/null 2>&1; then
  echo "Platform: Linux (pacman)"
  echo
  echo "Packages:"
  print_file_list "${REPO_ROOT}/packages/cachyos-pacman.txt" | sed 's/^/  /'
  echo
  echo "Optional AUR:"
  print_file_list "${REPO_ROOT}/packages/cachyos-aur.txt" | sed 's/^/  /'

  if [[ "$APPLY" -eq 1 ]]; then
    aur_helper=""
    if aur_helper="$(pick_aur_helper)"; then
      aur_helper="$(basename "$aur_helper")"
    fi
    echo
    echo "Run this manually:"
    echo "  sudo pacman -S --needed $(print_file_list "${REPO_ROOT}/packages/cachyos-pacman.txt" | tr '\n' ' ')"
    if [[ -n "$aur_helper" ]]; then
      echo "  ${aur_helper} -S --needed $(print_file_list "${REPO_ROOT}/packages/cachyos-aur.txt" | tr '\n' ' ')"
    fi
  fi
  exit 0
fi

echo "Platform: unsupported"
echo "This repo currently knows how to bootstrap:"
echo "  - macOS with Homebrew"
echo "  - Arch/CachyOS style systems with pacman"
exit 1
