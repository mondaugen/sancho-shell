import os
import re

NEWLINE=os.environ.get("NEWLINE","\n")
SELECTION_CHARS="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
WORD_MATCHER = re.compile('\w+')

def padline(s,w,pad=" "):
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

class TextRect:

    """ A rectangular region of text """

    def __init__(self,text,maxwidth,maxheight):
        """ text is a list of strings representing the sequence of lines """
        self.text=text
        self.maxwidth=maxwidth
        self.maxheight=maxheight

    def prompt_word_select(self,outfile,labelling='after'):
        # find all word matches
        # generate text where words are surrounded by escape sequences that highlight them
        # and also words are labelled by a character that is later used to select the word selection
        # then once the word has been selected it is written to the file supplied as an argument
        selectors=dict()
        itersc=iter(SELECTION_CHARS)
        for row,line in enumerate(self.text):
            for match in WORD_MATCHER.findall(line):
                selectors[next(itersc)]=(row,match)
            
