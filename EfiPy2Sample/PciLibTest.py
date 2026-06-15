#
# PciLibTest.py
#
# Copyright (C) 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
#   GPL-2.0
#
from EfiPy2.Lib import EfiPyPci


print (f'McfgBassAddress (1): {EfiPyPci.McfgBassAddress}')

Bus = 0x00
Dev = 0x00
Fun = 0x00
print (f'{Bus:02X}:{Dev:02X}.{Fun:02X} at 0x{EfiPyPci.GetPciEcam (Bus, Dev, Fun):016X}')

Bus = 0x00
Dev = 0x02
Fun = 0x00
print (f'{Bus:02X}:{Dev:02X}.{Fun:02X} at 0x{EfiPyPci.GetPciEcam (Bus, Dev, Fun):016X}')

print (f'McfgBassAddress (2): 0x{EfiPyPci.McfgBassAddress:016X}')