#
# ImportEfiPy.py
#
# Copyright (C) 2026 efipy.core@gmail.com All rights reserved.
#

#
#
#
import os, sys
import EfiPy2 as EfiPy

print ('Working folder', os.getcwd())
print ('EfiPy folder:', EfiPy.__file__)
print ()

print (os.name, sys.platform)

import platform
print ('architecture:', platform.architecture())
print ('platform:', platform.platform())
print ('processor:', platform.processor())

print ()

for k, v in EfiPy.Info.items ():
    print (f'{k}: {v}')