# MIPS Emulator

Author : 201711200 함어진 ([ham@dgist.ac.kr](mailto:ham@dgist.ac.kr))

This project is based on Project 2: Building a Simple MIPS Emulator from *Introduction to Computer Architecture (SE379)*.



## Introduction

이번 과제에서는 저번 과제로 구현한 MIPS Assembler를 통해 출력된 MIPS 바이너리 코드를 사용하여 MIPS ISA 가 실행되는 것을 모사하는 에뮬레이터를 구현하였다. 과제는 Windows Subsystem for Linux의 Ubuntu 18.04.1 LTS 환경에서 개발 및 테스트 되어졌다.

구조는 single cycle design을 기반으로 하였으며, loader는 stack 영역을 생성하지 않는다.



## How to Run

첨부된 파일의 압축을 푼 후 배시로 해당위치에 접근한다. 저번 과제로 구현한 MIPS Assembler에서 나온 출력물인 *.o 확장자의 `<input file>`을 아래의 배시코드에 맞추어 입력하면 바이너리 값에 따라 MIPS ISA의 실행 과정이 출력된다.

```bash
$ python3 ./mips_emulator.py [-m addr1:addr2] [-d] [-n num_instr] <input file>
```

- `-m` : 설정시 pc값, register `$0`\~`$31`값들과 함께 메모리 주소 범위(`addr1`\~`addr2`)에 있는 내용들도 출력한다. user text segment(0x00400000부터 시작) 및 data segment(0x10000000부터 시작)의 데이터를 읽어올 수 있으며, 각 주소에 할당 되지 않은 값들은 `0x0`을 출력한다. `-m` 미설정시에는 메모리 내용 없이 pc값과 register 값들만 출력된다. `addr1`와 `addr2`는 기본값이 없으므로 `-m `설정을 위해선 반드시 지정되어야 한다.
- `-d` : 설정시 각 instruction의 실행이 종료될 때 마다 register의 내용이 출력되고,  `-d` 미설정시에는 모든 instruction의 실행이 종료된 후 register가 출력이 된다. `-m` 옵션이 활성화 된 경우 register 출력시 지정된 memory 범위의 내용들도 함께 출력된다.
- `-n` : 설정시 실행가능한 최대 `num_instr`개의 instruction이 순서대로 실행이 된다. `-n` 미설정시에는 현재 pc값이 가르키는 instruction이 없을때까지 실행된다. `num_instr`는 기본값이 없으므로 `-n `설정을 위해선 반드시 음이 아닌 정수로 지정되어야 한다. `num_instr`가 0이면 instruction이 실행되지 않은 초기 설정이 출력이 되고, 0보다 작다면 `ValueError`가 raise된다.



## Output Form

아래는 과제의 예시로 주어진 'sample.o'파일을 실행하였을 때 0x10000000~0x10000010의 메모리 정보와 각 레지스터에 저장된 값들을 출력하는 예제이다.

```bash
$ python3 ./mips_emulator.py -m 0x10000000:0x10000010 sample.o
```

위의 bash 코드를 실행한 결과는 아래와 같다.

```bash
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


## Acknowledgements

[🤖 컴퓨터가 코드를 읽는 아주 구체적인 원리](https://parksb.github.io/article/25.html)를 정리해주신 박성범씨에게 감사의 인사를 드립니다.
