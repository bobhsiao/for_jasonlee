# -*- coding:UTF-8 -*-
'''
output binary format:
[Parameters][Header Len][Binary Len][Binary][CRC32]
'''
import sys, getopt, struct, binascii

def usage():
    print "usage: %s -p '[para1 para2 ... paraN]' -i [input filename] -o [output filename]" % (sys.argv[0])
    # example:
    # make_header.py ap eeprom ver: 3.7 2017/05/06 -i kernel.bin -o firmware.bin

def main():
    # parse input args
    parameters = ''
    ifilename = ''
    ofilename = ''
    ibuf = None
    crc32 = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hp:i:o:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ('-p', '-P'):
            parameters = arg
        elif opt in ('-i', '-I'):
            ifilename = arg
        elif opt in ('-o', '-O'):
            ofilename = arg


    # read ifilename to ibuf and calculate crc32
    with open(ifilename, "rb") as f:
        ibuf = f.read()
    crc32 = binascii.crc32(ibuf) & 0xffffffff

    # make header
    with open(ofilename, "wb") as f:
        f.write(parameters)                         # [Parameters]
        f.write(struct.pack("I", len(parameters)))  # [Header Len] 4 bytes
        f.write(struct.pack("I", len(ibuf)))        # [Binary Len] 4 bytes
        f.write(ibuf)                               # [Binary]
        f.write(struct.pack("I", crc32))            # [CRC32] 4 bytes

    # print summary
    print '%-12s %s\n%-12s %s\n%-12s %s\n%-12s 0x%08X' % ("Parameters:", parameters, "Input:", ifilename, "Output:", ofilename, "CRC32", crc32)

if __name__ == "__main__":
    main()
