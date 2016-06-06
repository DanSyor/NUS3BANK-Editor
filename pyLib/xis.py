# coding: utf-8
from __future__ import absolute_import, division, print_function
import pyLib.six as six
# import six
import sys

''' Attempting to solve UnicodeEncodeError problems for Python 2
        and doing nothing for Python 3
'''

def encode(s):
    if six.PY3:
        return s
    else:
        return s.encode(sys.getfilesystemencoding()) # afaik this always seems to work

def decode(s):
    if six.PY3:
        return s
    else:
        try:
            print(u"Attempt 1: no decoding")
            return s + u''
        except UnicodeDecodeError or UnicodeEncodeError:
            try:
                print(u"Attempt 2: decoding from file system encoding")
                return s.decode(sys.getfilesystemencoding()) + u''
            except UnicodeDecodeError or UnicodeEncodeError:
                print(u"Attempt 3: decoding from console output encoding")
                return s.decode(sys.stdout.encoding) + u'' # weird, but maybe 1st solution doesn't always work?
        
# if len(sys.argv) > 1:
    # print(decode(sys.argv[1]))
