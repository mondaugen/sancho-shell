from tmux_display_menu_formatter import interleave_commands
import sys
import re
rexp=re.compile('\s+')
rexp_ss=re.compile('\s')
def repl_ss(m):
    return '\\'+m.group(0)

base_path=""
if len(sys.argv) >= 3:
    base_path=sys.argv[2]
    base_path=rexp_ss.sub(repl_ss,base_path)

def gen_cmd(line,key):
    path, lnum = line.split(":")[:2]
    path=rexp_ss.sub(repl_ss,path)
    # opens file in vim, goes to line
    return f"send-keys Escape :e Space {base_path}/{path} Enter Escape :{lnum} Enter"

def fmt_line(line):
    return line[:70]

cheight=int(sys.argv[1])-2 # - 2 to allow menu border
lines=[line.replace(';','\;').strip() for line in sys.stdin.readlines()]
lines=[rexp.sub(' ',line) for line in lines]
if len(lines):
    cmd=interleave_commands(lines,fmt_line,gen_cmd,cheight=cheight)
    print(cmd)
