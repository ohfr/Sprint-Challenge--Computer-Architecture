"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.branchTable = {}
        self.branchTable[0b01000111] = self.handlePrint
        self.branchTable[0b10000010] = self.handleLDI
        self.branchTable[0b10100010] = self.handleMult
        self.branchTable[0b01000101] = self.push
        self.branchTable[0b01000110] = self.pop
        self.branchTable[0b01010000] = self.handleCall
        self.branchTable[0b00010001] = self.handleRet
        self.branchTable[0b10100000] = self.add
        self.branchTable[0b10100111] = self.CMP
        self.branchTable[0b01010110] = self.JNE
        self.branchTable[0b01010101] = self.JEQ
        self.branchTable[0b1010100] = self.JMP
        self.R7 = 7
        self.FL = 0

    def add(self, pc):
        firstNum = self.ram_read(pc+1)
        secondNum = self.ram_read(pc+2)
        self.register[firstNum] = self.register[firstNum] + self.register[secondNum]
        pc+=3
        return pc

    def CMP(self, pc):
        first_loc = self.ram_read(pc+1)
        second_loc = self.ram_read(pc+2)

        first_num = self.register[first_loc]
        second_num = self.register[second_loc]

        if first_num > second_num:
            self.FL = 2
        elif first_num < second_num:
            self.FL = 4
        elif first_num == second_num:
            self.FL = 1
        pc +=3
        return pc

    def JMP(self, pc):
        numSlot = self.ram_read(pc+1)
        addr = self.register[numSlot]
        pc = addr
        return pc

    def JNE(self, pc):
        if self.FL != 1:
            return self.JMP(pc)
        else:
            pc +=2
            return pc

    def JEQ(self, pc):
        if self.FL == 1:
            return self.JMP(pc)
        else:
            pc +=2
            return pc

    def push(self, pc):
        given_register = self.ram[pc + 1]
        value_in_register = self.register[given_register]
        # decrement the Stack Pointer
        self.register[self.R7] -= 1
        # write the value of the given register to memory AT the SP location
        self.ram[self.register[self.R7]] = value_in_register
        pc +=2
        return pc

    
    def pop(self, pc):
        given_register = self.ram[pc + 1]
        # Write the value in memory at the top of stack to the given register
        value_from_memory = self.ram[self.register[self.R7]]
        self.register[given_register] = value_from_memory
        # increment the stack pointer
        self.register[self.R7] += 1
        pc+=2
        return pc


    def handlePrint(self, pc):
        location = self.ram_read(pc+1)
        print(self.register[location])
        pc+=2
        return pc

    def handleLDI(self,pc):
        num = self.ram[pc + 2]
        location = self.ram[pc + 1]
        self.register[location] = num
        pc+=3
        return pc


    def handleMult(self,pc):
        firstNum = self.ram_read(pc+1)
        secondNum = self.ram_read(pc+2)
        self.register[firstNum] = self.register[firstNum] * self.register[secondNum]
        pc+=3
        return pc

    def handleCall(self, pc):
        given_register = self.ram[pc +1]
        self.register[self.R7] -=1 
        self.ram[self.register[self.R7]] = pc + 2
        pc = self.register[given_register]
        return pc

    def handleRet(self, pc):
        pc = self.ram[self.register[self.R7]]
        self.register[self.R7] +=1
        return pc



    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        if sys.argv[1]:
            program = None
            with open(sys.argv[1],'r') as f:
                program = f.readlines()
            for instruction in program:
                if len(instruction.split()) > 0 and not instruction.startswith('#'):
                    instructionArr = instruction.strip().split('#')
                    num = int(instructionArr[0], 2)
                    self.ram_write(address, num)
                    address+=1
            return
        else:
            print("Error: No file given to load")
            return

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self,address, value):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True
        pc= 0
        while running:
            instruction = self.ram[pc]
            if instruction in self.branchTable:
                pc = self.branchTable[instruction](pc)
            elif instruction == 0b00000001:
                running = False
            else:
                print("Instruction {} not recognized".format(instruction))
                return