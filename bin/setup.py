#!/usr/bin/env python3
"""
dotfiles setup
  default : interactive — prompt_toolkit live selector, back/quit supported
  --auto  : fully automatic, installs everything for this platform
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from io import StringIO
from pathlib import Path

# ── rich bootstrap ─────────────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.text import Text
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

# ── prompt_toolkit bootstrap ───────────────────────────────────────────────────
try:
    import prompt_toolkit  # noqa: F401
    _HAS_PT = True
except ImportError:
    _HAS_PT = False

# ── tty helpers (works with curl | bash) ──────────────────────────────────────
_tty_file = None

def _tty():
    global _tty_file
    if _tty_file is None:
        try:
            _tty_file = open("/dev/tty")
        except OSError:
            _tty_file = sys.stdin
    return _tty_file

def _raw_input(msg: str, default: str = "") -> str:
    sys.stdout.write(msg)
    sys.stdout.flush()
    try:
        line = _tty().readline()
        if not line:
            raise EOFError
        return line.rstrip("\n") or default
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

def _tty_is_interactive() -> bool:
    try:
        return os.path.exists("/dev/tty") or sys.stdin.isatty()
    except Exception:
        return False

# ── console singleton ──────────────────────────────────────────────────────────
console: "Console | None" = Console(highlight=False) if _HAS_RICH else None

def _clear() -> None:
    if console:
        console.clear()
    else:
        print("\033[2J\033[H", end="")

# ── i18n ──────────────────────────────────────────────────────────────────────
_lang = "zh"

TEXT = {
    "zh": {
        "subtitle":          "个人终端环境 · macOS & Linux",
        "step":              "步骤",
        "step_of":           "/",
        "title_language":    "语言 / Language",
        "hint_language":     "选择安装器的显示语言。",
        "title_modules":     "选择模块",
        "hint_modules":      "所有模块默认选中。Space/Enter 切换，c 继续，b 返回。",
        "note_modules":      "平台不支持的模块已自动过滤。",
        "title_pkgs":        "系统软件包",
        "hint_pkgs":         "是否安装 Homebrew / pacman 软件包？",
        "title_review":      "确认安装",
        "hint_review":       "确认以下内容，然后开始安装。",
        "option_lang_zh":    "中文",
        "option_lang_en":    "English",
        "option_pkgs_yes":   "安装软件包",
        "option_pkgs_yes_desc": "通过 Homebrew / pacman 安装所有工具包（推荐）。",
        "option_pkgs_no":    "跳过软件包",
        "option_pkgs_no_desc": "仅建立软链接，不安装系统包。",
        "option_install":    "开始安装",
        "option_install_desc": "建立软链，安装软件包，完成配置。",
        "option_back":       "返回",
        "option_quit":       "退出",
        "option_continue":   "继续",
        "label_lang":        "语言",
        "label_modules":     "模块",
        "label_pkgs":        "软件包",
        "footer_live":       "↑/↓ 移动 · Enter/Space 切换 · c 继续 · b 返回 · q 退出",
        "footer_live_single": "↑/↓ 移动 · Enter 确认 · b 返回 · q 退出",
        "footer_live_review": "↑/↓ 移动 · Enter 确认 · q 退出",
        "footer_text":       "输入数字 · Enter 确认 · b 返回 · q 退出",
        "footer_text_multi": "输入序号（逗号分隔）或留空 · Enter 确认 · b 返回 · q 退出",
        "current_summary":   "当前配置",
        "symlinks_title":    "建立软链接",
        "pkgs_title":        "安装软件包",
        "overrides_title":   "本地覆盖文件",
        "check_title":       "环境检查",
        "check_ok":          "✓  所有关键命令已就绪",
        "check_missing":     "缺少以下命令（重新运行安装器可修复）：",
        "backups":           "备份保存至：",
        "done":              "完成。",
        "aborted":           "已取消。",
        "brew_missing":      "✗  未找到 Homebrew，请先安装：https://brew.sh",
        "aur_missing":       "✗  未找到 AUR 助手（yay/paru），跳过：",
        "pkg_missing":       "✗  未找到支持的包管理器",
        "brew_lock_hint":    "Homebrew 检测到下载锁冲突：通常是另一条 brew 命令还在运行，或上次中断留下了 .incomplete 文件。先执行 `pgrep -af brew` 确认；如果没有残留进程，再删掉对应的 .incomplete 文件后重试。",
        "omt_ok":            "ok   oh-my-tmux 已安装",
        "omt_install":       "→    正在安装 oh-my-tmux…",
        "no_files":          "（模块暂无文件）",
        "skip_module":       "跳过（目录不存在）：",
        "npm_globals":       "npm 全局工具",
        "auto_notice":       "自动模式 · 安装当前平台全部模块",
        "dry_run_notice":    "预览模式 · 不执行任何写入操作",
        "default_tag":       " 默认",
        "title_conflicts":   "检测到已有工具",
        "hint_conflicts":    "安装器会安全接管，所有文件自动备份，可随时恢复。",
        "option_migrate":    "继续（自动处理冲突）",
        "option_migrate_desc": "备份现有配置，安装替代工具。",
        "option_keep":       "保持现状（跳过冲突处理）",
        "option_keep_desc":  "仅安装新配置，不干预已有工具。",
        "restore_title":     "恢复备份",
        "restore_hint":      "选择要恢复的备份版本。",
        "restore_none":      "未找到备份。请先运行安装器。",
        "restore_ok":        "已恢复：",
        "restore_skip":      "跳过（文件不存在）：",
        "uninstall_title":   "卸载 dotfiles",
        "uninstall_hint":    "移除所有托管软链，可选从备份恢复。",
        "uninstall_done":    "软链已移除。",
        "uninstall_restore": "是否恢复最近一次备份？",
        "conflict_migration": "冲突迁移",
    },
    "en": {
        "subtitle":          "Personal terminal environment · macOS & Linux",
        "step":              "Step",
        "step_of":           "/",
        "title_language":    "Language / 语言",
        "hint_language":     "Choose the display language for the installer.",
        "title_modules":     "Select modules",
        "hint_modules":      "All modules selected by default. Space/Enter to toggle, c to continue, b to go back.",
        "note_modules":      "Modules unsupported on this platform are filtered out.",
        "title_pkgs":        "System packages",
        "hint_pkgs":         "Install Homebrew / pacman packages?",
        "title_review":      "Review",
        "hint_review":       "Confirm the plan before installing.",
        "option_lang_zh":    "中文",
        "option_lang_en":    "English",
        "option_pkgs_yes":   "Install packages",
        "option_pkgs_yes_desc": "Install all tooling via Homebrew / pacman (recommended).",
        "option_pkgs_no":    "Skip packages",
        "option_pkgs_no_desc": "Symlinks only, skip system package installation.",
        "option_install":    "Install",
        "option_install_desc": "Symlink configs, install packages, and finish setup.",
        "option_back":       "Back",
        "option_quit":       "Quit",
        "option_continue":   "Continue",
        "label_lang":        "Language",
        "label_modules":     "Modules",
        "label_pkgs":        "Packages",
        "footer_live":       "↑/↓ move · Enter/Space toggle · c continue · b back · q quit",
        "footer_live_single": "↑/↓ move · Enter confirm · b back · q quit",
        "footer_live_review": "↑/↓ move · Enter confirm · q quit",
        "footer_text":       "Enter number · Enter confirm · b back · q quit",
        "footer_text_multi": "Enter numbers (comma-sep) or blank · Enter confirm · b back · q quit",
        "current_summary":   "Current plan",
        "symlinks_title":    "Symlinking configs",
        "pkgs_title":        "Installing packages",
        "overrides_title":   "Local override files",
        "check_title":       "Environment check",
        "check_ok":          "✓  All expected commands present",
        "check_missing":     "Missing commands (re-run installer to fix):",
        "backups":           "Backups saved to:",
        "done":              "Done.",
        "aborted":           "Aborted.",
        "brew_missing":      "✗  Homebrew not found. Install from https://brew.sh",
        "aur_missing":       "✗  No AUR helper (yay/paru), skipping:",
        "pkg_missing":       "✗  No supported package manager found",
        "brew_lock_hint":    "Homebrew hit a download lock. Usually another brew command is still running, or an interrupted run left behind an .incomplete file. Run `pgrep -af brew` first; if nothing is left, remove the matching .incomplete file and retry.",
        "omt_ok":            "ok   oh-my-tmux already installed",
        "omt_install":       "→    Installing oh-my-tmux…",
        "no_files":          "(no files in module yet)",
        "skip_module":       "skip (directory missing):",
        "npm_globals":       "npm globals",
        "auto_notice":       "Auto mode · installing all modules for this platform",
        "dry_run_notice":    "Dry-run mode · no changes will be written",
        "default_tag":       " default",
        "title_conflicts":   "Detected existing tools",
        "hint_conflicts":    "Installer can safely migrate; all replaced files are backed up and restorable.",
        "option_migrate":    "Continue (auto-resolve conflicts)",
        "option_migrate_desc": "Backup current files, then apply replacement setup.",
        "option_keep":       "Keep as-is (skip conflict handling)",
        "option_keep_desc":  "Install new config without touching existing tools.",
        "restore_title":     "Restore backup",
        "restore_hint":      "Select a backup snapshot to restore.",
        "restore_none":      "No backup found. Run installer first.",
        "restore_ok":        "Restored:",
        "restore_skip":      "Skip (file missing):",
        "uninstall_title":   "Uninstall dotfiles",
        "uninstall_hint":    "Remove all managed symlinks; optionally restore from backup.",
        "uninstall_done":    "Managed symlinks removed.",
        "uninstall_restore": "Restore the latest backup now?",
        "conflict_migration": "Conflict migration",
    },
}

def t(key: str) -> str:
    return TEXT[_lang].get(key, TEXT["en"].get(key, key))

# ── conflict detection ─────────────────────────────────────────────────────────
@dataclass
class ConflictInfo:
    tool: str
    replaces_with: str
    label_zh: str
    label_en: str
    desc_zh: str
    desc_en: str
    color: str = "#F97316"

    def label(self) -> str:
        return self.label_zh if _lang == "zh" else self.label_en

    def desc(self) -> str:
        return self.desc_zh if _lang == "zh" else self.desc_en


def _nvm_installed() -> bool:
    return (Path.home() / ".nvm" / "nvm.sh").exists() or bool(os.environ.get("NVM_DIR"))


def _pyenv_installed() -> bool:
    return bool(shutil.which("pyenv")) or (Path.home() / ".pyenv" / "bin" / "pyenv").exists()


def _rbenv_installed() -> bool:
    return bool(shutil.which("rbenv")) or (Path.home() / ".rbenv" / "bin" / "rbenv").exists()


def _rvm_installed() -> bool:
    return (Path.home() / ".rvm" / "scripts" / "rvm").exists()


def _omz_installed() -> bool:
    return (Path.home() / ".oh-my-zsh").is_dir()


ALL_CONFLICT_RULES: list[tuple] = [
    # (tool, replaces_with, detect_fn, label_zh, label_en, desc_zh, desc_en, color)
    (
        "asdf", "mise", lambda: bool(shutil.which("asdf")),
        "asdf  →  mise",
        "asdf  →  mise",
        "mise 直接读取 .tool-versions，已安装的配置零损失迁移。",
        "mise reads .tool-versions natively — zero-loss migration.",
        "#60A5FA",
    ),
    (
        "nvm", "mise", _nvm_installed,
        "nvm  →  mise",
        "nvm  →  mise",
        "mise 接管 Node 版本管理，读取 .nvmrc；现有 node 版本需用 mise 重装。",
        "mise takes over Node management, reads .nvmrc; reinstall node versions via mise.",
        "#84CC16",
    ),
    (
        "pyenv", "mise", _pyenv_installed,
        "pyenv  →  mise",
        "pyenv  →  mise",
        "mise 接管 Python 版本管理，读取 .python-version；现有 python 版本需用 mise 重装。",
        "mise takes over Python management, reads .python-version; reinstall python via mise.",
        "#FBBF24",
    ),
    (
        "rbenv", "mise", _rbenv_installed,
        "rbenv  →  mise",
        "rbenv  →  mise",
        "mise 接管 Ruby 版本管理，读取 .ruby-version；现有 ruby 版本需用 mise 重装。",
        "mise takes over Ruby management, reads .ruby-version; reinstall ruby via mise.",
        "#F43F5E",
    ),
    (
        "rvm", "mise", _rvm_installed,
        "rvm  →  mise",
        "rvm  →  mise",
        "mise 接管 Ruby 版本管理；rvm 目录 (~/.rvm) 保留不删。",
        "mise takes over Ruby management; rvm directory (~/.rvm) is left untouched.",
        "#FB923C",
    ),
    (
        "oh-my-zsh", "standalone zsh plugins", _omz_installed,
        "oh-my-zsh  →  独立插件",
        "oh-my-zsh  →  standalone plugins",
        "现有 ~/.zshrc 自动备份。新配置使用独立插件（自动补全、语法高亮、历史搜索），功能等价。",
        "Existing ~/.zshrc backed up. New config uses standalone plugins (autosuggestions, syntax-highlight, history-search) — same features.",
        "#A78BFA",
    ),
]


def detect_conflicts() -> list[ConflictInfo]:
    found: list[ConflictInfo] = []
    for tool, replaces, detect_fn, lzh, len_, dzh, den, color in ALL_CONFLICT_RULES:
        try:
            if detect_fn():
                found.append(ConflictInfo(
                    tool=tool, replaces_with=replaces,
                    label_zh=lzh, label_en=len_,
                    desc_zh=dzh, desc_en=den,
                    color=color,
                ))
        except Exception:
            pass
    return found


# ── module registry ────────────────────────────────────────────────────────────
# (key, label_zh, label_en, desc_zh, desc_en, color, platform_filter)
ALL_MODULES: list[tuple] = [
    ("zsh",        "zsh",        "zsh",
     "shell 配置、插件、别名，含智能补全与历史搜索",
     "shell config, plugins, aliases with smart completion",
     "#06B6D4", "all"),
    ("git",        "git",        "git",
     "全局配置，含 delta side-by-side diff",
     "global config with delta side-by-side diff",
     "#F97316", "all"),
    ("starship",   "starship",   "starship",
     "Gruvbox dark prompt，powerline 风格",
     "Gruvbox dark prompt with powerline style",
     "#FBBF24", "all"),
    ("atuin",      "atuin",      "atuin",
     "shell 历史数据库，支持跨设备同步",
     "shell history database with cross-device sync",
     "#A78BFA", "all"),
    ("mise",       "mise",       "mise",
     "运行时版本管理（Node、Python、Ruby…）",
     "runtime version manager (Node, Python, Ruby…)",
     "#60A5FA", "all"),
    ("nvim",       "neovim",     "neovim",
     "LazyVim 配置（LSP、Telescope、LazyGit）",
     "LazyVim config (LSP, Telescope, LazyGit)",
     "#22C55E", "all"),
    ("tmux",       "tmux",       "tmux",
     "oh-my-tmux 配置，含自定义主题",
     "oh-my-tmux config with custom theme",
     "#38BDF8", "all"),
    ("darwin",     "macOS",      "macOS",
     "macOS 专属设置",
     "macOS-specific settings",
     "#FB923C", "mac"),
    ("linux",      "Linux",      "Linux",
     "Linux 专属设置",
     "Linux-specific settings",
     "#84CC16", "linux"),
    ("hyprland",   "Hyprland",   "Hyprland",
     "Wayland 合成器配置",
     "Wayland compositor config",
     "#8B5CF6", "wayland"),
    ("quickshell", "QuickShell", "QuickShell",
     "桌面组件配置",
     "desktop widget config",
     "#14B8A6", "wayland"),
]

# ── platform detection ─────────────────────────────────────────────────────────
def detect_platform() -> dict:
    p: dict = {
        "os": platform.system(), "is_mac": False, "is_linux": False,
        "has_pacman": bool(shutil.which("pacman")),
        "has_brew":   bool(shutil.which("brew")),
        "is_wayland": False, "distro": "",
    }
    p["is_mac"]   = p["os"] == "Darwin"
    p["is_linux"] = p["os"] == "Linux"
    p["is_wayland"] = p["is_linux"] and bool(
        os.environ.get("WAYLAND_DISPLAY") or os.environ.get("XDG_SESSION_TYPE") == "wayland"
    )
    if p["is_linux"]:
        try:
            for line in Path("/etc/os-release").read_text().splitlines():
                if line.startswith("PRETTY_NAME="):
                    p["distro"] = line.split("=", 1)[1].strip().strip('"')
                    break
        except FileNotFoundError:
            pass
    return p

def eligible_modules(p: dict) -> list[tuple]:
    result = []
    for row in ALL_MODULES:
        key, lzh, len_, desc_zh, desc_en, color, filt = row
        label = lzh if _lang == "zh" else len_
        desc  = desc_zh if _lang == "zh" else desc_en
        if filt == "all":                                     result.append((key, label, desc, color))
        elif filt == "mac"     and p["is_mac"]:               result.append((key, label, desc, color))
        elif filt == "linux"   and p["is_linux"]:             result.append((key, label, desc, color))
        elif filt == "wayland" and p["is_wayland"]:           result.append((key, label, desc, color))
    return result

# ── banner ─────────────────────────────────────────────────────────────────────
def build_dotfiles_banner(width: int = 90) -> list[str]:
    """Last line is always the subtitle (styled dim by callers)."""
    subtitle = "personal terminal environment · macOS & Linux"
    if width < 72:
        return ["  SkyHua's Dotfiles", f"  {subtitle}"]
    if width >= 100:
        lines = [
            "  ███████╗██╗  ██╗██╗   ██╗██╗  ██╗██╗   ██╗ █████╗ ",
            "  ██╔════╝██║ ██╔╝╚██╗ ██╔╝██║  ██║██║   ██║██╔══██╗",
            "  ███████╗█████╔╝  ╚████╔╝ ███████║██║   ██║███████║",
            "  ╚════██║██╔═██╗   ╚██╔╝  ██╔══██║██║   ██║██╔══██║",
            "  ███████║██║  ██╗   ██║   ██║  ██║╚██████╔╝██║  ██║",
            "  ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝",
            f"  's Dotfiles  ·  {subtitle}",
        ]
        return [line[:width].rstrip() for line in lines]
    # medium: compact ASCII for "SkyHua's"
    lines = [
        "   ___  _     _  _             _ ",
        "  / __|| | __| || |_ _  _ __ _( )",
        "  \\__ \\| |/ /| ||  _| || / _` |/ ",
        "  |___/|_|\\_\\|_| \\__|\\_, \\__,_|  ",
        "                      |__/        ",
        f"  Dotfiles  ·  {subtitle}",
    ]
    return [line[:width].rstrip() for line in lines]

# ── selector row dataclass ─────────────────────────────────────────────────────
@dataclass(frozen=True)
class SelectorRow:
    value: str
    prefix: str
    marker: str
    marker_style: str
    label: str
    label_style: str
    description: str = ""
    description_style: str = "fg:#64748B italic"
    meta: str = ""
    meta_style: str = "fg:#64748B"
    is_pointed: bool = False
    checked: bool = False

# ── screen data ────────────────────────────────────────────────────────────────
STEP_ORDER = ("language", "conflicts", "modules", "packages", "review")

@dataclass
class Screen:
    step_id: str
    title: str
    hint: str
    options: list[tuple[str, str]]          # (value, label)
    descriptions: dict[str, str] = field(default_factory=dict)
    colors: dict[str, str] = field(default_factory=dict)
    default_value: str = "1"
    note: str = ""
    mode: str = "single"                    # "single" | "multi"

def _screen_width(c: "Console | None") -> int:
    if c is None:
        return 90
    try:
        return max(72, min(int(c.width), 160))
    except Exception:
        return 90

def _progress(step_id: str) -> str:
    idx = STEP_ORDER.index(step_id) + 1 if step_id in STEP_ORDER else 1
    total = len(STEP_ORDER)
    return f"{t('step')} {idx}{t('step_of')}{total}"

def _resolve_screen(step_id: str, plat: dict) -> Screen:
    if step_id == "language":
        return Screen(
            step_id="language",
            title=t("title_language"),
            hint=t("hint_language"),
            options=[("1", t("option_lang_zh")), ("2", t("option_lang_en"))],
            default_value="1" if _lang == "zh" else "2",
        )
    if step_id == "conflicts":
        return Screen(
            step_id="conflicts",
            title=t("title_conflicts"),
            hint=t("hint_conflicts"),
            options=[("1", t("option_migrate")), ("2", t("option_keep"))],
            descriptions={
                "1": t("option_migrate_desc"),
                "2": t("option_keep_desc"),
            },
            default_value="1",
        )
    if step_id == "modules":
        mods = eligible_modules(plat)
        options = [(str(i + 1), label) for i, (key, label, desc, color) in enumerate(mods)]
        descs   = {str(i + 1): desc  for i, (key, label, desc, color) in enumerate(mods)}
        colors  = {str(i + 1): color for i, (key, label, desc, color) in enumerate(mods)}
        return Screen(
            step_id="modules",
            title=t("title_modules"),
            hint=t("hint_modules"),
            options=options,
            descriptions=descs,
            colors=colors,
            default_value="1",
            note=t("note_modules"),
            mode="multi",
        )
    if step_id == "packages":
        return Screen(
            step_id="packages",
            title=t("title_pkgs"),
            hint=t("hint_pkgs"),
            options=[("1", t("option_pkgs_yes")), ("2", t("option_pkgs_no"))],
            descriptions={
                "1": t("option_pkgs_yes_desc"),
                "2": t("option_pkgs_no_desc"),
            },
            default_value="1",
        )
    # review
    return Screen(
        step_id="review",
        title=t("title_review"),
        hint=t("hint_review"),
        options=[("1", t("option_install")), ("2", t("option_back"))],
        descriptions={
            "1": t("option_install_desc"),
            "2": "",
        },
        default_value="1",
    )

def _build_rows(
    screen: Screen,
    *,
    pointed_value: str,
    checked_values: set[str],
    allow_back: bool,
) -> list[SelectorRow]:
    option_values = {v for v, _ in screen.options}
    rows: list[SelectorRow] = []
    for value, label in screen.options:
        is_pointed = value == pointed_value
        checked    = value in checked_values
        color = screen.colors.get(value, "#7DD3FC")
        prefix = "❯ " if is_pointed else "  "

        if screen.mode == "multi":
            if checked:
                marker_style = f"fg:{color} bold"
                marker = "●"
            else:
                marker_style = "fg:#64748B"
                marker = "○"
        else:
            marker, marker_style = "", ""

        if is_pointed:
            label_style = f"fg:{color} bold"
        elif value == screen.default_value and screen.mode == "single":
            label_style = "fg:#F8FAFC bold"
        else:
            label_style = "fg:#CBD5E1"

        meta = t("default_tag") if (value == screen.default_value and screen.mode == "single" and not is_pointed) else ""
        rows.append(SelectorRow(
            value=value, prefix=prefix,
            marker=marker, marker_style=marker_style,
            label=label, label_style=label_style,
            description=screen.descriptions.get(value, ""),
            is_pointed=is_pointed, checked=checked,
            meta=meta,
        ))

    # multi-select: "Continue" row
    if screen.mode == "multi":
        is_c = pointed_value == "c"
        rows.append(SelectorRow(
            value="c", prefix="❯ " if is_c else "  ",
            marker="", marker_style="",
            label=t("option_continue"),
            label_style="fg:#7DD3FC bold" if is_c else "fg:#CBD5E1",
            is_pointed=is_c,
        ))

    # back row (not on review, not on first screen)
    if allow_back and screen.step_id not in ("review",):
        is_b = pointed_value == "b"
        rows.append(SelectorRow(
            value="b", prefix="❯ " if is_b else "  ",
            marker="", marker_style="",
            label=t("option_back"),
            label_style="fg:#7DD3FC bold" if is_b else "fg:#64748B",
            is_pointed=is_b,
        ))

    # quit row
    is_q = pointed_value == "q"
    rows.append(SelectorRow(
        value="q", prefix="❯ " if is_q else "  ",
        marker="", marker_style="",
        label=t("option_quit"),
        label_style="fg:#7DD3FC bold" if is_q else "fg:#64748B",
        is_pointed=is_q,
    ))
    return rows

# ── print header (banner + progress + hint) ───────────────────────────────────
def _print_header(
    screen: Screen,
    *,
    console_obj: "Console | None",
    state: dict,
    clear: bool = True,
) -> None:
    if clear:
        if console_obj:
            console_obj.clear()
        else:
            print("\033[2J\033[H", end="")

    width = _screen_width(console_obj)
    banner_lines = build_dotfiles_banner(width)
    for i, line in enumerate(banner_lines):
        style = "dim" if i == len(banner_lines) - 1 else "bold #7DD3FC"
        if console_obj:
            console_obj.print(Text(line, style=style))
        else:
            print(line)

    prog = f"  {_progress(screen.step_id)}  ·  {screen.title}"
    if console_obj:
        console_obj.print()
        console_obj.print(Text(prog, style="bold"))
        console_obj.print(Text(f"  {screen.hint}", style="dim"))
        if screen.note:
            console_obj.print(Text(f"  {screen.note}", style="dim italic"))
    else:
        print(f"\n{prog}")
        print(f"  {screen.hint}")
        if screen.note:
            print(f"  {screen.note}")

    # conflict preview
    if screen.step_id == "conflicts" and state.get("conflicts"):
        if console_obj:
            console_obj.print()
            for c in state["conflicts"]:
                console_obj.print(f"  [bold {c.color}]● {c.label()}[/bold {c.color}]")
                console_obj.print(Text(f"      {c.desc()}", style="dim italic"))
        else:
            print()
            for c in state["conflicts"]:
                print(f"  ● {c.label()}")
                print(f"      {c.desc()}")

    # summary sidebar (only after language set)
    if console_obj and state.get("lang"):
        lang_label = "中文" if state["lang"] == "zh" else "English"
        mods_label = ", ".join(state.get("modules", [])) or "—"
        pkgs_label = t("option_pkgs_yes") if state.get("install_pkgs", True) else t("option_pkgs_no")
        summary = (
            f"  [dim]{t('label_lang')}:[/dim] {lang_label}  "
            f"[dim]{t('label_pkgs')}:[/dim] {pkgs_label}"
        )
        if state.get("modules"):
            summary += f"\n  [dim]{t('label_modules')}:[/dim] {mods_label}"
        console_obj.print()
        console_obj.print(summary)

    if console_obj:
        console_obj.print()
    else:
        print()

# ── plain-text renderer (fallback + testing) ──────────────────────────────────
def render_screen(
    screen: Screen,
    *,
    checked_values: set[str] | None = None,
    allow_back: bool = True,
) -> str:
    checked = checked_values or set()
    buf = StringIO()
    c = Console(file=buf, force_terminal=False, color_system=None, width=90)
    banner_lines = build_dotfiles_banner(90)
    for i, line in enumerate(banner_lines):
        style = "dim" if i == len(banner_lines) - 1 else "bold"
        c.print(Text(line, style=style))
    c.print()
    c.print(Text(f"  {_progress(screen.step_id)}  ·  {screen.title}", style="bold"))
    c.print(Text(f"  {screen.hint}", style="dim"))
    if screen.note:
        c.print(Text(f"  {screen.note}", style="dim italic"))
    c.print()
    rows = _build_rows(screen, pointed_value=screen.default_value, checked_values=checked, allow_back=allow_back)
    for row in rows:
        prefix = "❯ " if row.is_pointed else "  "
        if row.marker:
            c.print(f"{prefix}{row.marker} {row.value}. {row.label}{row.meta}")
        else:
            c.print(f"{prefix}{row.value}. {row.label}{row.meta}")
        if row.description:
            c.print(Text(f"      {row.description}", style="dim italic"))
    c.print()
    footer_key = "footer_live" if screen.mode == "multi" else (
        "footer_live_review" if screen.step_id == "review" else "footer_live_single"
    )
    c.print(Text(t(footer_key), style="dim"))
    return buf.getvalue().rstrip() + "\n"

# ── prompt_toolkit live selector ──────────────────────────────────────────────
def _select_with_prompt_toolkit(
    screen: Screen,
    *,
    checked_values: set[str],
    allow_back: bool,
    console_obj: "Console | None",
    state: dict,
) -> str:
    from prompt_toolkit.application import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.layout import Layout, Window
    from prompt_toolkit.layout.controls import FormattedTextControl

    _print_header(screen, console_obj=console_obj, state=state, clear=True)

    option_values = [v for v, _ in screen.options]
    rows_initial  = _build_rows(screen, pointed_value=screen.default_value,
                                checked_values=checked_values, allow_back=allow_back)
    all_values    = [r.value for r in rows_initial]
    pointed_index = all_values.index(screen.default_value) if screen.default_value in all_values else 0

    live_checked = set(checked_values)

    footer_key = "footer_live" if screen.mode == "multi" else (
        "footer_live_review" if screen.step_id == "review" else "footer_live_single"
    )
    live_footer = t(footer_key)

    def _current() -> str:
        return all_values[pointed_index]

    def _move(offset: int) -> None:
        nonlocal pointed_index
        pointed_index = (pointed_index + offset) % len(all_values)

    def _toggle(val: str) -> None:
        if val not in option_values:
            return
        if val in live_checked:
            if len(live_checked) > 1:
                live_checked.discard(val)
        else:
            live_checked.add(val)

    def _tokens():
        rows = _build_rows(screen, pointed_value=_current(),
                           checked_values=live_checked, allow_back=allow_back)
        frags: list[tuple[str, str]] = []
        for row in rows:
            frags.append(("", row.prefix))
            if row.marker:
                frags.append((row.marker_style, f"{row.marker} "))
            frags.append((row.label_style, row.label))
            if row.meta:
                frags.append((row.meta_style, row.meta))
            frags.append(("", "\n"))
            if row.description and row.is_pointed:
                frags.append(("", "      "))
                frags.append((row.description_style, row.description))
                frags.append(("", "\n"))
        frags.append(("fg:#64748B", f"\n  {live_footer}"))
        return frags

    kb = KeyBindings()

    @kb.add(Keys.Down, eager=True)
    def _down(event) -> None:
        _move(1)

    @kb.add(Keys.Up, eager=True)
    def _up(event) -> None:
        _move(-1)

    if screen.mode == "multi":
        @kb.add(" ", eager=True)
        def _space(event) -> None:
            cur = _current()
            if cur in option_values:
                _toggle(cur)

    @kb.add(Keys.ControlC, eager=True)
    @kb.add(Keys.Escape, eager=True)
    def _abort(event) -> None:
        event.app.exit(result="q")

    @kb.add(Keys.ControlM, eager=True)
    def _enter(event) -> None:
        cur = _current()
        if cur in ("b", "q"):
            event.app.exit(result=cur)
            return
        if screen.mode == "multi":
            if cur == "c":
                ordered = [v for v in option_values if v in live_checked]
                event.app.exit(result=",".join(ordered))
                return
            if cur in option_values:
                _toggle(cur)
                return
        event.app.exit(result=cur)

    @kb.add("q", eager=True)
    def _quit(event) -> None:
        event.app.exit(result="q")

    if screen.mode == "multi":
        @kb.add("c", eager=True)
        def _cont(event) -> None:
            ordered = [v for v in option_values if v in live_checked]
            event.app.exit(result=",".join(ordered))

    if allow_back and screen.step_id not in ("review",):
        @kb.add("b", eager=True)
        def _back(event) -> None:
            event.app.exit(result="b")

    for key in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0"):
        @kb.add(key, eager=True)
        def _pick(event, k=key) -> None:
            if k not in all_values:
                return
            nonlocal pointed_index
            pointed_index = all_values.index(k)
            if screen.mode == "multi" and k in option_values:
                _toggle(k)
            elif screen.mode == "single":
                event.app.exit(result=k)

    # Try to use /dev/tty so curl|bash works
    pt_input = None
    try:
        from prompt_toolkit.input.vt100 import Vt100Input
        pt_input = Vt100Input(open("/dev/tty", "rb", buffering=0))
    except Exception:
        pass

    app = Application(
        layout=Layout(Window(
            FormattedTextControl(_tokens, focusable=True, show_cursor=False),
            dont_extend_height=True,
            always_hide_cursor=True,
        )),
        key_bindings=kb,
        full_screen=False,
        mouse_support=False,
        **({"input": pt_input} if pt_input else {}),
    )
    choice = app.run()
    if choice is None:
        return "q"
    return str(choice)

# ── fallback text selector ─────────────────────────────────────────────────────
def _select_fallback(
    screen: Screen,
    *,
    checked_values: set[str],
    allow_back: bool,
    console_obj: "Console | None",
    state: dict,
) -> str:
    _print_header(screen, console_obj=console_obj, state=state, clear=True)
    # print options
    for value, label in screen.options:
        if screen.mode == "multi":
            mark = "●" if value in checked_values else "○"
            desc = screen.descriptions.get(value, "")
            if console_obj:
                color = screen.colors.get(value, "white")
                console_obj.print(f"  {mark} [bold]{value}.[/bold] [{color}]{label}[/{color}]")
                if desc:
                    console_obj.print(Text(f"      {desc}", style="dim italic"))
            else:
                print(f"  {mark} {value}. {label}")
                if desc:
                    print(f"      {desc}")
        else:
            desc = screen.descriptions.get(value, "")
            is_def = value == screen.default_value
            if console_obj:
                console_obj.print(f"  [bold]{value}.[/bold]  {label}{'  [dim]' + t('default_tag').strip() + '[/dim]' if is_def else ''}")
                if desc:
                    console_obj.print(Text(f"      {desc}", style="dim italic"))
            else:
                print(f"  {value}.  {label}{'  (' + t('default_tag').strip() + ')' if is_def else ''}")
                if desc:
                    print(f"      {desc}")

    footer_key = "footer_text_multi" if screen.mode == "multi" else "footer_text"
    footer = t(footer_key)
    if console_obj:
        console_obj.print()
        console_obj.print(Text(f"  {footer}", style="dim"))
    else:
        print(f"\n  {footer}")

    return _raw_input("\n  > ", default=screen.default_value).strip()

# ── top-level ask ──────────────────────────────────────────────────────────────
def _ask(
    screen: Screen,
    *,
    checked_values: set[str],
    allow_back: bool,
    state: dict,
) -> str:
    if _HAS_PT and _tty_is_interactive():
        try:
            return _select_with_prompt_toolkit(
                screen,
                checked_values=checked_values,
                allow_back=allow_back,
                console_obj=console,
                state=state,
            )
        except Exception:
            pass
    return _select_fallback(
        screen,
        checked_values=checked_values,
        allow_back=allow_back,
        console_obj=console,
        state=state,
    )

# ── step: language ─────────────────────────────────────────────────────────────
def step_language(state: dict) -> str | None:
    """Returns 'zh'/'en', 'back', or None (quit)."""
    screen = _resolve_screen("language", {})
    while True:
        raw = _ask(screen, checked_values=set(), allow_back=False, state=state)
        if raw == "q":
            return None
        if raw == "1":
            return "zh"
        if raw == "2":
            return "en"

def step_conflicts(state: dict) -> "bool | str | None":
    conflicts: list[ConflictInfo] = state.get("conflicts", [])
    if not conflicts:
        return True
    screen = _resolve_screen("conflicts", {})
    while True:
        raw = _ask(screen, checked_values=set(), allow_back=True, state=state)
        if raw == "q":
            return None
        if raw == "b":
            return "back"
        if raw in ("1", ""):
            state["resolve_conflicts"] = True
            return True
        if raw == "2":
            state["resolve_conflicts"] = False
            return True


def step_modules(plat: dict, state: dict) -> "tuple[list[str], bool] | str | None":
    """Returns (modules_list, _), 'back', or None (quit)."""
    screen = _resolve_screen("modules", plat)
    mods = eligible_modules(plat)
    # default: all selected
    all_vals = {str(i + 1) for i in range(len(mods))}
    checked  = set(all_vals)

    while True:
        raw = _ask(screen, checked_values=checked, allow_back=True, state=state)
        if raw == "q":
            return None
        if raw == "b":
            return "back"

        # multi-select: "c" or comma-list comes back
        if raw == "c":
            break
        if "," in raw or raw.isdigit():
            # prompt_toolkit returns comma-joined list of selected values
            selected_vals = {v.strip() for v in raw.split(",") if v.strip()}
            if selected_vals:
                checked = selected_vals
            break

    # convert checked value strings → module keys
    result_keys = [mods[int(v) - 1][0] for v in sorted(checked, key=lambda x: int(x)) if v.isdigit() and 0 < int(v) <= len(mods)]
    return result_keys, True

# ── step: packages ─────────────────────────────────────────────────────────────
def step_packages(plat: dict, state: dict) -> "bool | str | None":
    screen = _resolve_screen("packages", plat)
    while True:
        raw = _ask(screen, checked_values=set(), allow_back=True, state=state)
        if raw == "q":
            return None
        if raw == "b":
            return "back"
        if raw in ("1", ""):
            return True
        if raw == "2":
            return False

# ── step: review ───────────────────────────────────────────────────────────────
def step_review(plat: dict, state: dict) -> "bool | str | None":
    screen = _resolve_screen("review", plat)
    while True:
        raw = _ask(screen, checked_values=set(), allow_back=True, state=state)
        if raw == "q":
            return None
        if raw == "2":
            return "back"
        if raw in ("1", ""):
            return True

# ── symlink engine ─────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
_backup_root: Path | None = None

def _get_backup_root() -> Path:
    global _backup_root
    if _backup_root is None:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        _backup_root = Path.home() / ".dotfiles-backups" / ts
        _backup_root.mkdir(parents=True, exist_ok=True)
    return _backup_root

def _log(msg: str) -> None:
    if console:
        console.print(msg)
    else:
        # strip rich markup
        import re
        print(re.sub(r'\[/?[^\]]+\]', '', msg))

def link_file(src: Path, rel: str, dry_run: bool) -> None:
    dest = Path.home() / rel
    if dry_run:
        _log(f"  [dim]dry[/dim]  {rel}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() and dest.resolve() == src.resolve():
        _log(f"  [green]ok[/green]   {rel}")
        return
    if dest.exists() or dest.is_symlink():
        bak = _get_backup_root() / rel
        bak.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dest), str(bak))
        _log(f"  [yellow]bak[/yellow]  {rel}")
    dest.symlink_to(src)
    _log(f"  [cyan]ln[/cyan]   {rel}")

def install_module(module: str, dry_run: bool) -> None:
    module_root = REPO_ROOT / module
    if not module_root.is_dir():
        _log(f"  [dim]{t('skip_module')} {module}[/dim]")
        return
    linked = 0
    for src in sorted(module_root.rglob("*")):
        if src.is_dir() or src.name == ".gitkeep":
            continue
        link_file(src, str(src.relative_to(module_root)), dry_run)
        linked += 1
    if linked == 0:
        _log(f"  [dim]{t('no_files')}[/dim]")
    if module == "tmux":
        _setup_oh_my_tmux(dry_run)


def backup_path_exists(rel: str) -> bool:
    return any((snap / rel).exists() for snap in sorted_backup_snapshots())


def sorted_backup_snapshots() -> list[Path]:
    root = Path.home() / ".dotfiles-backups"
    if not root.exists():
        return []
    return sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)


def restore_snapshot(snapshot: Path, *, dry_run: bool) -> None:
    if not snapshot.exists() or not snapshot.is_dir():
        return
    for src in sorted(snapshot.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(snapshot)
        dest = Path.home() / rel
        if not src.exists():
            _log(f"  [dim]{t('restore_skip')} {rel}[/dim]")
            continue
        if dry_run:
            _log(f"  [dim]dry[/dim]  restore {rel}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() or dest.is_symlink():
            if dest.is_dir() and not dest.is_symlink():
                shutil.rmtree(dest)
            else:
                dest.unlink() if dest.is_symlink() or dest.is_file() else shutil.rmtree(dest)
        shutil.move(str(src), str(dest))
        _log(f"  [cyan]rs[/cyan]   {rel}")


def remove_managed_symlinks(modules: list[str], *, dry_run: bool) -> None:
    for module in modules:
        module_root = REPO_ROOT / module
        if not module_root.is_dir():
            continue
        for src in sorted(module_root.rglob("*")):
            if src.is_dir() or src.name == ".gitkeep":
                continue
            rel = src.relative_to(module_root)
            dest = Path.home() / rel
            try:
                if dest.is_symlink() and dest.resolve() == src.resolve():
                    if dry_run:
                        _log(f"  [dim]dry[/dim]  unlink {rel}")
                    else:
                        dest.unlink()
                        _log(f"  [yellow]rm[/yellow]   {rel}")
            except Exception:
                pass

def copy_if_missing(src: Path, dest: Path, dry_run: bool) -> None:
    if dest.exists():
        return
    rel = str(dest.relative_to(Path.home()))
    if dry_run:
        _log(f"  [dim]dry[/dim]  {rel}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    _log(f"  [cyan]cp[/cyan]   {rel}")

def scaffold_overrides(dry_run: bool) -> None:
    examples = REPO_ROOT / "examples"
    hostname = platform.node().split(".")[0]
    for src, dest in [
        (examples / "gitconfig.local.example",     Path.home() / ".gitconfig.local"),
        (examples / "local.zsh.example",           Path.home() / ".config/dotfiles/local.zsh"),
        (examples / "local.zprofile.example",      Path.home() / ".config/dotfiles/local.zprofile"),
        (examples / "hosts/host.zsh.example",      Path.home() / f".config/dotfiles/hosts/{hostname}.zsh"),
        (examples / "hosts/host.zprofile.example", Path.home() / f".config/dotfiles/hosts/{hostname}.zprofile"),
    ]:
        if src.exists():
            copy_if_missing(src, dest, dry_run)

def _setup_oh_my_tmux(dry_run: bool) -> None:
    tmux_dir  = Path.home() / ".tmux"
    tmux_conf = Path.home() / ".tmux.conf"
    if tmux_dir.is_dir() and (tmux_dir / ".tmux.conf").exists():
        _log(f"  [green]{t('omt_ok')}[/green]")
    else:
        _log(f"  [cyan]{t('omt_install')}[/cyan]")
        _run(["git", "clone", "--depth=1", "https://github.com/gpakosz/.tmux.git", str(tmux_dir)], dry_run)
    src = tmux_dir / ".tmux.conf"
    if not dry_run and not (tmux_conf.is_symlink() and tmux_conf.resolve() == src):
        if tmux_conf.exists() or tmux_conf.is_symlink():
            shutil.move(str(tmux_conf), str(_get_backup_root() / ".tmux.conf"))
        tmux_conf.symlink_to(src)
        _log("  [cyan]ln[/cyan]   .tmux.conf")

def apply_conflict_resolution(conflicts: list[ConflictInfo], *, dry_run: bool) -> None:
    if not conflicts:
        return
    _log(f"\n[bold]{t('conflict_migration')}[/bold]")
    for c in conflicts:
        _log(f"  [bold {c.color}]· {c.label()}[/bold {c.color}]")
        _log(f"    [dim]{c.desc()}[/dim]")

        if c.tool == "asdf":
            src = Path.home() / ".tool-versions"
            dst = Path.home() / ".config" / "mise" / "config.toml"
            if src.exists() and not dry_run:
                # keep source; no destructive move needed
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists():
                    lines = [ln.strip() for ln in src.read_text().splitlines() if ln.strip() and not ln.strip().startswith("#")]
                    mapped: list[str] = []
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 2:
                            tool = parts[0]
                            ver = parts[1]
                            if tool == "nodejs":
                                tool = "node"
                            mapped.append(f'{tool} = "{ver}"')
                    if mapped:
                        dst.write_text("[tools]\n" + "\n".join(mapped) + "\n")
                        _log("    [cyan]cp[/cyan]   .tool-versions -> .config/mise/config.toml")


def run_restore(*, dry_run: bool) -> None:
    snaps = sorted_backup_snapshots()
    if not snaps:
        _log(f"\n[yellow]{t('restore_none')}[/yellow]\n")
        return
    if console:
        _log(f"\n[bold]{t('restore_title')}[/bold]")
        _log(f"[dim]{t('restore_hint')}[/dim]\n")
        for i, s in enumerate(snaps[:20], 1):
            _log(f"  {i}. {s.name}")
    raw = _raw_input("\n  > ", default="1").strip()
    if not raw.isdigit():
        _log(t("aborted"))
        return
    idx = int(raw) - 1
    if idx < 0 or idx >= len(snaps[:20]):
        _log(t("aborted"))
        return
    chosen = snaps[idx]
    _log(f"\n[bold]{t('restore_ok')}[/bold] {chosen}\n")
    restore_snapshot(chosen, dry_run=dry_run)


def run_uninstall(plat: dict, *, dry_run: bool, restore: bool) -> None:
    mods = [k for k, *_ in eligible_modules(plat)]
    _log(f"\n[bold]{t('uninstall_title')}[/bold]")
    _log(f"[dim]{t('uninstall_hint')}[/dim]\n")
    remove_managed_symlinks(mods, dry_run=dry_run)
    _log(f"\n[green]{t('uninstall_done')}[/green]")
    if restore:
        run_restore(dry_run=dry_run)


# ── packages ───────────────────────────────────────────────────────────────────
INSTALL_LOG = Path.home() / ".dotfiles-install.log"


def _write_install_log(cmd: list[str], stdout: str, stderr: str) -> None:
    try:
        INSTALL_LOG.parent.mkdir(parents=True, exist_ok=True)
        with INSTALL_LOG.open("a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("$ " + " ".join(cmd) + "\n")
            if stdout:
                f.write("\n[stdout]\n" + stdout + ("\n" if not stdout.endswith("\n") else ""))
            if stderr:
                f.write("\n[stderr]\n" + stderr + ("\n" if not stderr.endswith("\n") else ""))
    except Exception:
        pass


def _brew_bundle_plan() -> tuple[list[str], dict[str, str], bool]:
    cmd = [
        "brew",
        "bundle",
        "--verbose",
        "--no-upgrade",
        "--file",
        str(REPO_ROOT / "packages" / "Brewfile"),
    ]
    env = {"HOMEBREW_NO_AUTO_UPDATE": "1"}
    return cmd, env, True


def _brew_bundle_lock_hint(output: str) -> str | None:
    lowered = output.lower()
    if "process has already locked" in lowered and ".incomplete" in lowered:
        return t("brew_lock_hint")
    return None


def _mise_install_plan() -> tuple[list[str], bool]:
    return ["mise", "install", "-y"], True


def _run(
    cmd: list[str],
    dry_run: bool,
    *,
    env: dict[str, str] | None = None,
    stream_output: bool = False,
) -> tuple[int, str, str]:
    _log("  [dim]$[/dim]  " + " ".join(cmd))
    if dry_run:
        return 0, "", ""
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    try:
        if stream_output:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=run_env,
            )
            output_lines: list[str] = []
            assert proc.stdout is not None
            for line in proc.stdout:
                output_lines.append(line)
                sys.stdout.write(line)
                sys.stdout.flush()
            proc.stdout.close()
            rc = proc.wait()
            stdout = "".join(output_lines)
            _write_install_log(cmd, stdout, "")
            return rc, stdout, ""

        proc = subprocess.run(cmd, capture_output=True, text=True, env=run_env)
    except KeyboardInterrupt:
        _log(f"\n[yellow]{t('aborted')}[/yellow]")
        raise SystemExit(130)
    _write_install_log(cmd, proc.stdout or "", proc.stderr or "")
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _npm_global_root() -> Path | None:
    try:
        proc = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True)
        if proc.returncode != 0:
            return None
        root = proc.stdout.strip()
        return Path(root) if root else None
    except Exception:
        return None


def _cleanup_npm_stale_dirs(pkgs: list[str], *, dry_run: bool) -> None:
    root = _npm_global_root()
    if root is None:
        return
    for pkg in pkgs:
        parts = pkg.split("/")
        if pkg.startswith("@") and len(parts) == 2:
            scope = parts[0]
            name = parts[1]
            target = root / scope / name
            stale_glob = root / scope
            stale_pattern = f".{name}-*"
        else:
            name = pkg
            target = root / name
            stale_glob = root
            stale_pattern = f".{name}-*"

        for path in [target, *stale_glob.glob(stale_pattern)]:
            if not path.exists():
                continue
            if dry_run:
                _log(f"  [dim]dry[/dim]  cleanup {path}")
                continue
            try:
                if path.is_symlink() or path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                _log(f"  [yellow]fix[/yellow]  removed stale npm dir: {path}")
            except Exception:
                pass


def install_packages(p: dict, dry_run: bool) -> None:
    if p["is_mac"]:
        if not p["has_brew"]:
            _log(f"  [yellow]{t('brew_missing')}[/yellow]")
        else:
            brew_cmd, brew_env, brew_stream = _brew_bundle_plan()
            rc, stdout, stderr = _run(
                brew_cmd,
                dry_run,
                env=brew_env,
                stream_output=brew_stream,
            )
            if rc == 0:
                _log("  [green]ok[/green]   brew bundle")
            else:
                hint = _brew_bundle_lock_hint("\n".join(part for part in (stdout, stderr) if part))
                if hint:
                    _log(f"  [yellow]hint[/yellow] {hint}")
                _log(f"  [yellow]warn[/yellow] brew bundle failed, details: {INSTALL_LOG}")
    elif p["is_linux"] and p["has_pacman"]:
        plist = REPO_ROOT / "packages" / "cachyos-pacman.txt"
        pkgs  = [l.strip() for l in plist.read_text().splitlines() if l.strip() and not l.startswith("#")]
        rc, _, _ = _run(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + pkgs, dry_run)
        if rc == 0:
            _log("  [green]ok[/green]   pacman packages")
        else:
            _log(f"  [yellow]warn[/yellow] pacman install failed, details: {INSTALL_LOG}")
        aur   = REPO_ROOT / "packages" / "cachyos-aur.txt"
        if aur.exists():
            apkgs = [l.strip() for l in aur.read_text().splitlines() if l.strip() and not l.startswith("#")]
            helper = shutil.which("yay") or shutil.which("paru")
            if helper and apkgs:
                rc, _, _ = _run([helper, "-S", "--needed", "--noconfirm"] + apkgs, dry_run)
                if rc == 0:
                    _log("  [green]ok[/green]   aur packages")
                else:
                    _log(f"  [yellow]warn[/yellow] AUR install failed, details: {INSTALL_LOG}")
            elif apkgs:
                _log(f"  [yellow]{t('aur_missing')} {', '.join(apkgs)}[/yellow]")
    else:
        _log(f"  [yellow]{t('pkg_missing')}[/yellow]")

    mise_config = Path.home() / ".config" / "mise" / "config.toml"
    if mise_config.exists() and (dry_run or shutil.which("mise")):
        mise_cmd, mise_stream = _mise_install_plan()
        _log("\n  [dim]mise[/dim]")
        rc, _, _ = _run(mise_cmd, dry_run, stream_output=mise_stream)
        if rc == 0:
            _log("  [green]ok[/green]   mise runtimes")
        else:
            _log(f"  [yellow]warn[/yellow] mise install failed, details: {INSTALL_LOG}")

    npm_list = REPO_ROOT / "packages" / "npm-global.txt"
    if npm_list.exists() and shutil.which("npm"):
        pkgs = [l.strip() for l in npm_list.read_text().splitlines() if l.strip() and not l.startswith("#")]
        if pkgs:
            _log(f"\n  [dim]{t('npm_globals')}[/dim]")
            rc, _, err = _run(["npm", "install", "-g"] + pkgs, dry_run)
            if rc != 0 and ("ENOTEMPTY" in err or "rename" in err):
                _log("  [yellow]warn[/yellow] npm found stale directories, cleaning and retrying...")
                _cleanup_npm_stale_dirs(pkgs, dry_run=dry_run)
                rc, _, _ = _run(["npm", "install", "-g"] + pkgs, dry_run)
            if rc == 0:
                _log("  [green]ok[/green]   npm globals")
            else:
                _log(f"  [yellow]warn[/yellow] npm install failed, details: {INSTALL_LOG}")

# ── env check ──────────────────────────────────────────────────────────────────
EXPECTED_CMDS = [
    ("zsh","zsh"),("starship","starship"),("atuin","atuin"),("zoxide","zoxide"),
    ("eza","eza"),("bat","bat"),("rg","ripgrep"),("fd","fd"),("delta","delta"),("mise","mise"),
]

def check_env() -> None:
    missing = [label for cmd, label in EXPECTED_CMDS if not shutil.which(cmd)]
    if missing:
        _log(f"  [yellow]{t('check_missing')}[/yellow]")
        for m in missing:
            _log(f"    [yellow]· {m}[/yellow]")
    else:
        _log(f"  [green]{t('check_ok')}[/green]")

# ── do install ─────────────────────────────────────────────────────────────────
def do_install(modules: list[str], install_pkgs: bool, plat: dict, dry_run: bool) -> None:
    _clear()
    if dry_run:
        _log(f"\n[yellow]{t('dry_run_notice')}[/yellow]\n")

    _log(f"\n[bold]{t('symlinks_title')}[/bold]")
    for mod in modules:
        _log(f"\n  [bold]{mod}[/bold]")
        install_module(mod, dry_run)

    _log(f"\n[bold]{t('overrides_title')}[/bold]")
    scaffold_overrides(dry_run)

    if install_pkgs:
        _log(f"\n[bold]{t('pkgs_title')}[/bold]")
        install_packages(plat, dry_run)

    if not dry_run:
        _log(f"\n[bold]{t('check_title')}[/bold]")
        check_env()
        if _backup_root:
            _log(f"\n[dim]{t('backups')} {_backup_root}[/dim]")

    _log(f"\n[bold green]{t('done')}[/bold green]\n")

# ── main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    global _lang

    ap = argparse.ArgumentParser(
        description="dotfiles setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Modes
            ──────────────────────────────────────
            (default)    Interactive wizard
            --auto       Automatic, no prompts
            --restore    Restore from backup snapshot
            --uninstall  Remove managed symlinks

            Options
            ──────────────────────────────────────
            --dry-run    Preview only, no writes
            --link-only  Symlinks only, skip packages
            --pkgs-only  Packages only, skip symlinks
            --rollback   (with --uninstall) restore latest backup
        """),
    )
    ap.add_argument("--auto",      action="store_true")
    ap.add_argument("--dry-run",   action="store_true")
    ap.add_argument("--link-only", action="store_true")
    ap.add_argument("--pkgs-only", action="store_true")
    ap.add_argument("--restore",   action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--rollback",  action="store_true")
    args = ap.parse_args()

    plat = detect_platform()

    if args.restore:
        run_restore(dry_run=args.dry_run)
        return

    if args.uninstall:
        run_uninstall(plat, dry_run=args.dry_run, restore=args.rollback)
        return

    # ── auto mode ──────────────────────────────────────────────────────────────
    if args.auto:
        modules      = [k for k, *_ in eligible_modules(plat)]
        install_pkgs = not args.link_only
        conflicts = detect_conflicts()
        apply_conflict_resolution(conflicts, dry_run=args.dry_run)
        do_install(modules, install_pkgs and not args.pkgs_only, plat, args.dry_run)
        return

    # ── interactive wizard ─────────────────────────────────────────────────────
    state: dict = {
        "lang": None,
        "modules": [],
        "install_pkgs": True,
        "conflicts": detect_conflicts(),
        "resolve_conflicts": True,
    }
    history: list[str] = []
    screen_id = "language"

    while True:
        if screen_id == "language":
            result = step_language(state)
            if result is None:
                print(t("aborted"))
                sys.exit(0)
            _lang = result
            state["lang"] = result
            history.append(screen_id)
            screen_id = "conflicts"

        elif screen_id == "conflicts":
            result = step_conflicts(state)
            if result is None:
                print(t("aborted"))
                sys.exit(0)
            if result == "back":
                screen_id = history.pop() if history else "language"
                continue
            history.append(screen_id)
            screen_id = "modules"

        elif screen_id == "modules":
            result = step_modules(plat, state)
            if result is None:
                print(t("aborted"))
                sys.exit(0)
            if result == "back":
                screen_id = history.pop() if history else "language"
                continue
            modules, _ = result
            state["modules"] = modules
            history.append(screen_id)
            screen_id = "packages"

        elif screen_id == "packages":
            result = step_packages(plat, state)
            if result is None:
                print(t("aborted"))
                sys.exit(0)
            if result == "back":
                screen_id = history.pop() if history else "modules"
                continue
            state["install_pkgs"] = bool(result)
            history.append(screen_id)
            screen_id = "review"

        elif screen_id == "review":
            result = step_review(plat, state)
            if result is None:
                print(t("aborted"))
                sys.exit(0)
            if result == "back":
                screen_id = history.pop() if history else "packages"
                continue
            break

    if state.get("resolve_conflicts", True):
        apply_conflict_resolution(state.get("conflicts", []), dry_run=args.dry_run)

    do_install(
        state["modules"],
        state["install_pkgs"] and not args.pkgs_only,
        plat,
        args.dry_run,
    )


if __name__ == "__main__":
    main()
