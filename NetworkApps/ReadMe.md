# Introduction
Network related application by EfiPy ecosystem.

Network stack is required.

# ifconfig4.py
## EFI_IP4_CONFIG2_INTERFACE_INFO
Using ```EFI_IP4_CONFIG2_PROTOCOL::GetData``` parameter ```Ip4Config2DataTypeInterfaceInfo```
```
EFI_IP4_CONFIG2_INTERFACE_INFO::Name
EFI_IP4_CONFIG2_INTERFACE_INFO::IfType
EFI_IP4_CONFIG2_INTERFACE_INFO::HwAddressSize
EFI_IP4_CONFIG2_INTERFACE_INFO::StationAddress
EFI_IP4_CONFIG2_INTERFACE_INFO::SubnetMask
```
## DNS server
Using ```EFI_IP4_CONFIG2_PROTOCOL::GetData``` parameter ```Ip4Config2DataTypeDnsServer```

# Working Environment
* UEFI Shell
