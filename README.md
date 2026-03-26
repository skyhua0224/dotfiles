# dotfiles

[![GitHub last commit](https://img.shields.io/github/last-commit/skyhua0224/dotfiles?style=flat-square)](https://github.com/skyhua0224/dotfiles/commits/main)
[![macOS](https://img.shields.io/badge/macOS-Homebrew-000000?style=flat-square&logo=apple)](https://github.com/skyhua0224/dotfiles)
[![Linux](https://img.shields.io/badge/Linux-pacman-1793D1?style=flat-square&logo=arch-linux)](https://github.com/skyhua0224/dotfiles)
[![Shell](https://img.shields.io/badge/Shell-zsh-F15A24?style=flat-square)](https://github.com/skyhua0224/dotfiles/tree/main/zsh)
[![Prompt](https://img.shields.io/badge/Prompt-Starship-DD0B78?style=flat-square)](https://github.com/starship/starship)
[![Runtime](https://img.shields.io/badge/Runtime-mise-7A5AF8?style=flat-square)](https://github.com/jdx/mise)

中文文档。English version: [README_EN.md](./README_EN.md)

面向 macOS 与 pacman 系 Linux 的终端 / CLI 配置。

- 管理共享的 shell、git、prompt、runtime、tmux、Neovim 配置
- 不管理密钥、SSH、个人 Git 身份、GUI 应用状态与机器私有数据
- 安装方式以软链接为主，支持备份、恢复、卸载与回滚

---

## 安装

### 交互式安装

```bash
curl -sL https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash
```

### 全自动安装

```bash
curl -sL https://raw.githubusercontent.com/skyhua0224/dotfiles/main/bin/get.sh | bash -s -- --auto
```

### 手动安装

```bash
git clone https://github.com/skyhua0224/dotfiles ~/dotfiles
python3 ~/dotfiles/bin/setup.py
```

`bin/get.sh` 会先检查 `git` 与 `python3`，然后克隆或更新仓库，最后转交给 `bin/setup.py`。

---

## 支持平台

| 平台 | 包管理器 | 状态 |
| --- | --- | --- |
| macOS | Homebrew | 官方支持 |
| Arch / CachyOS / 其他 pacman 系 Linux | pacman + AUR helper | 官方支持 |
| 其他 Unix-like | 仅软链层 | 尽力支持 |

如果只需要软链接管，不安装系统包：

```bash
python3 ~/dotfiles/bin/setup.py --link-only
```

---

## Usage

### 常用命令

| 命令 | 作用 |
| --- | --- |
| `ls` | `eza --icons --group-directories-first` |
| `ll` | 详细列表，含 git 状态与时间 |
| `la` | 含隐藏文件的详细列表 |
| `lt` | 3 层树形视图 |
| `b` | `bat --style=plain --paging=never` |
| `bp` | `bat --style=full` |
| `rg keyword` | 全局搜索 |
| `cdd` | `zoxide` 交互式目录跳转 |
| `pcd` | 原生 `cd` |
| `ta [session]` | 进入或创建 tmux session，默认 `main` |
| `tls` | 列出 tmux sessions |
| `treset` | 重置 tmux server |
| `nvim` | 打开 Neovim |

### Git

默认使用 `delta` 作为 pager：

```bash
git diff
git log -p
git show HEAD
```

### Runtime

统一使用 `mise` 管理运行时：

```bash
mise install
mise ls
```

### Neovim

同步插件：

```vim
:Lazy sync
```

## 管理范围

安装器实际管理以下模块：

- `zsh`
- `git`
- `starship`
- `atuin`
- `mise`
- `nvim`
- `tmux`

### 配置来源

| 模块 | 上游 / 基础 | 说明 |
| --- | --- | --- |
| `zsh` | 仓库自定义 | 组合 `zoxide`、`atuin`、`fzf-tab`、`zsh-autosuggestions`、`zsh-history-substring-search`、`carapace` 等工具 |
| `git` | 仓库自定义 | 以 `delta` 作为 pager 和 diff filter |
| `starship` | [starship](https://github.com/starship/starship) | Prompt 配置 |
| `atuin` | [atuin](https://github.com/atuinsh/atuin) | shell history 配置 |
| `mise` | [mise](https://github.com/jdx/mise) | runtime 版本声明 |
| `nvim` | [LazyVim](https://github.com/LazyVim/LazyVim) | Neovim 基础发行版 |
| `tmux` | [oh-my-tmux](https://github.com/gpakosz/.tmux) | tmux 主配置与自定义层 |

### 软件包清单

| 文件 | 作用 |
| --- | --- |
| `packages/Brewfile` | Homebrew 包清单 |
| `packages/cachyos-pacman.txt` | pacman 包清单 |
| `packages/cachyos-aur.txt` | AUR 包清单 |
| `packages/npm-global.txt` | npm 全局 CLI 清单 |

### 不纳入仓库的内容

- `~/.ssh`
- token / API key / 证书
- `~/.gitconfig.local` 中的个人身份信息
- 主机专属路径、环境变量、别名
- GUI 应用状态目录

---

## 安装器行为

主安装器是 `bin/setup.py`。

| 命令 | 作用 |
| --- | --- |
| `python3 ~/dotfiles/bin/setup.py` | 交互式安装 |
| `python3 ~/dotfiles/bin/setup.py --auto` | 自动安装当前平台全部模块 |
| `python3 ~/dotfiles/bin/setup.py --link-only` | 只建软链 |
| `python3 ~/dotfiles/bin/setup.py --pkgs-only` | 只装系统包 |
| `python3 ~/dotfiles/bin/setup.py --restore` | 恢复备份 |
| `python3 ~/dotfiles/bin/setup.py --uninstall` | 移除托管软链 |
| `python3 ~/dotfiles/bin/setup.py --uninstall --rollback` | 卸载并恢复最近备份 |
| `python3 ~/dotfiles/bin/setup.py --auto --dry-run` | 预览操作，不写入 |

实际流程：

1. 检测平台与包管理器
2. 检测旧方案冲突
3. 备份已有文件
4. 建立软链
5. 生成本地 override 模板
6. 安装系统包
7. 执行 `mise install -y`
8. 安装 npm globals
9. 进行环境检查

备份目录：

```text
~/.dotfiles-backups/<timestamp>/
```

---

## 包管理与安装细节

### macOS

安装器会执行：

```bash
brew bundle --verbose --no-upgrade --file=packages/Brewfile
```

并设置：

```bash
HOMEBREW_NO_AUTO_UPDATE=1
```

### pacman 系 Linux

官方仓库包使用：

```bash
sudo pacman -S --needed --noconfirm ...
```

如果命中过期数据库或镜像 404，安装器会自动执行一次：

```bash
sudo pacman -Syy --noconfirm
```

然后重试。

AUR helper 选择顺序：

1. `DOTFILES_AUR_HELPER`
2. `paru`
3. `yay`

例如：

```bash
DOTFILES_AUR_HELPER=yay python3 ~/dotfiles/bin/setup.py --auto
```

### npm globals

`packages/npm-global.txt` 当前包含：

- `@anthropic-ai/claude-code`
- `@openai/codex`
- `@google/gemini-cli`

如果 npm 因脏目录报 `ENOTEMPTY` 或 rename 错误，安装器会清理 stale 目录后再重试一次。

---

## 运行时管理

当前共享运行时版本：

| Runtime | Version |
| --- | --- |
| Node.js | `24.6.0` |
| Python | `3.12.3` |
| Ruby | `3.3.1` |
| Rust | `1.78.0` |

### `asdf` 迁移

如果检测到 `~/.tool-versions`：

- 共享运行时仍以仓库中的 `mise` 配置为准
- 额外条目会迁移到：

```text
~/.config/mise/conf.d/10-legacy-asdf.toml
```

- 原始 `~/.tool-versions` 会移动到备份目录

---

## Shell 行为

### 交互式 zsh

默认启用：

- `starship`
- `zoxide`
- `atuin`
- `fzf-tab`
- `zsh-autosuggestions`
- `zsh-history-substring-search`
- `carapace`
- 懒加载的 `thefuck`

### `cd` / `zoxide`

默认策略：

- 人类交互终端：`zoxide` 接管 `cd`
- `agent shell`：保守处理，减少自动化干扰

如果需要保留传统 `cd` 语义，可在本地配置中设置：

```bash
export DOTFILES_ZOXIDE_CMD=z
```

建议写入：

```text
~/.config/dotfiles/local.zsh
```

### agent shell

这套 CLI 配置会识别 `agent shell` 环境，并只在真实交互 TTY 下启用大部分增强行为。

包括：

- 避免在自动化环境中强行替换 `cd`
- 检测 Codex / Claude Code 相关环境标记
- 在 `TERM=dumb` 但实际有 TTY 时提升到 `xterm-256color`

---

## Git / Prompt / tmux / Neovim

### Git

默认启用：

- `delta` pager
- side-by-side diff
- `zdiff3` conflict style
- `submodule.recurse = true`

个人身份信息通过本地文件引入：

```text
~/.gitconfig.local
```

### Starship

使用 Gruvbox Dark 风格，并设置：

```toml
command_timeout = 2000
```

### tmux

基于 [oh-my-tmux](https://github.com/gpakosz/.tmux)。安装器会在需要时：

1. 克隆 `~/.tmux`
2. 把 `~/.tmux.conf` 指向 oh-my-tmux 主配置
3. 使用仓库中的 `tmux/.tmux.conf.local` 作为自定义层

### Neovim

基于 [LazyVim](https://github.com/LazyVim/LazyVim)。

当前配置以稳定骨架为主：

- `lazy.nvim` 负责插件管理
- `LazyVim` 作为基础发行版
- 自定义层保持精简

---

## 本地覆盖文件

安装器会在缺失时生成这些模板：

| 文件 | 用途 |
| --- | --- |
| `~/.gitconfig.local` | Git 姓名、邮箱、签名 key |
| `~/.config/dotfiles/local.zsh` | 本地 shell 自定义 |
| `~/.config/dotfiles/local.zprofile` | 本地登录 shell 自定义 |
| `~/.config/dotfiles/hosts/<hostname>.zsh` | 主机专属 shell 配置 |
| `~/.config/dotfiles/hosts/<hostname>.zprofile` | 主机专属登录 shell 配置 |
| `~/.config/mise/conf.d/10-legacy-asdf.toml` | `asdf` 迁移来的额外 runtime |

原则：共享配置进仓库，私有配置留本地。

---

## 维护命令

### 预览 bootstrap

```bash
./bin/bootstrap.sh
```

### 应用 bootstrap

```bash
./bin/bootstrap.sh --apply
```

- macOS：直接执行 `brew bundle`
- pacman 系 Linux：打印建议执行的 `pacman` / AUR 命令

### 健康检查

```bash
./bin/doctor.sh
```

检查项包括：

- 托管文件是否为软链
- 关键命令是否存在
- 当前 session 是否是 TTY
- git pager / delta 状态
- 交互式 zsh helper 是否可见
- `mise` / `asdf` 状态
- legacy leftovers
- 本地 override 文件是否存在

---

## 故障排查

### Homebrew 报锁或 `.incomplete`

先执行：

```bash
pgrep -af brew
```

确认没有残留 brew 进程后，再删除对应 `.incomplete` 文件并重试。

### pacman 镜像 404 / 过期数据库

安装器会自动尝试一次：

```bash
sudo pacman -Syy --noconfirm
```

如果仍失败，优先检查镜像或仓库配置。

### tmux 提示 `open terminal failed: not a terminal`

通常是旧 tmux server 仍在服务新的 client。先执行：

```bash
treset
```

然后重新进入 `tmux` 或 `ta`。

### shell 行为仍受旧环境影响

执行：

```bash
./bin/doctor.sh
```

重点检查：

- `Legacy leftovers`
- `~/.tool-versions`
- `.asdf` 是否仍在 `PATH` 中
- `.oh-my-zsh` / `.p10k.zsh` 是否残留

---

## 仓库结构

```text
bin/          安装器、bootstrap、doctor、兼容入口
packages/     Brew / pacman / AUR / npm 清单
zsh/          zsh 配置
git/          git 配置
starship/     Starship prompt
atuin/        Atuin 配置
mise/         mise runtime 声明
tmux/         tmux 自定义层
nvim/         LazyVim 配置骨架
examples/     本地 override 模板
tests/        smoke test + 安装器单测
flake.nix     只含 CLI 工具的 dev shell
```

---

## 测试

### Smoke test

```bash
tests/repo-smoke.sh
```

覆盖内容包括：

- `install.sh` 是否正确转发到 `setup.py`
- 包清单关键项是否存在
- `zsh` 中的 `agent shell` 兼容逻辑是否还在
- `doctor.sh` 的关键段落是否还在
- README 关键说明是否存在
- dry-run 输出是否正常

### Python 单测

```bash
python3 -m unittest tests/test_setup.py
```

覆盖内容包括：

- `brew bundle` 参数策略
- Homebrew 锁冲突提示
- AUR helper 选择逻辑
- `mise install` 计划
- pacman 404 自动刷新判断
- `asdf -> mise` 迁移解析逻辑
