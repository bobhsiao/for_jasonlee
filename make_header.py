# -*- coding:UTF-8 -*-
'''
output binary format:
[Parameters][Header Len][Binary Len][Binary][CRC32]

install crccheck:
linux: sudo pip install crccheck
windows: c:\Python27\Scripts\pip install crccheck

ref url:
http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
https://pypi.python.org/pypi/crccheck/0.6
'''
import sys, getopt, struct
from crccheck.crc import Crc32Mpeg2, Crc32

def usage():
    print "usage: %s -p '[para1 para2 ... paraN]' -i [input filename] -o [output filename]" % (sys.argv[0])
    # usage:
    # make_header.py -p '[para1 para2 ... paraN]' -i [input filename] -o [output filename]
    # example:
    # make_header.py -p 'ap eeprom ver: 3.7 2017/05/06' -i kernel.bin -o firmware.bin

def crc32_mpeg2(buf):
    return Crc32Mpeg2.calc(bytearray(buf))

def crc32_std(buf):
    return Crc32.calc(bytearray(buf))

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
    crc32 = crc32_std(ibuf)

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
    #buffer = [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39]
    #print "CRC32_MPEG2=0x%08X, CRC32_STD=0x%08X" % (crc32_mpeg2(buffer), crc32_std(buffer))
