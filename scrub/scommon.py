#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Copyright (c) Michael McKinley, 2010
#All code is released under the simplified (two-clause) BSD license

import os
def restore_pos(file_index):
    """Decorator that ensures the position in the file before and after the 
       function call remains the same. Takes one argument: which argument
       contains the file in question.
       """
    def wrap(func):
        def wrapped_f(*args, **kargs):
            pos_at = args[file_index].tell()
            rval = func(*args, **kargs)
            args[file_index].seek(pos_at, os.SEEK_SET)
            return rval
        return wrapped_f
    return wrap

def get_value(bytes_, little_endian = False):
    """
    Converts bytes_ to a number.
    """
    if little_endian:
        bytes_ = reduce(lambda acc, new: "%s%s" % (new, acc), bytes_, "")

    sum_ = 0
    for byte in bytes_:
        sum_ = (sum_ << 8) + ord(byte)
    return sum_
