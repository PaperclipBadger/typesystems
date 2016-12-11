# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod, abstractproperty
from copy import deepcopy
from overrides import overrides

from ..utils import Finalisable

linesep = '\n'
def padlines(lines, pad):
    return linesep.join(pad + line for line in lines.split(linesep))

class NotReduceable(Exception):
    def __init__(self, term):
        super().__init__("The term{sep}{}{sep}is not reduceable."
                         .format(str(term), sep=linesep))

class BarendregtViolation(Exception):
    def __init__(self):
        super().__init__("Barendregt's convention has been violated!")

    def __call__(self):
        return self

BarendregtViolation = BarendregtViolation()

class LambdaTerm(Finalisable, metaclass=ABCMeta):
    kind = 'term'

    @property
    def variables(self):
        assert not self.free_variables & self.bound_variables
        return self.free_variables | self.bound_variables
    
    @abstractproperty
    def free_variables(self):
        NotImplemented

    @abstractproperty
    def bound_variables(self):
        NotImplemented

    def substitute(self, name, term):
        """Replaces each free occurence of ``name`` with ``term``.
        
        Args:
            name (str): The name of the variable to substitute.
            term (LambdaTerm): The term to substitute for the
                variable.
        
        """
        return self.apply_substitution({name: term})

    @abstractmethod
    def apply_substitution(self, sub):
        """Applies a substitution.

        A substitution is a partial mapping from variables to terms. 
        When a substitution is applied to a term, each free occurence 
        of a substituted variable is replaced by the substituted term.

        Args:
            sub (Dict[str, LambdaTerm]): a substitution

        """
        NotImplemented

    def _app_sub(self, *args, **kwargs):
        return self.apply_substitution(*args, **kwargs)

    @abstractproperty
    def is_redex(self):
        """Checks if the term can be reduced by beta-reduction."""
        NotImplemented

    @abstractmethod
    def reduce(self):
        """Performs 1 step of beta reduction.

        The reduction rules are applied in the following order:
            
        ..math::
            (λx.N)M \\rightarrow_β N[M/x]

            N \\rightarrow_β N' \Rightarrow NM \\rightarrow_β N'M

            N \\rightarrow_β N' \Rightarrow MN \\rightarrow_β MN'

            N \\rightarrow_β N' \Rightarrow λx.N \\rightarrow_β λx.N'

        Raises:
            NotReduceable if the term is not a redex.
            
        """
        NotImplemented

    def alpha_eq(self, other):
        """True iff two terms are alpha equivalent.
        
        Returns:
            (AlphaEqResult) If the terms are alpha equivalent, 
            returns ``True`` and a variable substitution that makes
            the first term equivalent to the second. Otherwise
            returns ``AlphaEqResult(False)``.
        
        """
        r = self._alpha_eq_helper(other, {})
        if r:
            for k, v in list(r.sub.items()):
                if k == v: del r.sub[k]
        return r

    @abstractmethod
    def _alpha_eq_helper(self, other, sub):
        NotImplemented
    
    @abstractmethod
    def apply_alpha_substitution(self, sub):
        """Renames free and bound variables."""
        NotImplemented

    def alpha_substitute(self, a, b):
        return self.apply_alpha_substitution({a: b})

    @abstractmethod
    def __eq__(self, other):
        """True iff two terms are exactly equal."""
        NotImplemented

    @abstractmethod
    def __hash__(self, other):
        NotImplemented

class AlphaEqResult:
    """Much like a ``namedtuple``, but with better booleanness."""
    def __init__(self, res, sub=None):
        self.res = res
        self.sub = sub

    def __getitem__(self, index):
        if index < 0 or index > 1:
            raise IndexError('index {} is out of bounds'.format(index))
        elif index == 0:
            return self.res
        else:
            return self.sub

    def __bool__(self):
        return self.res

class Variable(LambdaTerm):
    kind = 'variable'
    freshcounter = -1

    def __init__(self, symbol):
        assert isinstance(symbol, str)
        self.symbol = symbol
        self.finalise()

    @classmethod
    def fresh(cls):
        cls.freshcounter += 1
        return cls('x_{:02d}'.format(cls.freshcounter))

    @property
    @overrides
    def free_variables(self):
        return {self}

    @property
    @overrides
    def bound_variables(self):
        return set()

    @overrides
    def apply_substitution(self, sub):
        return sub.get(self, self)

    @property
    @overrides
    def is_redex(self):
        return False

    @overrides
    def reduce(self):
        raise NotReduceable(self)

    @overrides
    def _alpha_eq_helper(self, other, sub):
        if other.kind == self.kind:
            if self in sub:
                if sub[self] == other:
                    return AlphaEqResult(True, sub)
                else:
                    return AlphaEqResult(False)
            else:
                sub[self] = other
                return AlphaEqResult(True, sub)
        else:
            return AlphaEqResult(False)

    @overrides
    def apply_alpha_substitution(self, sub):
        return sub[self] if self in sub else self

    @overrides
    def __eq__(self, other):
        return other.kind == self.kind and other.symbol == self.symbol

    @overrides
    def __hash__(self):
        return hash(self.symbol) ^ hash(self.kind)

    def __repr__(self):
        return 'Variable({!r})'.format(self.symbol)

    def __str__(self):
        s = self.symbol if len(self.symbol) == 1 else '({})'.format(self.symbol)
        return s


class Abstraction(LambdaTerm):
    kind = 'abstraction'

    def __init__(self, binds, term):
        self.binds = Variable(binds)
        self.term = term
        self.finalise()

        if self.free_variables & self.bound_variables:
            raise BarendregtViolation 

    @property
    @overrides
    def free_variables(self):
        v = self.term.free_variables
        v.discard(self.binds)
        return v

    @property
    @overrides
    def bound_variables(self):
        v = self.term.bound_variables
        if self.binds in v:
            raise BarendregtViolation
        v.add(self.binds)
        return v

    @overrides
    def apply_substitution(self, sub):
        sub = sub.copy()
        sub.pop(self.binds, None)
        return Abstraction(self.binds.symbol, self.term._app_sub(sub))

    @property
    @overrides
    def is_redex(self):
        return self.term.is_redex

    @overrides
    def reduce(self):
        if self.term.is_redex:
            return Abstraction(self.binds.symbol, self.term.reduce())
        else:
            raise NotReduceable(self)

    def apply(self, term):
        return self.term.substitute(self.binds, term)

    @overrides
    def _alpha_eq_helper(self, other, sub):
        if other.kind == self.kind:
            if self.binds in sub:
                raise BarendregtViolation
            sub[self.binds] = other.binds
            res, sub = self.term._alpha_eq_helper(other.term, sub)
            if res:
                return AlphaEqResult(True, sub)
            else: 
                return AlphaEqResult(False)
        else:
            return AlphaEqResult(False)

    @overrides
    def apply_alpha_substitution(self, sub):
        return Abstraction(
            sub.get(self.binds, self.binds).symbol, 
            self.term.apply_alpha_substitution(sub)
        )

    @overrides
    def __eq__(self, other):
        return (other.kind == self.kind and
                other.binds == self.binds and
                other.term == self.term)

    @overrides
    def __hash__(self):
        return hash(self.binds) ^ hash(self.term) ^ hash(self.kind)

    def __repr__(self):
        return 'Abstraction({!r}, {!r})'.format(self.binds.symbol, self.term)

    def __str__(self):
        s = '\\' + str(self.binds)
        term = self.term
        while term.kind == self.kind:
            s += str(term.binds)
            term = term.term
        s += '.' + str(term)
        return s

class Application(LambdaTerm):
    kind = 'application'

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.finalise()

    @property
    @overrides
    def free_variables(self):
        v = self.left.free_variables
        v.update(self.right.free_variables)
        return v

    @property
    @overrides
    def bound_variables(self):
        v = self.left.bound_variables
        v.update(self.right.bound_variables)
        return v
    
    @overrides
    def apply_substitution(self, sub):
        return Application(self.left._app_sub(sub), self.right._app_sub(sub))

    @property
    @overrides
    def is_redex(self):
        return (self.left.is_redex or self.right.is_redex or 
                self.left.kind == 'abstraction')

    @overrides
    def reduce(self):
        if self.left.kind == 'abstraction':
            right = self.right
            conflicts = self.left.variables & self.right.variables
            for x in conflicts:
                right = right.alpha_substitute(x, Variable.fresh())
            print(self.left.bound_variables, right)
            return self.left.apply(right)
        elif self.left.is_redex:
            return Application(self.left.reduce(), self.right)
        elif self.right.is_redex:
            return Application(self.left, self.right.reduce())
        else:
            raise NotReduceable(self)

    @overrides
    def _alpha_eq_helper(self, other, sub):
        if other.kind == self.kind:
            res, sub = self.left._alpha_eq_helper(other.left, sub)
            if res:
                res, sub = self.right._alpha_eq_helper(other.right, sub)
                if res:
                    return AlphaEqResult(True, sub)
                else:
                    return AlphaEqResult(False)
            else:
                return AlphaEqResult(False)
        else:
            return AlphaEqResult(False)

    @overrides
    def apply_alpha_substitution(self, sub):
        return Application(
            self.left.apply_alpha_substitution(sub),
            self.right.apply_alpha_substitution(sub)
        )

    @overrides
    def __eq__(self, other):
        return (other.kind == self.kind and
                other.left == self.left and other.right == self.right)

    @overrides
    def __hash__(self):
        return hash(self.left) ^ hash(self.right) ^ hash(self.kind)

    def __repr__(self):
        return 'Application({!r}, {!r})'.format(self.left, self.right)

    def __str__(self):
        left = ('(' + str(self.left) + ')' 
                if self.left.kind == 'abstraction' else
                str(self.left))
        right = ('(' + str(self.right) + ')' 
                 if self.right.kind in ['application', 'abstraction'] else
                 str(self.right))
        return left + right

