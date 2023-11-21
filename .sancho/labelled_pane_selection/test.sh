export MW=$(tput cols) MH=$(tput lines)
LOOPS=1
[ -z $TARGET_PANE ] && TARGET_PANE=11
do_capture ()
{
    echo "$LOOPS" >> /tmp/loops
    tmux capture-pane -pt$TARGET_PANE > /tmp/a
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
    cat /tmp/d | MODE=select python3 .sancho/labelled_pane_selection/region_selector.py > /tmp/c
    case $? in
        0)
            tmux load-buffer /tmp/c && echo
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
