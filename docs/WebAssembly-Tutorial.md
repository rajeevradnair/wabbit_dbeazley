# WebAssembly Code Generation Tutorial

Note: directly generating Wasm files as described here is probably
a bigger mess than it's worth.  See the file wabbit/wasm.py for a
discussion of how to encode the output in WAT--a text-based human
readable version of code.

This is tutorial on how to directly generate WebAssembly code without
any tools.  At first glance, it's going to see very low-level and
maybe a bit overwhelming.  Frankly, it's probably better to use
something more high-level like WAT. However, take it step-by-step and
experiment.  Getting it to work at all is the first major step.  Once
you have that, it gets a bit easier. 

## WebAssembly Overview

Wasm is a relatively new technology that is usually introduced with a
fairly complicated toolchain.  For example, it is possible to compile
C, C++, Rust, and other languages to Wasm and to have that code run
(somehow) in the browser.  You can even find demos of game engines and
other interesting things.  However, it can be a bit tough to wrap your
brain around what's happening with all of the tooling involved.  We're going to
try to work with it directly. This is probably more low-level than
you're used to (or would normally want to work with it), but it's also
instructive.

At a high-level, Wasm is a small "machine code" that simulates a stack machine.
Just to refresh your memory, a stack machine consists of a stack and operations
that only operate on elements on the stack.  For example, suppose you wanted to
compute 2\*3 + 4\*5 on a stack in Python.  Here's how you would do that:

```
>>> stack = []
>>> stack.append(2)       # Push
>>> stack.append(3)
>>> stack.append(stack.pop() * stack.pop())
>>> stack.append(4)
>>> stack.append(5)
>>> stack.append(stack.pop() * stack.pop())
>>> stack.append(stack.pop() + stack.pop())
>>> stack.pop()
26
>>>
```
Spend some time studying this. Convince yourself that it works.

Wasm, only understands 4 datatypes--integers and floats in both 32-bit and
64-bit encodings.  Wasm is encoded in a compact binary encoding---not a nice
text encoding.

As a note: To make it somewhat simpler to describe, our encoding will not be
as efficient as it could be.  Web Assembly uses a number of techniques
to compress the size of the output file at the expense of added encoding
complexity.  Our focus is on making something that works.  Making it work
faster is left as an exercise to the reader.

## Primitive Values and Encodings

To start out, Wasm dictates a precise encoding of integers, floats, and
text strings.

Integers are encoded into a LEB-128, a variable length encoding. The
following Python functions can be used for this purpose:

```
def encode_unsigned(value):
    '''
    Produce an LEB128 encoded unsigned integer.
    '''
    parts = []
    while value:
        parts.append((value & 0x7f) | 0x80)
        value >>= 7
    if not parts:
        parts.append(0)
    parts[-1] &= 0x7f
    return bytes(parts)

def encode_signed(value):
    '''
    Produce a LEB128 encoded signed integer.
    '''
    parts = [ ]
    if value < 0:
        # Sign extend the value up to a multiple of 7 bits
        value = (1 << (value.bit_length() + (7 - value.bit_length() % 7))) + value
        negative = True
    else:
        negative = False
    while value:
        parts.append((value & 0x7f) | 0x80)
        value >>= 7
    if not parts or (not negative and parts[-1] & 0x40):
        parts.append(0)
    parts[-1] &= 0x7f
    return bytes(parts)

assert encode_unsigned(624485) == bytes([0xe5, 0x8e, 0x26])
assert encode_unsigned(127) == bytes([0x7f])
assert encode_signed(-624485) == bytes([0x9b, 0xf1, 0x59])
assert encode_signed(127) == bytes([0xff, 0x00])
```

Floating point numbers are encoded directly as a little-endian 8-byte double precision
value using this function:

```
import struct

def encode_f64(value):
    '''
    Encode a 64-bit float point as little endian
    '''
    return struct.pack('<d', value)
```

Wasm also involves the encoding of a so-called "vector".  A vector is
list of identically typed items. For example, you could have a vector of 
integers, a vector of floats, a vector of bytes, and so forth.  Vectors are
encoded as an unsigned length followed by the raw encoding of whatever items
it contains.  So, write the following function:

```
def encode_vector(items):
    '''
    A size-prefixed collection of objects.  If items is already
    bytes, it is prepended by a length and returned.  If items
    is a list of byte-strings, the length of the list is prepended
    to byte-string formed by concatenating all of the items.
    '''
    if isinstance(items, bytes):
        return encode_unsigned(len(items)) + items
    else:
        return encode_unsigned(len(items)) + b''.join(items)
```

Strings are represented as a UTF-8 encoded vector of bytes.  The following
function will encode a string:

```
def encode_string(text):
    '''
    Encode a text string as a UTF-8 vector
    '''
    return encode_vector(text.encode('utf-8'))
```

The first rule of Wasm is that ALL literal values (integers, floats, names, etc.) must
be encoded by these functions. So, put these in a file `wasm.py` and use it as a starting
point.

Try a few examples to see what the encodings look like:

```
>>> encode_unsigned(1234)
b'\xd2\t'
>>> encode_signed(-1234)
b'\xaev'
>>> encode_f64(123.45)
b'\xcd\xcc\xcc\xcc\xcc\xdc^@'
>>> encode_string('spam')
b'\x04spam'
>>> 
```

Reminder: You must always use these functions.

## Primitive Data Types

Wasm only understands 4 primitive types of data.  Add the following definitions to your `wasm.py`
file:

```
# Wasm Type names
i32 = b'\x7f'   # (32-bit int)
i64 = b'\x7e'   # (64-bit int)
f32 = b'\x7d'   # (32-bit float)
f64 = b'\x7c'   # (64-bit float)
```

These specify the byte encoding of types.  Instead of using nice names
like "int" and "float", Wasm uses byte values like `'\x7f'` and
`'\x7c'`.  We're going to use the nice Python names like `i32` and
`f64`.

## The Basic Code Elements

All Wasm code is packaged into a module.  For our purposes, a module
contains imported functions, functions, and global variables. Create
the following arrangement of classes:

```
class WasmModule:
    def __init__(self, name):
        self.name = name
        self.imported_functions = [ ]
        self.functions = [ ]
	self.global_variables = [ ]

class WasmImportedFunction:
    '''
    A function defined outside of the Wasm environment
    '''
    def __init__(self, module):
        self.module = module
        self.idx = len(module.imported_functions)
	module.imported_functions.append(self)

class WasmFunction:
    '''
    A natively defined Wasm function
    '''
    def __init__(self, module):
        self.module = module
        self.idx = len(module.imported_functions) + len(module.functions)
        module.functions.append(self)

class WasmGlobalVariable:
    '''
    A natively defined Wasm global variable
    '''
    def __init__(self, module):
        self.module = module
        self.idx = len(module.global_variables)
        module.global_variables.append(self)
```

Think of these classes as a kind of database schema.  `WasmModule` is a top-level
container for everything.  There are three tables holding different kinds
of objects.  Each object is uniquely identified by a numeric index (`self.idx`)
that points into a table.

It might also help to think about Python. In Python, all code is contained within 
a module. You use the `import` statement to load a module.  Modules have a name.
Modules contain definitions of functions and variables.

## Functions

All executable code must exist in a function.  A function is defined
by a name, a list of argument types, and a list of return types.  The
argument and return types form the function "signature".  For example,
here is a textual representation of a signature:

```
pow: [f64, f64] -> [f64]
```

Modify the `WasmFunction` class to include name and signature information. For example:

```
class WasmFunction:
    '''
    A natively defined Wasm function
    '''
    def __init__(self, module, name, argtypes, rettypes):
        self.module = module
        self.name = name
        self.argtypes = argtypes
	self.rettypes = rettypes
        self.idx = len(module.imported_functions) + len(module.functions)
        module.functions.append(self)
```

Here is an example of how you would declare a function `func spam(x int, y float) int`:

```
spam = WasmFunction(mod, 'spam', [i32, f64], [i32])
```

An imported function is a function that is defined outside of the current
module environment.  Think about the `import` statement in Python.  Modify
the `WasmImportedFunction` class to also include name and signature information.
For example:

```
class WasmImportedFunction:
    '''
    An imported Wasm function
    '''
    def __init__(self, module, envname, name, argtypes, rettypes):
        self.module = module
        self.envname = envname
        self.name = name
        self.argtypes = argtypes
	self.rettypes = rettypes
        self.idx = len(module.imported_functions)
        module.imported_functions.append(self)
```

The one extra piece of information here is the `envname`
attribute. This is the name of the external environment (or namespace)
where the function is coming from.  For example, in Python:

```
import math

math.sin(2)      # envname = "math", name="sin"
```

Here is an example of how a comparable imported function would be defined:

```
sin = WasmImportedFunction(mod, "math", "sin", [f64], [f64])
```

## Global Variables

A global variable has a name, a type, and an initial value.  Add these to
the `WasmGlobalVariable` class:

```
class WasmGlobalVariable:
    '''
    A natively defined Wasm global variable
    '''
    def __init__(self, module, name, type, initializer):
        self.module = module
	self.name = name
	self.type = type
	self.initializer = initializer
        self.idx = len(module.global_variables)
        module.global_variables.append(self)
```

Here is an example of how an integer global variable `x` with an initial value of 0 would be defined:

```
x = WasmGlobalVariable(mod, 'x', i32, 0)
```

## Interlude : The Big Picture

At this point, we are really just putting all of the pieces in place to start
encoding.  There are some basic elements like types (e.g., `i32`, `f64`), modules,
functions, and global variables.  Make sure you understand how they fit together
before moving on.  The key to making this part work is to stay organized.

## Instruction Encoding and Function Bodies

All emitted code in Wasm must exist in the body of a function.  The code is
encoded as a binary byte string made up of opcodes.  Here is a table that
shows a few opcodes used for integer mathematical calculations:

```
b'\x41' <val>  => i32.const (val is signed integer)
b'\x6a'        => i32.add
b'\x6b'        => i32.sub
b'\x6c'        => i32.mul
b'\x6d'        => i32.div_s
b'\x0f'        => return
```

Take your `WasmFunction` class and extend it with the ability to
collect and emit opcodes:

```
class WasmFunction:
    '''
    A natively defined Wasm function
    '''
    def __init__(self, module, name, argtypes, rettypes):
        self.module = module
        self.name = name
        self.argtypes = argtypes
        self.rettypes = rettypes
        self.idx = len(module.imported_functions) + len(module.functions)
        module.functions.append(self)

        # Code generation
        self.code = b''

    def iconst(self, value):
        self.code += b'\x41' + encode_signed(value)

    def iadd(self):
        self.code += b'\x6a'

    def imul(self):
        self.code += b'\x6c'

    def ret(self):
        self.code += b'\x0f'
```

Consider the following function in Wabbit:

```
func f() int {
    return 2*3 + 4*5;
}
```

Here is how you encode it:

```
mod = WasmModule('example')
f = WasmFunction(mod, 'f', [], [i32])
f.iconst(2)
f.iconst(3)
f.imul()
f.iconst(4)
f.iconst(5)
f.imul()
f.iadd()
f.ret()
```

If you look at the resulting `f.code` attribute, you'll get this:

```
>>> f.code
b'A\x02A\x03lA\x04A\x05lj\x0f'
>>>
```

## Parameters and Local Variables

Functions have local variables.  For example, suppose you had this Wabbit function:

```
func g(x int, y int) int {
    var z int = x + y;
    return z;
}
```

To manage local variables, you need to store some extra information in your
`WasmFunction` class.  You'll also need some opcodes for allocating local variables.

In Wasm, local variables are referenced by numeric index. The function arguments
go first, starting at index 0.  Variables defined inside the body go afterwards
and continue where the numbering left off.  Thus, for the above function, you
have the following indices:

```
0:  x
1:  y
2:  z
```

There are two instructions for getting and setting the value of a local. They
require the numeric index:

```
b'\x20' <localidx>  => local.get
b'\x21' <localidx>  => local.set
```

To manage all of this, you need to extend your `WasmFunction` class slightly
to track declared local variables.  Modify it like this:

```
class WasmFunction:
    '''
    A natively defined Wasm function
    '''
    def __init__(self, module, name, argtypes, rettypes):
        ...
        # Code generation
        self.code = b''

        # Types of local variables
        self.local_types = []

    ...
    def alloca(self, type):
        idx = len(self.argtypes) + len(self.local_types)
        self.local_types.append(type)
        return idx

    def local_get(self, idx):
        self.code += b'\x20' + encode_unsigned(idx)

    def local_set(self, idx):
        self.code += b'\x21' + encode_unsigned(idx)
```

Here is an example of how you would encode the earlier `g` function:

```
g = WasmFunction(mod, 'g', [i32, i32], [i32])
z_idx = g.alloca(i32)
g.local_get(0)      # x
g.local_get(1)      # y
g.iadd()            # x + y
g.local_set(z_idx)  # z = x + y
g.local_get(z_idx)  # load z
g.ret()
```

## Global Variables

As you know, Wabbit code allows for global variables.  For example, consider this:

```
var n int = 13;

func h(d int) int {
    n = n + d;
    return n;
}
```

To load/store global variables, a pair of Wasm instructions are used:

```
b'\x23' <globidx>  => global.get
b'\x24' <globidx>  => global.set
```

You can support these by adding the following methods to your `WasmFunction`
class:

```
class WasmFunction:
    ...
    def global_get(self, gvar):
        self.code += b'\x23' + encode_unsigned(gvar.idx)

    def global_set(self, gvar):
        self.code += b'\x24' + encode_unsigned(gvar.idx)
```

Here's how you would use these to encode the above code:

```
n_var = WasmGlobalVariable(mod, "n", i32, 13)
h = WasmFunction(mod, "h", [i32], [i32])
h.global_get(n_var)     
h.local_get(0)       
h.iadd()
h.global_set(n_var)
h.global_get(n_var)
h.ret()
```

## Encoding a Module

At this point, we've defined three different Wabbit functions:

```
func f() int {
   return 2*3 + 4*5;
}

func g(x int, y int) int {
   var z int = x + y;
   return z;
}

var n int = 13;

func h(d int) int {
    n = n + d;
    return n;
}
```

Just to refresh, here was the code to do that:

```
mod = WasmModule('example')
f = WasmFunction(mod, 'f', [], [i32])
f.iconst(2)
f.iconst(3)
f.imul()
f.iconst(4)
f.iconst(5)
f.imul()
f.iadd()
f.ret()

g = WasmFunction(mod, 'g', [i32, i32], [i32])
z_idx = g.alloca(i32)
g.local_get(0)      # x
g.local_get(1)      # y
g.iadd()            # x + y
g.local_set(z_idx)  # z = x + y
g.local_get(z_idx)  # load z
g.ret()

n_var = WasmGlobalVariable(mod, "n", i32, 13)
h = WasmFunction(mod, "h", [i32], [i32])
h.global_get(n_var)     
h.local_get(0)       
h.iadd()
h.global_set(n_var)
h.global_get(n_var)
h.ret()

```

To turn it into something that can actually run , there is a step of
encoding and packaging the module into a form where Wasm can work with
it (i.e., so you can load it into the browser).  This involves turning
the module into a big blob of bytes.

The encoding a module involves encoding various information about functions,
imports, globals, and other metadata.  It is broken into sections like this:

```
                +----------------------------+
 Header    :    | b'\x00asm\x01\x00\x00\x00' |
                +----------------------------+
 Section 1 :    |    type signatures         |
                +----------------------------+    
 Section 2 :    |    imports                 |
                +----------------------------+         
 Section 3 :    |    function index          |
                +----------------------------+    
 Section 6 :    |    globals                 |
                +----------------------------+
 Section 7 :    |    exports                 |
                +----------------------------+          
 Section 10 :   |    function code           |
                +----------------------------+          
```

There are some other sections not shown or needed for now.  The encoding
of each section consists of a 1-byte section number, a section length (in bytes), 
and the section contents. Write the following function to encode a section:

```
def encode_section(sectnum, contents):
    return bytes([sectnum]) + encode_unsigned(len(contents)) + contents
```

Now, let's focus on each section individually

### Type Signatures (section 1)

The type signature section (section 1) is a vector of all function signatures.
Write the following function to encode a single function signature:

```
def encode_signature(func):
    return b'\x60' + encode_vector(func.argtypes) + encode_vector(func.rettypes)
```

Applying this, here s how you encode section 1.

```
all_funcs = module.imported_functions + module.functions
signatures = [encode_signature(func) for func in all_funcs]
section1 = encode_section(1, encode_vector(signatures))
```

### Imports (section 2)

The imports contains information for all imported functions.  Write the
following function to encode a single import:

```
def encode_import_function(func):
    return (encode_string(func.envname) + 
            encode_string(func.name) + 
	    b'\x00' +
	    encode_unsigned(func.idx))
```

Using this, create section 2 as follows:

```
all_imports = [ encode_import_function(func) for func in module.imported_functions ]
section2 = encode_section(2, encode_vector(all_imports))
```

### Function Table (section 3)

Section 3 is a mapping of internal function indices to the type signature table.
This is a little strange, but here's how to create it:

```
section3 = encode_section(3, encode_vector([encode_unsigned(f.idx) for f in module.functions]))
```

### Global Variables (section 6)

Global variables are encoded as a type and an initial value expression. The initial value
expression is a constant expressed using the `i32.const` or `f64.const` opcodes.  It's a little
messy but here is some code:

```
def encode_global(gvar):
    if gvar.type == i32:
        return i32 + b'\x01\x41' + encode_signed(gvar.initializer) + b'\x0b'
    elif gvar.type == f64:
        return f64 + b'\x01\x44' + encode_f64(gvar.initializer) + b'\x0b'
```

Here's how you create the entire section

```
all_globals = [ encode_global(gvar) for gvar in module.global_variables ]
section6 = encode_section(6, encode_vector(all_globals))
```

### Exports (section 7)

Section 7 lists the names of all defined functions that are exported to the outside
world.  This is necessary so that functions can be called from Javascript (or whatever).

Create a single export using this function:

```
def encode_export_function(func):
    return encode_string(func.name) + b'\x00' + encode_unsigned(func.idx)
```

Use this code to make the entire section

```
all_exports = [ encode_export_function(func) for func in module.functions ]
section7 = encode_section(7, encode_vector(all_exports))
```

### Function Code (section 10)

Section 10 consists of the code bodies for each defined function.  A code
body consists of the local variable types as well as all of the 
raw instructions. This is prepended by the length in bytes.
Write the following function that encodes a single function:

```
def encode_function_code(func):
    localtypes = [ b'\x01' + ltype for ltype in func.local_types ]
    if not func.code[-1:] == b'\x0b':
        func.code += b'\x0b'
    code = encode_vector(localtypes) + func.code
    return encode_unsigned(len(code)) + code
```

The contents of section 10 are created as follows:

```
allcode = [ encode_function_code(func) for func in module.functions ]
section10 = encode_section(10, encode_vector(allcode))
```

Put all of this together by adding an `encode_module()` method like
this:

```
def encode_module(module):
    # section 1 - signatures
    all_funcs = module.imported_functions + module.functions
    signatures = [encode_signature(func) for func in all_funcs]
    section1 = encode_section(1, encode_vector(signatures))

    # section 2 - Imports
    all_imports = [ encode_import_function(func) for func in module.imported_functions ]
    section2 = encode_section(2, encode_vector(all_imports))

    # section 3 - Functions
    section3 = encode_section(3, encode_vector([encode_unsigned(f.idx) for f in module.functions]))

    # section 7 - Exports
    all_exports = [ encode_export_function(func) for func in module.functions ]
    section7 = encode_section(7, encode_vector(all_exports))

    # section 6 - Globals
    all_globals = [ encode_global(gvar) for gvar in module.global_variables ]
    section6 = encode_section(6, encode_vector(all_globals))

    # section 10 - Code
    all_code = [ encode_function_code(func) for func in module.functions ]
    section10 = encode_section(10, encode_vector(all_code))

    return b''.join([b'\x00asm\x01\x00\x00\x00',
                    section1,
                    section2,
                    section3,
                    section6,
                    section7,
                    section10])
```

Put this in your file and use to to make the final module like this:

```
mod = WasmModule('example')
...
with open('out.wasm', 'wb') as file:
    file.write(encode_module(mod))
```

If it works, you'll end up with a file `out.wasm` in the current directory.

## Executing a Module (from Javascript)

Wasm doesn't run by itself.  It needs to be launched from Javascript.
Create a file `hello.html` that contains the following HTML and
Javascript:

```
<html>
<body>
<h3>Program Output</h3>

<pre id="fout">f out: </pre>
<pre id="gout">g out: </pre>
<pre id="hout">h out: </pre>

<script>
    var imports = { };
    fetch("out.wasm").then(response =>
       response.arrayBuffer()
    ).then(bytes =>
       WebAssembly.instantiate(bytes, imports)
    ).then(results => {
       fout = results.instance.exports.f();
       document.getElementById("fout").innerHTML += fout + "\n";

       gout = results.instance.exports.g(20, 30);
       document.getElementById("gout").innerHTML += gout + "\n";

       hout = results.instance.exports.h(100);
       document.getElementById("hout").innerHTML += hout + "\n";

    });
</script>
</body>
</html>
```

In this code, the `out.wasm` file is fetched and instantiated into a WebAssembly
instance.  The `f()`, `g()`, and `h()` functions are called via the instance exports
When called, its output is appended to the HTML in the `<pre>` 
section at the top.  

To test this, go to the command line and the same directory as the `hello.html`
and `out.wasm` file.  Run the following Python command:

```
bash % python3 -m http.server
```

This launches a web server.  Now click on
http://localhost:8000/hello.html.  You should see an output of "26", "50", and "113".
If you see nothing, open the JavaScript dev console in your browser,
reload, and look for error messages.  Even the slightest error in
encoding your module will cause it to fail. Ask for help if stuck.

## Building the Runtime

Wasm is extremely low-level and minimal.  Keep in mind you only get integers and floats.
There are no strings. Or even any built-in functions!  Wasm doesn't get access to
any part of Javascript or the browser environment all by itself.  This 
presents certain logistical problems.  For example, how do you implement printing
from Wabbit?

The solution here is that if you want printing,
you implement it in JavaScript, not Wasm.   Make a new file `hello_runtime.html` file and
enter the following code:

```
<html>
<body>
<h3>Program Output</h3>

<pre id="myout">The output is: </pre>

<script>
    var imports = { 
       runtime : {
           _print: (x) => { document.getElementById("myout").innerHTML += x + "\n"; },
       }	   
     };
    fetch("out_runtime.wasm").then(response =>
       response.arrayBuffer()
    ).then(bytes =>
       WebAssembly.instantiate(bytes, imports)
    ).then(results => {
       window.main = results.instance.exports.main;
       window.main();
    });
</script>
</body>
</html>
```

Carefully observe that we have added a `_print()` function to the
`imports` variable.   Instead of calling multiple functions, we're just
calling a `main()` function.

To make the `_print` function available to Wasm, it has to be explicitly
imported and called.  Give your `WasmFunction` class a new opcode for
function call:

```
class WasmFunction:
    ...
    def call(self, func):
        self.code += b'\x10' + encode_unsigned(func.idx)
    ...
```

Now, consider the following Wabbit function:

```
var main() void {
    print 42;
    print 2*3 + 4*5;
}
```

Here's how you would make the print statements work.

```
mod = WasmModule('example')
_print = WasmImportedFunction(mod, 'runtime','_print', [i32], [])
main = WasmFunction(mod, 'main', [], [])
main.iconst(42)
main.call(_print)
main.iconst(2)
main.iconst(3)
main.imul()
main.iconst(4)
main.iconst(5)
main.imul()
main.iadd()
main.call(_print)
main.ret()

# Write to a file
with open('out_runtime.wasm', 'wb') as file:
    file.write(encode_module(mod))
```

To test this, go to the command line and the same directory as the `hello_runtime.html`
and `out_runtime.wasm` file.  Run the following Python command:

```
bash % python3 -m http.server
```

This launches a web server.  Now click on
http://localhost:8000/hello_runtime.html.  You should see an output of "42" and "26".

## A Wasm Mini Reference

This section provides a short reference of a few useful Wasm instructions
and data encoding

Types :

```
i32 = b'\x7f'    # 32 bit int
f64 = b'\x7c'    # 64 bit float
```

To define constants corresponding to the above types generate the following:

```  
b'\x41' <value>  => i32.const value
b'\x44' <value>  => f64.const value
```

The `<value>` needs to be encoded using `encoded_signed()` or `encode_f64()` depending
on the type.

Here are some useful opcodes for math:

```
b'\x6a'        => i32.add
b'\x6b'        => i32.sub
b'\x6c'        => i32.mul
b'\x6d'        => i32.div_s

b'\xa0'        => f64.add
b'\xa1'        => f64.sub
b'\xa2'        => f64.mul
b'\xa3'        => f64.div
```

To access a global variable, use these load and store instructions:

```
b'\x23' <globalidx>  => global.get
b'\x24' <globalidx>  => global.set
```

To access a local variable, use load and store instructions:

```
b'\x20' <localidx>  => local.get
b'\x21' <localidx>  => local.set
```

To call and return from a function:

```
b'\x10' <funcidx>  => call  (funcidx is function index)
b'\x0f'            => ret
```

More instructions can be found in the Wasm official specification.

## Complete Decoder

Here is complete source for the decoder as written in this tutorial:

```
# wasm.py

import struct

def encode_unsigned(value):
    '''
    Produce an LEB128 encoded unsigned integer.
    '''
    parts = []
    while value:
        parts.append((value & 0x7f) | 0x80)
        value >>= 7
    if not parts:
        parts.append(0)
    parts[-1] &= 0x7f
    return bytes(parts)

def encode_signed(value):
    '''
    Produce a LEB128 encoded signed integer.
    '''
    parts = [ ]
    if value < 0:
        # Sign extend the value up to a multiple of 7 bits
        value = (1 << (value.bit_length() + (7 - value.bit_length() % 7))) + value
        negative = True
    else:
        negative = False
    while value:
        parts.append((value & 0x7f) | 0x80)
        value >>= 7
    if not parts or (not negative and parts[-1] & 0x40):
        parts.append(0)
    parts[-1] &= 0x7f
    return bytes(parts)

assert encode_unsigned(624485) == bytes([0xe5, 0x8e, 0x26])
assert encode_unsigned(127) == bytes([0x7f])
assert encode_signed(-624485) == bytes([0x9b, 0xf1, 0x59])
assert encode_signed(127) == bytes([0xff, 0x00])

def encode_f64(value):
    '''
    Encode a 64-bit float point as little endian
    '''
    return struct.pack('<d', value)

def encode_vector(items):
    '''
    A size-prefixed collection of objects.  If items is already
    bytes, it is prepended by a length and returned.  If items
    is a list of byte-strings, the length of the list is prepended
    to byte-string formed by concatenating all of the items.
    '''
    if isinstance(items, bytes):
        return encode_unsigned(len(items)) + items
    else:
        return encode_unsigned(len(items)) + b''.join(items)

def encode_string(name):
    '''
    Encode a text name as a UTF-8 vector
    '''
    return encode_vector(name.encode('utf-8'))

def encode_section(sectnum, contents):
    return bytes([sectnum]) + encode_unsigned(len(contents)) + contents

def encode_signature(func):
    return b'\x60' + encode_vector(func.argtypes) + encode_vector(func.rettypes)

def encode_import_function(func):
    return (encode_string(func.envname) + 
            encode_string(func.name) + 
	    b'\x00' +
	    encode_unsigned(func.idx))

def encode_export_function(func):
    return encode_string(func.name) + b'\x00' + encode_unsigned(func.idx)

def encode_function_code(func):
    localtypes = [ b'\x01' + ltype for ltype in func.local_types ]
    if not func.code[-1:] == b'\x0b':
        func.code += b'\x0b'
    code = encode_vector(localtypes) + func.code
    return encode_unsigned(len(code)) + code

def encode_global(gvar):
    if gvar.type == i32:
        return i32 + b'\x01\x41' + encode_signed(gvar.initializer) + b'\x0b'
    elif gvar.type == f64:
        return f64 + b'\x01\x44' + encode_f64(gvar.initializer) + b'\x0b'

def encode_module(module):
    # section 1 - signatures
    all_funcs = module.imported_functions + module.functions
    signatures = [encode_signature(func) for func in all_funcs]
    section1 = encode_section(1, encode_vector(signatures))

    # section 2 - Imports
    all_imports = [ encode_import_function(func) for func in module.imported_functions ]
    section2 = encode_section(2, encode_vector(all_imports))

    # section 3 - Functions
    section3 = encode_section(3, encode_vector([encode_unsigned(f.idx) for f in module.functions]))

    # section 6 - Globals
    all_globals = [ encode_global(gvar) for gvar in module.global_variables ]
    section6 = encode_section(6, encode_vector(all_globals))

    # section 7 - Exports
    all_exports = [ encode_export_function(func) for func in module.functions ]
    section7 = encode_section(7, encode_vector(all_exports))

    # section 10 - Code
    all_code = [ encode_function_code(func) for func in module.functions ]
    section10 = encode_section(10, encode_vector(all_code))

    return b''.join([b'\x00asm\x01\x00\x00\x00',
                    section1,
                    section2,
                    section3,
                    section6,
                    section7,
                    section10])

# Wasm Type names
i32 = b'\x7f'   # (32-bit int)
i64 = b'\x7e'   # (64-bit int)
f32 = b'\x7d'   # (32-bit float)
f64 = b'\x7c'   # (64-bit float)

class WasmModule:
    def __init__(self, name):
        self.name = name
        self.imported_functions = [ ]
        self.functions = [ ]
        self.global_variables = [ ]

class WasmImportedFunction:
    '''
    A function defined outside of the Wasm environment
    '''
    def __init__(self, module, envname, name, argtypes, rettypes):
        self.module = module
        self.envname = envname
        self.name = name
        self.argtypes = argtypes
        self.rettypes = rettypes
        self.idx = len(module.imported_functions)
        module.imported_functions.append(self)

class WasmFunction:
    '''
    A natively defined Wasm function
    '''
    def __init__(self, module, name, argtypes, rettypes):
        self.module = module
        self.name = name
        self.argtypes = argtypes
        self.rettypes = rettypes
        self.idx = len(module.imported_functions) + len(module.functions)
        module.functions.append(self)

        # Code generation
        self.code = b''

        # Types of local variables
        self.local_types = []

    def iconst(self, value):
        self.code += b'\x41' + encode_signed(value)

    def iadd(self):
        self.code += b'\x6a'

    def imul(self):
        self.code += b'\x6c'

    def ret(self):
        self.code += b'\x0f'

    def call(self, func):
        self.code += b'\x10' + encode_unsigned(func.idx)

    def alloca(self, type):
        idx = len(self.argtypes) + len(self.local_types)
        self.local_types.append(type)
        return idx

    def local_get(self, idx):
        self.code += b'\x20' + encode_unsigned(idx)

    def local_set(self, idx):
        self.code += b'\x21' + encode_unsigned(idx)

    def global_get(self, gvar):
        self.code += b'\x23' + encode_unsigned(gvar.idx)

    def global_set(self, gvar):
        self.code += b'\x24' + encode_unsigned(gvar.idx)

class WasmGlobalVariable:
    '''
    A natively defined Wasm global variable
    '''
    def __init__(self, module, name, type, initializer):
        self.module = module
        self.name = name
        self.type = type
        self.initializer = initializer
        self.idx = len(module.global_variables)
        module.global_variables.append(self)
```

    