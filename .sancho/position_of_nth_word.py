#!/usr/bin/env python3
import re
import sys
from itertools import islice
word_index=int(sys.argv[1])
s=sys.stdin.read()
word_finder=re.compile('\w+')
print(next(islice(word_finder.finditer(s),word_index,word_index+1)).span()[0])
