# tokenize.py
#
# The role of a tokenizer is to turn raw text into symbols known as
# tokens.  A token consists of a type and a value.  For example, the
# text "123" is represented as the token ('INTEGER', '123').
#
# The following set of tokens are defined. The suggested name of the
# token is on the left. An example of matching text is on the right.
#
# Reserved Keywords:
#     CONST   : 'const'
#     VAR     : 'var'  
#     PRINT   : 'print'
#     BREAK   : 'break'
#     CONTINUE: 'continue'
#     IF      : 'if'
#     ELSE    : 'else'
#     WHILE   : 'while'
#     FUNC    : 'func'
#     RETURN  : 'return'
#     TRUE    : 'true'
#     FALSE   : 'false'
#
# Identifiers/Names
#     NAME    : Text starting with a letter or '_', followed by any number
#               number of letters, digits, or underscores.
#               Examples:  'abc' 'ABC' 'abc123' '_abc' 'a_b_c'
#
# Literals:
#     INTEGER :  123   (decimal)
#
#     FLOAT   : 1.234
#
#     CHAR    : 'a'     (a single character - byte)
#               '\n'    (newline)
#
# Operators:
#     PLUS     : '+'
#     MINUS    : '-'
#     TIMES    : '*'
#     DIVIDE   : '/'
#     LT       : '<'
#     LE       : '<='
#     GT       : '>'
#     GE       : '>='
#     EQ       : '=='
#     NE       : '!='
#     LAND     : '&&'     (logical and, not bitwise)
#     LOR      : '||'     (logical or, not bitwise)
#     LNOT     : '!'      (logical not, not bitwise)
#    
# Miscellaneous Symbols
#     ASSIGN   : '='
#     SEMI     : ';'
#     LPAREN   : '('
#     RPAREN   : ')'
#     LBRACE   : '{'
#     RBRACE   : '}'
#     COMMA    : ','
#
# Comments:  To be ignored
#      //             Skips the rest of the line
#      /* ... */      Skips a block (no nesting allowed)
#
# Errors: Your lexer may optionally recognize and report errors
# related to bad characters, unterminated comments, and other problems.
# ----------------------------------------------------------------------

# Class that represents a token
class Token:
    def __init__(self, type, value, lineno, index):
        self.type = type
        self.value = value
        self.lineno = lineno   
        self.index = index

    def __repr__(self):
        return f'Token({self.type!r}, {self.value!r}, {self.lineno}, {self.index})'

# High level function that takes an input program and turns it into
# tokens.  This might be a natural place to use some kind of generator
# function or iterator.

lang_literal_tokens = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'TIMES',
    '/': 'DIVIDE',
    ';': 'SEMI',
    ',': 'COMMA',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACE',
    '}': 'RBRACE',
    '<': 'LT',
    '>': 'GT',
    '=': 'ASSIGN',
    '==': 'EQ',
    '>=': 'GE',
    '<=': 'LE',
    '!=': 'NE',
    '&&': 'LAND',
    '||': 'LOR',
    '!': 'LNOT'
}

lang_reserved_words = {
    'const', 'var', 'print', 'break', 'continue', 'if',
    'else', 'while', 'func', 'return', 'true', 'false'
}

def tokenize(program):
    lineno = 1
    n = 0
    text = program.source
    while n < len(text):

        # handle newline
        if text[n] == '\n':
            n += 1
            lineno += 1
            continue

        # handle whitespaces, tabs, newlines
        if text[n].isspace():
            n += 1
            if text[n] == '\n':
                lineno += 1
            continue

        # handle comments
        if text[n:n+2] == '/*':
            while n<len(text) and text[n:n+2] != '*/':
                if text[n]=='\n':
                    lineno += 1
                n += 1
            n+=2
            continue

        # handle single line comments
        if text[n:n+2] == '//':
            while n<len(text) and text[n] != '\n':
                n += 1
            continue

        # handle 2-characters language tokens
        if text[n:n+2] in lang_literal_tokens:
            yield Token(lang_literal_tokens[text[n:n+2]], text[n:n+2], lineno, n)
            n += 2
            continue

        # handle 1-character language tokens
        if text[n] in lang_literal_tokens:
            yield Token(lang_literal_tokens[text[n]], text[n], lineno, n)
            n += 1
            continue

        # Handle integers and floats
        if text[n].isdigit():
            start = n
            while n < len(text) and text[n].isdigit():
                n += 1
            if n < len(text) and text[n] == '.':
                n += 1
                while n < len(text) and text[n].isdigit():
                    n += 1
                yield Token('FLOAT', text[start:n], lineno, start)
            else:
                yield Token('INTEGER', text[start:n], lineno, start)
            continue

        # Handle characters
        if text[n] =="'":
            start = n
            n += 1
            while n < len(text) and text[n] != "'":
                n += 1
            yield Token('CHAR', text[start:n+1], lineno, start)
            # yield Token('CHAR', text[start+1:n], lineno, start)
            n += 1
            continue

        # Reserved words
        if text[n].isalpha() or text[n] == '_':
            start = n
            while n < len(text) and (text[n].isalnum() or text[n]=='_'):
                n += 1
            check_str = text[start:n]
            if check_str in lang_reserved_words:
                yield Token(check_str.upper(), check_str, lineno, start)
            else:
                yield Token('NAME', check_str, lineno, start)
            continue

        print(f'{lineno}: Illegal character {text[n]!r}')
        n += 1
        
    # Emit an EOF token at the end to signal end of input
    yield Token('EOF', 'EOF', lineno, n)

# Main program to test on input files
def main(filename):
    from .program import Program
    program = Program(filename)
    program.read_source()
    for tok in tokenize(program):
        print(tok)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 -m wabbit.tokenize filename")
    main(sys.argv[1])

    
            
        

            
    
