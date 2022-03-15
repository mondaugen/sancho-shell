import string

def interleave_commands(lines,fmt_line,gen_cmd,cheight=20,cmdstr="tmux display-menu "):
    """
    Interleave lines with keys and commands so you can generate a tmux menu.
    lines is a list of strings
    fmt_line is a function that takes a line and returns a string (can be used
    to ensure lines are smaller than some length)
    gen_cmd takes a line and a key an returns a string representing a command to be interpreted by tmux
    returns a string representing the command that could be executed
    """
    keys=string.digits[1:]+string.ascii_letters.replace("q","").replace("Q","")
    lines=lines[:min(len(lines),cheight)]
    return cmdstr+" ".join([f"'{fmt_line(line)}' {key} \"{gen_cmd(line,key)}\"" for line,key in zip(lines,keys)])
