#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Copyright (c) Michael McKinley, 2010
#All code is released under the simplified (two-clause) BSD license
"""Functions for removing any metadata from a JPEG file"""

import cStringIO
import os
from scrubdec import restore_pos


if __name__ == "__main__":
    import sys
    
def scrub(file_in, file_out):
    """
    Scrubs the jpeg file_in, returns results to file_out
    """
    #Before we do anything, make sure that file_out is writeable
    file(file_out, 'wb').close()
    stripped = cStringIO.StringIO()
    
    with file(file_in, 'rb') as input_:
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
    with file(file_out, 'wb') as output:
        output.write(stripped.getvalue())
    stripped.close()


def _get_handler(byte):
    """
    Returns the appropriate header based on the second byte in the marker
    """
    #most/least significant nibbles
    msn = ord(byte) >> 4
    lsn = ord(byte) - (msn << 4)
    if msn == 0xc or msn == 0xd:
        #Determine if we can use the "smart" copier
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

    @restore_pos(0)
    def is_jfif(inp):
        "Check if we're at a jfif segment"
        inp.seek(-1, os.SEEK_CUR)
        if inp.read(1) != '\xe0':
            rval = False
        else:
            inp.read(2)
            rval = (inp.read(6) == 'JFIF\x00\x01')
        return rval
        
    if is_jfif(inp):
        _jfif_handler(inp, out)
    else:
        length = _get_length(inp)
        inp.seek(length, os.SEEK_CUR) #
    
def _basic_handler(inp, out, copy_data):
    "Simple handler: scan the input until a new marker is reached"
    #Backtrack and write the marker
    if copy_data:
        inp.seek(-2, os.SEEK_CUR)
        out.write(inp.read(2))

    while True:
        byte = inp.read(1)
        #Stop if we reach EOF
        if len(byte) == 0:
            break
        #Handle potential markers
        if byte == '\xff':
            next_byte = inp.read(1)
            #If we reach a marker, backtrack and give it to the appropriate
            #handler
            if (0x00 < ord(next_byte) < 0xff):
                inp.seek(-2, os.SEEK_CUR)
                return
            #Write the non-marker
            elif copy_data:
                out.write(byte)
                out.write(next_byte)
        #Write the byte if necessary
        elif copy_data:
            out.write(byte)

def _smart_copy_handler(inp, out):
    "Use the length field to copy the segment in one chunk"
    length = _get_length(inp)
    inp.seek(-2, os.SEEK_CUR) #
    out.write(inp.read(length + 2))

def _jfif_handler(inp, out):
    "Strips the thumbnail from a JFIF segment"
    #Write the APP0 tag
    out.write('\xff\xe0')
    old_length = _get_length(inp)
    inp.seek(2, os.SEEK_CUR)
    #The new header will be 16 (0x10) bytes long
    out.write('\x00\x10')
    #Copy over the original JFIF data
    out.write(inp.read(12))
    #Ensure the thumbnail size is 0x0
    out.write('\x00\x00')
    #Skip over any thumbnail data
    inp.seek(old_length - 14, os.SEEK_CUR)

@restore_pos(0)
def _get_length(inp):
    "Read the reported length of the segment"
    val = (ord(inp.read(1)) << 8) + ord(inp.read(1))
    return val

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit("Not enough parameters")
    if len(sys.argv) == 2:
        outfile = "%s-scr" % sys.argv[1]
    else:
        outfile = sys.argv[2]
    scrub(sys.argv[1], outfile)
    
__all__ = [scrub]
