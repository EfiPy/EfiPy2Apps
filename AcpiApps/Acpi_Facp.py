# Acpi_Facp.py
#
#   part of EfiPy2
#
# Copyright (C) 2026 MaxWu efipy.core@gmail.com
#   GPL-2.0
#

from EfiPy2.Lib.StructDump import DumpStruct
from EfiPy2.Lib.HexDump import HexDump

if __name__ == '__main__':
    from EfiPy2.Lib.Acpi.AcpiFacpParser import AcpiFacpParser

    FacpSignature = b'FACP'

    from EfiPy2.Lib.Acpi.AcpiRetrieve import ExtractTable

    FacpRaw = ExtractTable (FacpSignature, 0)
    if not FacpRaw:
      print ('Can not retrieve FACP')
      exit (0)

    FacpObj, FacpType = AcpiFacpParser (FacpRaw)
    if FacpObj is None:
      print ('Can not parse FACP')
      exit (0)

    print (f"""
Fixed ACPI Description Table (FACP)
=======================================================================================================================""")
    DumpStruct (2, FacpObj, FacpType)

    print ('\n==== ACPI FACP RAW data ======')
    HexDump (FacpRaw)
