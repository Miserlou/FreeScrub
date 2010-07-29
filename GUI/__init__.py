import os
import sys

app_root = unicode(os.path.split(__path__[0])[0])
image_root = os.path.join(app_root, 'images')

if app_root.startswith(os.path.join(sys.prefix,'bin')):
    # I'm installed on *nix
    image_root, doc_root = map( lambda p: os.path.join(sys.prefix, p), calc_unix_dirs() )

