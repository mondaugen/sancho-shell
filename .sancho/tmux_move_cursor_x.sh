#!/bin/bash

# possibility to override default bindings
[ -z $MOVE_TO_LINE_BEGIN ] && MOVE_TO_LINE_BEGIN=0
[ -z $MOVE_RIGHT ] && MOVE_RIGHT=l
# move the cursor's x position to that supplied by the first argument
# first move to beginning of line
tmux send-keys $MOVE_TO_LINE_BEGIN
# then move right $1 times
tmux send-keys -N $1 $MOVE_RIGHT
