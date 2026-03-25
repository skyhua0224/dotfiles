# Shared shell config for macOS and Linux.

typeset -g DOTFILES_HOST="${DOTFILES_HOST:-${HOST%%.*}}"
typeset -g BREW_PREFIX=""

for _candidate in "${HOMEBREW_PREFIX:-}" /opt/homebrew /home/linuxbrew/.linuxbrew; do
  if [[ -n "$_candidate" && -d "$_candidate" ]]; then
    BREW_PREFIX="$_candidate"
    break
  fi
done

if [[ -n "$BREW_PREFIX" && -d "$BREW_PREFIX/opt/grep/libexec/gnubin" ]]; then
  export PATH="$BREW_PREFIX/opt/grep/libexec/gnubin:$PATH"
fi

if [[ -n "$BREW_PREFIX" && -d "$BREW_PREFIX/share/zsh/site-functions" ]]; then
  fpath=("$BREW_PREFIX/share/zsh/site-functions" $fpath)
fi

_dot_source_first() {
  local _path
  for _path in "$@"; do
    if [[ -f "$_path" ]]; then
      source "$_path"
      return 0
    fi
  done
  return 1
}

autoload -Uz compinit
_compdump="${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompdump-${ZSH_VERSION}"
mkdir -p "${_compdump:h}" 2>/dev/null
if [[ -s "$_compdump" ]]; then
  compinit -C -d "$_compdump"
else
  compinit -d "$_compdump"
fi

zstyle ':completion:*' format $'\e[2;37mCompleting %d\e[m'
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*:descriptions' format '[%d]'
zstyle ':completion:*' menu no
if [[ -n "${LS_COLORS:-}" ]]; then
  zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
fi

if _dot_source_first \
  "$BREW_PREFIX/opt/fzf-tab/share/fzf-tab/fzf-tab.zsh" \
  /usr/share/fzf-tab/fzf-tab.zsh \
  /usr/share/zsh/plugins/fzf-tab/fzf-tab.zsh; then
  zstyle ':fzf-tab:*' switch-group '<' '>'
  zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --icons --color=always $realpath'
  if [[ -n "${TMUX:-}" ]]; then
    zstyle ':fzf-tab:*' fzf-command ftb-tmux-popup
  fi
fi

if command -v starship >/dev/null 2>&1 && [[ "${TERM:-}" != "dumb" ]]; then
  eval "$(starship init zsh)"
fi

if _dot_source_first \
  "$BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh" \
  /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh \
  /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh; then
  ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=244'
  ZSH_AUTOSUGGEST_STRATEGY=(history completion)
  ZSH_AUTOSUGGEST_USE_ASYNC=true
fi

if [[ -d "$HOME/Library/pnpm" ]]; then
  export PNPM_HOME="$HOME/Library/pnpm"
elif [[ -d "$HOME/.local/share/pnpm" ]]; then
  export PNPM_HOME="$HOME/.local/share/pnpm"
fi

if [[ -n "${PNPM_HOME:-}" ]]; then
  case ":$PATH:" in
    *":$PNPM_HOME:"*) ;;
    *) export PATH="$PNPM_HOME:$PATH" ;;
  esac
fi

export PATH="${ASDF_DATA_DIR:-$HOME/.asdf}/shims:$PATH"
export PATH="$PATH:$HOME/.lmstudio/bin"
export PATH="$HOME/.antigravity/antigravity/bin:$PATH"
export PATH="$HOME/bin:$PATH"

if command -v code-insiders >/dev/null 2>&1; then
  alias code='code-insiders'
fi

# Interactive shell: ls/cd → enhanced tools. Scripts use subshells and don't inherit aliases.
alias ls='eza --icons --group-directories-first'
alias ll='eza --icons --group-directories-first -l --git --time-style=long-iso'
alias la='eza --icons --group-directories-first -la --git --time-style=long-iso'
alias lt='eza --icons --group-directories-first --tree --level=3'
alias b='bat --style=plain --paging=never'
alias bp='bat --style=full'
alias grep='grep --color=auto'
alias rg='rg --smart-case --follow'
alias dfu='duf'
alias duu='dust'
alias psg='procs --pager=disable --tree'
alias h='tldr'

if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh --cmd cd)"
  alias cdd='cdi'
fi

if command -v atuin >/dev/null 2>&1; then
  eval "$(atuin init zsh --disable-up-arrow --disable-ai)"
fi

export CARAPACE_BRIDGES='zsh,fish,bash,inshellisense'
if command -v carapace >/dev/null 2>&1; then
  source <(carapace _carapace)
fi

if command -v thefuck >/dev/null 2>&1; then
  fuck() {
    unset -f fuck
    eval "$(thefuck --alias)"
    fuck "$@"
  }
fi

_dot_source_first \
  "$BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" \
  /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh \
  /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

if _dot_source_first \
  "$BREW_PREFIX/share/zsh-history-substring-search/zsh-history-substring-search.zsh" \
  /usr/share/zsh-history-substring-search/zsh-history-substring-search.zsh \
  /usr/share/zsh/plugins/zsh-history-substring-search/zsh-history-substring-search.zsh; then
  bindkey '^[[A' history-substring-search-up
  bindkey '^[[B' history-substring-search-down
fi

export TLDR_LANGUAGE="zh"

export SDKMAN_DIR="$HOME/.sdkman"
if [[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]]; then
  sdk() {
    unset -f sdk
    source "$HOME/.sdkman/bin/sdkman-init.sh"
    sdk "$@"
  }
fi

if [[ "${TERM_PROGRAM:-}" == "vscode" ]] && command -v code >/dev/null 2>&1; then
  . "$(code --locate-shell-integration-path zsh)"
fi

if [[ -f "$HOME/.config/dotfiles/hosts/${DOTFILES_HOST}.zsh" ]]; then
  source "$HOME/.config/dotfiles/hosts/${DOTFILES_HOST}.zsh"
fi

if [[ -f "$HOME/.config/dotfiles/local.zsh" ]]; then
  source "$HOME/.config/dotfiles/local.zsh"
fi
