# metal.py
# 
# One of the main roles of a compiler is taking high-level programs
# such as what you might write in C or Python and reducing them to
# instructions that can execute on actual hardware.
#
# This file implements a very tiny CPU in the form of a Python
# program.  Although simulated, this CPU mimics the behavior of a real
# CPU.  There are registers for performing simple mathematical
# calculations, memory operations for loading/storing values, control
# flow instructions for branching and gotos, and an I/O port for
# performing output.  It's missing a lot of the instructions found
# on an actual CPU--our purpose is only to get a general idea of
# low-level coding.
#
# See the end of this file for some exercises.
#
# The CPU has 8 registers (R0, R1, ..., R7) that hold 32-bit unsigned
# integer values.  Register R0 is hardwired to always contains the
# value 0. Register R7 is initialized to the highest valid memory
# address. A special register PC holds the index of the next
# instruction that will execute.
#
# The memory of the machine consists of 65536 memory slots, each of
# which can hold an integer value.  Special LOAD/STORE instructions
# access the memory.  Instructions are stored separately.  All memory
# addresses from 0-65535 may be used.
#
# The machine has a single I/O port. Writing to memory address 65535
# (0xFFFF) prints a 32-bit integer value.  The symbolic constant
# IO_OUT contains the value 65535.  
#
# The machine understands the following instructions--which are
# encoded as tuples:
#
#   ('ADD', 'Ra', 'Rb', 'Rd')       ; Rd = Ra + Rb
#   ('SUB', 'Ra', 'Rb', 'Rd')       ; Rd = Ra - Rb
#   ('MUL', 'Ra', 'Rb', 'Rd')       ; Rd = Ra * Rb
#   ('INC', 'Ra')                   ; Ra = Ra + 1
#   ('DEC', 'Ra')                   ; Ra = Ra - 1
#   ('CMP', 'op', 'Ra', 'Rb', 'Rd') ; Rd = (Ra op Rb) (compare)
#   ('CONST', value, 'Rd')          ; Rd = value
#   ('LOAD', 'Rs', 'Rd', offset)    ; Rd = MEMORY[Rs + offset]
#   ('STORE', 'Rs', 'Rd', offset)   ; MEMORY[Rd + offset] = Rs
#   ('JMP', 'Rd', offset)           ; PC = Rd + offset
#   ('BZ', 'Rt', offset)            ; if Rt == 0: PC = PC + offset
#   ('HALT,)                        ; Halts machine
#
# In the the above instructions 'Rx' means some register number such
# as 'R0', 'R1', etc.  The 'PC' register may also be used as a
# register.  All memory instructions take their address from register
# plus an integer offset that's encoded as part of the instruction.

IO_OUT = 65535
MASK = 0xffffffff

class Metal:
    def run(self, instructions):
        '''
        Run a program. memory is a Python list containing the program
        instructions and other data.  Upon startup, all registers
        are initialized to 0.  R7 is initialized with the highest valid
        memory index (len(memory) - 2).
        '''
        self.registers = { f'R{d}':0 for d in range(8) }
        self.registers['PC'] = 0
        self.instructions = instructions
        self.memory = [0] * 65536
        self.registers['R7'] = len(self.memory) - 2
        self.running = True
        while self.running:
            op, *args = self.instructions[self.registers['PC']]
            # Uncomment to debug what's happening
            # print(self.registers['PC'], op, args)
            self.registers['PC'] += 1
            getattr(self, op)(*args)
            self.registers['R0'] = 0    # R0 is always 0 (even if you change it)
        return

    def ADD(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] + self.registers[rb]) & MASK

    def SUB(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] - self.registers[rb]) & MASK

    def MUL(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] * self.registers[rb]) & MASK        
        
    def INC(self, ra):
        self.registers[ra] = (self.registers[ra] + 1) & MASK

    def DEC(self, ra):
        self.registers[ra] = (self.registers[ra] - 1) & MASK

    def CMP(self, op, ra, rb, rd):
        if op == '==':
            self.registers[rd] = int(self.registers[ra] == self.registers[rb])
        elif op == '!=':
            self.registers[rd] = int(self.registers[ra] != self.registers[rb])
        elif op == '<':
            self.registers[rd] = int(self.registers[ra] < self.registers[rb])
        elif op == '>':
            self.registers[rd] = int(self.registers[ra] > self.registers[rb])
        elif op == '<=':
            self.registers[rd] = int(self.registers[ra] <= self.registers[rb])
        elif op == '>=':
            self.registers[rd] = int(self.registers[ra] >= self.registers[rb])
        else:
            raise RuntimeError(f'Bad comparison {op}. Must be ==, !=, <, >, <=, >=')
            
    def CONST(self, value, rd):
        self.registers[rd] = value & MASK

    def LOAD(self, rs, rd, offset):
        self.registers[rd] = (self.memory[self.registers[rs]+offset]) & MASK

    def STORE(self, rs, rd, offset):
        addr = self.registers[rd]+offset
        self.memory[self.registers[rd]+offset] = self.registers[rs]
        if addr == IO_OUT:
            print(self.registers[rs])

    def JMP(self, rd, offset):
        self.registers['PC'] = self.registers[rd] + offset

    def BZ(self, rt, offset):
        if not self.registers[rt]:
            self.registers['PC'] += offset

    def HALT(self):
        self.running = False

# =============================================================================

if __name__ == '__main__':        
    machine = Metal()

    # ----------------------------------------------------------------------
    # Program 1:  Computers
    #
    # The CPU of a computer executes low-level instructions.  Using the
    # Metal instruction set above, show how you would compute 3 + 4 - 5
    # and print out the result.
    # 

    prog1 = [ # Instructions here
              ('CONST', 3, 'R1'),
              ('CONST', 4, 'R2'),
              ('ADD','R1','R2','R1'),
              ('CONST', 5, 'R2'),
              ('SUB','R1','R2','R1'),
              # More instructions here
              # ...
              # Print the result.  Change R1 to location of result.
              ('STORE', 'R1', 'R0', IO_OUT),    
              ('HALT',),
              ]

    print("PROGRAM 1::: Expected Output: 2")
    machine.run(prog1)
    print(":::PROGRAM 1 DONE")

    # ----------------------------------------------------------------------
    # Problem 2: Computation
    #
    # Write a Metal program that computes 5 factorial (5 * 4 * 3 * 2 * 1).

    prog2 = [ # Instructions here
              ('CONST', 1, 'R2'),
              ('CONST', 5, 'R1'),      # The initial input
              ('MUL', 'R2','R1','R2'),
              ('DEC','R1'),
              ('BZ','R1',1),
              ('BZ','R0',-4),           #R0 is always zero
              # ...
              # Print result. Change R1 to location of result
              ('STORE', 'R2', 'R0', IO_OUT),
              ('HALT',),
            ]

    print("PROGRAM 2::: Expected Output: 120")
    machine.run(prog2)
    print(':::PROGRAM 2 DONE')

    # ----------------------------------------------------------------------
    # Problem 3: Abstraction and functions
    #
    # A major part of programming concerns abstraction. One of the most
    # common tools of abstraction is the concept of a function/procedure.
    # For example, consider this high-level Python code:
    #
    #    def fact(n):
    #        result = 1
    #        while n > 0:
    #            result *= n
    #            n -= 1
    #        return result
    #
    # How would you encode something like this into machine code?
    # Specifically.  How would you define the function fact(). How
    # would it receive inputs?  How would it return a value?  How
    # would the branching/jump statements work?   How would you use
    # it to print out the first 10 factorials?
    #
    # Note: This problem is HARD.  The hardware itself is limited
    # to the registers provided. You need to figure out how to
    # use the registers to carry out the calculation, perform the
    # function call, and get back to the original call site. You
    # might have to store data in memory and manipulate the PC
    # register.

    prog3 = [
        # n = 1
        #('CONST', 1, 'R1'),       # n = 1
                
        # while n <= 10:
        #     result = fact(n)
        #     print(result)
        #     n += 1
        #
        # ... instructions here
        #
        #
        #   ('ADD', 'Ra', 'Rb', 'Rd')       ; Rd = Ra + Rb
        #   ('SUB', 'Ra', 'Rb', 'Rd')       ; Rd = Ra - Rb
        #   ('MUL', 'Ra', 'Rb', 'Rd')       ; Rd = Ra * Rb
        #   ('INC', 'Ra')                   ; Ra = Ra + 1
        #   ('DEC', 'Ra')                   ; Ra = Ra - 1
        #   ('CMP', 'op', 'Ra', 'Rb', 'Rd') ; Rd = (Ra op Rb) (compare)
        #   ('CONST', value, 'Rd')          ; Rd = value
        #   ('LOAD', 'Rs', 'Rd', offset)    ; Rd = MEMORY[Rs + offset]
        #   ('STORE', 'Rs', 'Rd', offset)   ; MEMORY[Rd + offset] = Rs
        #   ('JMP', 'Rd', offset)           ; PC = Rd + offset
        #   ('BZ', 'Rt', offset)            ; if Rt == 0: PC = PC + offset
        #   ('HALT,)                        ; Halts machine
        #

        # Counter
        ('CONST', 10, 'R1'),
        ('STORE', 'R1', 'R0', IO_OUT),
        ('JMP', 'R0', 4),
        ('DEC','R1'),
        ('BZ', 'R1', 1),
        ('BZ', 'R0', -5),
        ('HALT',),
        # Factorial of a number
        ('STORE', 'R1', 'R0', 4),
        ('LOAD', 'R0', 4, 'R4'),
        ('CONST', 1, 'R5'),
        ('MUL', 'R4', 'R5', 'R5'),
        ('DEC', 'R4'),
        ('BZ', 'R4', 1),
        ('BZ', 'R0', -4),
        ('STORE', 'R5', 'R0', IO_OUT),
        ('JMP','R0',-14)

        # ----------------------------------
        # ; fact(n) -> n!
        # 
        #    def fact(n):
        #        result = 1
        #        while n > 1:
        #            result *= n
        #            n -= 1
        #        return result
        #
        # ... instructions here
    ]

    print("PROGRAM 3::: Should see first 10 factorials")
    machine.run(prog3)
    print(":::PROGRAM 3 DONE")
    
