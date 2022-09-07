#!/bin/bash

tmux run 'tmux capture-pane -S "#{copy_cursor_y}" -E "#{copy_cursor_y}" -p'
