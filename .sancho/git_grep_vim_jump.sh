grp ()
{
    grep -rnI --exclude-dir=.git --exclude-dir=venv "$@"
}

cheight=$(tmux display-message -p '#{client_height}')
# TODO: It would be nice to search in the repo or folder that contains the
# source file passed in as argument $2, but at that point it is hard to know
# where to limit the search...
#eval "$(grp "$1" "$(dirname $2)"|PYTHONPATH=~/.sancho:$PYTHONPATH python3 ~/.sancho/git_grep_vim_jump.py $cheight)"

eval "$(git grep --recurse-submodules -I -n -r "$1"|PYTHONPATH=~/.sancho:$PYTHONPATH python3 ~/.sancho/git_grep_vim_jump.py $cheight)"

