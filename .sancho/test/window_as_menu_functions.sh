#cool_guy ()
#{
echo "$1" | tmux display -It$P && sleep 5 && tmux kill-pane -t$P
#    echo "$1"
#}

