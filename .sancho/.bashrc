# enable menu completion to quicky choose completion entries
# these seem to be bound by default to do lowercase version
bind -r "\C-xn"
bind -r "\C-xN"
bind '"\C-xn":menu-complete'
bind '"\t":menu-complete'

# random helpful stuff
# use !#^:t to refer to file part of 1st argument on current command line
# handy for copying a file to some other dir

export VISUAL=vim
function _hist_w_jump_amt () {
    # Remember, ^P moves through history incrementally. The distances listed are
    # from the beginning. To go back to beginning, press Meta + >.
    _x="$(history|awk 'BEGIN{l=0}{l=$1;}END{print l}')"
    history|awk "{printf \"%d\", -1 * (\$1 - "${_x}") + 1; print \$0; }"|less +G
}
alias h='_hist_w_jump_amt'
alias j='jobs'
# Show where you are
alias ii='printf "%s@%s:%s\n"  `whoami` `hostname` `pwd`'
# Change the prompt to a minimal style because we have ii
export PS1="% "

# Jump to nth field on command line (up to 9th field)
bind '"\C-x1":"\C-a\ef\eb"'
bind '"\C-x2":"\C-a\e2\ef\eb"'
bind '"\C-x3":"\C-a\e3\ef\eb"'
bind '"\C-x4":"\C-a\e4\ef\eb"'
bind '"\C-x5":"\C-a\e5\ef\eb"'
bind '"\C-x6":"\C-a\e6\ef\eb"'
bind '"\C-x7":"\C-a\e7\ef\eb"'
bind '"\C-x8":"\C-a\e8\ef\eb"'
bind '"\C-x9":"\C-a\e9\ef\eb"'
# Put the "dirname" of the last field typed at the end of the line, useful for
# copying files in a non-local directory
bind '"\C-xl":"\e\C-]/\C-f\C-w\C-y\C-e \C-y"'
# forward bigword
bind '"\eF": vi-forward-bigword'
# backward bigword
bind '"\eB": vi-backward-bigword'

alias show_git_tree='git log --graph --all --decorate --oneline'

# cat just enough lines of a file to fill the terminal (assuming your prompt only takes up 1 line)
alias c='head -n $(($(tput lines) - 1))'

# systems using X11 only, e.g., Linux
# Remap capslock to ctl
remap_capslock ()
{
    setxkbmap -layout us -option ctrl:nocaps
}

# grep with options i always use
alias grp='grep -rnI --exclude-dir=.git'
alias grpc='grep --color=always -rnI --exclude-dir=.git'

# virtualenv that includes the basename of the current directory in the prompt
alias virtualenv='virtualenv --prompt '\''(`basename $PWD`/`basename "$VIRTUAL_ENV"`)'\'''

# turn off CTRL-S
stty -ixon

# list all untracked files in git
alias git_list_untracked='git ls-files --others --exclude-standard'

# list changed (tracked) files in git
alias git_list_changed='git diff --name-only'

# revert staged
git_rev ()
{
    git restore --staged "$@"
    git checkout -- "$@"
}

# list files that changed by more than just whitespace changes
# takes argument referring to branch or commit
git_list_nonws_changes ()
{
    git diff --name-only "$1" | \
    xargs -d'\n' -I{} bash -c '
        d="$(git diff -b '"$1"' -- {} |wc -l)";
        [[ $d -gt 0 ]] && echo "{}"
    '
}

# list files where only the whitespace changed
# takes argument referring to branch or commit
git_list_ws_changes ()
{
    git diff --name-only "$1" | \
    xargs -d'\n' -I{} bash -c '
        d="$(git diff -b '"$1"' -- {} |wc -l)";
        [[ $d -eq 0 ]] && echo "{}"
    '
}

# Searches up for the regex PATTERN that has INDENT less indent above the line
# number LN in the file FILE
find_containing_thing ()
{
    [ -z $LN ] && LN=1
    [ -z $FILE ] && FILE="/tmp/test"
    [ -z $INDENT ] && INDENT=4
    [ -z $PATTERN ] && PATTERN="class"
    line="$(head -n $LN $FILE |tail -n 1)"
    nws="$(echo "$line"|sed 's/\(^ *\).*$/\1/'|wc -m)"
    nws=$(( $nws - 1 - $INDENT ))
    lines_w_numbers () {
        head -n $LN $FILE | perl -p -e '$_="$.$_";'
    }
    lines_w_numbers | \
        tac | \
        perl -ne 'BEGIN { $matcher=(" "x'$nws')."'$PATTERN'"; }' \
            -e 'print $_ if s/(^[0-9]+)($matcher.*$)/$1:$2/' |head -n 1
}


# Takes a video in $1 and slows it down by amount in $2. So watch out, to speed
# up a video by 2, you pass 0.5 for $2.  If $3 not specified, the output is the
# input with the file ending stripped off, appended with -slowed-$2.gif (so the
# default output format is gif)
slow_down_video ()
{
    USAGE="args are path-to-video rate [output-path]"
    if [[ -z "$1" ]] || [[ -z "$2" ]]
    then
        echo "$USAGE"
        return
    fi
    OUTPUT_PATH="${1%.*}-slowed-$2.gif"
    if [[ -n "$3" ]]
    then
        OUTPUT_PATH="$3"
    fi
    ffmpeg -i "$1" -filter:v "setpts=$2*PTS" "$OUTPUT_PATH" && echo "Wrote to:
$OUTPUT_PATH"
}

show_git_fork ()
{
    OTHERBRANCH=master
    if [[ -n "$1" ]]; then
        OTHERBRANCH="$1"
    fi
    git merge-base HEAD "$OTHERBRANCH"
}
        
