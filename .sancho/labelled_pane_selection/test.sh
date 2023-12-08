lookup () 
{
    # create selector string
    s=$(seq -s' ' 0 $(($1 + 1)))
    s="${s/$1/x}"
    s="${s//[[:digit:]]/_}"
    while read $s; do echo -n "$x"; done
}

export MW=$(tput cols) MH=$(tput lines)
[ -z $ACTION ] && ACTION=select
LOOPS=1
[ -z $TARGET_PANE ] && TARGET_PANE=11
do_capture ()
{
    echo "$LOOPS" >> /tmp/loops
    copy_cursor_line=$(tmux display -pt$TARGET_PANE '#{copy_cursor_line}')
    if [[ -z $copy_cursor_line ]]; then
        tmux capture-pane -pt$TARGET_PANE > /tmp/a
    else
        # find out where we are in the history
        hist_line_num=$(tmux display -pt$TARGET_PANE '#{copy_cursor_line}' | sed -E 's!^[^[]+\[([0-9]+)/[0-9]+\]$!\1!g')
        tmux capture-pane -S-$hist_line_num \
            -E$(( $(tmux display -pt$TARGET_PANE '#{pane_height}') - $hist_line_num - 1 )) -pt$TARGET_PANE > /tmp/a
    fi 
    rm -f /tmp/d
    tmux neww -eLOOPS=$LOOPS -eMW=$MW -eMH=$MH -eMATCHER_STYLE=$MATCHER_STYLE 'tmux set-option -w remain-on-exit off && python3 .sancho/labelled_pane_selection/region_selector.py 2>/tmp/region_selector_error && cat /tmp/b | head -n $(($(tput lines) - 0)) | tail -n $(($(tput lines) - 0))| head --bytes=-1 && read -sn 1 tempy && echo -n "$tempy" > /tmp/d'
    # wait for /tmp/d to show up because it seems tmux neww is asynchronous
    while [ 1 ]
    do
        if [ -f /tmp/d ]
        then
            break
        fi
        sleep 0.1
    done
    cat /tmp/d | MODE="$ACTION" python3 .sancho/labelled_pane_selection/region_selector.py > /tmp/c
    case $? in
        0)
            if [[ "$ACTION" == select ]]; then
                tmux load-buffer /tmp/c && echo
            else
                # save where we are now
                cur_row=$(tmux display '#{cursor_y}')
                cur_col=$(tmux display '#{cursor_x}')
                # find out where we need to go
                new_row=$(cat /tmp/c | lookup 0)
                new_col=$(cat /tmp/c | lookup 1)
            fi
            ;;
        1)
            LOOPS=$(( $LOOPS + 1 )) do_capture
            ;;
        2)
            LOOPS=$(( $LOOPS - 1 )) do_capture
            ;;
        *)
            echo "got error $?" && exit $? # don't store any string
            ;;
    esac

}
do_capture
