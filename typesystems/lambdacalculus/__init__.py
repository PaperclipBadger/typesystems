# expose submodules
from . import *

# expose parse and repl
from .lexparse import parse

def repl():
    import string
    while True:
        lambdacalculus.Variable.freshcounter = -1
        lambdacalculus.Variable.freshletters = set(string.ascii_lowercase)
        term = parse(input('>>> '))
        try:
            while term.is_redex:
                term = term.reduce()
                print(term)
        except KeyboardInterrupt:
            pass
