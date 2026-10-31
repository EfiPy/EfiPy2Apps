# PciScan2.py
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
#   GPL-2.0
#

import argparse
from pprint import pprint
from EfiPy2.Lib.PciScanLib import ScanPciDevices, PCI_ACCESS_MCFG, PCI_ACCESS_IO

if __name__ == '__main__':
  parser = argparse.ArgumentParser (prog = 'PciScanBare.py')
  parser.add_argument ('-m', '--mode', choices = [PCI_ACCESS_MCFG, PCI_ACCESS_IO], default = PCI_ACCESS_MCFG,
                       help = 'PCI config space access mode: mcfg (MMIO) or io (CF8/CFC)')
  parser.add_argument ('-s', '--segment', type = lambda x: int (x, 0), default = None,
                       help = 'PCI Segment Group Number (optional)')
  args = parser.parse_args ()

  devices = ScanPciDevices (AccessMode = args.mode, Segment = args.segment)
  print (f"Access Mode: {args.mode}")
  pprint (devices)
