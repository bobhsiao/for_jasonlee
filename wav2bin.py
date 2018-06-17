#!/usr/bin/python
"""
This module converts wav files into: a binary, a c source file and a c header file.

usage:
    wav2bin.py [wav files] [start address] [output.bin] [output.c] [output.h]

example:
    wav2bin.py beep5.wav idok.wav idfail.wav 0x10000000 wav.bin wav.c wav.h
"""
from __future__ import print_function
import os
import sys
import textwrap
import struct


def usage():
    """
    Print usage
    """
    print("usage: wav2bin.py [wav files] [start address] [output.bin] [output.c] [output.h]")

def read_wav_files(wav_files):
    """
    Read all wave files and extract them into a binary and a list of each wave's info.

    Args:
        wav_files: the list of wav filenames.

    Returns:
        ret_wavbuf: all wave binary combined without header and each wave is aligned to 4 bytes.
        ret_wavstruct: a list of all wave files' info, including filename, length,
                       sample rate, channels and bps.
    """
    ret_wavbuf = bytes("".encode('utf-8'))
    ret_wavstruct = []
    wav_addr = 0
    wav_len = 0
    wav_samplerate = 0
    for wav in wav_files:
        with open(wav, "rb") as wav_file:
            # read each wave file
            wavdata = wav_file.read()
            ret_wavbuf += wavdata[44:] # 44 means skipping header
            # get sample rate
            wav_samplerate = struct.unpack('i', wavdata[24:28])[0]
            # get nr_channels
            wav_channels = struct.unpack('H', wavdata[22:24])[0]
            # get bitspersample
            wav_bps = struct.unpack('H', wavdata[34:36])[0]
            # ret_wavbuf alignment
            wav_len = len(wavdata) - 44
            if wav_len % 4 != 0:
                align_shift = 4 - (wav_len % 4)
            else:
                align_shift = 0
            ret_wavbuf += bytes(" ".encode('utf-8')) * align_shift  # paddings for 4-byte alignment
            # save wavname, addr, len, sample rate
            ret_wavstruct.append([wav, wav_addr, wav_len, wav_samplerate, wav_channels, wav_bps])
            wav_addr += (wav_len + align_shift)

    return ret_wavbuf, ret_wavstruct

def make_wav_header(output_name, start_address, wav_list):
    """
    Create the c header file.

    Args:
        output_name: the file name of the c header file.
        start_address: base address of these wave binary
        wav_list: the list contains each wave's info,
                  which is 2nd-returned value of read_wav_files()

    Returns:
        None
    """
    wav_bin_size = 0
    with open(output_name, "w") as ofile:
        # convert start_address from ascii to int
        str_start_addr = start_address

        # write guard text
        guardtext = output_name.replace(".h", "_H").upper()
        ofile.write("#ifndef __%s__\n" % guardtext)
        ofile.write("#define __%s__\n\n" % guardtext)

        # write wav defines
        for item in wav_list:
            basename = os.path.basename(item[0]).upper().replace(".", "_")
            ofile.write("#define %-36s (%-16s + 0x%08X)\n" % (basename + "_ADDR", str_start_addr, item[1]))
            ofile.write("#define %-36s (0x%08X)\n"         % (basename + "_SIZE", item[2]))
            ofile.write("#define %-36s (0x%08X)\n"         % (basename + "_RATE", item[3]))
            ofile.write("#define %-36s (0x%08X)\n"         % (basename + "_CHANNEL", item[4]))
            ofile.write("#define %-36s (0x%08X)\n"         % (basename + "_BIT_PER_SAMPLE", item[5]))
            ofile.write("\n")
            wav_bin_size += item[2]
            #print item
        ofile.write("#define %-36s (%-16s)\n"  % ("WAV_BIN_START_ADDR", str_start_addr))
        ofile.write("#define %-36s (0x%08X)\n" % ("WAV_BIN_SIZE", wav_bin_size))

        # write something unchanged
        ofile.write(textwrap.dedent("""\n\
            struct wavRamDataInfo{
                char name[16];
                unsigned int  wav_addr;
                unsigned int  wav_size;
                unsigned int  sample_rate;
                unsigned char nr_channel;
                unsigned char bit_per_sample;
            };

            extern struct wavRamDataInfo wavData[];

            int getWavRamDataIdex(char *name);
        """))

        # ending
        ofile.write("\n#endif /* __%s__ */\n" % guardtext)

def make_wav_cfile(header_file, output_name, wav_list):
    """
    Create the c source file.

    Args:
        header_file: the file name of the c header file.
        output_name: the file name of the c source file.
        wav_list: the list contains each wave's info,
                  which is 2nd-returned value of read_wav_files()

    Returns:
        None
    """
    with open(output_name, "w") as ofile:
        ofile.write("#include \"%s\"\n" % (header_file))
        ofile.write("#include <string.h>\n\n")
        ofile.write("struct wavRamDataInfo wavData[] = {\n")

        for wav in wav_list:
            basename = os.path.basename(wav[0]).upper().replace(".", "_")
            ofile.write("{%-24s, %-24s, %-24s, %-24s, %-24s, %-36s},\n" %
                        ('"' + os.path.basename(wav[0]) + '"',
                         basename + "_ADDR",
                         basename + "_SIZE",
                         basename + "_RATE",
                         basename + "_CHANNEL",
                         basename + "_BIT_PER_SAMPLE"))
        ofile.write("};\n")

        # write something unchanged
        ofile.write(textwrap.dedent("""\n\
            int getWavRamDataIdex(char *name ){
                int i;
                for(i=0; i<sizeof(wavData)/sizeof(wavData[0]); i++){
                if(strcmp(name, wavData[i].name) == 0)
                    break;			
                }
                return (i<sizeof(wavData)/sizeof(wavData[0])? i:-1);
            }
        """))

def main():
    """
    main function of this script.
    """
    # vars
    wavfiles = []
    wavbuf = ""
    wavlist = []
    start_address = ""
    output_bin = ""
    output_c = ""
    output_h = ""

    # parse argv
    if len(sys.argv) < 6:
        usage()
        return

    wavfiles = sys.argv[1:-4]
    start_address = sys.argv[-4]
    output_bin = sys.argv[-3]
    output_c = sys.argv[-2]
    output_h = sys.argv[-1]
    print(wavfiles, start_address, output_bin, output_c, output_h)

    # read all wavs
    wavbuf, wavlist = read_wav_files(wavfiles)

    # create wav.bin
    with open(output_bin, "wb") as output:
        output.write(wavbuf)

    # create wav.h
    make_wav_header(output_h, start_address, wavlist)

    # create wav.c
    make_wav_cfile(output_h, output_c, wavlist)


if __name__ == "__main__":
    main()
