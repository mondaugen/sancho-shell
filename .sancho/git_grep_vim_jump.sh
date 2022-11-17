cheight=$(tmux display-message -p '#{client_height}')
current_working_dir=
if [ -z "$2" ]; then
    current_working_dir="$(pwd)"
else
    current_working_dir=$(dirname "$2")
fi
echo "$2" > /tmp/2

dir_containing_git ()
{
    [ -n "$1" ] && cd "$1"
    while [ 1 ]; do
        gitdir="$(find . -maxdepth 1 -type d -path './.git')"
        if [ -n "$gitdir" ] || [ "$(pwd)" == / ] ; then
            break
        fi
        cd ..
    done
    pwd
}

gitdir="$(dir_containing_git "$current_working_dir")"
echo "$current_working_dir" > /tmp/current_working_dir
echo "$gitdir" > /tmp/gitdir
[ "$gitdir" == / ] && exit 1
eval "$(git -C "$gitdir" grep --no-index --exclude-standard -I -n -r $1|PYTHONPATH=~/.sancho:$PYTHONPATH python3 ~/.sancho/git_grep_vim_jump.py $cheight "$gitdir")"
