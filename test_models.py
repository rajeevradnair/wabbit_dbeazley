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
from wabbit import interp
# ----------------------------------------------------------------------
# A simple Expression
#
# This one is given to you as an example. You might need to adapt it
# according to the names/classes you defined in wabbit.model

print("\n\n--- Simple Expression")

expr_source = "2 + 3 * 4"

expr_model  = BinOp('+', Integer('2'),
                         BinOp('*', Integer('3'), Integer('4')))

# Can you turn it back into source code?  Note: the to_source()
# function is found in wabbit/model.py.

# Uncomment:
print(to_source_pp(expr_model,DisplayContext(None)))
print('**interpretation**')
#print(interp.interpret_program(expr_model))

# ----------------------------------------------------------------------
# Program 1: Printing
#
# Encode the following program which tests printing and evaluates some
# simple expressions using Wabbit's core math operators.
#

print('\n\n--- Program 1')

source1 = """
    print 2;
    print 2 + 3;
    print -2 + 3;
    print 2 + 3 * -4;
    print (2 + 3) * -4;
    print 2.0 - 3.0 / -4.0;
"""

model1 = Block([
    PrintStatement(Integer('2')),
    PrintStatement(BinOp('+',
                         Integer('2'),
                         Integer('3'))),
    PrintStatement(BinOp('+',
                         UnaryOp('-', Integer('2')),
                         Integer('3'))),
    PrintStatement(BinOp('+',
                         Integer('2'),
                         BinOp('*',
                               Integer('3'),
                               UnaryOp('-', Integer('4'))))),
    PrintStatement(BinOp('*',
                         Grouped(BinOp('+',
                                       Integer('2'),
                                       Integer('3'))),
                         UnaryOp('-', Integer('4')))),
    PrintStatement(BinOp('/',
                         BinOp('-',
                               Float('2.0'),
                               Float('3.0')),
                         UnaryOp('-', Float('4.0'))))
    ])

print(to_source_pp(model1,DisplayContext(None)))
print('\n<< interpreter running .... >>')
#print(interp.interpret_program(model1))

# ----------------------------------------------------------------------
# Program 2: Variable and constant declarations. 
#            Expressions and assignment.
#
# Encode the following statements.

print('\n\n--- Program 2')

source2 = """
    const pi = 3.14159;
    const tau = 2.0 * pi;
    var radius = 4.0;
    var perimeter float;
    perimeter = tau * radius;
    print perimeter;    // Should produce 25.13272
"""

model2 = Block([
    ConstDeclaration('pi', None, Float('3.14159')),
    ConstDeclaration('tau', None, BinOp('*', Float('2.0'), Name('pi'))),
    VarDeclaration('radius', None, Float('4.0')),
    VarDeclaration('perimeter', Type('float'), None),
    Assignment(Name('perimeter'), BinOp('*', Name('tau'), Name('radius'))),
    PrintStatement(Name('perimeter')),
    ])

# print(to_source(model2))
print(to_source_pp(model2, DisplayContext()))
print('\n<< interpreter running .... >>')
#print(interp.interpret_program(model2))

# ----------------------------------------------------------------------
# Program 3: Relations.  You have to be able to compare values.

print('\n\n--- Program 3')

source3 = '''
    // Each statement below prints "true"
    print 1 == 1;
    print 0 < 1;         
    print 1 > 0;
    print false != true;
'''

model3 = Block([
    PrintStatement(RelOp('==', Integer('1'), Integer('1'))),
    PrintStatement(RelOp('==', Integer('0'), Integer('1'))),
    PrintStatement(RelOp('>', Integer('1'), Integer('0'))),
    PrintStatement(RelOp('!=', Boolean('false'), Boolean('true')))
    ])

# Preview (later)
# parsed_model3 = parse_source(source3)
# assert parsed_model3 == model3

# print(to_source(model3))
print(to_source_pp(model3,DisplayContext()))
print('\n<< interpreter running .... >>')
#print(interp.interpret_program(model3))


# ----------------------------------------------------------------------
# Program 4: Conditionals.  This program prints out the minimum
# value of two variables.

print('\n\n--- Program 4')

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

model4 = Block([
    VarDeclaration('a', Type('int'), Integer('2')),
    VarDeclaration('b', Type('int'), Integer('3')),
    VarDeclaration('minval', Type('int'), None),
    IfStatement(RelOp('<', Name('a'), Name('b')),
                Block([
                    #ExprStatement(Assignment(Name('minval'), Name('a'))),
                    Assignment(Name('minval'), Name('a')),
                    ]),
                Block([
                    #ExprStatement(Assignment(Name('minval'), Name('b')))
                    Assignment(Name('minval'), Name('b'))
                    ])),
    PrintStatement(Name('minval'))
    ])

# print(to_source(model4))
print(to_source_pp(model4,DisplayContext()))
print('\n<< interpreter running .... >>')
#print(interp.interpret_program(model4))

# ----------------------------------------------------------------------
# Program 5: Loops.  This program prints out the first 10 factorials.

print('\n\n--- Program 5')

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

model5 = Block([
    ConstDeclaration('n', None, Integer('10')),
    VarDeclaration('x', Type('int'), Integer('1')),
    VarDeclaration('fact', Type('int'), Integer('1')),
    WhileStatement(RelOp('<=', Name('x'), Name('n')),
                   Block([
                       # ExprStatement(Assignment(Name('fact'), BinOp('*', Name('fact'), Name('x')))),
                       Assignment(Name('fact'), BinOp('*', Name('fact'), Name('x'))),
                       # ExprStatement(Assignment(Name('x'),BinOp('+', Name('x'),Integer('1')))),
                       Assignment(Name('x'),BinOp('+', Name('x'),Integer('1'))),
                       PrintStatement(Name('fact'))
                       ])),
    ])

# print(to_source(model5))
print(to_source_pp(model5,DisplayContext()))
print('\n<< interpreter running .... >>')
#print(interp.interpret_program(model5))

# -----------------------------------------------------------------------------
# Program 6: Break/continue.  This program changes loop control flow

print('\n\n--- Program 6')

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

model6=Block([
    VarDeclaration('n', None, Integer('0')),
    WhileStatement(
        Boolean('true'),
        Block([
            IfStatement(RelOp('==', Name('n'), Integer('2')),
                        Block([
                            PrintStatement(Name('n')),
                            BreakStatement()
                        ]),
                        Block([
                            Assignment(Name('n'),BinOp('+',Name('n'),Integer('1'))),
                            ContinueStatement()
                        ])),
            Assignment(Name('n'),BinOp('-', Name('n'),Integer('1')))
        ]))
])

# print(to_source(model6))
print(to_source_pp(model6, DisplayContext()))
print('\n<< interpreter running .... >>')
#print(interp.interpret_program(model6))


# ----------------------------------------------------------------------
# model 6a to debug ExprStatement and Assignment not working well
# ----------------------------------------------------------------------

print('\n\n--- Program 6a')

source6a = '''
    var y = 42;
    var x = 37
    y = x - 1;
    print y;   // Prints 37
'''
model6a = Block([
    VarDeclaration('y', None, Integer('42')),
    VarDeclaration('x', None, Integer('37')),
    # ExprStatement(Assignment(Name('y'), Name('x'))),
    # Assignment(Name('y'), BinOp('-',Name('x'),Integer('1'))),
    ExprStatement(Assignment(Name('y'), BinOp('-',Name('x'),Integer('1')))),
    PrintStatement(Name('y'))
])
print(to_source(model6a))
print('\n<< interpreter running .... >>')
#print(interp.interpret_program(model6a))

# ----------------------------------------------------------------------
# Program 7: Compound Expressions.  This program swaps the values of
# two variables using a single expression.
#
# A compound expression is a series of statements/expressions enclosed
# in { ... }.  The value of a compound expression is the value represented
# by the last operation. 

print('\n\n--- Program 7')

source7 = '''
    var x = 37;
    var y = 42;
    x = { var t = y; y = x; t; };  // Compound expression (value is "t")
    print x;   // Prints 42
    print y;   // Prints 37
'''

model7 = Block([
    VarDeclaration('x', None, Integer('37')),
    VarDeclaration('y', None, Integer('42')),
    ExprStatement(Assignment(Name('x'),
                            Compound([
                                VarDeclaration('t', None, Name('y')),
                                ExprStatement(Assignment(Name('y'), Name('x'))),
                                ExprStatement(Name('t'))
                            ]))),
    PrintStatement(Name('x')),
    PrintStatement(Name('y'))
    ])

# print(to_source(model7))
print(to_source_pp(model7,DisplayContext()))
print('\n<< interpreter running .... >>')
#print(interp.interpret_program(model7))




# ----------------------------------------------------------------------
# Program 8: Functions.  This program tests the basics of function
# calls and returns.  For this, you're going top need to have a number
# features in your model including:
#
#     1. Function definitions.
#     2. Function application (calling a function)
#     3. The return statement.
#

print('\n\n--- Program 8')

source8 = '''
func add(x int, y int) int {
    return x + y;
}

var result = add(2, 3);
print result;
'''
'''
model8 = Block([
                FunctionDefinition(
                              Name('add'),
                              FunctionParameters([
                                  FunctionParameter('x', Type('int'), None),
                                  FunctionParameter('y', Type('int'), None)
                              ]),
                              Type('int'),
                              Block([
                                  FunctionReturn(BinOp('+',Name('x'),Name('y')))
                              ])),
                VarDeclaration('result',
                               None,
                               FunctionApplication(
                                   Name('add'),
                                   FunctionArguments([
                                       Integer('2'),
                                       Integer('3')
                                   ])
                               )),
                PrintStatement(Name('result'))
])
'''

model8 = Block([
                FunctionDefinition(
                              Name('add'),
                              FunctionParameters([
                                  FunctionParameter('x', Type('int'), None),
                                  FunctionParameter('y', Type('float'), Integer('2'))
                              ]),
                              Type('int'),
                              Block([
                                  Assignment(Name('x'),BinOp('+',Name('x'),Integer('2'))),
                                  FunctionReturn(BinOp('*',Name('x'),Name('y')))
                              ])),
                VarDeclaration('result',
                               None,
                               FunctionApplication(
                                   Name('add'),
                                   FunctionArguments([
                                       Integer('4'),
                                       Integer('3'),
                                   ])
                               )),
    PrintStatement(Name('result'))
])

# print(to_source(model8))
print(to_source_pp(model8, DisplayContext()))
print('\n<< interpreter running .... >>')
print(interp.interpret_program(model8))


print('\n\n--- Program 9')
source9 = '''
    var x float = 1.234;
    var y int = 988;
    print x + float(y);  
'''