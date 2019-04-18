"""
MIPS Assembler
Author : github.com/auejin

how to Run : $ python3 ./mips_assembler.py <assembly file>
"""

import sys

class MipsAssembler :
    def __init__(self):
        self.pc = 0
        self.instructions = []
        self.labels = {}
        self.memory = {} # 0x400000~0x7ffffffc # a word = 4B씩 dictionary
        # .text : 0x00400000번지에서 시작한다
        # .data : 0x10000000번지에서 시작한다.
        # .word : Data segment 내에서32비트데이터(word)가 위치하는 영역.

        self.instr_r_format = ["addu", "and", "jr", "nor", "or", "sltu", "sll", "srl", "subu"]
        self.instr_i_format = ["addiu", "andi", "beq", "bne", "lui", "lw", "ori", "sltiu", "sw"]
        self.instr_j_format = ["j", "jal"]

        # .뒤에 있는거는 directives
        # :포함된거는 label
        self.diretives = [".data", ".word", ".text"]

        self.text_section_lines = 0
        self.data_section_lines = 0

    def read_files(self, file_name):
        f = open(file_name, 'r')
        is_data = False
        text_section_count = False

        self.pc = 0x10000000 # memory 상의 주소를 나타낼 때 사용
        current_label = ""

        while True:
            line = f.readline()
            if not line: break

            line = line.replace(',',' ')
            line = line.split('#')[0] # supporting code command
            args = line.split()
            if len(args) < 1 :
                continue
            if args[0] == self.diretives[0] :
                is_data = True
                continue
            else :
                if not is_data :
                    raise ValueError("*.s file should start with '.data'.")

            if args[0][-1] == ':' : # line includes label
                current_label = args[0][:-1]
                self.labels[current_label] = self.pc
                args = args[1:] # remove label since we already saved

            if len(args) > 0 and args[0] == self.diretives[1] : # add .word to data memory
                self.data_section_lines += 1
                self.memory[self.pc] = int(args[1],0)
                self.pc += 0x00000004

            if text_section_count : # add .text to instruction memory
                if len(args) > 1 :
                    if args[0] == "la" : # pseudo instruction # la $4, array2
                        total_address = hex(self.labels[args[2]])[2:]
                        upper_16bit = total_address[:4]
                        lower_16bit = total_address[4:]
                        if int(upper_16bit,16) > 0 : # lui $17, 100
                            self.text_section_lines += 1
                            self.instructions.append([ "lui", args[1], str(int('0x'+upper_16bit,0)) ])
                            self.pc += 0x00000004
                        if int(lower_16bit,16) > 0 : # ori rt, imm
                            self.text_section_lines += 1
                            self.instructions.append([ "ori", args[1], args[1], str(int('0x'+lower_16bit,0)) ])
                            self.pc += 0x00000004

                    else :
                        self.text_section_lines += 1
                        self.instructions.append(args)
                        self.pc += 0x00000004 # instr.도 word : 32bit = 4B

            elif args[0] == self.diretives[2] : # initial .text apperance
                self.pc = 0x00400000
                text_section_count = True
            # print(args)
        f.close()

        print(f"self.labels = {self.labels}")
        print(f"self.memory = {self.memory}")
        print(f"self.instructions = {self.instructions}")

    def save_files(self, file_name, binary = False):
        f = open(file_name.split('.')[0]+".o", 'w')

        #   <text section size>    #
        f.write(hex(self.text_section_lines*4)+'\n') # 4B per word

        #   <data section size>    #
        f.write(hex(self.data_section_lines*4)+'\n') # 4B per instr.

        #      <instruction>       #
        self.pc = 0x00400000
        for instr in self.instructions :
            if binary :
                f.write(str(self.args_to_binary(instr))+'\n') # binary output
                self.pc += 0x00000004
            else :
                binary_str = self.args_to_binary(instr)
                # print(f"{binary_str}")
                hex_str = hex(int(binary_str, 2))
                f.write(hex_str+'\n') # hexadecimal output
                self.pc += 0x00000004

        #         <value>          #
        for value in self.memory.values() :
            f.write(f"{hex(value)}\n") # 32bit int

        f.close()


    def args_to_binary(self, args) :
        if args[0] in self.instr_j_format :     # op jump_target
            # ["j", "jal"]
            self.filter_reg_operand_error(args, [0,0])
            self.filter_label_notfound_error(args[1])
            op_hex = [2,3]
            op = self.dec_to_bin_str( op_hex[self.instr_j_format.index(args[0])] , 6)
            # jump addressing ( real_address = PC[31..28] + jump_target + '00' )
            jump_target = self.dec_to_bin_str( self.labels[args[1]] , 32)[4:-2]
            return op + jump_target

        elif args[0] in self.instr_i_format :   # op rs rt immediate
            # ["addiu", "andi", "beq", "bne", "lui", "lw", "ori", "sltiu", "sw"]
            op_hex = [9, 0xc, 4, 5, 0xf, 0x23, 0xd, 0xb, 0x2b]
            op = self.dec_to_bin_str( op_hex[self.instr_i_format.index(args[0])] , 6)

            if args[0] == "beq" or args[0] == "bne" : # beq rs, rt, label
                self.filter_reg_operand_error(args, [0,1,1,0])
                self.filter_label_notfound_error(args[3])
                rs = self.dec_to_bin_str( int(args[1][1:]) , 5)
                rt = self.dec_to_bin_str( int(args[2][1:]) , 5)
                # branch addressing ( real_address = add(PC+4,offset) )
                real_address = int('0b'+self.dec_to_bin_str( self.labels[args[3]] , 32),0)
                offset = self.dec_to_bin_str( real_address - self.pc - 4, 18)[:-2]
                return op + rs + rt + offset

            elif args[0] == "lui" : # lui rt, imm
                self.filter_reg_operand_error(args, [0,1,0])
                rs = self.dec_to_bin_str( 0 , 5)
                rt = self.dec_to_bin_str( int(args[1][1:]) , 5)
                immediate = self.dec_to_bin_str( int(args[2],0) , 16)
                return op + rs + rt + immediate

            elif args[0] == "lw" or args[0] == "sw" :
                rt = self.dec_to_bin_str( int(args[1][1:]) , 5)
                if '(' in args[2] : # lw rt, offset(rs) # lw $9, 0($8)
                    offset_str = args[2].split('(')[0]
                    rs_str = args[2].split('(')[1][:-1]
                    # print(f"offset = {offset_str}, rs_str = {rs_str}")
                    self.filter_reg_operand_error(args[:-1] + [offset_str, rs_str] , [0,1,0,1])
                    rs = self.dec_to_bin_str( int( rs_str[1:] ) , 5)
                    offset = self.dec_to_bin_str( int( offset_str , 0 ) , 16)
                else :              # lw rt, rs         # lw $9, $8
                    self.filter_reg_operand_error(args, [0,1,1])
                    rs = self.dec_to_bin_str( int(args[2][1:]) , 5)
                    offset = self.dec_to_bin_str( 0 , 16)
                return op + rs + rt + offset

            else :
                self.filter_reg_operand_error(args, [0,1,1,0])
                rs = self.dec_to_bin_str( int(args[2][1:]) , 5)
                rt = self.dec_to_bin_str( int(args[1][1:]) , 5)
                immediate = self.dec_to_bin_str( int(args[3],0) , 16)
                return op + rs + rt + immediate

        elif args[0] in self.instr_r_format :   # op rs rt ds shampt funct
            # ["addu", "and", "jr", "nor", "or", "sltu", "sll", "srl", "subu"]
            op = self.dec_to_bin_str( 0 , 6)
            funct_hex = [0x21, 0x24, 8, 0x27, 0x25, 0x2b, 0, 2, 0x23]
            funct = self.dec_to_bin_str( funct_hex[self.instr_r_format.index(args[0])] , 6)

            if args[0] == "jr" : # jr rs
                self.filter_reg_operand_error(args, [0,1])
                rs = self.dec_to_bin_str( int(args[1][1:]) , 5)
                blank = self.dec_to_bin_str( 0 , 15)
                return op + rs + blank + funct

            elif args[0] == "sll" or args[0] == "srl" : # sll rd rt shampt
                self.filter_reg_operand_error(args, [0,1,1,0])
                rs = self.dec_to_bin_str( 0 , 5)
                rt = self.dec_to_bin_str( int(args[2][1:]) , 5)
                rd = self.dec_to_bin_str( int(args[1][1:]) , 5)
                shampt = self.dec_to_bin_str( int(args[3],0) , 5)
                return op + rs + rt + rd + shampt + funct

            else : # or rd, rs rt
                self.filter_reg_operand_error(args, [0,1,1,1])
                rs = self.dec_to_bin_str( int(args[2][1:]) , 5)
                rt = self.dec_to_bin_str( int(args[3][1:]) , 5)
                rd = self.dec_to_bin_str( int(args[1][1:]) , 5)
                shampt = self.dec_to_bin_str( 0 , 5)
                return op + rs + rt + rd + shampt + funct
        else:
            raise NotImplementedError(f"operator '{args[0]}' is not currently supported.")

    def dec_to_bin_str(self, dec, len) : # converts dec into bin with <len>digits
        if dec < 0 :
            dec *= -1
            neg = int(''.join(map(lambda s: '0' if s=='1' else '1', f'{dec:0>{len}b}')),2)
            neg += 0b1
            return bin(neg)[2:]
        else :
            return f'{dec:0>{len}b}'

    def filter_label_notfound_error(self, arg):
            if arg not in self.labels :
                raise ValueError(f"label {arg} not found.")

    def letters(self, string):
        return ''.join(filter(str.isalpha, string))

    def reg_name_to_num(self, reg_name):
        l = self.letters(reg_name)
        for j, name in enumerate(['zero', 'at', 'v', 'a', 't', 's', 'gp', 'sp', 'fp', 'ra']) :
            if name == l :
                if l == 'v':
                    return int(reg_name[1:])+2
                if l == 'a':
                    return int(reg_name[1:])+4
                if l == 't' :
                    offset = 8 if int(reg_name[1:]) < 8 else 16
                    return int(reg_name[1:]) + offset
                if l == 's' :
                    return int(reg_name[1:])+16
                else :
                    return [0,1,-1,-1,-1,-1,28,29,30,31][j]

    def filter_reg_operand_error(self, args, is_reg) : # this does not remove $ from args
        if len(args) != len(is_reg) :
            raise IndexError(f"{args[0]} should have {len(is_reg)} arguments, not {len(args)}.")
        for i, arg in enumerate(args) :
            if is_reg[i] :
                if arg[0] == '$' :
                    if len(self.letters(arg[1:])) > 0 :
                        args[i] = '$' + str(self.reg_name_to_num(arg[1:])) # changes reg name to reg num
                    pass # arg is register
                else :
                    raise TypeError(f"{i}th args of {args[0]} should be register address.")
            else :
                if arg[0] == '$' :
                    raise TypeError(f"{i}th args of {args[0]} should not be register address.")
                else :
                    pass # arg is value or label

if __name__ == "__main__":
    mips = MipsAssembler()
    mips.read_files(sys.argv[1])
    mips.save_files(sys.argv[1], binary = False); # binary=False : returns hex
