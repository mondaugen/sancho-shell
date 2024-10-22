import numpy as np
from itertools import chain

class scope_view:
    """
    This is designed to mimic the re.match object functions so it can be used interchangably
    """
    def __init__(self,_start,_end,_string):
        self._start=_start
        self._end=_end
        self.string=_string
    def start(self,grp):
        # TODO: Just ignores grp for now
        return self._start
    def end(self,grp):
        # TODO: Just ignores grp for now
        return self._end

def all_scope_depths(text,delims='{}'):
    scope_boundaries=np.zeros(len(text))
    scope_boundaries[[i for i,_ in filter(lambda t: t[1] == delims[0],enumerate(text))]] = 1
    scope_boundaries[[i for i,_ in filter(lambda t: t[1] == delims[1],enumerate(text))]] = -1
    scope_boundaries_delim0=np.where(scope_boundaries==1)[0]
    scope_boundaries_delim1=np.where(scope_boundaries==-1)[0]
    if (scope_boundaries_delim0.shape[0]>0):
        # remove delim[1]s that come before the first delim[0]
        first_delim0=scope_boundaries_delim0[0]
        scope_boundaries[[i for i,_ in filter(lambda t: t[1] == delims[1],enumerate(text[:first_delim0]))]]=0
    if (scope_boundaries_delim1.shape[0]>0):
        # remove delim[0]s that come after the last delim[1]
        last_delim1=scope_boundaries_delim1[-1]
        scope_boundaries[[last_delim1+i for i,_ in filter(lambda t: t[1] == delims[0],enumerate(text[last_delim1:]))]]=0
    #print("".join(['%u' % (i,) for i in scope_boundaries]))
    scope_depths=np.cumsum(scope_boundaries)
    return scope_depths

def scopes_at_depth(scope_depths,d=1):
    """
    Yield (start,end) pairs so that text[start:end] gives a substring containing
    a scope delimited by delims at depth d.
    """
    scopes=np.zeros(len(scope_depths)+1)
    scopes[1:][scope_depths >= d] = 1
    #print("".join(['%u' % (i,) for i in scopes[1:]]))
    scopes_diff=np.diff(scopes)
    for sta,sto in zip(np.where(scopes_diff>0)[0],np.where(scopes_diff<0)[0]):
        yield (int(sta),int(sto+1))

class scope_gen:
    def __init__(self,delims='{}',depth=1,left_offset=0,right_offset=0,pre_re_pat=None,only_yield_if_pre_re_match=True):
        """
        only_yield_if_pre_re_match, if True will yield the match if
        only pre_re_pat matched something. If False it will always yield the match. You
        would set this to True when you abolutely want to match a non-zero-lengthed string before the delimiter scope.
        """
        self.delims=delims
        self.depth=depth
        self.left_offset=left_offset
        self.right_offset=right_offset
        self.pre_re_pat=pre_re_pat
        self.only_yield_if_pre_re_match=only_yield_if_pre_re_match
    def finditer(self,text):
        scope_depths=all_scope_depths(text,self.delims)
        for sta,sto in scopes_at_depth(scope_depths,self.depth):
            if self.pre_re_pat is not None:
                # extract text ending at sta and reverse it so we can search
                # along it backwards, starting where the scope starts
                pre_text=text[:sta][::-1]
                match=self.pre_re_pat.match(pre_text)
                if match is not None:
                    sta -= match.span()[1] # (lambda t: t[1]-t[0])(match.span()) but t[0] will always be 0
                else:
                    if self.only_yield_if_pre_re_match:
                        continue
            yield scope_view(sta+self.left_offset,sto+self.right_offset,text)

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
