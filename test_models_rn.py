# test_models.py
#
# Within the bowels of your compiler, you need to represent programs
# as a data structure.  Sometimes this is known as an "Abstract Syntax
# Tree" or AST.  In this file, you will manually encode some simple
# Wabbit programs using the data model you're creating in the file
# wabbit/model.py
#
# The purpose of this is two-fold:
#
#   1. Make sure you understand the internal data structures
#      used by the compiler. You will need this to do everything else.
#
#   2. Have some program structures that you can use for later testing,
#      debugging, and experimentation.
#
# This file is broken into sections. Follow the instructions for
# each part.  Parts of this file might be referenced in later
# parts of the project.  Plan to have a lot of discussion.
#
# Also, these examples don't cover every possible language feature.
# More exhaustive testing becomes easier once you have the parser
# working.

from wabbit.model import *

# ----------------------------------------------------------------------
# A simple Expression
#
# This one is given to you as an example. You might need to adapt it
# according to the names/classes you defined in wabbit.model

print("--- Simple Expression")

expr_source = "2 + 3 * 4"

expr_model  = BinOp('+', Integer('2'),
                         BinOp('*', Integer('3'), Integer('4')))

def to_source(node):
    s = ""
    if type(node) == BinOp :
        if type(node.left) == BinOp:
            s = s+to_source(node.left)
        else:
            s = s+node.left.eval
        s = s+node.op
        if type(node.right) == BinOp:
            s = s+to_source(node.right)
        else:
            s = s+node.right.eval
    return s



# Can you turn it back into source code?  Note: the to_source()
# function is found in wabbit/model.py.

# Uncomment:
#print(to_source(expr_model))
#print(to_source01(expr_model))

# ----------------------------------------------------------------------
# Program 1: Printing
#
# Encode the following program which tests printing and evaluates some
# simple expressions using Wabbit's core math operators.
#

print('--- Program 1')

source1 = """
    print 2;
    print 2 + 3;
    print -2 + 3;
    print 2 + 3 * -4;
    print (2 + 3) * -4;
    print 2.0 - 3.0 / -4.0;
"""

expr_model  = BinOp('+', Integer('2'),
                         BinOp('*', Integer('3'), Integer('4')))
model1= [
    PrintStatement(Integer('2')),
    PrintStatement(BinOp('+', Integer('2'), Integer('3'))),
    PrintStatement(BinOp('+',Integer('-2'),Integer('3'))),
    PrintStatement((BinOp('+', Integer('2'), BinOp('*', Integer('3'), Integer('-4'))))),
    PrintStatement(BinOp('*',Group(BinOp('+',Integer('2'),Integer('3'))), Integer('-4'))),
    PrintStatement(BinOp('-',Float('2.0'), BinOp('/',Float('3.0'),Float('-4.0'))))
]

print(model1)
# ----------------------------------------------------------------------
# Program 2: Variable and constant declarations. 
#            Expressions and assignment.
#
# Encode the following statements.

print('--- Program 2')

source2 = """
    const pi = 3.14159;
    const tau = 2.0 * pi;
    var radius = 4.0;
    var perimeter float;
    perimeter = tau * radius;
    print perimeter;    // Should produce 25.13272
"""

#print(source2)

model2 = [
    ConstantDeclaration(Name('pi'),Float('3.14159')),
    ConstantDeclaration(Name('tau'),BinOp('*',Float('2.0'),Name('pi'))),
    VariableDeclaration(Name('radius'),Literal('4.0',None)),
    VariableDeclaration(Name('perimeter'), Literal(None,Type('float'))),
    AssignmentOp('=', Variable('perimeter'), BinOp('*',Name('tau'),Name('radius'))),
    PrintStatement(Variable('perimeter'))
]

print(model2)

# ----------------------------------------------------------------------
# Program 3: Relations.  You have to be able to compare values.

print('--- Program 3')

source3 = '''
    // Each statement below prints "true"
    print 1 == 1;
    print 0 < 1;         
    print 1 > 0;
'''

model3=[
    PrintStatement(RelOp('==',Integer('1'),Integer('1'))),
    PrintStatement(RelOp('<',Integer('0'),Integer('1'))),
    PrintStatement(RelOp('>', Integer('1'), Integer('0')))
]

print(model3)


# print(to_source(model3))

# ----------------------------------------------------------------------
# Program 4: Conditionals.  This program prints out the minimum
# value of two variables.

print('--- Program 4')

source4 = '''
    var a int = 2;
    var b int = 3;
    var minval int;
    if a < b {
        minval = a;
    } else {
        minval = b;
    }
    print minval;   // Should print 2
'''

model4 = [
    VariableDeclaration(Name('a'), Literal('2',Type('int'))), #VariableDeclaration('radius',Literal('4.0',None)),
    VariableDeclaration(Name('b'), Literal('3',Type('int'))),
    VariableDeclaration(Name('minval'), Literal(None,Type('int'))),
    IfThenElseBlock(
        RelOp('<',Name('a'),Name('b')),
        ThenBlock(Block([AssignmentOp('=',Name('minval'),Name('a'))])),
        None,
        ElseBlock(Block([AssignmentOp('=',Name('minval'),Name('b'))]))
    ),
    PrintStatement(Variable('minval'))
]
print(model4)
# print(to_source(model4))


# ----------------------------------------------------------------------
# Program 5: Loops.  This program prints out the first 10 factorials.

print('--- Program 5')

source5 = '''
    const n = 10;
    var x int = 1;
    var fact int = 1;

    while x < n {
        fact = fact * x;
        x = x + 1;
        print fact;
    }
'''

model5 = [
    ConstantDeclaration(Name('n'),Integer('10')),
    VariableDeclaration(Name('x'),Literal('1',Type('int'))),
    VariableDeclaration(Name('fact'),Literal('1',Type('int'))),
    WhileBlock(
        RelOp('<',Name('x'),Name('n')),
        Block([
            AssignmentOp('=',Name('fact'),BinOp('*',Name('fact'),Name('x'))),
            AssignmentOp('=',Name('x'),BinOp('+',Name('x'),Integer('1'))),
            PrintStatement(Variable('fact'))
        ])
    )
]

print(model5)

# print(to_source(model5))

# -----------------------------------------------------------------------------
# Program 6: Break/continue.  This program changes loop control flow

print('--- Program 6')

source6 = '''
    var n = 0;
    while true {
        if n == 2 {
            print n;
            break;
        } else {
            n = n + 1;
            continue;
        }
        n = n - 1;   // Should never execute
    }
'''
model6 = [
    VariableDeclaration(Name('n'),Literal('0',None)),
    WhileBlock(
        TrueCondition(),
        Block([
           IfThenElseBlock(
                RelOp('==',Name('n'),Integer('2')),
                ThenBlock(Block([
                    PrintStatement(Name('n')),
                    BreakStatement()
                ])),
                else_block=ElseBlock(Block([
                    AssignmentOp('=',Name('n'),BinOp('+',Name('n'),Integer('1'))),
                    ContinueStatement()
                ]))
           ),
           AssignmentOp('=',Name('n'),BinOp('-',Name('n'),Integer('1')))
        ]),
    )
]
print(model6)
# print(to_source(model6))

# ----------------------------------------------------------------------
# Program 7: Compound Expressions.  This program swaps the values of
# two variables using a single expression.
#
# A compound expression is a series of statements/expressions enclosed
# in { ... }.  The value of a compound expression is the value represented
# by the last operation. 

print('--- Program 7')

source7 = '''
    var x = 37;
    var y = 42;
    x = { var t = y; y = x; t; };  // Compound expression (value is "t")
    print x;   // Prints 42
    print y;   // Prints 37
'''

model7 = [
    VariableDeclaration(Name('x'), Literal('37', None)),
    VariableDeclaration(Name('y'), Literal('42', None)),
    AssignmentOp('=',Name('x'),
                 ExprStatement(Block([
                    VariableDeclaration(Name('t'),Literal(None,None)),
                    AssignmentOp('=',Name('t'),Name('y')),
                    AssignmentOp('=',Name('y'),Name('x')),
                    ReturnVal(Name('t'))
                 ]))
    ),
    PrintStatement(Name('x')),
    PrintStatement(Name('y')),
]

print(model7)
# print(to_source(model7))

# ----------------------------------------------------------------------
# Program 8: Functions.  This program tests the basics of function
# calls and returns.  For this, you're going top need to have a number
# features in your model including:
#
#     1. Function definitions.
#     2. Function application (calling a function)
#     3. The return statement.
#

print('--- Program 8')

source8 = '''
func add(x int, y int) int {
    return x + y;
}

var result = add(2, 3);
print result;
'''

model8 = [
    FnDeclaration(
        Name('add'),
        FnParameters([
            FnParameter(VariableDeclaration(Name('x'),Literal(None,Type('int')))),
            FnParameter(VariableDeclaration(Name('y'),Literal(None,Type('int')))),
        ]),
        FnReturnType(Type('int')),
        Block([
            FnReturnStatement(BinOp('+',Name('x'),Name('y')))
        ])
    ),
    #VariableDeclaration(
    #    Name('result'),
    #    FnCall(
    #       Name('add'),
    #        FnArguments([
    #            FnArgument(Integer('2')),
    #            FnArgument(Integer('3'))
    #        ])
    #    )
    #),
    PrintStatement(Variable('result'))
]
print(model8)
# print(to_source(model8))
