# -*- coding: utf-8 -*-
from .lambdacalculus import parse
from .currytypes import UnificationError, TypeVariable
from .currytypeassignment import principal_pair

def repl():
    while True:
        TypeVariable.freshcounter = -1
        term = parse(input('>>> '))
        try:
            context, type_ = principal_pair(term)
        except UnificationError as e:
            print(e)
        else:
            print('Type: {}'.format(type_))
            print('Context:')
            for k, v in context.items():
                print('  {} ↦ {}'.format(k, v))
            print('Reduction:')
            while term.is_redex:
                print('  {}'.format(term))
                term = term.reduce()
            print('  {}'.format(term))
