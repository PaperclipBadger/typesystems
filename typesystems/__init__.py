# -*- coding: utf-8 -*-
from .lambdacalculus import parse
from .currytypes import UnificationError, TypeVariable
from .currytypeassignment import principal_pair

def repl():
    import re
    def subscriptify(matchobj):
        s = matchobj.group()
        r = []
        digits = "₀₁₂₃₄₅₆₇₈₉"
        for c in s[1:]:
            r.append(digits[int(c)])
        return ''.join(r)

    while True:
        TypeVariable.freshcounter = -1
        term = parse(input('>>> '))
        try:
            context, type_ = principal_pair(term)
        except UnificationError as e:
            print(e)
        else:
            type_ = str(type_).replace('->', '⟶')
            type_ = re.sub('_\d+', subscriptify, type_)
            print('Type: {}'.format(type_))
            if context:
                print('Context:')
                for k, v in context.items():
                    v_str = re.sub('_\d+', subscriptify, str(v))
                    print('  {} ↦ {}'.format(k, v_str))
            if term.is_redex:
                print('Reduction:')
                print('  {}'.format(re.sub('_\d+', subscriptify, str(term))))
                while term.is_redex:
                    term = term.reduce()
                    term_str = re.sub('_\d+', subscriptify, str(term))
                    print('  ⟶ᵦ {}'.format(term_str))
