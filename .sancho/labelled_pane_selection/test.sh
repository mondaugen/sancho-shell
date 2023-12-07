export MW=$(tput cols) MH=$(tput lines)
LOOPS=1
[ -z $FINAL_MODE ] && FINAL_MODE=select
[ -z $TARGET_PANE ] && TARGET_PANE=11

do_move ()
{
    current_cmd=$(tmux display-message -pt$TARGET_PANE '#{pane_current_command}')
    echo -n "$current_cmd" > /tmp/curcmd
    case $current_cmd in
        vim)
            c_s=$(tmux display -pt$TARGET_PANE '#{cursor_x}')
            l_s=$(tmux display -pt$TARGET_PANE '#{cursor_y}')
            l_s_p=$(cat /tmp/c|awk '{print $1}')
            c_s_p=$(cat /tmp/c|awk '{print $2}')
            tmux send-keys -t$TARGET_PANE Escape :call Space MovTextAbs\($c_s,$l_s,$c_s_p,$l_s_p\) Enter
            ;;
        *)
            echo -ne '\e['$(( 1 + $(cat /tmp/c|awk '{print $1}') ))';'$(( 1 + $(cat /tmp/c|awk '{print $2}') ))'H' > \
                $(tmux display-message -pt$TARGET_PANE '#{pane_tty}')
    esac
}

text_op ()
{
    case $FINAL_MODE in
        select)
            tmux load-buffer /tmp/c && echo
            ;;
        move_start)
            do_move
            ;;
        move_end)
            do_move
            ;;
        *)
            echo "Bad mode $FINAL_MODE" >&2
            exit -1
            ;;
    esac
}

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
    cat /tmp/d | MODE=$FINAL_MODE python3 .sancho/labelled_pane_selection/region_selector.py 2>/tmp/final_selector_error > /tmp/c
    case $? in
        0)
            text_op && echo
            ;;
        1)
            echo "got error $?"
            cat /tmp/d
            LOOPS=$(( $LOOPS + 1 )) do_capture
            ;;
        2)
            echo "got error $?"
            cat /tmp/d
            LOOPS=$(( $LOOPS - 1 )) do_capture
            ;;
        *)
            echo "got error $?" && exit $? # don't store any string
            ;;
    esac

}
do_capture
