from tmux_display_menu_formatter import interleave_commands
import sys

def gen_cmd(line,key):
    path, lnum = line.split(":")[:2]
    # opens file in vim, goes to line
    return f"send-keys Escape :e Space {path} Enter Escape :{lnum} Enter"

def fmt_line(line):
    return line[:70]

cheight=int(sys.argv[1])-2 # - 2 to allow menu border
lines=[line.replace(';','\;').strip() for line in sys.stdin.readlines()]
print(interleave_commands(lines,fmt_line,gen_cmd,cheight=cheight))
