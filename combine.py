# -*- coding:UTF-8 -*-

import sys, os, c2bin

def usage():
    print "usage: %s [file1.c] [file2.c] ... [fileN.c] output.bin [L/B] [PIC_BASE_ADDRESS]" % (sys.argv[0])

def combine(argv):
    # vars
    binfiles = []
    binfile_size = {}
    
    # check argv
    if len(argv) < 2:
        usage()
        return
    elif argv[-2] not in ['l', 'L', 'b', 'B']:
        print "Endianness ARG ERROR"
        usage()
        return        
        
    # create each bin
    for file in argv[1:-3]:
        print "creating %s ... " % file
        binfile = c2bin.c2bin(["", file, argv[-2]])
        binfiles.append(binfile)

    # combine all files into all.bin
    print "combining all to %s " % argv[-3]
    with open(argv[-3], "wb") as outputbin:
        for f in binfiles:
            with open(f, "rb") as bin:
                outputbin.write(bin.read())
    
    # get size of each bin file
    for f in binfiles:
        binfile_size[f] = os.path.getsize(f)
    
    # create c header file
    total_size = 0
    cheadfilename = argv[-3].replace(".bin", ".h")
    guardtext = argv[-3].replace(".bin", "_H_INCLUDE").upper()
    print "creating %s ..." % (cheadfilename)
    with open(cheadfilename, "wt") as cheaderfile:
        cheaderfile.write("#ifndef __%s__\n" % guardtext)
        cheaderfile.write("#define __%s__\n\n" % guardtext)
        cheaderfile.write("#define %-24s %s\n" % ("PIC_ADDR", ("_ac" + binfiles[0].replace(".bin", "")))) #TODO!
        __BASE__ = int(argv[-1], 16)
        # print defines
        for file in binfiles:
            def_start = "_ac" + file.replace(".bin", "")
            def_size  = "_ac" + file.replace(".bin", "_size")
            cheaderfile.write("#define %-24s (0x%08X)\n" % (def_start, __BASE__ + total_size))
            cheaderfile.write("#define %-24s (0x%08X)\n" % (def_size, binfile_size[file]))
            total_size += binfile_size[file]
        
        # print "extern GUI_CONST_STORAGE GUI_BITMAP bmXXX"
        cheaderfile.write("\n\n")
        for file in binfiles:
            bmVarName = "bm" + file.replace(".bin", "")
            cheaderfile.write("extern GUI_CONST_STORAGE GUI_BITMAP %s;\n" % (bmVarName))
        cheaderfile.write("\n#endif /* __%s__ */" % guardtext)
        
    
if __name__ == "__main__":
    combine(sys.argv)