import sys
with open(sys.argv[1],'r') as file1:
    with open(sys.argv[2],'r') as file2:
        lines1=file1.readlines()
        lines2=file2.readlines()
        for word in sorted(set(lines1).intersection(set(lines2))):
            print(word,end='')
