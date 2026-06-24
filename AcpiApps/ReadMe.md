# EfiPy ACPI Application Note
EfiPy ACPI Applications are Python-based script for interacting with **ACPI (Advanced Configuration and Power Interface)** tables within UEFI environments and modern operating systems.

---

## Core Scripts & Utilities
### Performance & Graphics
*   **`Acpi_Bgrt.py`**  
    Handles the **Boot Graphics Resource Table (BGRT)**. Used for managing high-resolution status visuals and vendor logos displayed during the boot process.
    ```bash
    python Acpi_Bgrt.py
    ```
*   **`Acpi_Fpdt.py`**  
    Interfaces with the **Firmware Performance Data Table (FPDT)** to analyze boot performance metrics and detailed timing records.
    ```bash
    python Acpi_Fpdt.py
    ```
### System Configuration
*   **`Acpi_Mcfg.py`**  
    Manages the **PCI Express Memory Mapped Configuration Space (MCFG)** table, describing the base addresses for PCIe configuration access.
    ```bash
    python Acpi_Mcfg.py
    ```
### Analysis & Extraction Tools
*   **`AcpiAnalyze.py`**  
    A diagnostic tool used to parse, validate, and verify the integrity of existing ACPI tables on the system.
*   **`AcpiRetrieve.py`**  
    A utility designed to extract raw ACPI table data directly from system memory for offline debugging.
*   **`AcpiTableList.py`**  
    Provides a comprehensive inventory of all ACPI tables currently installed in the system configuration area.

---

## Supported Environments

EfiPy is designed to be cross-platform, supporting low-level access across:

* **UEFI Shell**: Direct firmware-level execution (requires Python EFI interpreter).
* **Windows**: System-level analysis.
* **Linux**: Integration via `/sys/firmware/acpi/tables` or memory mapping (requires Administrative privileges).

---

## Quick Start
1. Ensure a **Python 3.x** interpreter is available in your environment.
2. To list all detected ACPI tables, run:
   ```bash
   python AcpiTableList.py
   ```