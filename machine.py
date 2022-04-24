import sys

from wabbit.parse import parse_file
from wabbit.model import *


class Machine:
    def __init__(self):
        self.stack=[]

    def run(self, instructions):
        for instruction in instructions:
            opcode = instruction[0]
            args = instruction[1:]
            getattr(self, opcode)(*args)

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def ADD(self):
        right=self.pop()
        left=self.pop()
        self.push(left + right)

    def MUL(self):
        right=self.pop()
        left=self.pop()
        self.push(left * right)

    def SUB(self):
        right=self.pop()
        left=self.pop()
        self.push(left - right)

    def DIV(self):
        right=self.pop()
        left=self.pop()
        self.push(left / right)

    def PRINT(self):
        print(self.pop())


def generate_code(node, instructions):
    if isinstance(node, Integer):
        instructions.append(('push',int(node.value)))

    elif isinstance(node, BinOp):
        generate_code(node.left,instructions)
        generate_code(node.right,instructions)
        if node.op == '+':
            instructions.append(('ADD',))
        elif node.op == '*':
            instructions.append(('MUL',))

    elif isinstance(node, PrintStatement):
        generate_code(node.value, instructions)
        instructions.append(('PRINT',))

    elif isinstance(node, Block):
        for statement in node.statements:
            generate_code(statement, instructions)

    else:
        raise RuntimeError(f"Can't generate code for {node}")


program = parse_file(sys.argv[1])
print(program.model)

instructions = []

generate_code(program.model, instructions)
print(instructions)


machine = Machine()
machine.run(instructions)