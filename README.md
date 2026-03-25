# dotfiles

[![GitHub last commit](https://img.shields.io/github/last-commit/skyhua0224/dotfiles?style=flat-square)](https://github.com/skyhua0224/dotfiles/commits/main)
[![macOS](https://img.shields.io/badge/macOS-13%2B-000000?style=flat-square&logo=apple)](https://github.com/skyhua0224/dotfiles)
[![CachyOS](https://img.shields.io/badge/CachyOS%20%2F%20Arch-pacman-1793D1?style=flat-square&logo=arch-linux)](https://github.com/skyhua0224/dotfiles)
[![Shell](https://img.shields.io/badge/shell-zsh-F15A24?style=flat-square)](https://github.com/skyhua0224/dotfiles/tree/main/zsh)
[![Prompt](https://img.shields.io/badge/prompt-Starship-DD0B78?style=flat-square)](https://github.com/starship/starship)
[![Runtime](https://img.shields.io/badge/runtime-mise-7A5AF8?style=flat-square)](https://github.com/jdx/mise)

我的终端与 shell 环境配置，支持 macOS 和 CachyOS / Arch Linux。

> 链接说明：
> - 项目页和文档页统一使用 GitHub 原链。
> - 下载命令额外提供国内镜像，目前实测可用的是 `ghfast.top` 的 `raw.githubusercontent.com` / tarball 代理。

---

## 安装

```bash
# 全自动（GitHub 原链）
curl -sL https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash -s -- --auto

# 交互式（GitHub 原链）
curl -sL https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash
```

国内镜像（同一脚本）：

```bash
# 全自动（国内镜像）
curl -sL https://ghfast.top/https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash -s -- --auto

# 交互式（国内镜像）
curl -sL https://ghfast.top/https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash
```

### 安装器做了什么

1. 检测平台（macOS / CachyOS / Arch / Linux）
2. 如果缺少 `git` 或 `python3` 则自动安装
3. 克隆本仓库到 `~/dotfiles`
4. **检测冲突工具**，自动迁移（备份后替换，可恢复）
5. 建立配置软链（已有文件自动备份到 `~/.dotfiles-backups/<时间戳>/`）
6. 通过 Homebrew / pacman + AUR 安装软件包
7. 安装 npm 全局工具（Claude Code、Codex、Gemini CLI）
8. 如果选择了 tmux 模块，自动安装 oh-my-tmux

### 安装模式

| 命令 | 模式 |
|------|------|
| `curl ... \| bash` | 交互式：先选语言，再勾选模块（全部默认选中） |
| `curl ... \| bash -s -- --auto` | 全自动：识别平台，直接安装全部适配模块 |

### 手动安装

```bash
git clone https://github.com/skyhua0224/dotfiles ~/dotfiles
python3 ~/dotfiles/bin/setup.py
```

`bin/install.sh` 仍然保留，但现在只是兼容入口，内部直接转发到 `setup.py`。

---

## 冲突迁移

安装器会自动检测以下已有工具，并提供无损替换到 mise / 独立插件体系：

| 检测到 | 替换为 | 说明 |
|--------|--------|------|
| `asdf` | `mise` | mise 直接读取 `.tool-versions`，零损失迁移 |
| `nvm` | `mise` | mise 接管 Node 版本管理，读取 `.nvmrc` |
| `pyenv` | `mise` | mise 接管 Python 版本管理，读取 `.python-version` |
| `rbenv` / `rvm` | `mise` | mise 接管 Ruby 版本管理，读取 `.ruby-version` |
| `oh-my-zsh` | 独立 zsh 插件 | 功能等价；autosuggestions、syntax-highlight、history-search |

所有被替换的配置文件在动前一律备份至 `~/.dotfiles-backups/<时间戳>/`。
交互式安装会询问是否处理冲突，也可选跳过。

---

## 恢复 / 卸载

### 恢复历史备份

```bash
python3 ~/dotfiles/bin/setup.py --restore
```

列出所有历史备份快照，选择一个即可恢复。预览用：

```bash
python3 ~/dotfiles/bin/setup.py --restore --dry-run
```

### 卸载

移除所有 dotfiles 托管的软链（不影响其他文件）：

```bash
python3 ~/dotfiles/bin/setup.py --uninstall
```

卸载并同时恢复最近一次备份：

```bash
python3 ~/dotfiles/bin/setup.py --uninstall --rollback
```

---

## 支持平台

| 平台 | Shell | 包管理器 |
|------|-------|---------|
| macOS 13+ | zsh | Homebrew |
| CachyOS / Arch Linux | zsh | pacman + AUR（yay / paru）|
| 其他 Linux（pacman） | zsh | pacman |

---

## Shell 配置

### 命令别名

| 命令 | 说明 |
|------|------|
| `ls` | eza — 图标 + 目录优先 |
| `ll` | eza — 详细列表，含 git 状态和时间戳 |
| `la` | eza — 详细列表，含隐藏文件 |
| `lt` | eza — 树形视图（3 层） |
| `cd` | zoxide — 智能跳转，自动学习历史 |
| `cdd` | zoxide — fzf 交互式目录选择 |
| `b` | bat — 语法高亮查看文件（简洁模式） |
| `bp` | bat — 完整模式，含行号和标题 |
| `rg` | ripgrep — 智能大小写，跟随符号链接 |
| `grep` | grep 带颜色 |
| `dfu` | duf — 磁盘空间概览 |
| `duu` | dust — 目录大小分布 |
| `psg` | procs — 进程树 |
| `h` | tldr — 命令速查（中文） |

> `ls` 和 `cd` 的替换**只在交互式 zsh 中生效**。
> 脚本、Claude Code、Codex 调用的永远是系统原生命令，不受影响。

### 快捷键

| 按键 | 功能 |
|------|------|
| `↑` / `↓` | 按当前行前缀搜索历史（zsh-history-substring-search） |
| `Ctrl-R` | atuin 全局模糊历史搜索 |
| `Tab` | fzf-tab 模糊补全面板 |

---

## Git

使用 [delta](https://github.com/dandavison/delta) 作为 diff pager，支持左右对比、语法高亮、行号显示。

```bash
git diff        # 左右对比 diff
git log -p      # 带高亮的提交历史
git show HEAD   # 单次提交 diff
```

---

## tmux — oh-my-tmux

基于 [oh-my-tmux](https://github.com/gpakosz/.tmux)。
选择 tmux 模块时，安装器自动克隆 oh-my-tmux 并建立软链。
自定义主题和设置在 `tmux/.tmux.conf.local` 中。

### Shell helper

| 命令 | 说明 |
|------|------|
| `ta [session]` | 进入 tmux；不存在就创建，默认 session 名为 `main` |
| `tls` | 列出当前 tmux sessions |
| `treset` | 杀掉旧 tmux server，适合改完 shell / tmux 配置后重置环境 |

### 快捷键

| 按键 | 功能 |
|------|------|
| `Ctrl-b` | Prefix 键 |
| `<prefix> \|` | 垂直分割面板 |
| `<prefix> -` | 水平分割面板 |
| `<prefix> h/j/k/l` | vim 风格切换面板 |
| `<prefix> H/J/K/L` | 调整面板大小 |
| `<prefix> Tab` | 切换到上一个窗口 |
| `<prefix> Enter` | 进入复制模式 |
| `<prefix> m` | 切换鼠标模式 |
| `<prefix> e` | 编辑 `.tmux.conf.local` 并重载 |
| `<prefix> r` | 重载配置 |

默认开启鼠标支持。

### 简短排障

如果你看到 `open terminal failed: not a terminal`，先执行一次 `treset`，再重新进入 `tmux` 或 `ta`。

这通常不是新 shell 本身坏了，而是旧 tmux server 还活着，继续拿着上一版终端环境服务新的 client。

---

## Neovim — LazyVim

基于 [LazyVim](https://github.com/LazyVim/LazyVim)。配置在 `nvim/.config/nvim/`。
当前保持 LazyVim 基础结构，先把环境拉起来，个人插件和桌面级定制后面再继续加。

### 更新插件

```
:Lazy sync
```

### 常用快捷键

`<leader>` = `Space`

| 按键 | 功能 |
|------|------|
| `<leader>ff` | 查找文件 |
| `<leader>fg` | 全局搜索 |
| `<leader>fb` | 切换 buffer |
| `<leader>fr` | 最近文件 |
| `<leader>e` | 文件树 |
| `<leader>gg` | LazyGit |
| `<leader>l` | Lazy 插件管理器 |
| `<leader>cm` | Mason（LSP / linter 管理） |
| `K` | 悬浮文档 |
| `gd` | 跳转到定义 |
| `gr` | 查看引用 |
| `<leader>ca` | 代码操作 |

完整快捷键：`:h lazyvim-keymaps` 或 [LazyVim keymaps](https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua)

---

## AI CLI 工具

通过 npm 全局安装，需要 Node.js（由 mise 管理）。

| 工具 | 命令 | 说明 |
|------|------|------|
| [Claude Code](https://github.com/anthropics/claude-code) | `claude` | Anthropic 官方 CLI |
| [Codex](https://github.com/openai/codex) | `codex` | OpenAI 编程助手 CLI |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `gemini` | Google Gemini CLI |

---

## Prompt — Starship

使用 Starship 官方 `Gruvbox Rainbow` preset，powerline 风格。配置在 `starship/.config/starship.toml`。

显示内容：操作系统图标 · 用户名 · 当前目录 · git 分支/状态 · 语言版本 · 时间

---

## 运行时版本管理 — mise

| 运行时 | 版本 |
|--------|------|
| Node.js | 24.6.0 |
| Python | 3.12.3 |
| Ruby | 3.3.1 |
| Rust | 1.78.0 |

配置在 `mise/.config/mise/config.toml`，同时兼容 `.tool-versions` 和 `.nvmrc` / `.python-version` / `.ruby-version` 格式。
原来使用 asdf / nvm / pyenv 的用户无需手动迁移，安装器自动处理。

---

## 本地覆盖

共享配置提交进仓库，个人差异留在本地不跟踪。
安装器从模板自动生成以下文件（如不存在）：

| 文件 | 用途 |
|------|------|
| `~/.gitconfig.local` | 姓名、邮箱、签名 key |
| `~/.config/dotfiles/local.zsh` | 个人 zsh 配置 |
| `~/.config/dotfiles/local.zprofile` | 个人 zprofile 配置 |
| `~/.config/dotfiles/hosts/<hostname>.zsh` | 机器专属配置 |

---

## Nix（可选）

`flake.nix` 提供包含所有 CLI 工具的 dev shell，macOS 和 Linux 行为一致：

```bash
nix develop
```

不替代 symlink 安装方式，适合在新机器上快速拉起工具链。

---

## 环境自检

```bash
python3 ~/dotfiles/bin/setup.py --link-only --dry-run   # 预览软链
python3 ~/dotfiles/bin/setup.py --restore --dry-run     # 预览恢复
python3 ~/dotfiles/bin/setup.py --uninstall --dry-run   # 预览卸载
~/dotfiles/bin/doctor.sh                                  # 检查当前状态
```

---

<details>
<summary>English README</summary>

## dotfiles

My terminal and shell environment for macOS and CachyOS / Arch Linux.

### Install

```bash
# Fully automatic (GitHub)
curl -sL https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash -s -- --auto

# Interactive (GitHub)
curl -sL https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash

# China mirror
curl -sL https://ghfast.top/https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash
```

| Mode | Behaviour |
|------|-----------|
| default | Language → conflict check → module picker (all pre-checked) → packages → confirm |
| `--auto` | Detect platform, auto-resolve conflicts, install everything |

### What the installer does

1. Detect platform (macOS / CachyOS / Arch / Linux)
2. Install `git` / `python3` if missing
3. Clone this repo to `~/dotfiles`
4. Detect conflicting tools and offer migration (all backed up first)
5. Symlink configs (existing files backed up to `~/.dotfiles-backups/<timestamp>/`)
6. Install packages via Homebrew / pacman + AUR
7. Install npm globals (Claude Code, Codex, Gemini CLI)
8. Auto-install oh-my-tmux if tmux module selected

Package output is captured — you see clean `ok / warn` status.
Full logs saved to `~/.dotfiles-install.log`.

### Conflict migration

Detected automatically; you choose to migrate or skip:

| Detected | Replaced by | Notes |
|----------|-------------|-------|
| `asdf` | `mise` | `.tool-versions` kept, converted to mise format |
| `nvm` | `mise` | reads `.nvmrc` |
| `pyenv` | `mise` | reads `.python-version` |
| `rbenv` / `rvm` | `mise` | reads `.ruby-version` |
| `oh-my-zsh` | standalone plugins | autosuggestions, syntax-highlight, history-search |

All replaced files are backed up before any changes.

### Restore and uninstall

```bash
# Pick a backup snapshot and restore it
python3 ~/dotfiles/bin/setup.py --restore

# Remove all managed symlinks
python3 ~/dotfiles/bin/setup.py --uninstall

# Remove symlinks and restore latest backup
python3 ~/dotfiles/bin/setup.py --uninstall --rollback

# Preview any of the above without writing
python3 ~/dotfiles/bin/setup.py --restore --dry-run
python3 ~/dotfiles/bin/setup.py --uninstall --dry-run
```

### Aliases

| Command | Description |
|---------|-------------|
| `ls` | eza — icons, dirs first |
| `ll` | eza — detailed with git status |
| `la` | eza — detailed, show hidden |
| `lt` | eza — tree view (3 levels) |
| `cd` | zoxide — smart directory jump |
| `cdd` | zoxide — interactive fuzzy picker |
| `b` | bat — plain syntax-highlighted view |
| `bp` | bat — full view with line numbers |
| `rg` | ripgrep — smart-case search |
| `dfu` | duf — disk usage |
| `duu` | dust — directory size breakdown |
| `psg` | procs — process tree |
| `h` | tldr — quick reference |

> `ls` and `cd` replacements only apply in interactive zsh. Scripts and AI tools always use native system commands.

### Keybindings

| Key | Action |
|-----|--------|
| `↑` / `↓` | History search by prefix |
| `Ctrl-R` | Fuzzy history search (atuin) |
| `Tab` | Fuzzy completion (fzf-tab) |

### tmux keybindings (oh-my-tmux)

Helper commands:

| Command | Action |
|---------|--------|
| `ta [session]` | attach to a session or create it, defaulting to `main` |
| `tls` | list tmux sessions |
| `treset` | kill the current tmux server so the next launch starts clean |

| Key | Action |
|-----|--------|
| `Ctrl-b` | Prefix |
| `<prefix> \|` | Split vertical |
| `<prefix> -` | Split horizontal |
| `<prefix> h/j/k/l` | Navigate panes |
| `<prefix> Tab` | Last window |
| `<prefix> r` | Reload config |

If you hit `open terminal failed: not a terminal`, run `treset` once and start tmux again. In practice this usually means an older tmux server is still running with stale terminal state.

### Neovim (LazyVim) — `<leader>` = Space

| Key | Action |
|-----|--------|
| `<leader>ff` | Find files |
| `<leader>fg` | Live grep |
| `<leader>e` | File explorer |
| `<leader>gg` | LazyGit |
| `gd` | Go to definition |
| `K` | Hover docs |

Update plugins: `:Lazy sync`

### Runtime version management — mise

| Runtime | Version |
|---------|---------|
| Node.js | 24.6.0 |
| Python | 3.12.3 |
| Ruby | 3.3.1 |
| Rust | 1.78.0 |

Config at `mise/.config/mise/config.toml`. Reads `.tool-versions`, `.nvmrc`, `.python-version`, `.ruby-version` natively.

</details>
