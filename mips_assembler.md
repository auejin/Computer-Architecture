# MIPS Assembler

Author : 201711200 함어진 ([ham@dgist.ac.kr](mailto:ham@dgist.ac.kr))

This project is based on Project 1: Simple MIPS assembler from *Introduction to Computer Architecture (SE379)*.



## Introduction

이번 과제를 통해 MIPS 어셈블리 코드를 바이너리 코드로 변환하는 MIPS ISA assembler를 구현하였다.

이 과제는 Windows Subsystem for Linux의 Ubuntu 18.04.1 LTS 환경에서 개발 및 테스트 되어졌다.



## How to Code

각 instruction은 줄바꿈으로 구분되며 모든 인자는 띄어쓰기나 탭과 같은 공란 혹은 "**,**"로 구분된다.

각 줄 별로 "**#**" 이후에 작성된 모든 내용은 무시된다.



이 assembler가 지원하는 operator는  다음과 같다.

- **J format : ** j, jal
- **I format : ** addiu, andi, beq, bne, lui, lw, ori, sltiu, sw
- **R format : **addu, and, jr, nor, or, sltu, sll, srl, subu
- **Pseudo Instructions : **la



이 assembler는 아래와 같은 MIPS register convention에서 name과 number를 모두 지원한다.

| Name | Register # | Usage | Preserved on call |
| ---- | ---- | ---- | ---- |
| \$zero | \$0 | constant value 0 | N/A |
| \$at | \$1 | reserved for assembler | N/A |
| \$v0 - \$v1 | \$2 - \$3 | returned values | F |
| \$a0 - \$a3 | \$4 - \$7 | arguments | F |
| \$t0 - \$t7 | \$8 - \$15 | temporaries | F |
| \$s0 - \$s7 | \$16 - \$23 | saved values | T |
| \$t8 - \$t9 | \$24 - \$25 | temporaries | F |
| \$gp | \$28 | global pointer | T |
| \$sp | \$29 | stack pointer | T |
| \$fp | \$30 | frame pointer | T |
| \$ra | \$31 | return address | T |




어셈블리 코드 내에서 다음과 같이 문법에 맞지 않게 잘못 기입한 경우 컴파일 없이 Error를 띄우고 종료된다.

- 어셈블리 코드가 `.data` 로 시작하지 않으면 `ValueError`
- jump나 branch시 해당 label를 찾을 수 없다면 `ValueError`
- 지원하지 않는 Operator를 사용한 경우 `NotImplementedError`
- 레지스터나 상수를 특정 operand의 잘못된 위치에 기입한 경우 `TypeError`
- instruction이 요구하는 operand의 수보다 많거나 적게 operand를 기입한 경우 `IndexError`



## How to Compile

첨부된 파일의 압축을 푼 후 배시로 해당위치에 접근한다. 그 후 *.s 확장자로 작성한 `<assembly file>`을 만들고 아래의 배시코드를 실행하면 바이너리로 컴파일한 결과값이 동일 위치에 *.o 확장자로 저장된다.

```bash
$ python3 ./mips_assembler.py <assembly file>
```



컴파일을 하면 `<assembly file>`에서 정의한 word와 instruction의 크기와 각 instruction의 정보를 아래와 같이 출력한다. 아래는 첨부된 `sample.s`를 컴파일 했을 때 bash에 출력된 내용이다.

```bash
$ python3 mips_assembler.py sample.s
self.labels = {'array': 268435456, 'array2': 268435468, 'main': 4194304}
self.memory = {268435456: 3, 268435460: 123, 268435464: 4346, 268435468: 286331153}
self.instructions = [['addiu', '$2', '$0', '1024'], ['addu', '$3', '$2', '$2'], ['or', '$4', '$3', '$2'], ['addiu', '$5', '$0', '1234'], ['sll', '$6', '$5', '16'], ['addiu', '$7', '$6', '9999'], ['subu', '$8', '$7', '$2'], ['nor', '$9', '$4', '$3'], ['ori', '$10', '$2', '255'], ['srl', '$11', '$6', '5'], ['srl', '$12', '$6', '4'], ['lui', '$4', '4096'], ['ori', '$4', '$4', '12'], ['and', '$13', '$11', '$5'], ['andi', '$14', '$4', '100'], ['subu', '$15', '$0', '$10'], ['lui', '$17', '100'], ['addiu', '$2', '$0', '0xa']]
```

