#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scrubber for jpeg files
"""

if __name__ == "__main__":
    import sys
    
import cStringIO
import os


jfif_header_1 = '\xff\xd8\xff\xe0'
jfif_header_2 = 'JFIF\x00'
    
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
        return _keep_handler

    if msn == 0xe: #APPn segments
        return _app_handler

    if ord(byte) == 0xfe: #COM
        return _ignore_handler

    
    if not (0x00 < ord(byte) < 0xff):   #0xff00 and 0xffff aren't markers
        return lambda inp, out: out.write('\xff%s' % byte)
    
    
    return _keep_handler #TODO: handle every case properly

def _app_handler(inp, out):
    """
    Handle APPn segments
    """
    _keep_handler(inp, out) #TODO: actually do something here

def _ignore_handler(inp, out):
    """
    Ignore the data until we reach a new marker
    """
    _copy_handler(inp, out, False)


def _keep_handler(inp, out):
    """
    Copy the data to the output until we reach a new marker
    """
    _copy_handler(inp, out, True)


def _copy_handler(inp, out, keep):
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
            #called by _keep_handler
            elif keep:
                out.write(byte)
                out.write(byte2)
        elif keep:
            out.write(byte)


def _jfif_handler(inp, out):
    """
    Handle jfif segments
    """
    pass

if __name__ == "__main__":
    scrub(sys.argv[1], "%s-scr" % sys.argv[1])
    
__all__ = [scrub]
