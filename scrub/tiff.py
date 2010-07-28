#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Copyright (c) Michael McKinley, 2010
#All code is released under the simplified (two-clause) BSD license
"""Functions for removing any metadata from a TIFF file"""

import cStringIO
import os

if __name__ == "__main__":
    import sys

def tiff(file_in, file_out):
    pass


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit("Not enough parameters")
    if len(sys.argv) == 2:
        outfile = "%s-scr" % sys.argv[1]
    else:
        outfile = sys.argv[2]
    scrub(sys.argv[1], outfile)
