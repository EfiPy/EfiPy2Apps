# IoOut80PortSample.py
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
#   GPL-2.0
# 

from EfiPy2.Lib.X86Processor import Me

if __name__ == '__main__':

  Me.Iow8 (0x80, 0x22)
  