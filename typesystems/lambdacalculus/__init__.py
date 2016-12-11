# expose submodules
from . import *

# expose parse and repl
from .lexparse import parse

def repl():
    while True:
        term = parse(input('>>> '))
        try:
            while term.is_redex:
                term = term.reduce()
                print(term)
        except KeyboardInterrupt:
            pass
