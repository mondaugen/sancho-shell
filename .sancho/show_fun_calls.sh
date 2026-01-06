#!/usr/bin/env bash

# if no path specified searches from current directory recursively

grep -l$([[ ${#2} == 0 ]] && echo -n "r") --include="${INCLUDE:-*.c}" -e "$1" $([[ ${#2} > 0 ]] && echo -n "$2") |xargs -d'\n' -I{} bash -c 'echo && echo "{}" && MODE=allfuncalls python3 ~/.sancho/labelled_pane_selection/scope_matcher.py '"$1"' <"{}"'
