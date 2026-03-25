typeset -U path PATH

# Keep stale asdf shims from shadowing mise or system runtimes.
path=(${path:#$HOME/.asdf/shims})
path=(${path:#$HOME/.asdf/bin})
