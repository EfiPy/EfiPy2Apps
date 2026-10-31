# PciTree3.py
#
# Copyright (C) 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
# GPL-v2
#
# Modified by Google DeepMind Antigravity (Gemini)
#

from EfiPy2.Lib.PciScanLib import PrintBusTree, PCI_ACCESS_IO

if __name__ == '__main__':
  PrintBusTree (AccessMode = PCI_ACCESS_IO, Segment = 0)
