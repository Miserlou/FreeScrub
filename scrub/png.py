#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Copyright (c) Michael McKinley, 2010
#All code is released under the simplified (two-clause) BSD license
"""Functions for removing any metadata from a TIFF file"""

from scommon import restore_pos, get_value
import cStringIO
import os

#Chunks we probably want to keep, but are safe to discard
SAFA_CHUNKS = ["bKGD", "cHRM", "gAMA", "hIST", "iCCP", "pHYs", "sPLT", \
    "sRGB", "tRNS"]
PNG_HEADER = '\x89PNG\x0d\x0a\x1a\x0a'
if __name__ == "__main__":
    import sys

def scrub(file_in, file_out, paranoid = False):
    """
    Scrub a PNG file. If paranoid is set, all ancillary chunks will be
    deleted.
    """
    file(file_out, 'wb').close()
    scrubbed = cStringIO.StringIO()
    with file(file_in, 'rb') as inp:
        _verify_png(inp)
        scrubbed.write(PNG_HEADER)
        while True:
            (c_type, header, data, crc) = _read_chunk(inp)
            if c_type is None:
                break
            if _is_safe(c_type, paranoid):
                scrubbed.write(header)
                scrubbed.write(data)
                scrubbed.write(crc)
    with file(file_out, 'wb') as out:
        out.write(scrubbed.getvalue())
    scrubbed.close()

def _is_safe(chunk, paranoia):
    #All critical chunks will be copied
    if chunk[0].isupper():
        return True
    #If we're paranoid, ignore everything else
    if paranoia:
        return False
    #Discard private chunks
    if chunk[1].islower():
        return False
    return chunk in SAFA_CHUNKS

def _read_chunk(inp):
    header = inp.read(8)
    if len(header) < 8:
        return [None] * 4
    c_length = get_value(header[0:4])
    c_type = header[5:]
    data = inp.read(c_length)
    crc = inp.read(4)
    return (c_type, header, data, crc)


def _verify_png(inp):
    data = inp.read(8)
    if data != PNG_HEADER:
        raise Exception("Invalid PNG file")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit("Not enough parameters")
    if len(sys.argv) == 2:
        outfile = "%s-scr" % sys.argv[1] 
    else:
        outfile = sys.argv[2]
    scrub(sys.argv[1], outfile, True)
