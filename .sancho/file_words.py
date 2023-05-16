import re
import sys

m=re.compile('\w+')
s=sys.stdin.read()
words=set(m.findall(s))
for w in sorted(words):
    print(w)
