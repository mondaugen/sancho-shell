#interleave_debug ()
#{
#    funfun="debug"
#    if [[ -n "$1" ]]; then
#        funfun="$1"
#    fi
##    awk 'BEGIN{x=0}{printf("echo '"'"'"); printf("'"$funfun"'(\"%d\\\\n\");",x); print($0); printf("'"'"'\n"); x++}' | bash
#    awk 'BEGIN{x=0}{printf("echo '"'"'"); printf("'"$funfun"'(\"%d\\\\n\");",x); print($0); printf("'"'"'\n"); x++}' | bash
#}

import sys
funfun="debug"
if len(sys.argv)>=2:
    funfun=sys.argv[1]
x=0
for line in sys.stdin.readlines():
    print(funfun,"(\"%d\\n\");" % (x,),line,sep='',end='')
    x += 1
