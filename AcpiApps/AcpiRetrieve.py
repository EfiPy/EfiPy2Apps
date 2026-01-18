# AcpiRetrieve.py
#
#   part of EfiPy2
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com
#   GPL-2.0
#

from EfiPy2.Lib.Acpi.AcpiRetrieve import ExtractMain

if __name__ == '__main__':
    import os
    try:
        ExtractMain ()
    except Exception as e:
        print (e)
