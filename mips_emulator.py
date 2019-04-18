"""
MIPS Emulator
Author : github.com/auejin

how to Run : $ python3 ./mips_emulator.py [-m addr1:addr2] [-d] [-n num_instruction] <input file>
"""

import sys

class MipsEmulator : # This emulator is based on single cycle design
    def __init__(self):
        self._addr_range = (-1,-1)
        self._memory_ranged = False
        #   True  : -m 설정   함 : 메모리 주소 범위의 내용들을 +4B 단위로 출력
        # 해당주소가 text section의 주소(0x00400000에서시작)혹은 datasection의 주소(0x10000000에서시작)를 벗어난 범위를 가리키고 있을경우,해당주소에는 값이 할당되지 않았으므로 0을 출력한다.
        #   False : -m 설정 안함 : memory content 출력 안함

        self.print_for_each_instr = False
        #   True  : -d 설정  함 : 각 instr 실행 끝날때마다 모든 레지 내용 + -m시 지정 메모리 범위도  출력
        #   False : -d 설정안함 :  프로그램 종료 시점에 pc포함 레지 내용 출력 + -m시 지정 메모리 범위도 출력

        self._num_instruction = -1
        self._instruction_limited = False
        #   True  : -n 설정   함 : 수행될 명령어 갯수. for문 len
        #   False : -n 설정 안함 : 정의되지는 않았지만 모두 출력하는걸로 해야 하지 않을까

        self.pc = 0x00400000
        self.instructions = {} # {pc, bin_str}
        self.register = [0]*32 # [int] # $0~31. jal등의 instr서 사용되는 $ra = $31
        self.memory = {} # {pc, int} # 0x400000~0x7ffffffc # a word = 4B씩 dictionary
        # .text : 0x00400000번지에서 시작한다
        # .data : 0x10000000번지에서 시작한다.
        # .word : Data segment 내에서32비트데이터(word)가 위치하는 영역.

    def read_files(self, file_name):
        f = open(file_name, 'r')
        text_section_lines = int(f.readline(),0)//4
        data_section_lines = int(f.readline(),0)//4

        self.pc = 0x00400000
        for _ in range(text_section_lines):
            line = f.readline()
            bin_str = format(int(line,0), '032b')
            self.instructions[self.pc] = bin_str
            self.pc += 0x00000004

        self.pc = 0x10000000
        for _ in range(data_section_lines):
            line = f.readline()
            value = self._signed_bin(int(line,0),bin_length=32) # int(line,0)
            self.memory[self.pc] = value
            self.pc += 0x00000004
        
        f.close()

    def run_files(self,fixed_print_length=False): 
        self.pc = 0x00400000        
        try:
            i = -1
            while (self._instruction_limited and i<self._num_instruction) or (not self._instruction_limited) :
                if self.print_for_each_instr or (self._instruction_limited and i+1==self._num_instruction)  :
                    self._print_info(fixed_print_length)
                self._exec_instr_of_pc(self.pc) # break when KeyError
                i += 1
                
        except KeyError : # -n에 과다하게 온 경우, jump to exit인경우
            if not self.print_for_each_instr :
                self._print_info(fixed_print_length)

    def _print_info(self,fixed_print_length):
        self._print_register(fixed_print_length)
        if self._memory_ranged :
            print()
            self._print_memory(fixed_print_length)
            print()
        print()

    def _exec_instr_of_pc(self,pc): # jump를 위해 pc에 기반하여 instr를 실행하도록 하자.
        instr_str = self.instructions[pc]
        self.pc += 0x00000004 # 실제 pipeline처럼 이미 pc+=4를 해둠
        self.execute_instruction(instr_str)

    def _exec_instr_of_index(self,index):
        instr_pc = 0x00400000 + index*0x00000004
        self._exec_instr_of_pc(instr_pc)


    def execute_instruction(self,bin_instr):
        op = int(bin_instr[:6],2)
        # ["j", "jal"]
        j_op_hex = [2,3]
        # ["addiu", "andi", "beq", "bne", "lui", "lw", "ori", "sltiu", "sw"]
        i_op_hex = [9, 0xc, 4, 5, 0xf, 0x23, 0xd, 0xb, 0x2b]

        if op == 0 : # r-type
            # ["addu", "and", "jr", "nor", "or", "sltu", "sll", "srl", "subu"]
            r_funct_hex = [0x21, 0x24, 8, 0x27, 0x25, 0x2b, 0, 2, 0x23]
            r_funcs = [self._addu, self._and, self._jr, self._nor, self._or, self._sltu, self._sll, self._srl, self._subu]
            rs,rt,rd,shampt,funct = bin_instr[6:11],bin_instr[11:16],bin_instr[16:21],bin_instr[21:26],bin_instr[26:]
            r_funcs[r_funct_hex.index(int(funct,2))](rs,rt,rd,shampt)
            # rs,rt,rd는 3번레지스터의 '$3'에서 3을 binary로 저장한 string임

        elif op in j_op_hex : # j-type 
            if op == j_op_hex[1] : # jal
                self.register[31] = self.pc # $ra = +4된 pc; go to L
            self.pc = int(f'{self.pc:0>{32}b}'[:4] + bin_instr[6:] + "00",2)
            
        elif op in i_op_hex : # i-type
            i_funcs = [self._addiu, self._andi, self._beq, self._bne, self._lui, self._lw, self._ori, self._sltiu, self._sw]
            rs,rt,imm = bin_instr[6:11],bin_instr[11:16],bin_instr[16:]
            i_funcs[i_op_hex.index(op)](rs,rt,imm)

    # 자리수를 변화시키는거는 8자리 초과시 무조건 끝8자리만 남는다.
    #      <r-type instructions>       #
    def _addu(self,rs,rt,rd,shampt): # add unsigned (no overflow)
        self.register[int(rd,2)] = (self.register[int(rs,2)] + self.register[int(rt,2)])%0x100000000
    def _and(self,rs,rt,rd,shampt): # bitwise and
        self.register[int(rd,2)] = self.register[int(rs,2)] & self.register[int(rt,2)]
    def _jr(self,rs,rt,rd,shampt): # jump to address contained in $rs
        self.pc = self.register[int(rs,2)]
    def _nor(self,rs,rt,rd,shampt): # $rd = (not $rs) and (not $rt)
        b_str = lambda d:f'{d:0>{32}b}'
        nor_int = int(self._complement(b_str(self.register[int(rs,2)])),2) & int(self._complement(b_str(self.register[int(rt,2)])),2)
        self.register[int(rd,2)] = nor_int
    def _or(self,rs,rt,rd,shampt): # bitwise or
        self.register[int(rd,2)] = self.register[int(rs,2)] | self.register[int(rt,2)]
    def _sltu(self,rs,rt,rd,shampt): # unsigned니까 : -1(0xffffffff) > 1(0x00000001) 처리가 되야함
        self.register[int(rd,2)] = 1 if self.register[int(rs,2)] < self.register[int(rt,2)] else 0
    def _sll(self,rs,rt,rd,shampt): # shampt 음수처리 안해도됨
        self.register[int(rd,2)] = (self.register[int(rt,2)] << int(shampt,2))%0x100000000
    def _srl(self,rs,rt,rd,shampt): # shampt 음수처리 안해도됨
        self.register[int(rd,2)] = (self.register[int(rt,2)] >> int(shampt,2))%0x100000000
    def _subu(self,rs,rt,rd,shampt): # subtract unsigned (no overflow) 
        self.register[int(rd,2)] = (self.register[int(rs,2)] + self._two_s_complement_int(self.register[int(rt,2)]))%0x100000000

    def _complement(self,bin_str):
        return ''.join(map(lambda s: '0' if s=='1' else '1', bin_str))

    def _two_s_complement_int(self,dec,bin_length=32): # returns 2s-complement binary int of 'dec'
        dec *= -1
        neg = int(self._complement(f'{dec:0>{bin_length}b}'),2)
        neg += 0b1
        return neg
    
    def _signed_bin(self,dec,bin_length=32): # dec (-inf~inf) -> signed binary int (0x0~)
        if dec >= 0 :
            return dec
        else :
            return self._two_s_complement_int(-1*dec,bin_length)

    def _signed_int(self,bin_int,bin_length=32): # 2s-complementary binary int (0x0~) -> decimal int (-inf~inf)
        bin_str = f'{bin_int:0>{bin_length}b}'
        return int(bin_str[1:],2) - int(bin_str[0])*(2**(bin_length-1))

    # i format에서 쓰이는 모든 immediate 중 가용범위가 -inf~inf인 offset의 경우 _signed_int 씌우자.
    #      <i-type instructions>       #
    def _addiu(self,rs,rt,imm): # 음수도 더해야 하므로 imm in -inf~inf
        imm = imm[0]*16 + imm # sign extended
        self.register[int(rt,2)] = (self.register[int(rs,2)] + int(imm,2) )%0x100000000
        # self.register[int(rt,2)] = (self.register[int(rs,2)] + self._signed_bin(self._signed_int(int(imm,2),16),32))%0x100000000 # this is also possible
    def _andi(self,rs,rt,imm):
        self.register[int(rt,2)] = self.register[int(rs,2)] & int(imm,2)
    def _beq(self,rs,rt,offset): # offset = beq 다음 pc랑 lable의 pc의 차이 = -inf~inf
        if self.register[int(rs,2)] == self.register[int(rt,2)] :
            self.pc = self._signed_int(int(offset,2),16)*4 + self.pc
    def _bne(self,rs,rt,offset): # offset = beq 다음 pc랑 lable의 pc의 차이 = -inf~inf
        if self.register[int(rs,2)] != self.register[int(rt,2)] :
            self.pc = self._signed_int(int(offset,2),16)*4 + self.pc
    def _lui(self,rs,rt,imm): # load upper immediate
        self.register[int(rt,2)] = int(imm,2)<<16
    def _lw(self,rs,rt,offset):
        self.register[int(rt,2)] = self.memory[self.register[int(rs,2)]+self._signed_int(int(offset,2),16)]
    def _ori(self,rs,rt,imm): # bitwise or immediate
        self.register[int(rt,2)] = self.register[int(rs,2)] | int(imm,2)
    def _sltiu(self,rs,rt,imm): # unsigned니까 : -1(0xffffffff) > 1(0x00000001) 처리가 되야함
        self.register[int(rt,2)] = 1 if self.register[int(rs,2)] < int(imm,2) else 0
    def _sw(self,rs,rt,offset):
        self.memory[self.register[int(rs,2)]+self._signed_int(int(offset,2),16)] = self.register[int(rt,2)]
    
    def _print_register(self,fixed_print_length=False):
        tohex = (lambda value:'0x{:08x}'.format(value)) if fixed_print_length else hex
        print("Current register values :")
        print("-"*37)
        print(f"PC: {tohex(self.pc)}")
        print("Registers:")
        for i in range(32) :
            print(f"R{i}: {tohex(self.register[i])}")

    def _print_memory(self,fixed_print_length=False):
        tohex = (lambda value:'0x{:08x}'.format(value)) if fixed_print_length else hex
        print(f"Memory content [{tohex(self._addr_range[0])}..{tohex(self._addr_range[1])}] :")
        print("-"*37)
        mem_pc = self._addr_range[0]
        while mem_pc <= self._addr_range[1] : 
            if mem_pc in self.memory.keys() :
                value_from_pc = tohex(self.memory[mem_pc])
            elif mem_pc in self.instructions.keys() : # 0x10000000이상의 instr영역도 출력하게 했음
                value_from_pc = tohex(int(self.instructions[mem_pc],2))
            else:
                value_from_pc = tohex(0)
            print(f"{tohex(mem_pc)}: {value_from_pc}")
            mem_pc += 0x00000004

    @property
    def addr_range(self) :
        return self._addr_range
    @addr_range.setter
    def addr_range(self,value) :
        self._memory_ranged = True
        self._addr_range = value if value[0] <= value[1] else value[::-1]
        
    @property
    def num_instruction(self) :
        return self._num_instruction
    @num_instruction.setter
    def num_instruction(self,value) :
        if value >= 0 :
            self._instruction_limited = True
            self._num_instruction = value
        else :
            raise ValueError("num_instruction must not be lower than 0")
    # end of class MipsEmulator() #



if __name__ == "__main__":
    argv = sys.argv
    mips = MipsEmulator()

    if "-m" in argv :
        addr1,addr2 = argv[argv.index("-m")+1].split(":")
        mips.addr_range = int(addr1,0),int(addr2,0)

    if "-d" in argv :
        mips.print_for_each_instr = True

    if "-n" in argv :
        mips.num_instruction = int(argv[argv.index("-n")+1],0)

    mips.read_files(sys.argv[-1])
    mips.run_files()

    # test for -m
    # $ python3 ./mips_emulator.py -m 0x10000000:0x10000010 sample.o

    # test for -n & -d
    # $ python3 ./mips_emulator.py -n 0 sample.o # PC : 0x400000만 출력
    # $ python3 ./mips_emulator.py -n 0 -d sample.o # PC : 0x400000만 출력
    # $ python3 ./mips_emulator.py -n 1 sample.o # PC : 0x400004만 출력
    # $ python3 ./mips_emulator.py -n 1 -d sample.o # PC : 0x400000~0x400004
    # $ python3 ./mips_emulator.py -n 100 sample.o # 전부 실행후 마지막만 출력
    # $ python3 ./mips_emulator.py sample.o # 전부 실행후 마지막만 출력
    # $ python3 ./mips_emulator.py -n 100 -d sample.o # 전부 출력
    # $ python3 ./mips_emulator.py -d sample.o # 전부 출력
    
