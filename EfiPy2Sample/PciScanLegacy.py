# PciScan3.py
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
#   GPL-2.0
#

from EfiPy2.Lib.PciScanLib import PrintPciDeviceList, PCI_ACCESS_IO

if __name__ == '__main__':
  PrintPciDeviceList (AccessMode = PCI_ACCESS_IO, Segment = 0)
