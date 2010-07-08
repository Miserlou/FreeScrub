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
    msn = ord(byte) >> 4 #Most significant nibble

    if msn == 0xc or msn == 0xd: #Image data segments
        return _copy_handler

    if msn == 0xe: #APPn segments
        return _app_handler
    
    if ord(byte) == 0x00 or ord(byte) == 0xff:
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
        length = (ord(inp.read(1)) << 8) + ord(inp.read(1))
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
    

def _trash_handler(inp, out):
    """
    Ignore the data until we reach a new marker
    """
    _basic_handler(inp, out, False)

def _copy_handler(inp, out):
    """
    Copy the data to the output until we reach a new marker
    """
    _basic_handler(inp, out, True)


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

        #If we hit a potential marker, check if the next byte is 0x00 or
        #0xff. If so, then it's not a marker. Otherwise, seek backwards
        #and leave.
        if ord(byte) == 0xff:
            byte2 = inp.read(1)
            if (0x00 < ord(byte2) < 0xff):
                inp.seek(-2, os.SEEK_CUR)
                return
            #Only write out if we're keeping the data (e.g, this was
            #called by _copy_handler
            elif keep:
                out.write(byte)
                out.write(byte2)
        elif keep:
            out.write(byte)

def _jfif_handler(inp, out):
    """
    Strip out the thumbnail from a JFIF segment
    """
    out.write('\xff\xe0')
    old_length = (ord(inp.read(1)) << 8) + ord(inp.read(1))
    out.write('\x00\x10')   #Our new JFIF segment will not contain a thumbnail
    out.write(inp.read(12)) #Copy over everything but the thumbnail
    out.write('\x00\x00')   #Set thumbnail size to 0 by 0
    inp.seek(old_length - 14, os.SEEK_CUR)

if __name__ == "__main__":
    scrub(sys.argv[1], "%s-scr" % sys.argv[1])
    
__all__ = [scrub]
