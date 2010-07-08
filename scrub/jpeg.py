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
    otmp = cStringIO.StringIO()
    with open(file_in, 'rb') as input_:
        while True:
            byte = input_.read(1)
            if len(byte) == 0:
                break
            if ord(byte) != 0xff:
                otmp.write(byte)
            else:
                byte2 = input_.read(1)
                _get_handler(byte2)(input_, otmp)
    with open(file_out, 'wb') as output:
        output.write(otmp.getvalue())
    otmp.close()

def _get_handler(byte):
    """
    Returns the appropriate header based on the second byte in the marker
    """
    msn = ord(byte) >> 4
    if msn == 0xc or msn == 0xd: #Image data segments
        return _copy_handler
    if msn == 0xe: #APPn segments
        return _app_handler
    if byte == '\x00' or byte == '\xff':
        return lambda inp, out: out.write('\xff%s' % byte)
    
    return _trash_handler 

def _app_handler(inp, out):
    """
    Handle APPn segments
    """
    if _is_jfif(inp):   #We want to keep non-thumbnail JFIF data.
        _jfif_handler(inp, out)
    else:   #APPn segments seem to be  ordered 0xFFEn #### where #### is the
            #number of bytes
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

def _trash_handler(inp, out):
    """
    Ignore the data until we reach a new marker
    """
    length = _get_length(inp)
    inp.seek(length, os.SEEK_CUR)

def _copy_handler(inp, out):
    """
    Copy the data to the output until we reach a new marker
    """
    length = _get_length(inp)
    inp.seek(-2, os.SEEK_CUR)
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
    scrub(sys.argv[1], "%s-scr" % sys.argv[1])
    
__all__ = [scrub]
