# Acpi_Apic.py
#
#   part of EfiPy2
#
# Copyright (C) 2026 MaxWu efipy.core@gmail.com
#   GPL-2.0
#

from EfiPy2.Lib.StructDump import DumpStruct
from EfiPy2.Lib.HexDump import HexDump

if __name__ == '__main__':
    from EfiPy2.Lib.Acpi.AcpiApicParser import AcpiApicParser
    from EfiPy2.Lib.Acpi.AcpiRetrieve import ExtractTable
    from EfiPy2.MdePkg.IndustryStandard import Acpi

    ApicSignature = b'APIC'

    ApicRaw = ExtractTable(ApicSignature, 0)
    if not ApicRaw:
        print('Can not retrieve APIC')
        exit(0)

    ApicObj, ApicType = AcpiApicParser(ApicRaw)
    if ApicObj is None:
        print('Failed to parse APIC')
        exit(0)

    print("""
Multiple APIC Description Table (MADT / APIC)
=======================================================================================================================""")
    DumpStruct(2, ApicObj, ApicType)

    # Aggregate sub-structures across all groups (including repeated groups like ProcessorLocalApic_1)
    SummaryCounts = {}
    BaseFieldsCount = len(Acpi.EFI_ACPI_6_5_MULTIPLE_APIC_DESCRIPTION_TABLE_HEADER._fields_)
    for FieldName, _ in ApicType._fields_[BaseFieldsCount:]:
        Category = FieldName.rsplit('_', 1)[0] if ('_' in FieldName and FieldName.rsplit('_', 1)[1].isdigit()) else FieldName
        ArrayVal = getattr(ApicObj, FieldName)
        SummaryCounts[Category] = SummaryCounts.get(Category, 0) + len(ArrayVal)

    SummaryItems = [f"{Count} {Category}(s)" for Category, Count in SummaryCounts.items()]
    if SummaryItems:
        print(f"\n[Summary] Discovered: {', '.join(SummaryItems)}")

    print('\n==== ACPI APIC RAW data ======')
    HexDump(ApicRaw)

