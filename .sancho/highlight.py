# highlight different pieces of text according to a pattern
import sys
import re

ENCODING='utf-8'

matcher=re.compile(b'[\w./][\w./]+.')

HL_START=b"\033[48;5;55m"
HANDLE_FG_START=b"\033[38;5;16m"
HANDLE_BG_START=b"\033[48;5;220m"
FMT_RESET=b"\033[0m"

def bts(s):
    return bytes(s,encoding="utf-8")

class replacer:
    def __init__(self):
        self.handles=iter(
            reversed(
                bts('0123456789abcdefghijklmnoprstuvwxyzABCDEFGHIJKLMNOPRSTUVWXYZ')
            )
        )
    def __call__(self,match):
        ret = match.group(0)
        if re.match(b'\\b\d+\\b',match.group(0)):
            # don't highlight if all numbers
            return ret
        try:
            h=bytes(chr(next(self.handles)),encoding=ENCODING)
            #ret = HL_START + match.group(0)[:-1] + HANDLE_FG_START + HANDLE_BG_START + h + FMT_RESET
            ret = FMT_RESET[::-1] + match.group(0)[:-1] + HL_START[::-1] + FMT_RESET[::-1] + h[::-1] + HANDLE_BG_START[::-1] + HANDLE_FG_START[::-1] 
        except StopIteration:
            pass
        return ret

text=sys.stdin.read()
textb=bts(text)
textbr=re.sub(matcher,replacer(),textb[::-1])[::-1]


# msg=HL_START+bts("hello friends")+FMT_RESET+bts("\n")
sys.stdout.buffer.write(textbr)
