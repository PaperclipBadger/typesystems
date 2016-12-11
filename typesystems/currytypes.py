# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod, abstractproperty
from collections.abc import MutableMapping  
from overrides import overrides

from .utils import Finalisable, Substitution

class UnificationError(Exception):
    def __init__(self, t1, t2):
        message = "could not unify types {} and {}".format(str(t1), str(t2))
        super().__init__(message)

class CurryType(Finalisable, metaclass=ABCMeta):
    kind = 'currytype'

    def __setattr__(self, name, value):
        if not hasattr(self, '_mutable') or self._mutable:
            super().__setattr__(name, value)
        else:
            raise AttributeError("LambdaTerms are immutable once instantiated.")

    @abstractmethod
    def __eq__(self, other):
        NotImplemented

    @abstractmethod
    def __contains__(self, other):
        NotImplemented

    @abstractmethod
    def apply_substitution(self, sub):
        NotImplemented

    def substitute(self, a, b):
        return self.apply_substitution(Substitution((a, b)))

class ArrowType(CurryType):
    kind = 'arrowtype'

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.finalise()

    @overrides
    def __eq__(self, other):
        return (other.kind == self.kind and 
                self.left == other.left and self.right == other.right)

    @overrides
    def __contains__(self, other):
        return self == other or other in self.left or other in self.right

    @overrides
    def apply_substitution(self, sub):
        left = self.left.apply_substitution(sub)
        right = self.right.apply_substitution(sub)
        return ArrowType(left, right)

    def __repr__(self):
        return 'ArrowType({!r}, {!r})'.format(self.left, self.right)

    def __str__(self):
        left = ('({})'.format(self.left) if self.left.kind == 'arrowtype'
                else self.left)
        return "{} -> {}".format(left, self.right)

class ConstantType(CurryType):
    kind = 'constanttype'

    def __init__(self, name):
        self.name = name
        self.finalise()

    @overrides
    def __eq__(self, other):
        return self.name == other.name

    @overrides
    def __contains__(self, other):
        return self == other

    @overrides
    def apply_substitution(self, sub):
        return self

    def __repr__(self):
        return 'ConstantType({!r})'.format(self.name)

    def __str__(self):
        return self.name

class TypeVariable(CurryType):
    kind = 'typevariable'
    freshcounter = -1

    def __init__(self, name):
        self.name = name
        self.finalise()

    @classmethod
    def fresh(cls):
        cls.freshcounter += 1
        return cls('φ_{:02d}'.format(cls.freshcounter))

    @overrides
    def __eq__(self, other):
        return self.kind == other.kind and self.name == other.name

    @overrides
    def __hash__(self):
        return hash(self.name) ^ hash(self.kind)

    @overrides
    def __contains__(self, other):
        return self == other

    @overrides
    def apply_substitution(self, sub):
        return sub.get(self, self)

    def __repr__(self):
        return 'TypeVariable({!r})'.format(self.name)

    def __str__(self):
        return self.name

def unify(a, b, *args):
    if args:
        s0 = unify(a, b)
        s1 = unify(s0(b), *map(s0, args))
        return s1 >> s0
    if a.kind == 'typevariable':
        if b.kind == 'typevariable' and a.name == b.name: 
            return Substitution()
        elif b.kind == 'typevariable' or a not in b: 
            return Substitution({a: b})
        else:
            raise UnificationError(a, b)
    elif b.kind == 'typevariable':
        return unify(b, a)
    elif a.kind == b.kind == 'arrowtype':
        s0 = unify(a.left, b.left)
        s1 = unify(s0(a.right), s0(b.right))
        return s0 >> s1
    elif a.kind == b.kind == 'constanttype' and a.name == b.name:
        return Substitution()
    else:
        raise UnificationError(a, b)

def unifiable(*args):
    try:
        unify(*args)
    except UnificationError:
        return False
    else:
        return True
