export MW=$(tput cols) MH=$(tput lines)
LOOPS=1
[ -z $TARGET_PANE ] && TARGET_PANE=11
do_capture ()
{
    tmux capture-pane -pt$TARGET_PANE > /tmp/a && \
    python3 .sancho/labelled_pane_selection/region_selector.py && \
    cat /tmp/b | \
    head -n $(($(tput lines) - 0)) | \
    tail -n $(($(tput lines) - 0))| \
    head --bytes=-1 && \
    read -sn 1 tempy && \
    echo "$tempy" | \
    MODE=select python3 .sancho/labelled_pane_selection/region_selector.py > /tmp/c
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
            echo # don't store any string
            ;;
    esac

}
do_capture
