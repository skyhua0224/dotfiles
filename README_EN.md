# dotfiles

[![GitHub last commit](https://img.shields.io/github/last-commit/skyhua0224/dotfiles?style=flat-square)](https://github.com/skyhua0224/dotfiles/commits/main)
[![macOS](https://img.shields.io/badge/macOS-Homebrew-000000?style=flat-square&logo=apple)](https://github.com/skyhua0224/dotfiles)
[![Linux](https://img.shields.io/badge/Linux-pacman-1793D1?style=flat-square&logo=arch-linux)](https://github.com/skyhua0224/dotfiles)
[![Shell](https://img.shields.io/badge/Shell-zsh-F15A24?style=flat-square)](https://github.com/skyhua0224/dotfiles/tree/main/zsh)
[![Prompt](https://img.shields.io/badge/Prompt-Starship-DD0B78?style=flat-square)](https://github.com/starship/starship)
[![Runtime](https://img.shields.io/badge/Runtime-mise-7A5AF8?style=flat-square)](https://github.com/jdx/mise)

English documentation. 中文版： [README.md](./README.md)

Terminal and CLI dotfiles for macOS and pacman-based Linux.

- Manages shared shell, git, prompt, runtime, tmux, and Neovim config
- Does not manage secrets, SSH, personal Git identity, GUI app state, or host-private data
- Uses a symlink-based install flow with backup, restore, uninstall, and rollback support

---

## Installation

### Interactive

```bash
curl -sL https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash
```

### Automatic

```bash
curl -sL https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash -s -- --auto
```

### Manual

```bash
git clone https://github.com/skyhua0224/dotfiles ~/dotfiles
python3 ~/dotfiles/bin/setup.py
```

`bin/get.sh` checks for `git` and `python3`, clones or updates the repo, then hands off to `bin/setup.py`.

---

## Supported platforms

| Platform | Package manager | Status |
| --- | --- | --- |
| macOS | Homebrew | supported |
| Arch / CachyOS / other pacman-based Linux | pacman + AUR helper | supported |
| other Unix-like systems | symlink layer only | best effort |

If you only want the symlink layer and no system packages:

```bash
python3 ~/dotfiles/bin/setup.py --link-only
```

---

## Usage

### Common commands

| Command | Purpose |
| --- | --- |
| `ls` | `eza --icons --group-directories-first` |
| `ll` | detailed list with git state and timestamps |
| `la` | detailed list including hidden files |
| `lt` | 3-level tree view |
| `b` | `bat --style=plain --paging=never` |
| `bp` | `bat --style=full` |
| `rg keyword` | recursive search |
| `cdd` | interactive `zoxide` directory jump |
| `pcd` | builtin `cd` |
| `ta [session]` | attach/create tmux session, default `main` |
| `tls` | list tmux sessions |
| `treset` | reset tmux server |
| `nvim` | open Neovim |

### Git

`delta` is configured as the pager by default:

```bash
git diff
git log -p
git show HEAD
```

### Runtime

`mise` is the runtime manager:

```bash
mise install
mise ls
```

### Neovim

Sync plugins with:

```vim
:Lazy sync
```

---

## Scope

### Managed modules

The installer manages these modules:

- `zsh`
- `git`
- `starship`
- `atuin`
- `mise`
- `nvim`
- `tmux`

### Upstream bases

| Module | Upstream / base | Notes |
| --- | --- | --- |
| `zsh` | repo-defined | combines tools such as `zoxide`, `atuin`, `fzf-tab`, `zsh-autosuggestions`, `zsh-history-substring-search`, and `carapace` |
| `git` | repo-defined | uses `delta` as pager and diff filter |
| `starship` | [starship](https://github.com/starship/starship) | prompt configuration |
| `atuin` | [atuin](https://github.com/atuinsh/atuin) | shell history configuration |
| `mise` | [mise](https://github.com/jdx/mise) | runtime version declarations |
| `nvim` | [LazyVim](https://github.com/LazyVim/LazyVim) | Neovim base distro |
| `tmux` | [oh-my-tmux](https://github.com/gpakosz/.tmux) | tmux main config and custom layer |

### Package manifests

| File | Purpose |
| --- | --- |
| `packages/Brewfile` | Homebrew packages |
| `packages/cachyos-pacman.txt` | pacman packages |
| `packages/cachyos-aur.txt` | AUR packages |
| `packages/npm-global.txt` | npm global CLIs |

### Out of scope

- `~/.ssh`
- tokens / API keys / certificates
- personal identity in `~/.gitconfig.local`
- host-specific paths, env vars, aliases
- GUI app state

---

## Installer behavior

The main installer is `bin/setup.py`.

| Command | Purpose |
| --- | --- |
| `python3 ~/dotfiles/bin/setup.py` | interactive install |
| `python3 ~/dotfiles/bin/setup.py --auto` | install all eligible modules for this platform |
| `python3 ~/dotfiles/bin/setup.py --link-only` | symlinks only |
| `python3 ~/dotfiles/bin/setup.py --pkgs-only` | packages only |
| `python3 ~/dotfiles/bin/setup.py --restore` | restore from backup |
| `python3 ~/dotfiles/bin/setup.py --uninstall` | remove managed symlinks |
| `python3 ~/dotfiles/bin/setup.py --uninstall --rollback` | uninstall and restore latest backup |
| `python3 ~/dotfiles/bin/setup.py --auto --dry-run` | preview without writes |

Actual flow:

1. detect platform and package manager
2. detect legacy tool conflicts
3. back up existing files
4. create symlinks
5. scaffold local override templates
6. install system packages
7. run `mise install -y`
8. install npm globals
9. run environment checks

Backup directory:

```text
~/.dotfiles-backups/<timestamp>/
```

---

## Package management and install details

### macOS

The installer runs:

```bash
brew bundle --verbose --no-upgrade --file=packages/Brewfile
```

with:

```bash
HOMEBREW_NO_AUTO_UPDATE=1
```

### pacman-based Linux

Official repo packages use:

```bash
sudo pacman -S --needed --noconfirm ...
```

If pacman hits stale sync data or mirror 404s, the installer runs once:

```bash
sudo pacman -Syy --noconfirm
```

and retries.

AUR helper preference order:

1. `DOTFILES_AUR_HELPER`
2. `paru`
3. `yay`

Example:

```bash
DOTFILES_AUR_HELPER=yay python3 ~/dotfiles/bin/setup.py --auto
```

### npm globals

`packages/npm-global.txt` currently includes:

- `@anthropic-ai/claude-code`
- `@openai/codex`
- `@google/gemini-cli`

If npm fails because of stale directories (`ENOTEMPTY` or rename errors), the installer cleans them up and retries once.

---

## Runtime management

Current shared runtime versions:

| Runtime | Version |
| --- | --- |
| Node.js | `24.6.0` |
| Python | `3.12.3` |
| Ruby | `3.3.1` |
| Rust | `1.78.0` |

### `asdf` migration

If `~/.tool-versions` exists:

- shared runtimes still come from the repo `mise` config
- extra entries are migrated to:

```text
~/.config/mise/conf.d/10-legacy-asdf.toml
```

- the original `~/.tool-versions` is moved into the backup directory

---

## Shell behavior

### Interactive zsh

Enabled by default:

- `starship`
- `zoxide`
- `atuin`
- `fzf-tab`
- `zsh-autosuggestions`
- `zsh-history-substring-search`
- `carapace`
- lazy-loaded `thefuck`

### `cd` / `zoxide`

Default policy:

- human interactive shells let `zoxide` take over `cd`
- agent shells are handled conservatively to reduce automation interference

If you want to keep traditional `cd` semantics, set this in local config:

```bash
export DOTFILES_ZOXIDE_CMD=z
```

Recommended location:

```text
~/.config/dotfiles/local.zsh
```

### Agent shells

The CLI config detects agent-shell environments and only enables most enhancements in real interactive TTYs.

This includes:

- avoiding forced smart `cd` behavior in automation environments
- checking Codex / Claude Code style markers
- promoting `TERM=dumb` to `xterm-256color` when a real TTY exists

---

## Git / Prompt / tmux / Neovim

### Git

Enabled by default:

- `delta` pager
- side-by-side diff
- `zdiff3` conflict style
- `submodule.recurse = true`

Personal identity is loaded from:

```text
~/.gitconfig.local
```

### Starship

Uses a Gruvbox Dark prompt and sets:

```toml
command_timeout = 2000
```

### tmux

Built on [oh-my-tmux](https://github.com/gpakosz/.tmux). The installer will, when needed:

1. clone `~/.tmux`
2. point `~/.tmux.conf` to the oh-my-tmux main config
3. use `tmux/.tmux.conf.local` from this repo as the custom layer

### Neovim

Built on [LazyVim](https://github.com/LazyVim/LazyVim).

The current config keeps a stable base:

- `lazy.nvim` manages plugins
- `LazyVim` is the base distro
- the custom layer stays small

---

## Local override files

The installer creates these templates if missing:

| File | Purpose |
| --- | --- |
| `~/.gitconfig.local` | Git name, email, signing key |
| `~/.config/dotfiles/local.zsh` | local shell customizations |
| `~/.config/dotfiles/local.zprofile` | local login-shell customizations |
| `~/.config/dotfiles/hosts/<hostname>.zsh` | host-specific shell config |
| `~/.config/dotfiles/hosts/<hostname>.zprofile` | host-specific login-shell config |
| `~/.config/mise/conf.d/10-legacy-asdf.toml` | extra runtimes migrated from `asdf` |

Shared config lives in the repo; private config stays local.

---

## Maintenance

### Preview bootstrap

```bash
./bin/bootstrap.sh
```

### Apply bootstrap

```bash
./bin/bootstrap.sh --apply
```

- macOS: runs `brew bundle`
- pacman-based Linux: prints the suggested `pacman` / AUR commands

### Health check

```bash
./bin/doctor.sh
```

Checks include:

- whether managed files are symlinks
- whether required commands exist
- whether the current session is a TTY
- git pager / delta status
- interactive zsh helper visibility
- `mise` / `asdf` state
- legacy leftovers
- local override file presence

---

## Troubleshooting

### Homebrew lock or `.incomplete`

Run:

```bash
pgrep -af brew
```

If no brew process is left, remove the matching `.incomplete` file and retry.

### pacman mirror 404 or stale database

The installer automatically tries once after:

```bash
sudo pacman -Syy --noconfirm
```

If it still fails, inspect mirrors or repo configuration first.

### tmux reports `open terminal failed: not a terminal`

This usually means an old tmux server is still serving a new client. Run:

```bash
treset
```

Then re-enter `tmux` or `ta`.

### Shell behavior still looks affected by old tools

Run:

```bash
./bin/doctor.sh
```

Pay attention to:

- `Legacy leftovers`
- `~/.tool-versions`
- whether `.asdf` is still in `PATH`
- whether `.oh-my-zsh` / `.p10k.zsh` still exist

---

## Repository layout

```text
bin/          installer, bootstrap, doctor, compatibility entrypoints
packages/     Brew / pacman / AUR / npm manifests
zsh/          zsh config
git/          git config
starship/     Starship prompt
atuin/        Atuin config
mise/         mise runtime declarations
tmux/         tmux custom layer
nvim/         LazyVim base config
examples/     local override templates
tests/        smoke tests and installer unit tests
flake.nix     CLI-only dev shell
```

---

## Tests

### Smoke test

```bash
tests/repo-smoke.sh
```

Coverage includes:

- `install.sh` delegation to `setup.py`
- key package manifest entries
- agent-shell compatibility logic in `zsh`
- required sections in `doctor.sh`
- key README statements
- dry-run output sanity

### Python unit tests

```bash
python3 -m unittest tests/test_setup.py
```

Coverage includes:

- `brew bundle` argument policy
- Homebrew lock hints
- AUR helper selection
- `mise install` plan
- pacman 404 refresh detection
- `asdf -> mise` migration parsing
