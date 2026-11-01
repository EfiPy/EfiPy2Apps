# Acpi_Bgrt.py 與 AcpiBgrtParser.py 設計提案與規範建議書 (Proposal & Specification)

## 一、 提案背景與收斂原則

### 1.1 背景說明
在 UEFI 韌體開機流程中，**BGRT（Boot Graphics Resource Table）** 是 ACPI 5.0+ 規範中用於描述系統開機階段 OEM 品牌 Logo 或開機狀態畫面的核心表格，官方 Signature 為 `b'BGRT'`。

其主要職責是將 UEFI 開機期間在螢幕上繪製的高解析度圖形資訊（通常為 BMP 格式）傳遞給作業系統（OS）：
* **無縫開機體驗（Seamless Boot Experience）**：作業系統（如 Windows Bootmgr、Linux plymouth）在接管顯示輸出時，可直接讀取 BGRT 表中指定的實體記憶體位址（`ImageAddress`），延續顯示韌體 Logo，避免螢幕閃爍或黑屏。
* **圖像屬性與坐標定位**：提供圖像在螢幕上的偏移坐標（`ImageOffsetX`, `ImageOffsetY`）、圖像類型（`ImageType`，目前規範定義 BMP 為 0，即 `Acpi.EFI_ACPI_5_0_BGRT_IMAGE_TYPE_BMP`）以及旋轉與顯示狀態（`Status`）。

本提案參照 `Acpi_Apic.md` 之二階架構標準（Parser 專注於二進位資料解析，App 負責從系統提取、展示並存取實體硬體資源），針對既有程式碼進行檢視與收斂。

### 1.2 核心收斂原則
1. **表格固定結構與長度精準核對**：
   * BGRT 表格為固定長度結構體（共 56 Bytes），由 36 Bytes 標準 ACPI Header、2 Bytes 版本號、1 Byte 狀態、1 Byte 圖片型別、8 Bytes 圖片實體位址、4 Bytes X 偏移與 4 Bytes Y 偏移組成。
   * Parser 必須核對 `len(BgrtRaw) >= 56` 且 `Header.Length == 56`，嚴格防範資料截斷或長度異常。

2. **`Status` 欄位拆解為 Bit Field**：
   * 依據 ACPI 6.5 Table 5.48 規範，BGRT 的 1 Byte `Status` 包含關鍵屬性：
     - Bit 0: **Displayed**（`1` = 圖像在開機時已繪製於螢幕上，OS 可繼續保留；`0` = 未繪製）
     - Bits 1..2: **OrientationOffset**（圖像旋轉角度：`00b`=0°, `01b`=90° 順時針, `10b`=180°, `11b`=270° 順時針）
     - Bits 3..7: **Reserved**（保留，必須為 0）
   * 比照 `Acpi_Apic` 標準，採用 EDK2 `Union`（`Uint8` + `Bits` 結構）解構，使 `DumpStruct` 能清晰列出開機畫面之繪製狀態與旋轉參數。

3. **跨平台實體記憶體對映健全性（Fix GetBufFromPa Crash）**：
   * 讀取實體記憶體前先核對 `ImageAddress != 0`。
   * 修正 Windows 環境下 `GetBufFromPa` 回傳 `-1` 導致呼叫端 tuple 解包（`BgrtMem, Offset = -1`）拋出 `TypeError` 崩潰之問題，統一回傳 `(None, None)`。
   * Linux 環境下若開檔（`/dev/mem`）或記憶體映射（`mmap`）失敗，統一回傳 `(None, None)`；映射使用完畢後主動關閉映射與檔案資源。
   * 呼叫端加入嚴謹的 `if (None, None) == (VaBuff, Offset): return` 防護，安全略過不拋出例外。
   * 消除同一實體位址重複呼叫 `GetBufFromPa` 3 次的冗餘存取。

4. **修復標題誤植與邊界防禦**：
   * 修正 `Acpi_Bgrt.py` 終端輸出中誤植為 `Firmware Performance Descript Table (FPDT)` 的錯誤文字，正名為 `Boot Graphics Resource Table (BGRT)`。
   * 將提取表格之判斷由 `if BgrtRaw is None:` 強化為 `if not BgrtRaw:`，避免在提取傳回空 `bytearray` 時引發 Buffer 過小崩潰。
   * 修正 `AcpiBgrtParser.py` CLI 參數索引（由 `sys.argv[4]` 改為標準 `sys.argv[1]`）。

---

## 二、 模組架構與資料流

```mermaid
graph LR
    A["System Firmware (UEFI / OS)"] -->|ExtractTable b'BGRT'| B["Acpi_Bgrt.py (App)"]
    B -->|BgrtRaw| C["AcpiBgrtParser.py (Parser)"]
    
    subgraph Parser Core Engine
        C -->|1. Boundary Check| C1["Header & Buffer Length Check (56 Bytes)"]
        C -->|2. Status Bitfield| C2["Status Union: Displayed & Rotation"]
        C -->|3. Type Binding| C3["EFI_ACPI_6_5_BOOT_GRAPHICS_RESOURCE_TABLE"]
    end
    
    C3 -->|Return (BgrtObj, BgrtType)| B
    B -->|Formatted Output| D["DumpStruct(2, BgrtObj, BgrtType)"]
    
    subgraph Physical Memory Probe
        B -->|GetBufFromPa ImageAddress| E["OS / Firmware Memory (PA)"]
        E -->|Map BMP Header| F["Parsing BMP_IMAGE_HEADER"]
        F -->|Dump BMP Structure| G["DumpStruct(2, BmpHeader, BmpType)"]
    end
    
    B -->|Raw Binary Bytes| H["HexDump(BgrtRaw & BMP Payload)"]
```

---

## 三、 AcpiBgrtParser.py 規格說明

* **檔案位置**：`d:\EfiPyWorkSpaceII\VmQemu\QemuDisk\Efi\StdLib\lib\python36.8\site-packages\EfiPy2\Lib\Acpi\AcpiBgrtParser.py`
* **輸入參數**：`BgrtRaw (bytes / bytearray)`
* **輸出結果**：`(BgrtObj, BgrtType)`，若資料無效或長度不足 56 Bytes 則回傳 `(None, None)`。
* **核心實作機制**：
  1. **邊界與長度防護**：
     - 檢查 `BgrtRaw` 是否為空。
     - 檢查 `len(BgrtRaw) >= 56` 且 `Header.Length == 56`，若不合直接回傳 `(None, None)`，杜絕拋出例外。
     - 改採 `from_buffer_copy`，相容唯讀 `bytes` 與 `bytearray`。
  2. **`Status` 位元階層解構**：
     - 定義 `BGRT_STATUS_BITS` 與 `BGRT_STATUS` Union，包含 `Displayed` (1-bit)、`OrientationOffset` (2-bit) 與 `Reserved` (5-bit)。
     - 替換預設結構之 `Status` 欄位，精準維持 56 Bytes 大小。
  3. **獨立 CLI 命令列支援**：
     - 支援 `python AcpiBgrtParser.py <BgrtBinaryFile>`，參數索引修正為 `sys.argv[1]`，並提供健全的引數個數與檔案存在性檢查。

---

## 四、 Acpi_Bgrt.py 規格說明

* **檔案位置**：`d:\EfiPyWorkSpaceII\VmQemu\QemuDisk\Efi\Apps\AcpiApps\Acpi_Bgrt.py`
* **表格 Signature**：`b'BGRT'`
* **執行職責與流程**：
  1. 呼叫 `ExtractTable(b'BGRT', 0)` 自系統韌體中提取 BGRT 二進位表格。
  2. 加入防禦性檢查 `if not BgrtRaw:`，在無表格或未具備讀取權限時提示並退出。
  3. 呼叫 `AcpiBgrtParser(BgrtRaw)` 進行二進位反序列化；若解析失敗則報錯退出。
  4. 透過 `DumpStruct(2, BgrtObj, BgrtType)` 輸出標準階層樹狀結構，修正標題為 `Boot Graphics Resource Table (BGRT)`。
  5. 讀取 `BgrtObj.ImageAddress`，確認 `ImageAddress != 0` 後透過改善後的 `GetBufFromPa` 映射實體記憶體：
     - 在 Windows 或無權限環境下安全略過（回傳 `(None, None)` 不拋出例外）。
     - Linux 環境下若開檔或映射失敗回傳 `(None, None)`；映射使用完畢後主動關閉映射與檔案資源。
     - 在 UEFI Shell / Linux 環境下，若 `BgrtObj.ImageType == Acpi.EFI_ACPI_5_0_BGRT_IMAGE_TYPE_BMP` (0x00)，解析並印出 `BMP_IMAGE_HEADER` 結構。
     - 呼叫 `HexDump` 輸出該圖片實體記憶體前段資料。
  6. 透過 `HexDump(BgrtRaw)` 印出 BGRT ACPI 原始表格十六進位與 ASCII 內容。

---

## 五、 預期執行輸出範例

在 UEFI Shell 或具備權限之 Linux 命令列下執行 `python Acpi_Bgrt.py` 的標準輸出如下：

```text
FS0:\Efi\Apps\AcpiApps\> python Acpi_Bgrt.py

Boot Graphics Resource Table (BGRT)
=======================================================================================================================
EFI_ACPI_6_5_BOOT_GRAPHICS_RESOURCE_TABLE:
  Header:
    Signature: b'BGRT'
    Length: 0x00000038 (56)
    Revision: 0x01
    Checksum: 0xB2
    OemId: b'INTEL '
    OemTableId: b'EDK2    '
    OemRevision: 0x00000002
    CreatorId: b'EDK2'
    CreatorRevision: 0x01000013
  Version: 0x0001
  Status: Union BGRT_STATUS
    Uint8: 0x01
    Bits: Struct BGRT_STATUS_BITS
      Displayed: 0x01 (1)
      OrientationOffset: 0x00 (2)
      Reserved: 0x00 (5)
  ImageType: 0x00 (BMP)
  ImageAddress: 0x000000007AF20018
  ImageOffsetX: 0x00000168 (360)
  ImageOffsetY: 0x000001B8 (440)

BMP Image Header:
=======================================================================================================================
BMP_IMAGE_HEADER:
  CharB: 0x42 (B)
  CharM: 0x4D (M)
  Size: 0x00038436 (230454)
  Reserved[0]: 0x0000
  Reserved[1]: 0x0000
  ImageOffset: 0x00000036 (54)
  HeaderSize: 0x00000028 (40)
  PixelWidth: 0x00000140 (320)
  PixelHeight: 0x000000F0 (240)
  Planes: 0x0001
  BitPerPixel: 0x0018 (24)
  CompressionType: 0x00000000
  ImageSize: 0x00038400 (230400)
  XPixelsPerMeter: 0x00000B12 (2834)
  YPixelsPerMeter: 0x00000B12 (2834)
  NumberOfColors: 0x00000000
  ImportantColors: 0x00000000
  (註：EDK2 之 BMP_IMAGE_HEADER.Reserved 定義為 UINT16 * 2，實際展開為兩元素；亦可簡化示意為 Reserved: 0x0000)

BGRT Image Address: 0x7AF20018
=======================================================================================================================
            0  1  2  3  4  5  6  7   8  9  A  B  C  D  E  F  01234567 89ABCDEF
------------------------------------------------------------------------------
00000000   42 4D 36 84 03 00 00 00  00 00 36 00 00 00 28 00  BM6..... ..6...(.
00000010   00 00 40 01 00 00 F0 00  00 00 01 00 18 00 00 00  ..@..... ........
00000020   00 00 00 84 03 00 12 0B  00 00 12 0B 00 00 00 00  ........ ........
00000030   00 00 00 00 00 00 FF FF  FF FF FF FF FF FF FF FF  ........ ........

==== ACPI BGRT RAW data ======
            0  1  2  3  4  5  6  7   8  9  A  B  C  D  E  F  01234567 89ABCDEF
------------------------------------------------------------------------------
00000000   42 47 52 54 38 00 00 00  01 B2 49 4E 54 45 4C 20  BGRT8... ..INTEL 
00000010   45 44 4B 32 20 20 20 20  02 00 00 00 45 44 4B 32  EDK2     ....EDK2
00000020   13 00 00 01 01 00 01 00  18 00 F2 7A 00 00 00 00  ........ ...z....
00000030   68 01 00 00 B8 01 00 00                           h.......         
```

---

## 六、 結論與優勢

1. **架構標準化**：完全對齊 `Acpi_Apic` 與整體 EfiPy2 ACPI 模組之規範，消除歷史複製貼上殘留的 FPDT 錯誤字串。
2. **記憶體安全防護**：修正 `GetBufFromPa` 在 Windows 下回傳 `-1` 造成的解包崩潰，支援無實體存取權限時的安全降級。
3. **細緻位元解構**：將 `Status` 展開為 `Displayed` 與 `OrientationOffset`，便於快速確認品牌開機 Logo 之顯示與旋轉狀態。
4. **健全邊界防護**：導入嚴格的 56 Bytes 長度核對，杜絕在資料截斷或空 Buffer 時發生例外。

