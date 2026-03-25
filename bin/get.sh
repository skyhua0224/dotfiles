#!/usr/bin/env bash
# get.sh — dotfiles bootstrap entry point
# Usage: curl -sL get.sky-hua.xyz | bash                    # interactive
#        curl -sL get.sky-hua.xyz | bash -s -- --auto       # fully automatic
set -euo pipefail

REPO_URL="https://github.com/skyhua0224/dotfiles.git"
DOTFILES_DIR="${DOTFILES_DIR:-$HOME/dotfiles}"

# ── colours ──────────────────────────────────────────────────────────────────
if [ -t 1 ]; then
  BOLD="\033[1m"; DIM="\033[2m"; RED="\033[31m"; GREEN="\033[32m"
  YELLOW="\033[33m"; CYAN="\033[36m"; RESET="\033[0m"
else
  BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; CYAN=""; RESET=""
fi

info()    { printf "  ${CYAN}·${RESET}  %s\n" "$*"; }
ok()      { printf "  ${GREEN}✓${RESET}  %s\n" "$*"; }
warn()    { printf "  ${YELLOW}!${RESET}  %s\n" "$*"; }
die()     { printf "  ${RED}✗${RESET}  %s\n" "$*" >&2; exit 1; }
header()  { printf "\n${BOLD}── %s ${DIM}%s${RESET}\n" "$1" "$(printf '─%.0s' {1..50})"; }

# ── banner ────────────────────────────────────────────────────────────────────
printf "${CYAN}${BOLD}"
cat <<'EOF'

  ██████╗  ██████╗ ████████╗███████╗██╗██╗     ███████╗███████╗
  ██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝██║██║     ██╔════╝██╔════╝
  ██║  ██║██║   ██║   ██║   █████╗  ██║██║     █████╗  ███████╗
  ██║  ██║██║   ██║   ██║   ██╔══╝  ██║██║     ██╔══╝  ╚════██║
  ██████╔╝╚██████╔╝   ██║   ██║     ██║███████╗███████╗███████║
  ╚═════╝  ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝

EOF
printf "${RESET}"
printf "  ${DIM}Personal terminal environment · macOS & Linux${RESET}\n\n"

# ── detect os ─────────────────────────────────────────────────────────────────
OS="$(uname -s)"
header "Platform"

if [ "$OS" = "Darwin" ]; then
  info "macOS $(sw_vers -productVersion)"
elif [ "$OS" = "Linux" ]; then
  DISTRO=""
  if [ -f /etc/os-release ]; then
    DISTRO="$(grep ^PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"')"
  fi
  info "${DISTRO:-Linux}"
else
  die "Unsupported OS: $OS"
fi

# ── ensure git ────────────────────────────────────────────────────────────────
header "Dependencies"

ensure_git() {
  if command -v git >/dev/null 2>&1; then
    ok "git $(git --version | awk '{print $3}')"
    return
  fi
  warn "git not found — installing..."
  if [ "$OS" = "Darwin" ]; then
    # Triggers Xcode CLT install on first run; fallback to brew if available
    if command -v brew >/dev/null 2>&1; then
      brew install git
    else
      xcode-select --install 2>/dev/null || true
      # Wait for git to become available (CLT install is async)
      local i=0
      while ! command -v git >/dev/null 2>&1; do
        sleep 3; i=$((i+1))
        [ $i -gt 20 ] && die "git still not found after waiting. Install Xcode Command Line Tools then re-run."
      done
    fi
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --noconfirm --needed git
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get install -y git
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y git
  else
    die "Cannot install git automatically. Please install git and re-run."
  fi
  ok "git installed"
}

ensure_python3() {
  if command -v python3 >/dev/null 2>&1; then
    ok "python3 $(python3 --version | awk '{print $2}')"
    return
  fi
  warn "python3 not found — installing..."
  if [ "$OS" = "Darwin" ]; then
    if command -v brew >/dev/null 2>&1; then
      brew install python3
    else
      die "Homebrew not found. Install from https://brew.sh then re-run."
    fi
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --noconfirm --needed python
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get install -y python3
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3
  else
    die "Cannot install python3 automatically. Please install python3 and re-run."
  fi
  ok "python3 installed"
}

ensure_git
ensure_python3

# ── ensure rich ───────────────────────────────────────────────────────────────
header "Python deps"
if python3 -c "import rich" 2>/dev/null; then
  ok "rich already available"
else
  info "Installing rich (required for installer UI)..."
  python3 -m pip install --quiet --user rich
  ok "rich installed"
fi

# ── clone or update ───────────────────────────────────────────────────────────
header "Repository"

if [ -d "$DOTFILES_DIR/.git" ]; then
  ok "Already cloned at $DOTFILES_DIR"
  info "Pulling latest changes..."
  git -C "$DOTFILES_DIR" pull --ff-only 2>/dev/null && ok "Up to date" || warn "Could not pull (local changes?), continuing with existing"
else
  info "Cloning into $DOTFILES_DIR ..."
  git clone --depth=1 "$REPO_URL" "$DOTFILES_DIR"
  ok "Cloned"
fi

# ── hand off to setup.py ──────────────────────────────────────────────────────
printf "\n"
# exec replaces this process; stdin is restored to /dev/tty inside setup.py
exec python3 "$DOTFILES_DIR/bin/setup.py" "$@"
