# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod, abstractproperty
from copy import deepcopy
from overrides import overrides

linesep = '\n'
def padlines(lines, pad):
    return linesep.join(pad + line for line in lines.split(linesep))

class NotReduceable(Exception):
    def __init__(self, term):
        super().__init__("The term{sep}{}{sep}is not reduceable."
                         .format(str(term), sep=linesep))

class LambdaTerm(ABC):
    kind = 'term'
    _fresh_name_counter = -1

    @classmethod
    def fresh_name(class_):
        count += 1
        return 'x_{:02d}'.format(count)

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

    @abstractmethod
    def __eq__(self, other):
        """True iff two terms are exactly equal."""
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
    
    def __init__(self, symbol):
        self.symbol = symbol

    @property
    @overrides
    def free_variables(self):
        return {self.symbol}

    @property
    @overrides
    def bound_variables(self):
        return set()

    @overrides
    def apply_substitution(self, sub):
        return deepcopy(sub.get(self.symbol, self))

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
            if self.symbol in sub:
                if sub[self.symbol] == other.symbol:
                    return AlphaEqResult(True, sub)
                else:
                    return AlphaEqResult(False)
            else:
                sub[self.symbol] = other.symbol
                return AlphaEqResult(True, sub)
        else:
            return AlphaEqResult(False)

    @overrides
    def apply_alpha_substitution(self, sub):
        return (Variable(sub[self.symbol]) if self.symbol in sub else
                deepcopy(self))

    @overrides
    def __eq__(self, other):
        try:
            return other.kind == self.kind and other.symbol == self.symbol
        except AttributeError:
            return False

    def __repr__(self):
        return '<Variable {}>'.format(self.symbol)

    def __str__(self):
        s = self.symbol if len(self.symbol) == 1 else '({})'.format(self.symbol)
        return s


class Abstraction(LambdaTerm):
    kind = 'abstraction'

    def __init__(self, bound_symbol, term):
        self.bound_symbol = bound_symbol
        self.term = term

        if self.free_variables & self.bound_variables:
            raise Exception("Barendregt's convention violation!")

    @property
    @overrides
    def free_variables(self):
        v = self.term.free_variables
        v.discard(self.bound_symbol)
        return v

    @property
    @overrides
    def bound_variables(self):
        v = self.term.bound_variables
        if self.bound_symbol in v:
            raise Exception("Barendregt's convention violation!")
        v.add(self.bound_symbol)
        return v

    @overrides
    def apply_substitution(self, sub):
        sub = sub.copy()
        sub.pop(self.bound_symbol, None)
        return Abstraction(self.bound_symbol, self.term._app_sub(sub))

    @property
    @overrides
    def is_redex(self):
        return self.term.is_redex

    @overrides
    def reduce(self):
        if self.term.is_redex:
            return Abstraction(self.bound_symbol, self.term.reduce())
        else:
            raise NotReduceable(self)

    def apply(self, term):
        return self.term.substitute(self.bound_symbol, term)

    @overrides
    def _alpha_eq_helper(self, other, sub):
        if other.kind == self.kind:
            if self.bound_symbol in sub:
                raise Exception("Barendregt's convention violation!")
            sub[self.bound_symbol] = other.bound_symbol
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
            sub[self.bound_symbol], 
            self.term.apply_alpha_substitution(sub)
        )

    @overrides
    def __eq__(self, other):
        try:
            return (other.kind == self.kind and
                    other.bound_symbol == self.bound_symbol and
                    other.term == self.term)
        except AttributeError:
            return False

    def __repr__(self):
        return '<Abstraction {} {}>'.format(self.bound_symbol, self.term)

    def __str__(self):
        s = '\\' + self.bound_symbol
        term = self.term
        while term.kind == self.kind:
            s += term.bound_symbol
            term = term.term
        s += '.' + str(term)
        return s

class Application(LambdaTerm):
    kind = 'application'

    def __init__(self, left, right):
        self.left = left
        self.right = right

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
                isinstance(self.left, Abstraction))

    @overrides
    def reduce(self):
        if isinstance(self.left, Abstraction):
            return self.left.apply(self.right)
        elif self.left.is_redex:
            return Application(self.left.reduce(), self.right)
        elif self.right.is_redex:
            return Application(self.left, self.right.reduce())
        else:
            raise NotReduceable(self)

    @overrides
    def _alpha_eq_helper(self, other, sub):
        res, sub = self.left._alpha_eq_helper(other.left, sub)
        if res:
            res, sub = self.right._alpha_eq_helper(other.right, sub)
            if res:
                return AlphaEqResult(True, sub)
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
        try:
            return (other.kind == self.kind and
                    other.left == self.left and other.right == self.right)
        except AttributeError:
            return False

    def __repr__(self):
        return '<Application {} {}>'.format(self.left, self.right)

    def __str__(self):
        left = ('(' + str(self.left) + ')' 
                if self.left.kind == 'abstraction' else
                str(self.left))
        right = ('(' + str(self.right) + ')' 
                 if self.right.kind in ['application', 'abstraction'] else
                 str(self.right))
        return left + right

