#!/usr/bin/env python
from __future__ import print_function
import sys

# embed as PostScript comment
print(u'%!PS-Adobe-2.0 EPSF-2.0 ', ' '.join(sys.argv))
print(r'%%BoundingBox:126 267 486 526')
for line in sys.stdin:
    sys.stdout.write('% ' + line)
