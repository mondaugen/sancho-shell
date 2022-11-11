cheight=$(tmux display-message -p '#{client_height}')
eval "$(git grep --no-index --exclude-standard -I -n -r "$1"|PYTHONPATH=~/.sancho:$PYTHONPATH python3 ~/.sancho/git_grep_vim_jump.py $cheight)"
