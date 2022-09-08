#!/usr/bin/env python3
import re
import sys
from itertools import islice
word_index=int(sys.argv[1])
s=sys.stdin.read()
word_finder=re.compile('\S+')
words = list(word_finder.finditer(s))
word=words[word_index] if word_index < len(words) else words[-1]
print(word.span()[0])
