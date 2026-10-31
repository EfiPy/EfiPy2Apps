# PciScan.py
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
#   GPL-2.0
#

import argparse
from EfiPy2.Lib.PciScanLib import PrintPciDeviceList, PCI_ACCESS_MCFG, PCI_ACCESS_IO

if __name__ == '__main__':
  parser = argparse.ArgumentParser (prog = 'PciScan.py')
  parser.add_argument ('-m', '--mode', choices = [PCI_ACCESS_MCFG, PCI_ACCESS_IO], default = PCI_ACCESS_MCFG,
                       help = 'PCI config space access mode: mcfg (MMIO) or io (CF8/CFC)')
  parser.add_argument ('-s', '--segment', type = lambda x: int (x, 0), default = None,
                       help = 'PCI Segment Group Number (optional)')
  args = parser.parse_args ()

  PrintPciDeviceList (AccessMode = args.mode, Segment = args.segment)
