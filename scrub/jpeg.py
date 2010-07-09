#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scrubber for jpeg files
"""

if __name__ == "__main__":
    import sys
    
import cStringIO
import os

def scrub(file_in, file_out):
    """
    Scrubs the jpeg file_in, returns results to file_out
    """
    stripped = cStringIO.StringIO()
    with open(file_in, 'rb') as input_:
        header = input_.read(2)
        if header != '\xff\xd8':
            raise Exception("Not a JPEG!")
        input_.seek(-2, os.SEEK_CUR)
        while True:
            byte = input_.read(1)
            if len(byte) == 0:
                break
            if byte != '\xff':
                stripped.write(byte)
            else:
                next_byte = input_.read(1)
                _get_handler(next_byte)(input_, stripped)
    with open(file_out, 'wb') as output:
        output.write(stripped.getvalue())
    stripped.close()

def _get_handler(byte):
    """
    Returns the appropriate header based on the second byte in the marker
    """
    msn = ord(byte) >> 4
    lsn = ord(byte) - (msn << 4)
    if msn == 0xc or msn == 0xd:
        if msn == 0xc and lsn != 0x8:
            return _smart_copy_handler
        if msn == 0xd and lsn >= 0xb and lsn != 0xe:
            return _smart_copy_handler
        return lambda inp, out: _basic_handler(inp, out, True)
    if msn == 0xe:
        return _app_handler
    if byte == '\x00' or byte == '\xff':
        return lambda ___, out: out.write('\xff%s' % byte)
    
    return lambda inp, out: _basic_handler(inp, out, False) 

def _app_handler(inp, out):
    """
    Handle APPn segments
    """
    if _is_jfif(inp):
        _jfif_handler(inp, out)
    else:
        length = _get_length(inp)
        inp.seek(length - 2, os.SEEK_CUR)
    
def _is_jfif(inp):
    """
    Determine if the data inp is currently seeked to indicates JFIF
    """
    save_loc = inp.tell()
    inp.seek(-1, os.SEEK_CUR)
    if inp.read(1) != '\xe0':
        rval = False
    else:
        inp.read(2)
        rval = (inp.read(6) == 'JFIF\x00\x01')
    inp.seek(save_loc, os.SEEK_SET)
    return rval
    
def _get_length(inp):
    """
    Get the length of the current frame (pointed to by inp)
    """
    return (ord(inp.read(1)) << 8) + ord(inp.read(1))

def _basic_handler(inp, out, keep):
    """
    Backend for keep and ignore handlers
    """
    #Backtrack and write the marker
    if keep:
        inp.seek(-2, os.SEEK_CUR)
        out.write(inp.read(2))
    while True:
        byte = inp.read(1)
        if len(byte) == 0:
            break
        #Handle potential markers
        if byte == '\xff':
            next_byte = inp.read(1)
            if (0x00 < ord(next_byte) < 0xff):
                inp.seek(-2, os.SEEK_CUR)
                return
            elif keep:
                out.write(byte)
                out.write(next_byte)
        elif keep:
            out.write(byte)

def _smart_copy_handler(inp, out):
    """
    Copy the data to the output until we reach a new marker
    """
    length = _get_length(inp)
    inp.seek(-4, os.SEEK_CUR)
    out.write(inp.read(length + 2))

def _jfif_handler(inp, out):
    """
    Strip out the thumbnail from a JFIF segment
    """
    out.write('\xff\xe0')
    old_length = _get_length(inp)
    out.write('\x00\x10')
    out.write(inp.read(12))
    out.write('\x00\x00')
    inp.seek(old_length - 14, os.SEEK_CUR)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit("Not enough parameters")
    if len(sys.argv) == 2:
        outfile = sys.argv[1].replace(".jpg", "-scr.jpg") 
    else:
        outfile = sys.argv[2]
    scrub(sys.argv[1], "%s-scr" % sys.argv[2])
    
__all__ = [scrub]
