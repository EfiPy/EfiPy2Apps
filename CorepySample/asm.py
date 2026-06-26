#
# asm.py
#
# Copyright (C) 2016 - 2026 efipy.core@gmail.com All rights reserved.
#
# asm.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# PaTest.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EfiPy.  If not, see <http://www.gnu.org/licenses/>.
#

import corepy.arch.x86_64.isa as x86
from corepy.arch.x86_64.types.registers import *
import corepy.arch.x86_64.platform as env

prgm = env.Program()
code = prgm.get_stream()
proc = env.Processor()

code.add(x86.mov(dx, 0x80))
code.add(x86.mov(al, 0xaa))
code.add(x86.out(dx, al))

prgm.add(code)
prgm.print_code(pro = True, epi = True, hex = True)

CodeAddr, CodeBytes = prgm.get_code_bytes ()
print (f'Dump binary code from address 0x{CodeAddr:08X}...')
from EfiPy2.Lib.HexDump import HexDump
HexDump (bytes (CodeBytes[:]), HexOffset = CodeAddr, DumpLead = 1)

ret = proc.execute(prgm, mode = 'int')
print (f'0x{ret:08X}')
