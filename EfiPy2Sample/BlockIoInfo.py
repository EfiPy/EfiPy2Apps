# BlockIoInfo.py
#
#   part of EfiPy2
#
# Copyright (C) 2024 - 2026 MaxWu efipy.core@gmail.com
#   GPL-2.0
#

import sys
import EfiPy2 as EfiPy

from EfiPy2.Lib.EfiPyStatus import EfiStatus
from EfiPy2.Lib.StructDump import DumpStruct
from EfiPy2.MdePkg.Protocol.BlockIo import (
    gEfiBlockIoProtocolGuid, EFI_BLOCK_IO_PROTOCOL, EFI_BLOCK_IO_MEDIA
)
from EfiPy2.MdePkg.Protocol.DevicePathEfiPy import (
    EFI_DEVICE_PATH_PROTOCOL, gEfiDevicePathProtocolGuid
)

# This function would need to run within a UEFI application using Python bindings (conceptual)
def BlockIoInfoMain ():

    BufferSize = EfiPy.UINTN (0)
    Status = EfiPy.gBS.LocateHandle(
                         EfiPy.ByProtocol,
                         EfiPy.byref (gEfiBlockIoProtocolGuid),
                         None,
                         EfiPy.byref(BufferSize),
                         None
                         )
    Status = EfiStatus(Status)

    # EFI_BUFFER_TOO_SMALL is expected for this initial size query.
    if Status != EfiPy.EFI_BUFFER_TOO_SMALL:
        if EfiPy.EFI_ERROR(Status):
            print("LocateHandle (buffer size) error:", Status)
        return Status

    HandleArrayType = EfiPy.EFI_HANDLE * (
                              BufferSize.value // EfiPy.sizeof(EfiPy.EFI_HANDLE)
                              )
    HandleArray     = HandleArrayType ()
    Status = EfiPy.gBS.LocateHandle(
                         EfiPy.ByProtocol,
                         EfiPy.byref(gEfiBlockIoProtocolGuid),
                         None,
                         EfiPy.byref(BufferSize),
                         HandleArray
                         )
    Status = EfiStatus(Status)
    if EfiPy.EFI_ERROR(Status):
        print("LocateHandle (handles) error:", Status)
        return Status
    if Status != EfiPy.EFI_SUCCESS:
        return Status

    HandleCount = BufferSize.value // EfiPy.sizeof(EfiPy.EFI_HANDLE)
    for Handle in HandleArray[:HandleCount]:
        TmpDevPath = EfiPy.PVOID ()
        Status = EfiPy.gBS.HandleProtocol (
                             Handle,
                             EfiPy.byref (gEfiDevicePathProtocolGuid),
                             EfiPy.byref (TmpDevPath)
                             )
        Status = EfiStatus(Status)
        if EfiPy.EFI_ERROR(Status):
            print("HandleProtocol (DevicePath) error:", Status)
        elif Status == EfiPy.EFI_SUCCESS:
            DevicePath = EfiPy.cast(
                                 TmpDevPath, EfiPy.POINTER(EFI_DEVICE_PATH_PROTOCOL)
                                 )[0]
            print(f"Found BlockIo device:\n  {DevicePath}")

        VoidBlockIo = EfiPy.PVOID ()
        Status = EfiPy.gBS.HandleProtocol(
                             Handle,
                             EfiPy.byref (gEfiBlockIoProtocolGuid),
                             EfiPy.byref (VoidBlockIo)
                             )
        Status = EfiStatus(Status)

        if EfiPy.EFI_ERROR(Status):
            print("HandleProtocol (BlockIo) error:", Status)
            continue
        if Status != EfiPy.EFI_SUCCESS:
            continue

        BlockIoProtocol = EfiPy.cast(
                                  VoidBlockIo, EfiPy.POINTER(EFI_BLOCK_IO_PROTOCOL)
                                  )[0]
        Media = BlockIoProtocol.Media[0]
        DiskType = "Removable" if Media.RemovableMedia else "Fixed"
        if Media.MediaPresent:
            print(f"  {DiskType} Disk has {Media.LastBlock + 1} sectors.")
        else:
            print(f"  {DiskType} Disk has no media present.")

        DumpStruct(4, Media, EFI_BLOCK_IO_MEDIA)

    Status = EfiStatus (EfiPy.EFI_SUCCESS)
    print(f"No more disk detected ({Status}).")
    return Status


if __name__ == '__main__':
  BlockIoInfoMain ()