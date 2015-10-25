# -*- coding:UTF-8 -*-

import os, sys

def usage():
    print "usage: %s [file.c]" % (sys.argv[0])

def c2bin(argv):
    # check # of argv
    if len(argv) < 2:
        usage()
        return
    
    # open file
    cfilebuf = []
    with open(argv[1], "rt") as f:
        cfilebuf = f.readlines()
    
    # search the c variable and 
    # parsing line by line to fill element into carray
    found = False;
    carray = []
    for line in cfilebuf:
        # search " [] = " 
        if found is False and line.find("[] =") >= 0:
            found = True
            continue
        
        # break if " }; " is found
        if found is True and line.find("};") >= 0:
            break
        
        # read element
        if found is True:
            for element in line.split():
                if element.endswith(','):
                    element = element[:-1]
                #print element
                len_element = len(element)
                if len_element == 4:        # it's byte, 0x12
                    carray.append(int(element, 16))
                elif len_element == 6:      # it's short, 0x1234
                    e2 = int(element[2:4],  16)
                    e1 = int(element[4:6],  16)
                    #print "%s = %x %x | %x " % (element, e1, e2, int(element, 16))
                    carray.append(e1)
                    carray.append(e2)
                elif len_element == 10:     # it's long, 0x12345678
                    e4 = int(element[2:4],  16)
                    e3 = int(element[4:6],  16)
                    e2 = int(element[6:8],  16)
                    e1 = int(element[8:10], 16)
                    #print "%s = %x %x %x %x | %x " % (element, e1, e2, e3, e4, int(element, 16))
                    carray.append(e1)
                    carray.append(e2)
                    carray.append(e3)
                    carray.append(e4)
                    
    # output to a binary file
    outputfile = "%s.bin" % ( argv[1].split(".")[0] )
    carray = bytearray(carray)
    with open(outputfile, "wb") as f:
        f.write(carray)
    
    # return outputfile
    return outputfile
    
if __name__ == "__main__":
    c2bin(sys.argv)