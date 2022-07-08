get_word_under_cursor ()
{
    tmux capturep -p | python3 -c '
import sys
import re
matcher=re.compile("\S")
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

# The argument is a string (or regular expression) that will match anywhere in
# path names tracked by git
generate_path_matches ()
{   
    git grep --recurse-submodules -l -I -n -r -e '.*' | grep "$1"
}

complete_path_under_cursor ()
{
    generate_path_matches $(get_word_under_cursor $1 $2)
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

make_tmux_menu ()
{
    # take a list of files, separated by newlines, on stdin
    # interleave them with a key to select that menu item and a command to run that will insert it
    cheight=$(tmux display-message -p '#{client_height}')
    cwidth=$(tmux display-message -p '#{client_width}')
    wlen=$(word_length_under_cursor $1 $2)
    x=$(complete_path_under_cursor $1 $2 | python3 -c '
import sys
import string
# remove q so we can quit the menu, j and k so we can scroll like vim
keys=string.digits[1:]+string.ascii_letters.replace("q","").replace("Q","").replace("j","").replace("k","")
wlen=int(sys.argv[1])
cheight=int(sys.argv[2])-2 # - 2 to allow menu border
cwidth=int(sys.argv[3])-22 # - 2 to allow menu border
lines=[l.replace(" ","\ ") for l in sys.stdin.readlines()]
if len(lines) == 0:
    sys.exit(1)
lines=lines[:min(len(lines),cheight)]
lines=list(filter(lambda l: len(l.strip()) <= cwidth,lines))
def escape_space(s):
    return s.replace(" ","\\\\ Space ")
tmux_cmd="tmux display-menu "+" ".join([f"{line.strip()} {key} \"send-keys -N {wlen}  ; send-keys {escape_space(line.strip())}\"" for line,key in zip(lines,keys)])
print(tmux_cmd)
' $wlen $cheight $cwidth)
    eval "$x"
}

make_tmux_menu $1 $2
