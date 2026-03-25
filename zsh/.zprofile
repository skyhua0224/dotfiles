for _brew in /opt/homebrew/bin/brew /home/linuxbrew/.linuxbrew/bin/brew; do
  if [[ -x "$_brew" ]]; then
    eval "$("$_brew" shellenv)"
    break
  fi
done

if [[ -f "$HOME/.orbstack/shell/init.zsh" ]]; then
  source "$HOME/.orbstack/shell/init.zsh"
fi

typeset -g DOTFILES_HOST="${DOTFILES_HOST:-${HOST%%.*}}"

if [[ -f "$HOME/.config/dotfiles/hosts/${DOTFILES_HOST}.zprofile" ]]; then
  source "$HOME/.config/dotfiles/hosts/${DOTFILES_HOST}.zprofile"
fi

if [[ -f "$HOME/.config/dotfiles/local.zprofile" ]]; then
  source "$HOME/.config/dotfiles/local.zprofile"
fi
