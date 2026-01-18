#
# EfiPyAdminSample.py
#
# Copyright (C) 2026 efipy.core@gmail.com All rights reserved.
#

try:
    from EfiPy2.Lib import Admin
except ModuleNotFoundError as e:
    import os
    if os.name == 'nt':
        def IsAdmin():
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        if (IsAdmin ()):
            print ('In Windows administrator mode, EfiPy.Lib.Admin is not found')
            print ('Please add EfiPy into PYTHONPATH in system environment variable')
            input ('Press any key to exit')
            import sys
            sys.exit (-1)
    else:
        print (e)
        sys.exit(-1)

if not Admin.IsAdmin ():
    print ('Is not Admin')
    Admin.ForkToAdmin ()

print ('In Admin mode?', Admin.IsAdmin ())
wait = input("Test OK. Press Enter to continue.")