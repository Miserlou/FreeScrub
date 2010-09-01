#!/usr/bin/env python

from distutils.core import setup
import py2exe
import glob

opts = {
    "py2exe": {
    "includes":"cairo, pango, pangocairo, atk, gobject"
               ",encodings,encodings.*",
    }
}

setup(windows=[{'script': 'scrubber.py',
                "icon_resources": [(1, "icon.png")]}],
      options=opts,
     ) 
