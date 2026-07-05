#
# HelloEfiPy2.py
#
# Copyright (C) 2023 - 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
# HelloEfiPy2.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# EfiPy2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EfiPy2.  If not, see <http://www.gnu.org/licenses/>.
#

import EfiPy2 as EfiPy

print ( "FirmwareVendor: ", EfiPy.gST.FirmwareVendor)
print (f"FirmwareRevision: 0x{EfiPy.gST.FirmwareRevision:08X}")
print (f"gRT Signature: 0x{EfiPy.gRT.Hdr.Signature:016X} {'Pass' if EfiPy.gRT.Hdr.Signature == EfiPy.EFI_RUNTIME_SERVICES_SIGNATURE else 'Fail'}")
print (f"gST Signature: 0x{EfiPy.gST.Hdr.Signature:016X} {'Pass' if EfiPy.gST.Hdr.Signature == EfiPy.EFI_SYSTEM_TABLE_SIGNATURE     else 'Fail'}")
print (f"gBS Signature: 0x{EfiPy.gBS.Hdr.Signature:016X} {'Pass' if EfiPy.gBS.Hdr.Signature == EfiPy.EFI_BOOT_SERVICES_SIGNATURE    else 'Fail'}")
print (f"gDS Signature: 0x{EfiPy.gDS.Hdr.Signature:016X} {'Pass' if EfiPy.gDS.Hdr.Signature == EfiPy.MdePkg.Pi.PiDxeCis.DXE_SERVICES_SIGNATURE  else 'Fail'}")
EfiPy.gST.ConOut[0].OutputString(EfiPy.gST.ConOut, "Hello EfiPy2\r\n")
