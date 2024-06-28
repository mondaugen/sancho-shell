import numpy as np

def all_scope_depths(text,delims='{}'):
    scope_boundaries=np.zeros(len(text))
    scope_boundaries[[i for i,_ in filter(lambda t: t[1] == delims[0],enumerate(text))]] = 1
    scope_boundaries[[i for i,_ in filter(lambda t: t[1] == delims[1],enumerate(text))]] = -1
    #print("".join(['%u' % (i,) for i in scope_boundaries]))
    scope_depths=np.cumsum(scope_boundaries)
    return scope_depths

def scopes_at_depth(scope_depths,d=1,):
    """
    Yield (start,end) pairs so that text[start:end] gives a substring containing
    a scope delimited by delims at depth d.
    """
    scopes=np.zeros(len(scope_depths)+1)
    scopes[1:][scope_depths >= d] = 1
    #print("".join(['%u' % (i,) for i in scopes[1:]]))
    scopes_diff=np.diff(scopes)
    for sta,sto in zip(np.where(scopes_diff>0)[0],np.where(scopes_diff<0)[0]):
        yield (sta,sto+1)

if __name__ == "__main__":
    import os
    import sys

    MODE=os.environ.get("MODE","rm")

    if MODE == "rm":
        
        import re

        slash_comment_remover=re.compile(r'//.*$',re.MULTILINE)
        left_comment_converter=re.compile(r'/\*',re.MULTILINE)
        right_comment_converter=re.compile(r'\*/',re.MULTILINE)
        newline_shrinker=re.compile(r'\n([^\n])',re.MULTILINE)
        whitespace_shrinker=re.compile(r'[ \t]+',re.MULTILINE)
        
        # read file from standard input
        s=right_comment_converter.sub('}}',left_comment_converter.sub('{{',slash_comment_remover.sub('',sys.stdin.read())))
        r=list(s)
        for sta,sto in scopes_at_depth(all_scope_depths(s),1):
            r[sta:sto]=[None for _ in range(sto-sta)]
        s2="".join(filter(lambda x: x is not None,r))
        s3=whitespace_shrinker.sub(' ',newline_shrinker.sub(r' \1', s2))
        for l in s3.split('\n'):
            ls=l.strip()
            if len(l)>0:
                print(l.strip())
    
    if MODE == "test":
        s='   {{}} {} {  } {{ } } '
        t='   {{}} {} {  } {{ } { '
        u=' { {{}} {} {  } {{ } } '

        for ss in [s,t,u]:
            print(ss)
            for dd in [1,2]:
                scope_depths=all_scope_depths(ss)
                print("depth:",dd)
                print("".join(['%u' % (i,) for i in scope_depths]))
                for sta,sto in scopes_at_depth(scope_depths,d=dd):
                    print("".join([ss[:sta]]+["x" for _ in range(sta,sto)]+[ss[sto:]]))
            print()
