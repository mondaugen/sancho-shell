export MW=$(tput cols) MH=$(tput lines)
export FORLANG=python
tmux capture-pane -pt4 > /tmp/a && python3 .sancho/labelled_pane_selection/region_selector.py && cat /tmp/b |head -n $(($(tput lines) - 1)) && read -sn 1 tempy && echo "$tempy" | MODE=select python3 .sancho/labelled_pane_selection/region_selector.py > /tmp/c && tmux load-buffer /tmp/c
