get_word_under_cursor ()
{
    tmux capturep -p | python3 -c '
import sys
import re
import os
try:
    GET_WORD_MODE=os.environ["GET_WORD_MODE"]
except KeyError:
    GET_WORD_MODE="nonwhitespace"
if GET_WORD_MODE=="nonwhitespace":
    matcher=re.compile("\S")
elif GET_WORD_MODE=="cvar":
    matcher=re.compile("[a-zA-Z0-9]+")
# x, y position read from stdin
lines = sys.stdin.readlines()
y=min(int(sys.argv[2]),len(lines)-1)
line=lines[y]
x=min(int(sys.argv[1]),len(line)-1)
def word_begin(line,x):
    while x > 0 and matcher.match(line[x-1]):
        x -= 1
    return x
begin = word_begin(line,x)
word = line[begin:x]
print(word)' $1 $2
}

# $1 is a string (or regular expression) that will match anywhere in
# path names tracked by git
# $2 is the root folder where searches will be carried out from
generate_path_matches ()
{   
    git -C $2 grep --exclude-standard --no-index -l -I -n -r -e '.*' | grep "$1" | sed 's|^|'$2'/&|'
}

# generate unique matches starting with $1
generate_word_matches ()
{
    git grep -Iho "\<$1[0-9a-zA-Z_]\+" .|sort|uniq
}

get_dirname_under_cursor ()
{
    word=$(get_word_under_cursor $1 $2)
    word_dirname=$(dirname $word | sed 's|^~|'$HOME'|')
    echo $word_dirname
}
    

complete_path_under_cursor ()
{
    word=$(get_word_under_cursor $1 $2)
    word_dirname=$(get_dirname_under_cursor $1 $2)
    word_basename=$(basename $word)
    generate_path_matches $word_basename $word_dirname
}

complete_word_under_cursor ()
{
    word=$(get_word_under_cursor $1 $2)
    generate_word_matches $word
}

word_length_under_cursor ()
{
    python3 -c 'import sys; print(len(sys.argv[1]))' $(get_word_under_cursor $1 $2)
}

delete_word_under_cursor ()
{
    wlen=$(word_length_under_cursor $1 $2)
    tmux send-keys -N $wlen 
}

get_empty_string ()
{
    echo -n ""
}

make_tmux_menu ()
{
    # take a list of files, separated by newlines, on stdin
    # interleave them with a key to select that menu item and a command to run that will insert it
    cheight=$(tmux display-message -p '#{client_height}')
    cwidth=$(tmux display-message -p '#{client_width}')
    wlen=$(word_length_under_cursor $1 $2)
    word_dirname=$($4 $1 $2)
    x=$($3 $1 $2 | python3 -c '
import sys
import string
# remove q so we can quit the menu, j and k so we can scroll like vim
keys=string.digits[1:]+string.ascii_letters.replace("q","").replace("Q","").replace("j","").replace("k","")
wlen=int(sys.argv[1])
cheight=int(sys.argv[2])-2 # - 2 to allow menu border
cwidth=int(sys.argv[3])-22 # - 2 to allow menu border
len_word_dirname=int(len(sys.argv[4])) + 1 if len(sys.argv) == 5 else 0 # To remove joining /
lines=[l.replace(" ","\ ") for l in sys.stdin.readlines()]
if len(lines) == 0:
    sys.exit(1)
lines=lines[:min(len(lines),cheight)]
lines=list(filter(lambda l: len(l.strip()[len_word_dirname:]) <= cwidth,lines))
def escape_space(s):
    return s.replace(" ","\\\\ Space ")
tmux_cmd="tmux display-menu "+" ".join([f"{line.strip()[len_word_dirname:]} {key} \"send-keys -N {wlen}  ; send-keys {escape_space(line.strip())}\"" for line,key in zip(lines,keys)])
print(tmux_cmd)
' $wlen $cheight $cwidth $word_dirname)
    eval "$x"
}

[ -z $MODE ] && MODE=path
case $MODE in
    path)
        make_tmux_menu $1 $2 complete_path_under_cursor get_dirname_under_cursor
        ;;
    word)
        GET_WORD_MODE=cvar make_tmux_menu $1 $2 complete_word_under_cursor get_empty_string
        ;;
    *)
        echo "ERROR: unknown mode" 1>&2
        exit 1
        ;;
esac
