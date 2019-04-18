# Computer Architecture
This repo contains 4 projects made for *Introduction to Computer Architecture (SE379), DGIST*.

Every project is developed and tested on Ubuntu 18.04.1 LTS of Windows Subsystem for Linux.

Please check out `*.md` file of each project to see how to use.



All projects are listed as follows :

* [MIPS Assembler](#MIPS-Assembler)
* [MIPS Emulator](#MIPS-Emulator)




## MIPS Assembler

**[Full README](https://github.com/auejin/Computer-Architecture/blob/master/mips_assembler.md)**

**[mips_assembler.py](https://github.com/auejin/Computer-Architecture/blob/master/mips_assembler.py)**

This project is MIPS ISA assembler which compiles MIPS assembly code into binary or hexadecimal code.

Bash code written below prints out data and instructions written on assembly code `sample.s` and saves compiled hexadecimal code `sample.o` on the exact location.

```bash
$ python3 mips_assembler.py sample.s
self.labels = {'array': 268435456, 'array2': 268435468, 'main': 4194304}
self.memory = {268435456: 3, 268435460: 123, 268435464: 4346, 268435468: 286331153}
self.instructions = [['addiu', '$2', '$0', '1024'], ['addu', '$3', '$2', '$2'], ['or', '$4', '$3', '$2'], ['addiu', '$5', '$0', '1234'], ['sll', '$6', '$5', '16'], ['addiu', '$7', '$6', '9999'], ['subu', '$8', '$7', '$2'], ['nor', '$9', '$4', '$3'], ['ori', '$10', '$2', '255'], ['srl', '$11', '$6', '5'], ['srl', '$12', '$6', '4'], ['lui', '$4', '4096'], ['ori', '$4', '$4', '12'], ['and', '$13', '$11', '$5'], ['andi', '$14', '$4', '100'], ['subu', '$15', '$0', '$10'], ['lui', '$17', '100'], ['addiu', '$2', '$0', '0xa']]
```



## MIPS Emulator

**[Full README](https://github.com/auejin/Computer-Architecture/blob/master/mips_emulator.md)**

**[mips_emulator.py](https://github.com/auejin/Computer-Architecture/blob/master/mips_emulator.py)**

This project is an MIPS emulator simulating the execution of MIPS ISA using the MIPS binary code made from MIPS Assembler (upper project). The structure is based on single cycle design, and loader does not create stack area.

Bash code written below prints out the executed result (register values and memory content) of `sample.o` of MIPS ISA. The result can be printed out whenever each instruction is executed with custom options.

```bash
$ python3 mips_emulator.py -m 0x10000000:0x10000010 sample.o
Current register values :
-------------------------------------
PC: 0x400048
Registers:
R0: 0x0
R1: 0x0
R2: 0xa
R3: 0x800
R4: 0x1000000c
R5: 0x4d2
R6: 0x4d20000
R7: 0x4d2270f
R8: 0x4d2230f
R9: 0xfffff3ff
R10: 0x4ff
R11: 0x269000
R12: 0x4d2000
R13: 0x0
R14: 0x4
R15: 0xfffffb01
R16: 0x0
R17: 0x640000
R18: 0x0
R19: 0x0
R20: 0x0
R21: 0x0
R22: 0x0
R23: 0x0
R24: 0x0
R25: 0x0
R26: 0x0
R27: 0x0
R28: 0x0
R29: 0x0
R30: 0x0
R31: 0x0

Memory content [0x10000000..0x10000010] :
-------------------------------------
0x10000000: 0x3
0x10000004: 0x7b
0x10000008: 0x10fa
0x1000000c: 0x11111111
0x10000010: 0x0


```

