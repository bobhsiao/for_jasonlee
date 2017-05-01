#!/usr/bin/python

import os, sys, textwrap, struct

def usage():
    print "usage: wav2bin.py [wav files] [start address] [output.bin] [output.c] [output.h]"

def ReadWavs(tWavfiles):
    ret_wavbuf = ""
    ret_wavstruct = []
    wav_addr = 0
    wav_len = 0
    wav_samplerate = 0
    for wav in tWavfiles:
        with open(wav, "rb") as f:
            # read each wave file
            wavdata = f.read()
            ret_wavbuf += wavdata[44:] # 44 means skipping header
            # get sample rate
            wav_samplerate = struct.unpack('i', wavdata[24:28])[0]
            # ret_wavbuf alignment 
            wav_len = len(wavdata) - 44
            if wav_len % 4 != 0:
                align_shift = 4 - (wav_len % 4)
            else:
                align_shift = 0
            ret_wavbuf += " " * align_shift  # paddings for 4-byte alignment
            # save wavname, addr, len, sample rate
            ret_wavstruct.append([wav, wav_addr, wav_len, wav_samplerate])
            wav_addr += (wav_len + align_shift)
    
    return ret_wavbuf, ret_wavstruct

def MakeWavH(tOutputName, tStartAddr, tWavList):
    wav_bin_size = 0
    with open(tOutputName, "w") as cheaderfile:
        # convert tStartAddr from ascii to int 
        numStartAddr = int(tStartAddr, 16)
        
        # write guard text
        guardtext = tOutputName.replace(".h", "_H").upper()
        cheaderfile.write("#ifndef __%s__\n" % guardtext)
        cheaderfile.write("#define __%s__\n\n" % guardtext)
        
        # write wav defines
        for item in tWavList:
            basename = os.path.basename(item[0]).upper().replace(".", "_")
            cheaderfile.write("#define %-24s (0x%08X)\n" % (basename + "_ADDR", item[1] + numStartAddr))
            cheaderfile.write("#define %-24s (0x%08X)\n" % (basename + "_SIZE", item[2]))
            cheaderfile.write("#define %-24s (0x%08X)\n" % (basename + "_RATE", item[3]))
            cheaderfile.write("\n")
            wav_bin_size += item[2]
            #print item
        cheaderfile.write("#define %-24s (0x%08X)\n" % ("WAV_BIN_START_ADDR", numStartAddr))
        cheaderfile.write("#define %-24s (0x%08X)\n" % ("WAV_BIN_SIZE", wav_bin_size))
        
        # write something unchanged
        cheaderfile.write(textwrap.dedent("""\n\
            struct wavRamDataInfo{
                char name[16];
                unsigned int  wav_addr;
                unsigned int  wav_size;
                unsigned int  sample_rate;
            };

            extern struct wavRamDataInfo wavData[];

            int getWavRamDataIdex(char *name);
        """))
        
        # ending
        cheaderfile.write("\n#endif /* __%s__ */\n" % guardtext)

def MakeWavC(tHeaderFile, tOutputName, tWavList):
    with open(tOutputName, "w") as cfile:
        cfile.write("#include \"%s\"\n" % (tHeaderFile))
        cfile.write("#include <string.h>\n\n")
        cfile.write("struct wavRamDataInfo wavData[] = {\n")
 
        for wav in tWavList:
            basename = os.path.basename(wav[0]).upper().replace(".", "_")
            cfile.write("{%-24s, %-24s, %-24s, %-24s},\n" % ('"' + os.path.basename(wav[0]) + '"', basename + "_ADDR", basename + "_SIZE", basename + "_RATE"))
        cfile.write("};\n")

        # write something unchanged
        cfile.write(textwrap.dedent("""\n\
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
    # vars
    wavfiles = []
    wavbuf = ""
    wavlist = []
    start_address = 0
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
    print wavfiles, start_address, output_bin, output_c, output_h

    # read all wavs
    wavbuf, wavlist = ReadWavs(wavfiles)

    # create wav.bin
    with open(output_bin, "wb") as f:
        f.write(wavbuf)        

    # create wav.h    
    MakeWavH(output_h, start_address, wavlist)
    
    # create wav.c
    MakeWavC(output_h, output_c, wavlist)
    

if __name__ == "__main__":
    main()
