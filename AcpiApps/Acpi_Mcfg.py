# Acpi_Mcfg.py
#
#   part of EfiPy2
#
# Copyright (C) 2026 MaxWu efipy.core@gmail.com
#   GPL-2.0
#

from EfiPy2.Lib.StructDump import DumpStruct
from EfiPy2.Lib.HexDump import HexDump

if __name__ == '__main__':
    from EfiPy2.Lib.Acpi.AcpiMcfgParser import AcpiMcfgParser

    McfgSignature = b'MCFG'

    from EfiPy2.Lib.Acpi.AcpiRetrieve import ExtractTable

    McfgRaw = ExtractTable (McfgSignature, 0)
    if McfgRaw is None:
      print ('Can not retrieve MCFG')
      exit(0)
    McfgObj, McfgType = AcpiMcfgParser (McfgRaw)

    DumpStruct (2, McfgObj, McfgType)
    HexDump (McfgRaw, 0, 4)

