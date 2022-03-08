import re
import sys
f=lambda x,y,r=re.split:r("\W",x[:y])[-1]+r("\W",x[y:])[0]
print(f(sys.argv[1],int(sys.argv[2])))
