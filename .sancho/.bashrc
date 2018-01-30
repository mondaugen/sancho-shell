# enable menu completion to quicky choose completion entries
# these seem to be bound by default to do lowercase version
bind -r "\C-xn"
bind -r "\C-xN"
bind '"\C-xn":menu-complete'
bind '"\t":menu-complete'

# random helpful stuff
# use !#^:t to refer to file part of 1st argument on current command line
# handy for copying a file to some other dir

VISUAL=vim
function _hist_w_jump_amt () { 
    # Remember, ^P moves through history incrementally. The distances listed are
    # from the beginning. To go back to beginning, press Meta + >.
    _x="$(history|awk 'BEGIN{l=0}{l=$1;}END{print l}')";
    history|awk "{printf \"%d\", -1 * (\$1 - "${_x}") + 1; print \$0; }"; 
}
alias h='_hist_w_jump_amt'
alias j='jobs'
# Show where you are
alias ii='printf "%s@%s:%s\n"  `whoami` `hostname` `pwd`'
# Change the prompt to a minimal style because we have ii
export PS1="% "

# Jump to nth field on command line (up to 9th field)
bind '"\C-x1":"\C-a"'
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