from .currytypes import *
from .utils import Substitution
from .lambdacalculus.lambdacalculus import *

class Context(Substitution):
    def apply_substitution(self, sub):
        return self.__class__({k: sub(v) for k, v in self.items()})

def unify_contexts(a, b):
    s = Substitution()
    for k in a:
        if k in b:
            s = unify(s(a[k]), s(b[k])) >> s
    return s

def principal_pair(term):
    if term.kind == 'variable':
        type_ = TypeVariable.fresh()
        return Context({term: type_}), type_

    elif term.kind == 'abstraction':
        context, type_ = principal_pair(term.term)
        if term.binds in context:
            type_ = ArrowType(context(term.binds), type_)
            del context[term.binds]
            return context, type_
        else:
            return context, TypeVariable.fresh()
        
    elif term.kind == 'application':
        context_l, type_l = principal_pair(term.left)
        context_r, type_r = principal_pair(term.right)
        type_ = TypeVariable.fresh()
        s = unify(type_l, ArrowType(type_r, type_))
        s = unify_contexts(s(context_l), s(context_r)) >> s

        context_l.update(context_r)
        return s(context_l), s(type_) 
    
    else:
        raise Exception('no case found for {!r}'.format(term))
