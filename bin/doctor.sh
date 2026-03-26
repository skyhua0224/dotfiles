#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANAGED_FILES=(
  ".zshenv"
  ".zshrc"
  ".zprofile"
  ".gitconfig"
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

printf '\nSession\n'
for fd in 0 1 2; do
  case "$fd" in
    0) label="stdin" ;;
    1) label="stdout" ;;
    2) label="stderr" ;;
  esac
  if [[ -t "$fd" ]]; then
    printf '  ok   %s is a tty\n' "$label"
  else
    printf '  warn %s is not a tty\n' "$label"
  fi
done

printf '  info TERM=%s\n' "${TERM:-}"
printf '  info TERM_PROGRAM=%s\n' "${TERM_PROGRAM:-}"
printf '  info COLORTERM=%s\n' "${COLORTERM:-}"

parent_pid="$(ps -o ppid= -p $$ 2>/dev/null | tr -d ' ')"
parent_cmd="$(ps -o command= -p "${parent_pid:-0}" 2>/dev/null | sed 's/^[[:space:]]*//')"
if [[ -n "$parent_cmd" ]]; then
  printf '  info parent=%s\n' "$parent_cmd"
fi

if [[ -n "${CODEX_SHELL:-}" || -n "${CODEX_THREAD_ID:-}" || -n "${CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:-}" ]]; then
  printf '  info agent-shell markers detected\n'
else
  printf '  info no agent-shell markers detected\n'
fi

printf '\nGit Pager\n'
pager="$(git config --global --get core.pager 2>/dev/null || true)"
diff_filter="$(git config --global --get interactive.diffFilter 2>/dev/null || true)"
if [[ -n "$pager" ]]; then
  printf '  info core.pager=%s\n' "$pager"
else
  printf '  warn core.pager is unset\n'
fi
if [[ -n "$diff_filter" ]]; then
  printf '  info interactive.diffFilter=%s\n' "$diff_filter"
fi
if command -v delta >/dev/null 2>&1; then
  printf '  ok   delta -> %s\n' "$(command -v delta)"
else
  printf '  warn delta not found in PATH\n'
fi

printf '\nInteractive zsh view\n'
if command -v zsh >/dev/null 2>&1; then
  while IFS= read -r line; do
    printf '  %s\n' "$line"
  done < <(
    zsh -ic '
      for item in cd cdd pcd tmux ta treset; do
        if whence -w "$item" >/dev/null 2>&1; then
          type "$item"
        else
          printf "%s not found\n" "$item"
        fi
      done
    ' 2>/dev/null
  )
fi

printf '\nRuntime manager\n'
if command -v mise >/dev/null 2>&1; then
  printf '  ok   mise\n'
elif command -v asdf >/dev/null 2>&1; then
  printf '  ok   asdf\n'
else
  printf '  miss asdf/mise\n'
fi

printf '\nLegacy leftovers\n'
if [[ -f "${HOME}/.tool-versions" ]]; then
  printf '  warn %s still exists and may override mise with legacy asdf syntax\n' "${HOME}/.tool-versions"
else
  printf '  ok   ~/.tool-versions not present\n'
fi

if [[ ":${PATH}:" == *":${HOME}/.asdf/shims:"* ]]; then
  printf '  warn PATH still includes %s\n' "${HOME}/.asdf/shims"
else
  printf '  ok   .asdf shims not in PATH\n'
fi

if [[ ":${PATH}:" == *":${HOME}/.asdf/bin:"* ]]; then
  printf '  warn PATH still includes %s\n' "${HOME}/.asdf/bin"
else
  printf '  ok   .asdf bin not in PATH\n'
fi

if [[ -d "${HOME}/.asdf" ]]; then
  printf '  warn %s still exists\n' "${HOME}/.asdf"
else
  printf '  ok   .asdf directory removed\n'
fi

if [[ -d "${HOME}/.oh-my-zsh" ]]; then
  printf '  warn %s still exists\n' "${HOME}/.oh-my-zsh"
else
  printf '  ok   .oh-my-zsh directory removed\n'
fi

if [[ -f "${HOME}/.p10k.zsh" ]]; then
  printf '  warn %s still exists\n' "${HOME}/.p10k.zsh"
else
  printf '  ok   .p10k.zsh removed\n'
fi

printf '\nLocal overrides\n'
for file in \
  "${HOME}/.gitconfig.local" \
  "${HOME}/.config/dotfiles/local.zsh" \
  "${HOME}/.config/dotfiles/local.zprofile" \
  "${HOME}/.config/mise/conf.d/10-legacy-asdf.toml"; do
  if [[ -e "$file" ]]; then
    printf '  ok   %s\n' "$file"
  else
    printf '  miss %s\n' "$file"
  fi
done

printf '\nRepo root: %s\n' "$REPO_ROOT"
