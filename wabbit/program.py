# program.py
#
# A central problem when writing a compiler is keeping all of the parts
# organized.   One way to handle this might be to organize everything
# under a top-level "Program" object of some sort.  The program can be
# a container of everything--source code, the model, error messages,
# generated code, and so forth.
#
# This file is a bit underspecified.  You can choose to do nothing
# here if you wish.   However, you might find it convenient to do a
# bit more as the compiler evolves.


class Program:
    def __init__(self, filename):
        self.filename = filename
        self.source = None
        self.model = None
        self.have_errors = False

    def read_source(self):
        with open(self.filename) as file:
            self.source = file.read()

    def error_message(self, message):
        # Create a nice error message
        print(message)
        self.have_errors = True

    
