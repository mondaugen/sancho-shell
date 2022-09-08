#!/bin/bash
D="$(dirname ${BASH_SOURCE[0]})"
word_pos=$($D/get_current_line.sh | $D/position_of_nth_word.py $1)
$D/tmux_move_cursor_x.sh $word_pos

