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
print(x,y)
print(lines)
def word_begin(line,x):
    while x > 0 and matcher.match(line[x-1]):
        x -= 1
    return x
begin = word_begin(line,x)
word = line[begin:x]
print(word)' $1 $2
}

get_word_under_cursor $1 $2
