# Acpi_Facp.py 與 AcpiFacpParser.py 設計提案與規範建議書 (Proposal & Specification)

## 一、 提案背景與收斂原則

### 1.1 背景說明
在 ACPI（Advanced Configuration and Power Interface）規範中，**FACP / FADT（Fixed ACPI Description Table）** 是整個 ACPI 系統不可或缺的核心控制表格，官方 Signature 為 `b'FACP'`。

FADT 扮演著硬體與作業系統電源管理（OSPM）溝通的關鍵樞紐：
* **固定硬體暫存器區塊（Fixed Hardware Registers）**：定義 PM1a/PM1b 事件控制暫存器、PM2 控制暫存器、PM 定時器（PM Timer）與一般目的事件（GPE0/GPE1）區塊。
* **韌體控制與喚醒機制**：透過 `FirmwareCtrl` / `XFirmwareCtrl` 指向 FACS（Firmware ACPI Control Structure），負責系統休眠（S3 Sleep）喚醒向量。
* **系統 DSDT 描述表指標**：透過 `Dsdt` / `XDsdt` 欄位指向系統差分定義區塊（DSDT），提供核心 ACPI 命名空間與 AML 位元碼。
* **重置與電源管理設定**：定義系統重置暫存器（`ResetReg`）、重置數值（`ResetValue`）、電源管理設定檔（`PreferredPmProfile`）及 ACPI 啟用／停用控制命令埠（`SmiCmd`, `AcpiEnable`, `AcpiDisable`）。

由於 FADT 隨著 ACPI 規範從 1.0、2.0、3.0、4.0、5.0 到 6.5 歷經多次擴充，表格長度由 116 Bytes 擴展至 276 Bytes，因此其解析架構依賴 `AcpiFacp` 資料庫進行動態版本對映。本提案參照 `Acpi_Apic.md` 與 `Acpi_Bgrt.md` 之二階架構標準進行檢視與收斂。

### 1.2 核心收斂原則
1. **多版本動態分派與邊界防護**：
   * FADT 各版本長度各異（Rev 1: 116 Bytes, Rev 3: 244 Bytes, Rev 4: 244 Bytes, Rev 5: 268 Bytes, Rev 6: 276 Bytes）。
   * `AcpiFacpParser` 必須先驗證 `len(FacpRaw) >= 36`（標準 Header），再檢驗 `FacpHead.Signature == b'FACP'`。
   * 透過 `AcpiFacp.get(FacpHead.Revision)` 取得結構定義，若遇未知版本或 `len(FacpRaw) < sizeof(FacpType)`，嚴格回傳 `(None, None)`，防範 `KeyError` 與 `ValueError`。
2. **`Flags` 與 `IaPcBootArch` 位元階層解構（Bit Field Expansion）**：
   * 依據 ACPI 6.5 Table 5.10 與 Table 5.12 規範：
     - **`IaPcBootArch` (16-bit)**：定義 `LegacyDevices`、`Boot8042`、`VgaNotPresent`、`MsiNotSupported`、`PcieAspmControls` 與 `CmosRtcNotPresent` 等開機硬體特徵。
     - **`Flags` (32-bit)**：定義 `Wbinvd`、`ProcC1`、`SlpButton`、`RtcS4`、`ResetRegSup`、`UsePlatformClock`、`HwReducedAcpi`、`LowPowerS0IdleCapable` 等 22 個關鍵特徵。
   * 比照 `Acpi_Apic` 與 `Acpi_Bgrt` 標準，採用 EDK2 `Union`（純量與 `Bits` 結構）進行封裝，使 `DumpStruct` 能夠自動展現細部硬體特徵支援狀態。
3. **App 終端展示與輸出規範化**：
   * 補齊標準標題 Banner：`Fixed ACPI Description Table (FACP)`。
   * 補齊二進位 Raw Dump 分隔標題：`==== ACPI FACP RAW data ======`，維持跨表格輸出的一致性。
   * 修正 `HexDump` 呼叫格式，統一維持左對齊無縮排之標準十六進位檢視。
4. **健全的邊界與防禦性編程**：
   * 將表格提取檢查由 `if FacpRaw is None:` 強化為 `if not FacpRaw:`，防範 Windows 或權限不足時取得長度為 0 之空資料。
   * App 端呼叫 Parser 後加入 `if FacpObj is None:` 驗證，杜絕解析失敗後傳遞 `None` 至 `DumpStruct` 引發二度崩潰。
5. **CLI 工具健全性與多餘檔案清理**：
   * 修正 `AcpiFacpParser.py` 之 CLI 參數索引（由錯誤的 `sys.argv[4]` 改為標準 `sys.argv[1]`），並補上引數長度與檔案存在性檢查。
   * 移除誤放於 `site-packages/EfiPy2/Lib/Acpi/` 底下之重複檔案 `Acpi_Facp.py`（應用程式應統一收納於 `Apps/AcpiApps/`）。

---

## 二、 模組架構與資料流

```mermaid
graph LR
    A["System Firmware (UEFI / OS)"] -->|ExtractTable b'FACP'| B["Acpi_Facp.py (App)"]
    B -->|FacpRaw| C["AcpiFacpParser.py (Parser)"]
    
    subgraph Parser Core Engine
        C -->|1. Header Check| C1["Header Length >= 36 & Signature == b'FACP'"]
        C -->|2. Version Lookup| C2["AcpiFacp.get(FacpHead.Revision)"]
        C -->|3. Bitfield Expansion| C3["_GetExpandedFacpType: Flags & IaPcBootArch Unions"]
        C -->|4. Boundary Check| C4["len(FacpRaw) >= sizeof(FacpType) & FacpHead.Length"]
        C -->|5. Type Binding| C5["FacpType.from_buffer_copy(FacpRaw)"]
    end
    
    C5 -->|Return (FacpObj, FacpType)| B
    B -->|Formatted Output| D["DumpStruct(2, FacpObj, FacpType)"]
    B -->|Raw Binary Bytes| E["HexDump(FacpRaw)"]
```

---

## 三、 AcpiFacpParser.py 規格說明

* **檔案位置**：`d:\EfiPyWorkSpaceII\VmQemu\QemuDisk\Efi\StdLib\lib\python36.8\site-packages\EfiPy2\Lib\Acpi\AcpiFacpParser.py`
* **輸入參數**：`FacpRaw (bytes / bytearray)`
* **輸出結果**：`(FacpObj, FacpType)`，若資料無效、簽章不符、未知版本或長度不足則回傳 `(None, None)`。
* **核心實作機制**：
  1. **邊界與表頭檢查**：
     - 檢查 `not FacpRaw` 或 `len(FacpRaw) < 36`。
     - 解析 `EFI_ACPI_DESCRIPTION_HEADER`，核對簽章是否為 `b'FACP'`。
  2. **版本結構對映與位元欄位解構**：
     - 透過 `AcpiFacp.get(FacpHead.Revision)` 查詢結構定義型別。
     - 若版本未註冊或為未知數值，直接回傳 `(None, None)`。
     - 透過 `_GetExpandedFacpType` 將 `IaPcBootArch`（16-bit）替換為 `IA_PC_BOOT_ARCH` Union，將 `Flags`（32-bit）替換為 `FADT_FLAGS` Union。
  3. **資料長度嚴格驗證**：
     - 核對 `len(FacpRaw) >= sizeof(FacpType)` 且 `len(FacpRaw) >= FacpHead.Length`。
     - 使用 `from_buffer_copy` 生成結構物件。
  4. **獨立 CLI 命令列支援**：
     - 修正 CLI 引數索引為 `sys.argv[1]`，並提供完善的例外捕捉與說明輸出。

---

## 四、 Acpi_Facp.py 規格說明

* **檔案位置**：`d:\EfiPyWorkSpaceII\VmQemu\QemuDisk\Efi\Apps\AcpiApps\Acpi_Facp.py`
* **表格 Signature**：`b'FACP'`
* **執行職責與流程**：
  1. 呼叫 `ExtractTable(b'FACP', 0)` 自系統韌體中提取 FADT 二進位表格。
  2. 防禦性檢查 `if not FacpRaw:`，未取得表格時提示並退出。
  3. 呼叫 `AcpiFacpParser(FacpRaw)` 進行反序列化；若回傳 `(None, None)` 則提示錯誤退出。
  4. 輸出標準表格標題：
     ```text
     Fixed ACPI Description Table (FACP)
     =======================================================================================================================
     ```
  5. 呼叫 `DumpStruct(2, FacpObj, FacpType)` 輸出樹狀階層結構。
  6. 輸出二進位資料分隔標題 `==== ACPI FACP RAW data ======`，並呼叫 `HexDump(FacpRaw)` 輸出完整十六進位資料。

---

## 五、 預期執行輸出範例

在 UEFI Shell 或具備權限之系統下執行 `python Acpi_Facp.py` 的標準輸出範例（以 QEMU/Bochs ACPI 2.0+ Revision 3 為例）：

```text
FS0:\Efi\Apps\AcpiApps\> python Acpi_Facp.py

Fixed ACPI Description Table (FACP)
=======================================================================================================================
  Header                                                         Struct EFI_ACPI_DESCRIPTION_HEADER
    Signature                                                      0x50434146
    Length                                                         0x000000F4
    Revision                                                       0x03
    Checksum                                                       0xB0
    OemId << UINT8 * 6 (0x0006) >>
          0  1  2  3  4  5  6  7   8  9  A  B  C  D  E  F  01234567 89ABCDEF
    ------------------------------------------------------------------------
    00   42 4F 43 48 53 20                                 BOCHS            

    OemTableId                                             0x2020202043505842
    OemRevision                                                    0x00000001
    CreatorId                                                      0x43505842
    CreatorRevision                                                0x00000001
  FirmwareCtrl                                                   0x7FBC4000
  Dsdt                                                           0x7FB79000
  Reserved0                                                      0x01
  PreferredPmProfile                                             0x00
  SciInt                                                         0x0009
  SmiCmd                                                         0x000000B2
  AcpiEnable                                                     0x02
  AcpiDisable                                                    0x03
  S4BiosReq                                                      0x00
  PstateCnt                                                      0x00
  Pm1aEvtBlk                                                     0x00000600
  Pm1bEvtBlk                                                     0x00000000
  Pm1aCntBlk                                                     0x00000604
  Pm1bCntBlk                                                     0x00000000
  Pm2CntBlk                                                      0x00000000
  PmTmrBlk                                                       0x00000608
  Gpe0Blk                                                        0x00000620
  Gpe1Blk                                                        0x00000000
  Pm1EvtLen                                                      0x04
  Pm1CntLen                                                      0x02
  Pm2CntLen                                                      0x00
  PmTmrLen                                                       0x04
  Gpe0BlkLen                                                     0x10
  Gpe1BlkLen                                                     0x00
  Gpe1Base                                                       0x00
  CstCnt                                                         0x00
  PLvl2Lat                                                       0x0FFF
  PLvl3Lat                                                       0x0FFF
  FlushSize                                                      0x0000
  FlushStride                                                    0x0000
  DutyOffset                                                     0x00
  DutyWidth                                                      0x00
  DayAlrm                                                        0x00
  MonAlrm                                                        0x00
  Century                                                        0x32
  IaPcBootArch                                                   Union IA_PC_BOOT_ARCH
    Uint16                                                         0x0002
    Bits                                                           Struct IA_PC_BOOT_ARCH_BITS
      LegacyDevices                                          0x0000 (1)
      Boot8042                                               0x0001 (1)
      VgaNotPresent                                          0x0000 (1)
      MsiNotSupported                                        0x0000 (1)
      PcieAspmControls                                       0x0000 (1)
      CmosRtcNotPresent                                      0x0000 (1)
      Reserved                                               0x0000 (10)
  Reserved1                                                      0x00
  Flags                                                          Union FADT_FLAGS
    Uint32                                                         0x000084A5
    Bits                                                           Struct FADT_FLAGS_BITS
      Wbinvd                                                 0x00000001 (1)
      WbinvdFlush                                            0x00000000 (1)
      ProcC1                                                 0x00000001 (1)
      PLvl2Up                                                0x00000000 (1)
      PwrButton                                              0x00000000 (1)
      SlpButton                                              0x00000001 (1)
      FixRtc                                                 0x00000000 (1)
      RtcS4                                                  0x00000001 (1)
      TmrValExt                                              0x00000000 (1)
      DckCap                                                 0x00000000 (1)
      ResetRegSup                                            0x00000001 (1)
      SealedCase                                             0x00000000 (1)
      Headless                                               0x00000000 (1)
      CpuSwSlp                                               0x00000000 (1)
      PciExpWak                                              0x00000000 (1)
      UsePlatformClock                                       0x00000001 (1)
      S4RtcStsValid                                          0x00000000 (1)
      RemotePowerOnCapable                                   0x00000000 (1)
      ForceApicClusterModel                                  0x00000000 (1)
      ForceApicPhysicalDestinationMode                       0x00000000 (1)
      HwReducedAcpi                                          0x00000000 (1)
      LowPowerS0IdleCapable                                  0x00000000 (1)
      Reserved                                               0x00000000 (10)
  ResetReg                                                       Struct EFI_ACPI_2_0_GENERIC_ADDRESS_STRUCTURE
    AddressSpaceId                                                 0x01
    RegisterBitWidth                                               0x08
    RegisterBitOffset                                              0x00
    Reserved                                                       0x00
    Address                                                0x0000000000000CF9
  ResetValue                                                     0x0F
  Reserved2 << UINT8 * 3 (0x0003) >>
        0  1  2  3  4  5  6  7   8  9  A  B  C  D  E  F  01234567 89ABCDEF
  ------------------------------------------------------------------------
  00   00 00 00                                          ...              

  XFirmwareCtrl                                          0x0000000000000000
  XDsdt                                                  0x000000007FB79000
  XPm1aEvtBlk                                                    Struct EFI_ACPI_2_0_GENERIC_ADDRESS_STRUCTURE
    AddressSpaceId                                                 0x01
    RegisterBitWidth                                               0x20
    RegisterBitOffset                                              0x00
    Reserved                                                       0x00
    Address                                                0x0000000000000600
  XPm1bEvtBlk                                                    Struct EFI_ACPI_2_0_GENERIC_ADDRESS_STRUCTURE
    AddressSpaceId                                                 0x00
    RegisterBitWidth                                               0x00
    RegisterBitOffset                                              0x00
    Reserved                                                       0x00
    Address                                                0x0000000000000000
  XPm1aCntBlk                                                    Struct EFI_ACPI_2_0_GENERIC_ADDRESS_STRUCTURE
    AddressSpaceId                                                 0x01
    RegisterBitWidth                                               0x10
    RegisterBitOffset                                              0x00
    Reserved                                                       0x00
    Address                                                0x0000000000000604
  XPm1bCntBlk                                                    Struct EFI_ACPI_2_0_GENERIC_ADDRESS_STRUCTURE
    AddressSpaceId                                                 0x00
    RegisterBitWidth                                               0x00
    RegisterBitOffset                                              0x00
    Reserved                                                       0x00
    Address                                                0x0000000000000000
  XPm2CntBlk                                                     Struct EFI_ACPI_2_0_GENERIC_ADDRESS_STRUCTURE
    AddressSpaceId                                                 0x00
    RegisterBitWidth                                               0x00
    RegisterBitOffset                                              0x00
    Reserved                                                       0x00
    Address                                                0x0000000000000000
  XPmTmrBlk                                                      Struct EFI_ACPI_2_0_GENERIC_ADDRESS_STRUCTURE
    AddressSpaceId                                                 0x01
    RegisterBitWidth                                               0x20
    RegisterBitOffset                                              0x00
    Reserved                                                       0x00
    Address                                                0x0000000000000608
  XGpe0Blk                                                       Struct EFI_ACPI_2_0_GENERIC_ADDRESS_STRUCTURE
    AddressSpaceId                                                 0x01
    RegisterBitWidth                                               0x80
    RegisterBitOffset                                              0x00
    Reserved                                                       0x00
    Address                                                0x0000000000000620
  XGpe1Blk                                                       Struct EFI_ACPI_2_0_GENERIC_ADDRESS_STRUCTURE
    AddressSpaceId                                                 0x00
    RegisterBitWidth                                               0x00
    RegisterBitOffset                                              0x00
    Reserved                                                       0x00
    Address                                                0x0000000000000000

==== ACPI FACP RAW data ======
            0  1  2  3  4  5  6  7   8  9  A  B  C  D  E  F  01234567 89ABCDEF
------------------------------------------------------------------------------
00000000   46 41 43 50 F4 00 00 00  03 B0 42 4F 43 48 53 20  FACP.... ..BOCHS 
00000010   42 58 50 43 20 20 20 20  01 00 00 00 42 58 50 43  BXPC     ....BXPC
00000020   01 00 00 00 00 40 BC 7F  00 90 B7 7F 01 00 09 00  .....@.. ........
00000030   B2 00 00 00 02 03 00 00  00 06 00 00 00 00 00 00  ........ ........
00000040   04 06 00 00 00 00 00 00  00 00 00 00 08 06 00 00  ........ ........
00000050   20 06 00 00 00 00 00 00  04 02 00 04 10 00 00 00   ....... ........
00000060   FF 0F FF 0F 00 00 00 00  00 00 00 00 32 02 00 00  ........ ....2...
00000070   A5 84 00 00 01 08 00 00  F9 0C 00 00 00 00 00 00  ........ ........
00000080   0F 00 00 00 00 00 00 00  00 00 00 00 00 90 B7 7F  ........ ........
00000090   00 00 00 00 01 20 00 00  00 06 00 00 00 00 00 00  ..... .. ........
000000A0   00 00 00 00 00 00 00 00  00 00 00 00 01 10 00 00  ........ ........
000000B0   04 06 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ........ ........
000000C0   00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ........ ........
000000D0   01 20 00 00 08 06 00 00  00 00 00 00 01 80 00 00  . ...... ........
000000E0   20 06 00 00 00 00 00 00  00 00 00 00 00 00 00 00   ....... ........
000000F0   00 00 00 00                                       ....             
```

---

## 六、 結論與優勢

1. **版本健全性防護**：修正直接以 `Revision` 查字典引發之 `KeyError` 風險，透過嚴謹的邊界檢查確保損壞或未知資料回傳 `(None, None)`。
2. **輸出風格統一**：補齊標準標題 Banner、RAW Dump 分割線，並移除不合規範的多餘縮排。
3. **消除潛在崩潰**：以 `if not FacpRaw:` 杜絕 Windows 環境下的空 bytearray 繞過檢查，避免 Parser 拋出 `ValueError`。
4. **目錄結構淨化**：清除誤放於庫目錄的重複應用程式檔案，維持模組架構職責分明。

