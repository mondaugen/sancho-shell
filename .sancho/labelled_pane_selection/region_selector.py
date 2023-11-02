import sys
import os
import re
import string

MODE=os.environ.get("MODE","display")
NEWLINE=os.environ.get("NEWLINE","\n")
FORLANG=os.environ.get("FORLANG")
SELECTION_CHARS="0123456789abcdefghijklmorstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOOPS=int(os.environ.get("LOOPS","1"))

class RevComment:
    def __init__(self,pat='"""(.|\n)*?"""|""".(.|\n)*?$'):
        self.pat=re.compile(pat)
    def sub(self,repl,s):
        ret = self.pat.sub(repl,s[::-1])[::-1]
        return ret

# I think to do this properly you need to have an object that implements sub for each matcher
# The sub function will put back the comment delimiters and just replace the comment contents

WORD_MATCHER = re.compile(b'\\b[a-zA-Z_]+\\b')
if FORLANG == "python":
    WORD_MATCHER = re.compile(b'\\b[a-zA-Z_]+\\b')
    COMMENTS_MATCHERS=[
    re.compile('"""(.|\n)*?"""|#.*\n|""".(.|\n)*?$'),
    RevComment(),
    ]
if FORLANG == "c":
    WORD_MATCHER = re.compile(b'\\b[a-zA-Z_]+\\b')
    COMMENTS_MATCHERS=[re.compile('(?m)/\*.*\*/|//.*$')]
COMMENT_CONTENTS=re.compile('\S')

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
    selectors=dict()
    iter_labels=iter(labels)
    for m in list(matcher.finditer(text))[::-1]:
        loc_in_line=m.end() - m.string.rfind(b'\n',0,m.end())
        if loc_in_line < maxwidth:
            try:
                selectors[next(iter_labels)]=m
            except StopIteration:
                loops -= 1
                if loops > 0:
                    iter_labels=iter(labels)
                else:
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

    def prompt_select(self,outfile,matcher,labelling='after',mode='display',loops=1,text_mask=id_text_mask):
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
        if mode == 'select':
            selected_label=sys.stdin.read(1)
            if selected_label == 'n':
                sys.exit(1)
            if selected_label == 'p':
                sys.exit(2)
            if selected_label == 'q':
                sys.exit(3)
            m=selectors[selected_label]
            outfile.write(bytes(m.string[m.start():m.end()]))
            sys.exit(0)

MW=int(os.environ['MW'])
MH=int(os.environ['MH'])
INFILE=os.environ.get('INFILE','/tmp/a')
OUTFILE=os.environ.get('OUTFILE','/tmp/b')

if MODE == "display":
    with open(INFILE,'r') as fda:
        with open(OUTFILE,'wb') as fdb:
            TextRect(fda.read(),MW,MH).prompt_select(fdb,WORD_MATCHER,loops=LOOPS)
if MODE == "select":
    with open(INFILE,'r') as fda:
        TextRect(fda.read(),MW,MH).prompt_select(open(sys.stdout.fileno(),mode='wb'),WORD_MATCHER,mode='select',loops=LOOPS)
    
