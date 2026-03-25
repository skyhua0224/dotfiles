typeset -U path PATH

for _brew_prefix in "${HOMEBREW_PREFIX:-}" /opt/homebrew /home/linuxbrew/.linuxbrew; do
  if [[ -n "$_brew_prefix" && -d "$_brew_prefix/bin" ]]; then
    path=("$_brew_prefix/bin" "$_brew_prefix/sbin" $path)
    export HOMEBREW_PREFIX="$_brew_prefix"
    break
  fi
done

# Keep stale asdf shims from shadowing mise or system runtimes.
path=(${path:#$HOME/.asdf/shims})
path=(${path:#$HOME/.asdf/bin})
