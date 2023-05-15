import sys
import os
import re

NEWLINE=os.environ.get("NEWLINE","\n")
FORLANG=os.environ.get("FORLANG","python")
SELECTION_CHARS="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
if FORLANG == "python":
    WORD_MATCHER = re.compile(b'\\b[a-zA-Z_]+\\b')
    COMMENTS_MATCHER=re.compile('(?m)""".*"""|#.*$')
if FORLANG == "c":
    WORD_MATCHER = re.compile(b'\\b[a-zA-Z_]+\\b')
    COMMENTS_MATCHER=re.compile('(?m)/\*.*\*/|//.*$')
COMMENT_CONTENTS=re.compile('\S')

def comment_repl(m):
    return COMMENT_CONTENTS.sub(' ',m.group())

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

def label_matches(text,matcher,labels,maxwidth):
    selectors=dict()
    iter_labels=iter(labels)
    for m in list(matcher.finditer(text))[::-1]:
        loc_in_line=m.end() - m.string.rfind(b'\n',0,m.end())
        if loc_in_line < maxwidth:
            print("loc_in_line: ",loc_in_line,"val: ",m.string[m.end()])
            try:
                selectors[next(iter_labels)]=m
            except StopIteration:
                break
    return selectors

def label_text(text,selectors):
    starts=[Edit(m.start(),ESCAPES.GREEN) for _,m in selectors.items()]
    ends=[Edit(m.end(),ESCAPES.RESET) for _,m in selectors.items()]
    labels=[Edit(m.end(),ESCAPES.WHITE_BOLD+bytes(k,encoding='utf-8')+ESCAPES.RESET,
            skip=0 if m.string[m.end()] == ord(b'\n') else 1) for k,m in selectors.items()]
    text=do_edits(text,starts+ends+labels)
    return text

class TextRect:

    """ A rectangular region of text """

    def __init__(self,text,maxwidth,maxheight):
        """ text is a list of strings representing the sequence of lines """
        self.text=text
        self.maxwidth=maxwidth
        self.maxheight=maxheight

    def prompt_select(self,outfile,matcher,labelling='after'):
        # find all word matches
        # generate text where words are surrounded by escape sequences that
        # highlight them and also words are labelled by a character that is
        # later used to select the word selection then once the word has been
        # selected it is written to the file supplied as an argument
        selectors=label_matches(
            bytes(COMMENTS_MATCHER.sub(comment_repl,self.text),encoding='utf-8'),
            matcher,
            SELECTION_CHARS,
            self.maxwidth
        )
        outfile.write(label_text(bytes(self.text,encoding='utf-8'),selectors))

MW=int(os.environ['MW'])
MH=int(os.environ['MH'])
OUTFILE=os.environ.get('OUTFILE','/tmp/a')
with open(OUTFILE,'wb') as fd:
    TextRect(sys.stdin.read(),MW,MH).prompt_select(fd,WORD_MATCHER)
