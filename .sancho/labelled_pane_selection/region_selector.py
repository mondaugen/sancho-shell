import sys
import os
import re
import string
import numpy as np
import functools

MODE=os.environ.get("MODE","display")
NEWLINE=os.environ.get("NEWLINE","\n")
MATCHER_STYLE=os.environ.get("MATCHER_STYLE","word")
SELECTION_CHARS="0123456789abcdefghijklmorstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOOPS=int(os.environ.get("LOOPS","1"))

def matches_by_uniqueness(mre,mgrp,text):
    """
    Look for matches described by mre in text.
    Count the number of times each match occurs. The most unique matches will be presented first.
    In case there are ties, the longer unique matches will be presented first.
    """
    matches_by_string=dict()
    for m in mre.finditer(text):
        s=m.string[m.start(mgrp):m.end(mgrp)]
        if s in matches_by_string:
            matches_by_string[s].append(m)
        else:
            matches_by_string[s]=[m]
    for s in sorted(matches_by_string.keys(),key=lambda s_: (len(matches_by_string[s_]),-1*len(s_))):
        # return all the matches
        yield matches_by_string[s]

class RevComment:
    def __init__(self,pat='"""(.|\n)*?"""|""".(.|\n)*?$'):
        self.pat=re.compile(pat)
    def sub(self,repl,s):
        ret = self.pat.sub(repl,s[::-1])[::-1]
        return ret

# I think to do this properly you need to have an object that implements sub for each matcher
# The sub function will put back the comment delimiters and just replace the comment contents

def id_post_proc(s):
    return s

def strip_post_proc(s):
    return s.strip()

def text_mask_single_delim(text,delim="'"):
    pol=1
    val=0
    result=[0]*len(text)
    for i,c in enumerate(text):
        if c == delim:
            val += pol
            pol *= -1
        result[i]=val
    return result

def id_text_mask(text):
    return [0]*len(text)

def text_mask_leading_line_numbers(text):
    ret = [0]*len(text)
    matcher=re.compile('\n\s*([0-9]+)')
    for m in matcher.finditer(text):
        sta=m.start(1)
        sto=m.end(1)
        ret[sta:sto]=[1 for _ in range(sta,sto)]
    return ret

def text_mask_outside_parens(text):
    ret = [1]*len(text)
    pat=re.compile('\([^)]*\)')
    for m in pat.finditer(text):
        sta=m.start(0)
        sto=m.end(0)
        ret[sta:sto]=[0 for _ in range(sta,sto)]
    return ret

#if MATCHER_STYLE == "words"
PATH_RE=b'[-~a-zA-Z_0-9/.]+'
WORD_MATCHER = {"re":re.compile(b'[a-zA-Z_0-9]+'),"group":0}
WORD_POST_PROC = id_post_proc
TEXT_MASK=id_text_mask
if MATCHER_STYLE == "word_no_ln":
    TEXT_MASK=text_mask_leading_line_numbers
if MATCHER_STYLE == "line":
    WORD_MATCHER={"re":re.compile(b'\n?([^\n]+)'),"group":1}
    #WORD_POST_PROC = strip_post_proc # the group strips it for you
if MATCHER_STYLE == "line_no_ln":
    # lines omitting leading line numbers
    WORD_MATCHER={"re":re.compile(b'\n?\s*([^\n]*)'),"group":1}
    TEXT_MASK=text_mask_leading_line_numbers
if MATCHER_STYLE == "path":
    WORD_MATCHER = {"re":re.compile(PATH_RE),"group":0}
if MATCHER_STYLE == "error_path":
    # This is a format you see when grep shows the path and line number or a
    # compiler says the path, line number and character
    WORD_MATCHER = {"re":re.compile(b'[-~a-zA-Z_0-9/.]+(:[0-9]+)+:'),"group":0}
if MATCHER_STYLE == 'git_branches':
    WORD_MATCHER = {"re":re.compile(b'[-~a-zA-Z_0-9/.]+'),"group":0}
    TEXT_MASK=text_mask_outside_parens
if MATCHER_STYLE == 'hash':
    WORD_MATCHER = {"re":re.compile(b'\\b[a-fA-F0-9]+\\b'),"group":0}
if MATCHER_STYLE == 'git_diff':
    # you see these paths when git shows you a diff: the paths to the two
    # compared files start with a/ and b/ respectively
    # we usually just want to copy the path after the a/ or b/
    WORD_MATCHER = {"re":re.compile(b'\\b[ab]/('+PATH_RE+b')'),"group":1}
    
# TODO: These ones are still half baked
# If you have nested () or {}, they will stop at the first matching } which is
# almost never what you want.
# They also show the masked text highlighted, but it is not copied (so that's
# good but confusing)
if MATCHER_STYLE == "arguments":
    WORD_MATCHER={"re":re.compile(b'(\(([^)]|\n)*\))'),"group":1}
    TEXT_MASK=text_mask_leading_line_numbers
if MATCHER_STYLE == "scope":
    WORD_MATCHER={"re":re.compile(b'({([^}]|\n)*})'),"group":1}
    TEXT_MASK=text_mask_leading_line_numbers
    

COMMENT_CONTENTS=re.compile('\S')

## process string before it is copied to clipboard

def comment_repl(m):
    return COMMENT_CONTENTS.sub(' ',m.group())

def apply_comments_matchers(s):
    for m in COMMENTS_MATCHERS:
        s = m.sub(comment_repl,s)
    return s

class ESCAPES:
    WHITE_BOLD=b'\033[1m'
    GREEN=b'\033[32m'
    RED=b'\033[31m'
    RESET=b'\033[0m'

def padline(s,w,pad=" "):
    # yo yo guys
    """
    pad s at end with pad character so line is w long
    the newline at the end of the line is not included in the length of the line
    the following example illusrates
    s="example line\n"
    w=16
    result="example line    \n"
    if the length of the line before the newline is greater than w then only w
    characters of it are returned
    """
    stub = s[:s.find(NEWLINE)]
    l = len(stub)
    padding = pad * max(0,w-l)
    return (stub + padding)[:w] + NEWLINE

def apply_text_mask(text,mask,sub=" "):
    return "".join([sub if m != 0 and t not in string.whitespace else t for t,m in zip(text,mask)])

class Edit:
    """ a data structure that describes a text insertion or replacement """
    def __init__(self,anchor,text,skip=0):
        self.anchor=anchor
        self.text=text
        self.skip=skip

def do_edits(s,edits):
    offset=0
    for e in sorted(edits,key=lambda e: e.anchor):
        anchor = e.anchor + offset
        s = s[:anchor] + e.text + s[anchor + e.skip:]
        offset += len(e.text) - e.skip
    return s

def label_matches(text,matcher,labels,maxwidth,loops):
    # if loops is 1 it will iterate through iter_labels once
    # if loops is 2 it will iterate through iter_labels twice, but only keep the
    # label locations from the second loop
    # this allows you to label chunks of text where there would be more matches
    # than labels, by discarding earlier chunks
    # This returns a dictionary whose keys are the selector labels (single
    # characters that can be typed to select the region) and whose items are
    # lists of matches indicating where the string is
    selectors=dict()
    iter_labels=iter(labels)
    mre=matcher['re']
    mgrp=matcher['group']
    for ms in list(matches_by_uniqueness(mre,mgrp,text)):
        # m is a list of matches (if the match yields the same string multiple
        # times, all these matches are returned)
        # Filter out matches that have 0 length or we can't render properly
        ms=filter(lambda m_: not (m_.start(mgrp) == m_.end(mgrp)),ms)
        ms=filter(lambda m_: (m_.end(mgrp) - m_.string.rfind(b'\n',0,m_.end(mgrp))) < maxwidth,ms)
        ms=list(ms)
        if len(ms) > 0:
            try:
                label=next(iter_labels)
            except StopIteration:
                loops -= 1
                if loops > 0:
                    iter_labels=iter(labels)
                    label=next(iter_labels)
                else:
                    break
            selectors[label]=(ms,mgrp)
    return selectors

def _flatten(l):
    return functools.reduce(lambda a,b:a+b,l)

def label_text(text,selectors):
    starts=[[Edit(m.start(g),ESCAPES.GREEN) for m in ms] for _,(ms,g) in selectors.items()]
    ends=[[Edit(m.end(g),ESCAPES.RESET) for m in ms] for _,(ms,g) in selectors.items()]
    labels=[[Edit(m.end(g),ESCAPES.WHITE_BOLD+bytes(k,encoding='utf-8')+ESCAPES.RESET,
            skip=0 if m.string[m.end(g)] == ord(b'\n') else 1) for m in ms] for k,(ms,g) in selectors.items()]
    # flatten them
    starts=_flatten(starts)
    ends=_flatten(ends)
    labels=_flatten(labels)
    text=do_edits(text,starts+ends+labels)
    return text

class TextRect:

    """ A rectangular region of text """

    def __init__(self,text,maxwidth,maxheight):
        """ text is a list of strings representing the sequence of lines """
        self.text=text
        self.maxwidth=maxwidth
        self.maxheight=maxheight

    def index_to_row_col(self,i):
        """
        Row and column are 0-indexed.
        """
        rownum=np.cumsum([1 if c == '\n' else 0 for c in self.text])
        return (rownum[i],i-np.where(rownum == rownum[i])[0][0]-1)

    def prompt_select(self,outfile,matcher,labelling='after',mode='display',loops=1,text_mask=id_text_mask,post_proc=id_post_proc):
        # find all word matches
        # generate text where words are surrounded by escape sequences that
        # highlight them and also words are labelled by a character that is
        # later used to select the word selection then once the word has been
        # selected it is written to the file supplied as an argument
        selectors=label_matches(
            bytes(apply_text_mask(self.text,text_mask(self.text)),encoding='utf-8'),
            matcher,
            SELECTION_CHARS,
            self.maxwidth,
            loops
        )
        if mode == 'display':
            outfile.write(label_text(bytes(self.text,encoding='utf-8'),selectors))
        if mode in ['select','move_start','move_end']:
            selected_label=sys.stdin.read(1)
            if selected_label == 'n':
                sys.exit(1)
            if selected_label == 'p':
                sys.exit(2)
            if selected_label == 'q':
                sys.exit(3)
            (ms,g)=selectors[selected_label]
            # Just use the last match (could be the first, it doesn't matter, we just want the string)
            m=ms[-1]
            if mode == 'select':
                outfile.write(bytes(post_proc(m.string[m.start(g):m.end(g)])))
            elif mode == 'move_start':
                # TODO: how to move to a specific one in a group?
                # Probably "move" should give a unique label to each selection
                # even if they don't share the same string
                outfile.write(bytes('%d %d' % self.index_to_row_col(m.start(g)),encoding='ascii'))
            elif mode == 'move_end':
                outfile.write(bytes('%d %d' % self.index_to_row_col(m.end(g)),encoding='ascii'))
        sys.exit(0)

MW=int(os.environ['MW'])
MH=int(os.environ['MH'])
INFILE=os.environ.get('INFILE','/tmp/a')
OUTFILE=os.environ.get('OUTFILE','/tmp/b')

if MODE == "display":
    with open(INFILE,'r') as fda:
        with open(OUTFILE,'wb') as fdb:
            TextRect(fda.read(),MW,MH).prompt_select(fdb,WORD_MATCHER,loops=LOOPS,text_mask=TEXT_MASK)
if MODE in ["select","move_start","move_end"]:
    with open(INFILE,'r') as fda:
        TextRect(fda.read(),MW,MH).prompt_select(open(sys.stdout.fileno(),mode='wb'),WORD_MATCHER,mode=MODE,loops=LOOPS,post_proc=WORD_POST_PROC,text_mask=TEXT_MASK)
    
