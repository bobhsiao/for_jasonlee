# -*- coding:UTF-8 -*-

import sys, c2bin

def usage():
    print "usage: %s [file1.c] [file2.c] ... [fileN.c] output.bin [L/B]" % (sys.argv[0])

def combine(argv):
    # vars
    binfiles = []
    
    # check argv
    if len(argv) < 2:
        usage()
        return
    elif argv[-1] not in ['l', 'L', 'b', 'B']:
        print "LAST ARG ERROR"
        usage()
        return        
        
    # create each bin
    for file in argv[1:-2]:
        print "creating %s ... " % file
        binfile = c2bin.c2bin(["", file, argv[-1]])
        binfiles.append(binfile)

    # combine all files into all.bin
    print "combining all to %s " % argv[-2]
    with open(argv[-2], "wb") as allbin:
        for f in binfiles:
            with open(f, "rb") as infile:
                allbin.write(infile.read())
    
if __name__ == "__main__":
    combine(sys.argv)