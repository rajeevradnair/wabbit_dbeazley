# parse.py
#
# Wabbit parser.  The parser needs to construct the data model or an
# abstract syntax tree from text input.  The precise format of Wabbit
# source code is described by a grammar.  The grammar for Wabbit can
# be found in the document docs/Wabbit-Specification.md.
#
# For our purposes, however, it may be easier to work from syntax
# diagrams which can be found in the document docs/WabbitSyntax.pdf.
#
# Our plan for writing the parser is going to proceed in two phases.
#
# Phase 1:  Statements
# --------------------
# In phase 1, we will write all of the parsing code for statements.
# However, we'll restrict expression parsing to only work with a
# single integer value.  Here are examples of statements we'll
# parse in this phase:
#
#      break;
#      continue;
#      print 1;
#      const x = 1;
#      var x int;
#      if 1 { print 2; } else { print 3; }
#      while 1 { print 2; }
#      1;             
#
# Again, expressions will restricted to a single integer value in this
# first part.
#
# Phase 2: Expressions
# --------------------
# One you have everything in phase 1 working, we'll work on expression
# parsing.  Expression parsing is probably the most difficult part of
# writing the parser because expressions need to capture precedence
# rules from math class.  For example, how is the following expression
# parsed?
#
#           2 + 3 * 4 < 30 / 6 - 7
#
# There are essentially different parsing "levels".  For example, to
# evaluate this expression, multiplication and division go first:
#
#            2 + (3 * 4) < (30 / 6) - 7
#            2 + 12 < 5 - 7
#
# Addition and subtraction then go next:
#
#            (2 + 12) < (5 - 7)
#              14     <   -2
#
# The relation goes last, producing false in this example.
# To make this work, each level of precedence is going to get its
# own parsing rule.
#
# It should be noted that assignment is also an expression.
#
#            x = 2 + 3;
#
# The value of an assignment is the right hand side.  So, statements
# such as this are legal:
#
#            print x = 2 + 3;     // Prints 5, assigns to x.
#
# Assignments can also be chained:
#
#            x = y = 2 + 3;
#
# This is to be interpreted as meaning the following:
#
#            x = (y = 2 + 3);
#
# A plan for testing
# ------------------
# At first, it's going to be difficult to make substantial
# progress.  You'll need to focus on isolated simple statements
# and work your way up to more complicated things as you
# expand to more Wabbit features.
#
# The directory tests/Parser contains a series of parsing tests
# arranged in order of difficulty.  Each test file also contains
# some implementation notes to help guide you.  Thus, start here
# and work your way up to more complicated tests.
#
# Eventually, you should be able to parse programs in the
# test_models.py file.   At this point, you're well on your
# way to parsing real programs.   The directory tests/Programs
# contains actual Wabbit programs that you can try.
#
# If you're feeling lucky, modify your interpreter to read source
# code, parse it, and run it.   Try your interpreter by running
# it on various programs in the tests/Programs directory.

import sys
from .model import *
from .tokenize import tokenize
from wabbit import interp

SYMBOL_TABLE = {}


class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens  # Tokens from the tokenizer
        self.lookahead = None  # Next unconsumed token (or None)
        self.fn_def_flag = False

    # expect() expects a particular type and then returns the actual Token object that was just read
    def expect(self, type):
        # print('expecting', type)
        # Require the next token to exactly match type
        if self.peek(type):
            # Does it match?
            tok = self.lookahead
            self.lookahead = None  # Consume the lookahead (eat it)
            return tok
        else:
            raise SyntaxError(f"On lineno {self.lookahead.lineno} -> Expected {type}. Got {self.lookahead}")

    # peek() is not really a peek, but really the next token that I want to consume
    def peek(self, type):

        # See if the next token matches type and return True/False
        # idea is lookahead on the python token generator, if previously no lookahead
        # but if already looked-ahead on the generator, then no need to look-ahead and just read
        if self.lookahead is None:
            self.lookahead = next(self.tokens)  # Get the next token

        return self.lookahead.type == type

    # if the lookahead is of the expected type, then consume the token, else return None
    def accept(self, type):
        # Optionally accept a token of given type.  Return and consume it
        # if found, otherwise return None
        if self.peek(type):
            tok = self.lookahead
            self.lookahead = None
            return tok
        else:
            return None


# Top-level function that runs everything.  You'll need to modify
# this part to integrate with your tokenizer and representation of
# source code.  Also,
def parse_source(program):
    tokens = tokenize(program)  # Previous project
    # One challenge. How do you encapsulate the token stream in a way that
    # it can be used to write the rest of the parser?  What do you pass
    # as an argument to the various functions below?
    stream = TokenStream(tokens)
    program.model = parse_program(stream)
    return program.model


def parse_program(stream: TokenStream):  # Token stream
    # Code this to recognize any Wabbit program and return the model.
    # How do you modify this to parse multiple statements?
    # model = parse_statement(stream)
    model = parse_statements(stream)
    stream.expect('EOF')
    return model


def parse_statements(stream: TokenStream):
    statements = []
    while not (stream.peek('EOF') or stream.peek('RBRACE')):
        statement = parse_statement(stream)
        # print('parse.py --> ast for the parsed statement', statement)
        statements.append(statement)
    return Block(statements)


def parse_statement(stream: TokenStream):
    # Parse any Wabbit statement.  How do you modify this to recognize more
    # than one statement kind?
    if stream.peek('BREAK'):  # peek looks ahead at next token (does not consume)
        return parse_break_statement(stream)
    elif stream.peek('CONTINUE'):
        return parse_continue_statement(stream)
    elif stream.peek('PRINT'):
        return parse_print_statement(stream)
    elif stream.peek('WHILE'):
        return parse_while_statement(stream)
    elif stream.peek('CONST'):
        return parse_const_statement(stream)
    elif stream.peek('VAR'):
        return parse_var_statement(stream)
    elif stream.peek('IF'):
        return parse_if_statement(stream)
    elif stream.peek('FUNC'):
        return parse_function_definition(stream)
    elif stream.peek('RETURN'):
        return parse_return_statement(stream)
    else:
        # fall-back is to assume a expression statement
        return parse_expression_statement(stream)


def parse_break_statement(stream: TokenStream):
    # Example of parsing a simple statement (pseudocode).  You work left-to-right
    # over the expected tokens and return a model node upon success.
    stream.expect('BREAK')
    stream.expect('SEMI')
    return BreakStatement()


def parse_continue_statement(stream: TokenStream):
    # Example of parsing a simple statement (pseudocode).  You work left-to-right
    # over the expected tokens and return a model node upon success.
    stream.expect('CONTINUE')
    stream.expect('SEMI')
    return ContinueStatement()


def parse_print_statement(stream: TokenStream):
    stream.expect('PRINT')
    value = parse_expression(stream)
    stream.expect('SEMI')
    return PrintStatement(value)


def parse_while_statement(stream: TokenStream):
    stream.expect('WHILE')
    test = parse_expression(stream)
    stream.expect('LBRACE')
    body = parse_statements(stream)
    stream.expect('RBRACE')
    return WhileStatement(test, body)


def parse_const_statement(stream: TokenStream):
    stream.expect('CONST')
    name = stream.expect('NAME').value
    const_type = None
    if stream.peek('NAME'):  # types are being tokenized into NAME
        const_type = Type(stream.expect('NAME').value)
    stream.expect('ASSIGN')
    initializer = parse_expression(stream)
    stream.expect('SEMI')
    return ConstDeclaration(name, const_type, initializer)


def parse_var_statement(stream: TokenStream):
    stream.expect('VAR')
    name = stream.expect('NAME').value
    var_type = None
    if stream.peek('NAME'):  # types are being tokenized into NAME
        var_type = Type(stream.expect('NAME').value)
    else:
        var_type = None
    initializer = None
    if stream.peek('ASSIGN'):
        stream.expect('ASSIGN')
        initializer = parse_expression(stream)
    stream.expect('SEMI')
    return VarDeclaration(name, var_type, initializer)


def parse_if_statement(stream: TokenStream):
    stream.expect('IF')
    test = parse_expression(stream)
    stream.expect('LBRACE')
    consequence = parse_statements(stream)
    stream.expect('RBRACE'),
    alternative = None
    if stream.peek('ELSE'):
        stream.expect('ELSE')
        stream.expect('LBRACE')
        alternative = parse_statements(stream)
        stream.expect('RBRACE')
    return IfStatement(test, consequence, alternative)


def parse_function_definition(stream: TokenStream):

    print('entered function definition')

    token = stream.accept('FUNC')
    if not token:
        raise SyntaxError(f'Expected func keyword !')

    # parse the function name
    token = stream.accept('NAME')
    if token:
        name = Name(token.value)
    else:
        raise SyntaxError(f'Expected func name')

    # We are starting a function definition
    # stream.fn_def_flag = True

    # update the symbol table with the special meaning
    SYMBOL_TABLE[token.value] = 'func'

    # consume LPAREN
    token = stream.accept('LPAREN')
    if not token:
        raise SyntaxError(f'Expecting a "(" in func definition for {name}')

    # parse the function parameters
    fn_parameters = parse_function_parameters(stream, name)
    if not fn_parameters:
        raise SyntaxError(f'Parser could not parse the func parameters')

    # consume RPAREN
    token = stream.accept('RPAREN')
    if not token:
        raise SyntaxError(f'Expecting a ")" in func definition for {name}')

    # parse the function return type
    fn_return_type = None
    if stream.peek('NAME'):  # types are being tokenized into NAME
        fn_return_type = Type(stream.expect('NAME').value)

    # consume LBRACE
    stream.expect('LBRACE')

    # parse the function code block
    fn_code_block = parse_function_block(stream)

    # consume RBRACE
    stream.expect('RBRACE')

    # No longer in function definition
    # stream.fn_def_flag = False

    return FunctionDefinition(name, fn_parameters, fn_return_type, fn_code_block)


def parse_function_parameters(stream: TokenStream, fn_name=None):
    parameters = []
    while not (stream.peek('RPAREN')):
        parameter = parse_function_parameter(stream, fn_name)
        parameters.append(parameter)
        if not stream.peek('RPAREN'):
            stream.expect('COMMA')
    return FunctionParameters(parameters)


def parse_function_parameter(stream: TokenStream, fn_name=None):
    # parse parameter name
    token = stream.expect('NAME')
    param_name = None
    if token:
        param_name = token.value
    else:
        raise SyntaxError(f'Expecting a parameter name in the func definition {fn_name}')

    # parse parameter type
    if stream.peek('NAME'):  # types are being tokenized into NAME
        param_type = Type(stream.expect('NAME').value)
    else:
        raise SyntaxError(f'Expecting a type for the function parameter {param_name} in the func definition {fn_name}')

    # parse parameter initializer
    param_initializer = None
    return FunctionParameter(param_name, param_type, param_initializer)


def parse_function_block(stream: TokenStream):
    fn_body = parse_statements(stream)
    return fn_body


def parse_return_statement(stream: TokenStream):

    # consume RETURN token
    stream.accept('RETURN')

    # TODO - should I restore this block
    expression = parse_expression_statement(stream)
    # TODO - restore the block

    # TODO - delete the below i.e. testing for expression containing multiple fn_call()s
    # expression = parse_expression(stream)
    # print('ast for expression ->', expression)
    # stream.expect('SEMI')
    # TODO - DELETE THE BLOCK

    return FunctionReturn(expression)


def parse_function_application(name:str, stream: TokenStream):

    # consume LPAREN
    if stream.peek('LPAREN'):
        stream.expect('LPAREN')

    # parse the function-call arguments
    fn_arguments = parse_function_arguments(stream)

    # consume RPAREN
    token = stream.accept('RPAREN')
    if not token:
        raise SyntaxError(f"Expecting ')' in the function call to {name}")

    return FunctionApplication(Name(name), fn_arguments)


def parse_function_arguments(stream: TokenStream):

    arguments = []
    while not (stream.peek('RPAREN')):
        argument = parse_function_argument(stream)
        arguments.append(argument)
        if not stream.peek('RPAREN'):
            stream.expect('COMMA')

    return FunctionArguments(arguments)


def parse_function_argument(stream: TokenStream):
    expression = parse_expression(stream)
    return expression


# Within the expression parse, the hierarchy being followed is as follows
# where the idea is to "parse into ast" the lowest level tokens first and then build
# your way upwards
# lor                                   (<---- HIGHEST level - parse into AST last)
# land
# > < >= <= == !=
# +,-
# * /
# () i.e. grouping
# unary operator
# NAME (i.e. variable or constant), true, false
# integers, floats, chars                (<---- LOWEST level - parse into AST first)


def parse_expression_statement(stream: TokenStream):
    expression = parse_assignment(stream)
    stream.expect('SEMI')
    return expression


def parse_expression(stream: TokenStream):
    # token = stream.expect('INTEGER')      # Pseudocode
    # return Integer(token.value)    # Pseudocode (adjust to your model)
    # return parse_factor(stream)
    # return parse_add_term(stream)
    # return parse_rel_term(stream)
    # return parse_land_term(stream)
    # return parse_lor_term(stream)
    return parse_assignment(stream)  # parse_assignment is the highest level


def parse_assignment(stream: TokenStream):
    lor_term = parse_lor_term(stream)
    # print('parse.py --> assignment left term = ',lor_term)
    if tok := stream.accept('ASSIGN'):
        value = parse_lor_term(stream)
        # print('parse.py --> assignment right term = ', value)
        lor_term = Assignment(lor_term, value)
    # print('parse.py --> packaged up assignment = ', lor_term)
    return lor_term


def parse_lor_term(stream: TokenStream):
    land_term = parse_land_term(stream)
    while tok := (stream.accept('LOR')):
        right_land_term = parse_land_term(stream)
        land_term = LogicalOp('||', land_term, right_land_term)
    return land_term


def parse_land_term(stream: TokenStream):
    rel_term = parse_rel_term(stream)
    while tok := (stream.accept('LAND')):
        right_rel_term = parse_rel_term(stream)
        rel_term = LogicalOp('&&', rel_term, right_rel_term)
    return rel_term


def parse_rel_term(stream: TokenStream):
    left_term = parse_add_term(stream)
    # wabbit does not allow chaining of rel operators like a < b < c < d not allowed
    if tok := (
            stream.accept('LT') or stream.accept('LE') or
            stream.accept('GT') or stream.accept('GE') or
            stream.accept('EQ') or stream.accept('NE')):
        right_term = parse_add_term(stream)
        left_term = RelOp(tok.value, left_term, right_term)

    return left_term


# Higher level doing BinOps of + and -
# Joins terms received from the parse_stream into BinOps of + and -
def parse_add_term(stream: TokenStream):
    # idea is to implement ADD_TERM = term +/- (term +/- (term +/- (term +/- .... where term is a*/b
    # so start with collecting as many MULT or DIV terms as possible
    term = parse_term(stream)

    print(term)

    # when the stream of MULT, DIVIDE is over, check for PLUS or MINUS
    while tok := (stream.accept('PLUS') or stream.accept('MINUS')):
        # if PLUS or MINUS is found, then check again for a stream of MULT or DIVIDE and store into right_term
        right_term = parse_term(stream)
        # Make the ADD_TERM and stage it for the next round
        term = BinOp(tok.value, term, right_term)

    return term


# Lower level doing BinOps of * and /
# Aggressively collects a continuous streak of * and - and stitches into BinOps
def parse_term(stream: TokenStream):
    factor = parse_factor(stream)
    while stream.peek('TIMES'):
        stream.expect('TIMES')
        right_factor = parse_factor(stream)
        factor = BinOp('*', factor, right_factor)
    while stream.peek('DIVIDE'):
        stream.expect('DIVIDE')
        right_factor = parse_factor(stream)
        factor = BinOp('/', factor, right_factor)

    return factor


# to be called by parse_expression
def parse_factor(stream: TokenStream):
    if stream.peek('INTEGER'):
        token = stream.expect('INTEGER')
        return Integer(token.value)

    token = stream.accept('FLOAT')
    if token:
        return Float(token.value)

    token = stream.accept('CHAR')
    if token:
        return Char(token.value)

    token = stream.accept('TRUE')
    if token:
        return Boolean('true')

    token = stream.accept('FALSE')
    if token:
        return Boolean('false')

    token = stream.accept('NAME')
    if token:
        k = SYMBOL_TABLE.get(token.value, None)
        print(f'token -> {token.value}, {k}')
        if _t := SYMBOL_TABLE.get(token.value, None):
            if _t == 'func':
                # print(f'fn def flag -> {stream.fn_def_flag}, func -> {token.value} ')
                return parse_function_application(token.value, stream)
            else:
                raise RuntimeError(f"No AST handler assigned for the {token.value} in the symbol table")
        else:
            return Name(token.value)

    tok = stream.accept('MINUS') or stream.accept('PLUS') or stream.accept('LNOT')
    if tok:
        factor = parse_factor(stream)
        return UnaryOp(tok.value, factor)

    if stream.accept('LPAREN'):
        factor = parse_expression(stream)
        stream.expect('RPAREN')
        return Grouped(factor)

    if stream.peek('LBRACE'):
        stream.expect('LBRACE')
        statements = []
        while not stream.peek('RBRACE'):
            statement = parse_statement(stream)
            statements.append(statement)
        stream.accept('RBRACE')
        return Compound(statements)

    print(next(stream.tokens))

    raise SyntaxError('Bad factor !')


# Main program
def parse_file(filename):
    from .program import Program
    print('\nPARSER initiated ...')
    print('PARSER generated the following AST(model) =>')
    program = Program(filename)
    program.read_source()
    parse_source(program)
    print(program.model.statements)
    print(f'PARSER finished execution')
    return program


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 -m wabbit.parse filename')
    program = parse_file(sys.argv[1])
    print(program.model)
    print(program.model.statements)
