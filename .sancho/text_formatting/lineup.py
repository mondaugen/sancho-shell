import sys
import re
START_RE='\S+\s*'
start_pat=re.compile(START_RE)
WIDTH=80 # maximum width
ln=int(sys.argv[2]) # line index (starting at 0)
col=int(sys.argv[3]) # column index (starting at 0)
nextln=ln+1 # the line number coming after the selection
with open(sys.argv[1],'r') as fd:
    lines=fd.readlines()
    chunk=lines[ln][col:]
    stchr=start_pat.match(chunk).group(0) # This is usually the comment prefix like '//'
                     # TODO: either regex under cursor or pass in strch
                     # explicitly
    cont_pat=re.compile('^\s*'+''.join(['[%s]'%(c,) for c in stchr]))
    while cont_pat.match(lines[nextln]):
        chunk += cont_pat.sub('',lines[nextln])
        nextln += 1
    outchunk=lines[ln][:col]
    prefix=''
    for w in re.split('\s+',chunk): # assumes we want to split at ' '
        if (len(outchunk[outchunk.rfind("\n")+1:]) + len(w)) >= WIDTH:
            w = "\n" + (' ' * col) + stchr + w
        else:
            w = prefix + w
        outchunk += w
        prefix = ' ' # assumes we want to prefix with the split character
    print(ord(chunk[-1]))
    print(chunk,end='')
    print(outchunk)
    result=lines[:ln]+[outchunk]+lines[nextln:]
    with open(sys.argv[4],'w') as ofd:
        for line in result:
            ofd.write(line)

