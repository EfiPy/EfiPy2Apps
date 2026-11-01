# Acpi_Apic.py 與 AcpiApicParser.py 設計提案與規範建議書 (Proposal & Specification)

## 一、 提案背景與收斂原則

### 1.1 背景說明
在 UEFI 韌體環境下，**MADT（Multiple APIC Description Table）** 是描述系統中斷控制器架構與處理器核心的核心 ACPI 表格，其官方 Signature 為 `b'APIC'`，在 EfiPy2 程式庫中對應的標準命名為 **`AcpiApicParser.py`** 與 **`Acpi_Apic.py`**。其結構由固定長度的標準表頭，以及後續連續排列的多個可變長度子結構（Sub-structures）組成。

本提案比照 `Acpi_Bgrt.py` 與 `AcpiBgrtParser.py` 的二階分層架構（Parser 專注於二進位資料解析，App 負責從系統提取並輸出），並針對實際運作特性聚焦收斂以下重點原則：

### 1.2 核心收斂原則
1. **限定 x86 結構**：
   * 核心支援 x86 / x64 常見的關鍵中斷控制器型別：
     * Type 0x00: **Processor Local APIC**
     * Type 0x01: **I/O APIC**
     * Type 0x02: **Interrupt Source Override (ISO)**
     * Type 0x03: **Non-Maskable Interrupt Source (NMI Source)**
     * Type 0x04: **Local APIC NMI**
     * Type 0x05: **Local APIC Address Override**
     * Type 0x06: **I/O SAPIC**
     * Type 0x07: **Processor Local SAPIC**
     * Type 0x08: **Platform Interrupt Sources**
     * Type 0x09: **Processor Local x2APIC**
     * Type 0x0A: **Local x2APIC NMI**
     * Type 0x10: **Multiprocessor Wakeup**
   * 其餘架構型別（如 ARM GIC 系列、RISC-V / LoongArch 系列）或未定義型別，統一作為原始資料結構（包含 Type, Length 與 RawData）保留，不擴充無效定義。

2. **確保結構布局符合每筆 Length（解決記憶體偏移錯位問題）**：
   * 在既有解析邏輯中，解析指標以 `SubLength` 向前推進，但 ctypes 複合結構（`_fields_`）則是依照 `sizeof(TargetClass)` 依序配置位移。
   * 若韌體填入的 `SubLength` 與 EDK2 預定義結構體的 `sizeof(TargetClass)` 不一致，將導致 ctypes 欄位位移與二進位 Buffer 脫節，使後續所有子結構全部讀取錯位。
   * **解決機制**：
     - 若為已知 x86 型別且 `SubLength == sizeof(TargetClass)`，方套用具體結構體。
     - 若為已知型別但長度不符，或為非 x86 / 未知型別，則依據該筆實際的 `SubLength` 動態建構 raw 結構（長度固定為 `SubLength - 2`），保證整體複合結構與原始二進位資料 100% 吻合。

3. **連續同型別聚合為 ctypes Array (`ProcessorLocalApic[0]`, `ProcessorLocalApic[1]`...)**：
   * **相同 Type 內部定義一致**：同一 Type 的子結構長度與欄位皆相同（例如每個 Local APIC 皆為 8 Bytes，IO APIC 皆為 12 Bytes，ISO 皆為 10 Bytes）。
   * **動態聚合機制**：
     - 解析器逐筆掃描子結構時，將連續出現的相同型別結構**聚合成 ctypes Array**：`("ProcessorLocalApic", TargetClass * Count)`。
     - `DumpStruct` 內部內建之 `DumpArray` 會自動將各元素印為 `ProcessorLocalApic[0]`、`ProcessorLocalApic[1]`、`IoApic[0]`、`InterruptSourceOverride[0]`...，取代舊有的 `_00`、`_01` 命名。
     - 上層程式能直接以 `ApicObj.ProcessorLocalApic[0]`、`len(ApicObj.ProcessorLocalApic)`、`for item in ApicObj.ProcessorLocalApic` 進行操作。
     - 若遇伺服器跨 Socket 交錯排列（例如 Local APIC 區塊中間插入 IOAPIC），若該型別再次出現，則自動立新分組（如 `ProcessorLocalApic_1[0]`），保證記憶體映射永不錯位。

4. **`Flags` 欄位拆解為 Bit Field（支援 Local APIC、x2APIC 與 ISO）**：
   * **處理器旗標（Local APIC & x2APIC Flags, 32-bit）**：
     - Bit 0: **Enabled**（處理器已啟用且就緒）
     - Bit 1: **OnlineCapable**（支援執行期動態熱插拔上線）
     - Bits 2..31: **Reserved**（保留，必須為 0）
   * **中斷來源重定位旗標（MPS INTI Flags, 16-bit）**：
     - 依據 ACPI 6.5 Table 5.40 規範，針對 `InterruptSourceOverride`、`LocalApicNmi` 等結構的 16-bit Flags 進行解構：
     - Bits 0..1: **Polarity**（極性：00=Conforms to Bus, 01=Active High, 10=Reserved, 11=Active Low）
     - Bits 2..3: **TriggerMode**（觸發模式：00=Conforms to Bus, 01=Edge-triggered, 10=Reserved, 11=Level-triggered）
     - Bits 4..15: **Reserved**（保留，必須為 0）
   * 採用 EDK2 標準之 **`Union`（數值 + `Bits` 結構）** 宣告：
     - 記憶體長度嚴格維持 4 Bytes（LAPIC/x2APIC）與 2 Bytes（ISO），結構整體大小精確維持 8 Bytes（LAPIC）、16 Bytes（x2APIC）與 10 Bytes（ISO），與 ACPI 規格 100% 吻合。
     - `DumpStruct` 原生支援 Union 與 Bit Field 階層印出，能同時清晰展示原始數值與個別 Bit 的詳細解構。

5. **嚴格邊界與完整性檢查（Strict Boundary Check）**：
   * 進入解析前，檢查 `len(ApicRaw)` 是否足以容納基底表頭。
   * 檢查表頭宣告的 `TotalLength` 是否不小於表頭大小且不超出 Buffer 邊界；若 `TotalLength > len(ApicRaw)` 或 `TotalLength < BaseHeaderSize`，視為資料損壞，直接回傳 `(None, None)`。
   * 逐筆迭代子結構時，確認：
     - 剩餘位元組至少有 2 Bytes 供讀取 `Type` 與 `Length`。
     - 每筆 `SubLength >= 2`（防止長度小於 2 或為 0 造成異常與死迴圈）。
     - 每筆子結構範圍不越界（`Offset + SubLength <= TotalLength`）。
     - 遇到上述任一異常時，立即回傳 `(None, None)`，不容許殘缺物件。
   * 迭代結束時嚴格核對 `Offset == TotalLength`，確保宣告的位元組皆完整被子結構消耗完畢，否則回傳 `(None, None)`。

6. **App 職責極簡化**：
   * 移除額外的 MMIO 記憶體探測與複雜硬體測試項目。
   * `Acpi_Apic.py` 專注於標準工具流程：提取 `b'APIC'`、呼叫 `AcpiApicParser`、透過 `DumpStruct` 輸出結構樹狀資料，並透過 `HexDump` 輸出原始二進位資料。

---

## 二、 模組架構與資料流

```mermaid
graph LR
    A["System Firmware (UEFI / OS)"] -->|ExtractTable b'APIC'| B["Acpi_Apic.py (App)"]
    B -->|ApicRaw| C["AcpiApicParser.py (Parser)"]
    
    subgraph Parser Core Engine
        C -->|1. Boundary Check| C1["Header & Buffer Boundary Check"]
        C2_1["Flags Union / Bitfield Breakdown (LAPIC & ISO)"] --> C2
        C -->|2. Length Verification| C2["Verify SubLength == sizeof(Class)"]
        C -->|3. Run-length Grouping| C3["TargetClass * Count (Array)"]
    end
    
    C3 -->|Return (ApicObj, ApicType)| B
    B -->|Formatted Output (Array View)| D["DumpStruct(2, ApicObj, ApicType)"]
    B -->|Raw Binary Bytes| E["HexDump(ApicRaw)"]
```

---

## 三、 AcpiApicParser.py 規格說明

* **檔案位置**：`Efi\StdLib\lib\python36.8\site-packages\EfiPy2\Lib\Acpi\AcpiApicParser.py`
* **輸入參數**：`ApicRaw (bytes / bytearray)`
* **輸出結果**：`(ApicObj, ApicType)`，若資料無效或長度不足則回傳 `(None, None)`。
* **相容別名**：模組內提供 `AcpiMadtParser = AcpiApicParser` 別名，確保呼叫 MADT 命名的相依模組無縫相容。
* **核心實作機制**：
  1. **嚴格邊界與長度防護**：進入解析時核對表頭長度與 `Header.Length`，逐筆迭代時檢查剩餘位元組與 `SubLength >= 2`；若遇截斷、不合法長度或迭代結束時 `Offset != TotalLength`，一律直接回傳 `(None, None)`，嚴格杜絕殘缺結構與死迴圈。
  2. **x86 型別與長度嚴格核對**：支援上述 12 種 APIC/MADT 子結構型別；僅在 `SubLength == sizeof(CandidateClass)` 時套用專屬型別，否則動態建構相符長度的 raw 結構。
  3. **Flags 位元階層解構**：使用 Union（`Uint32`/`Uint16` + `Bits`）拆解 Local APIC/x2APIC 之 `Enabled`、`OnlineCapable`，以及 ISO 之 `Polarity`、`TriggerMode`。
  4. **連續同型別動態聚合**：掃描過程中自動將連續同型別子結構聚合為 `TargetClass * Count` 的 ctypes Array，天然支援 `DumpStruct` 的陣列輸出與 Python 索引操作。

---

## 四、 Acpi_Apic.py 規格說明

* **檔案位置**：`Efi\Apps\AcpiApps\Acpi_Apic.py`
* **表格 Signature**：`b'APIC'`
* **執行職責與流程**：
  1. 呼叫 `ExtractTable(b'APIC', 0)` 自系統韌體中提取 APIC/MADT 二進位表格。
  2. 加入防禦性檢查 `if not ApicRaw:`，在無表格或未具備讀取權限時提示並退出。
  3. 呼叫 `AcpiApicParser(ApicRaw)` 進行二進位反序列化與複合型別建置。
  4. 透過 `DumpStruct(2, ApicObj, ApicType)` 輸出標準階層樹狀結構（自動以 `[0]`, `[1]` 原生陣列格式展開，並逐項列出 `Flags` 各 bit 狀態）。
  5. 遍歷並自動依類別累加所有子結構分組（包含交錯時產生的後續分組如 `ProcessorLocalApic_1`），精確輸出各類結構的總計摘要。
  6. 透過 `HexDump(ApicRaw)` 印出原始表格十六進位與 ASCII 內容。

---

## 五、 預期執行輸出範例

在 UEFI Shell 或命令列下執行 `python Acpi_Apic.py` 的標準輸出如下：

```text
FS0:\Efi\Apps\AcpiApps\> python Acpi_Apic.py

Multiple APIC Description Table (MADT / APIC)
=======================================================================================================================
EFI_ACPI_6_5_MULTIPLE_APIC_DESCRIPTION_TABLE_HEADER:
  Header:
    Signature: b'APIC'
    Length: 0x0000005C (92)
    Revision: 0x03
    Checksum: 0x85
    OemId: b'BOCHS '
    OemTableId: b'BXPCAPIC'
    OemRevision: 0x00000001
    CreatorId: b'BXPC'
    CreatorRevision: 0x00000001
  LocalApicAddress: 0xFEE00000
  Flags: 0x00000001
  ProcessorLocalApic[0]                                        Struct EFI_ACPI_6_5_PROCESSOR_LOCAL_APIC_STRUCTURE
    Type: 0x00
    Length: 0x08
    AcpiProcessorUid: 0x00
    ApicId: 0x00
    Flags: Union PROCESSOR_LOCAL_APIC_FLAGS
      Uint32: 0x00000001
      Bits: Struct PROCESSOR_LOCAL_APIC_FLAGS_BITS
        Enabled: 0x00000001 (1)
        OnlineCapable: 0x00000000 (1)
        Reserved: 0x00000000 (30)
  ProcessorLocalApic[1]                                        Struct EFI_ACPI_6_5_PROCESSOR_LOCAL_APIC_STRUCTURE
    Type: 0x00
    Length: 0x08
    AcpiProcessorUid: 0x01
    ApicId: 0x01
    Flags: Union PROCESSOR_LOCAL_APIC_FLAGS
      Uint32: 0x00000001
      Bits: Struct PROCESSOR_LOCAL_APIC_FLAGS_BITS
        Enabled: 0x00000001 (1)
        OnlineCapable: 0x00000000 (1)
        Reserved: 0x00000000 (30)
  IoApic[0]                                                    Struct EFI_ACPI_6_5_IO_APIC_STRUCTURE
    Type: 0x01
    Length: 0x0C
    IoApicId: 0x00
    Reserved: 0x00
    IoApicAddress: 0xFEC00000
    GlobalSystemInterruptBase: 0x00000000
  InterruptSourceOverride[0]                                   Struct EFI_ACPI_6_5_INTERRUPT_SOURCE_OVERRIDE_STRUCTURE
    Type: 0x02
    Length: 0x0A
    Bus: 0x00
    Source: 0x00
    GlobalSystemInterrupt: 0x00000002
    Flags: Union MPS_INTI_FLAGS
      Uint16: 0x0000
      Bits: Struct MPS_INTI_FLAGS_BITS
        Polarity: 0x0000 (2)
        TriggerMode: 0x0000 (2)
        Reserved: 0x0000 (12)
  InterruptSourceOverride[1]                                   Struct EFI_ACPI_6_5_INTERRUPT_SOURCE_OVERRIDE_STRUCTURE
    Type: 0x02
    Length: 0x0A
    Bus: 0x00
    Source: 0x09
    GlobalSystemInterrupt: 0x00000009
    Flags: Union MPS_INTI_FLAGS
      Uint16: 0x000D
      Bits: Struct MPS_INTI_FLAGS_BITS
        Polarity: 0x0001 (2)
        TriggerMode: 0x0003 (2)
        Reserved: 0x0000 (12)

[Summary] Discovered: 2 ProcessorLocalApic(s), 1 IoApic(s), 2 InterruptSourceOverride(s)

==== ACPI MADT RAW data ======
00000000: 41 50 49 43 5C 00 00 00 03 85 42 4F 43 48 53 20  APIC\.....BOCHS 
00000010: 42 58 50 43 41 50 49 43 01 00 00 00 42 58 50 43  BXPCAPIC....BXPC
00000020: 01 00 00 00 00 00 E0 FE 01 00 00 00 00 08 00 00  ................
00000030: 01 00 00 00 00 08 01 01 01 00 00 00 01 0C 00 00  ................
00000040: 00 00 C0 FE 00 00 00 00 02 0A 00 00 02 00 00 00  ................
00000050: 00 00 02 0A 00 09 09 00 00 00 0D 00              ............
```

---

## 六、 結論與優勢

1. **架構一致性**：完全貼合 `Acpi_Mcfg.py` 與 `Acpi_Bgrt.py` 現存規範，命名統一對齊 `APIC` 表簽名，保持程式碼精簡、可讀性高且易於維護。
2. **原生陣列語法 (`[0]`, `[1]`)**：將連續同型別聚合為 `TargetClass * Count`，使 `DumpStruct` 天然輸出 `ProcessorLocalApic[0]`、`ProcessorLocalApic[1]`、`IoApic[0]`，符合直覺且取代舊式 `_00`、`_01` 命名。
3. **全面位元解構 (`Flags` Bit Field)**：
   - 處理器 Flags：展開 `Enabled` (Bit 0) 與 `OnlineCapable` (Bit 1)。
   - 中斷重定位 Flags（MPS INTI）：展開 `Polarity` (Bits 0..1) 與 `TriggerMode` (Bits 2..3)。
   - 兼顧除錯易讀性與二進位精準對齊。
4. **布局零錯位**：透過 `SubLength == sizeof(CandidateClass)` 嚴格檢驗，杜絕因韌體長度差異或非標準欄位導致的 ctypes 位移錯位問題。
5. **安全邊界防護**：加入表頭、宣告長度與每筆子結構的基本邊界校驗，有效防範長度為 0 造成的死迴圈及 Buffer 越界存取。
