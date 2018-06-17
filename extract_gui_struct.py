# -*- coding:UTF-8 -*-

import sys

def usage():
    print "usage: %s [file1.c] [file2.c] ... [fileN.c] output.c" % (sys.argv[0])


def get_struct(filename):
    print "parsing %s ..." % (filename),
    struct = []
    flag_save = False
    with open(filename, "rt") as f:
        lines = f.readlines()
        for line in lines:
            if flag_save == False and line.startswith("GUI_CONST_STORAGE GUI_BITMAP"):
                struct.append(line)
                flag_save = True
            elif flag_save == True:
                struct.append(line)
                if line.startswith("};"):
                    break
    
    if len(struct) == 0: print "Failed"
    else: print "OK"
    
    return struct
    
def extract_gui_struct(argv):
    # vars
    structs = []
    
    # check argv
    if len(argv) < 2:
        usage()
        return
      
    # traverse all c files
    for f in argv[1:-1]:
        structs.append(get_struct(f))
    
    # create output.c
    output_filename = argv[-1]
    guardtext = output_filename.replace(".c", "_h_include").upper()
    with open(output_filename, "wb") as f:
        f.write("#include <stdlib.h>\n")
        f.write("#include \"GUI.h\"\n")
        f.write("#include \"Window_Pic.h\"\n\n")
        f.write("#undef GUI_CONST_STORAGE\n#define GUI_CONST_STORAGE \n\n")
        
        for s in structs:
            for line in s:
                f.write(line)
            f.write("\n")

     
if __name__ == "__main__":
    extract_gui_struct(sys.argv)