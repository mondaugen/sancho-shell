# Spawn a new window and set it up to be like a menu

KEYTABLE=$(mktemp -u XXXXXXXXX)
P=$(tmux splitw -dPF '#{pane_id}' '')
tmux resize-pane -Zt$P
dself="$(dirname ${BASH_SOURCE[0]})"

tmux bind-key -T$KEYTABLE a run-shell 'cd '"$PWD"' && P="'$P'" bash '"$dself"'/window_as_menu_functions.sh "heyeyeye"'
#tmux bind-key -T$KEYTABLE a run-shell 'cd '"$PWD"' && export P="'$P'" && ls test'
tmux bind-key -T$KEYTABLE b run-shell 'export P="'$P'" && source '"$dself"'/window_as_menu_functions.sh && cool_guy "bun bunns"'
#tmux bind-key -T$KEYTABLE a run-shell 'echo "hey yo" |tmux display -It'$P' && sleep 5 && tmux kill-pane -t'$P
#tmux bind-key -T$KEYTABLE b run-shell 'touch /tmp/abc && tmux kill-pane -t'$P

echo "a: print \"hey yo\"" | tmux display -It$P
echo "b: print \"bun bunns\"" | tmux display -It$P

tmux switch-client -T$KEYTABLE
