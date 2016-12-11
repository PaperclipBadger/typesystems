from collections.abc import MutableMapping

class Finalisable:
    def finalise(self):
        self._mutable = False

    def __setattr__(self, name, value):
        if not hasattr(self, '_mutable') or self._mutable:
            super().__setattr__(name, value)
        else:
            raise AttributeError("LambdaTerms are immutable once instantiated.")

class Substitution(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.dict = dict(*args, **kwargs)

    # --------------------- all of this is boring ---------------------
    def __getattr__(self, name):
        return getattr(self.dict, name)

    def __contains__(self, item):
        return item in self.dict

    def __getitem__(self, name):
        return self.dict[name]

    def __setitem__(self, name, value):
        self.dict[name] = value

    def __delitem__(self, name):
        del self.dict[name]

    def __iter__(self):
        return iter(self.dict)

    def __len__(self):
        return len(self.dict)
    # -----------------------------------------------------------------

    def fromkeys(self, *args, **kwargs):
        d = self.dict.fromkeys(*args, **kwargs)
        s = self.__class__(d)
        return s

    def copy(self, *args, **kwargs):
        d = self.dict.copy(*args, **kwargs)
        s = self.__class__(d)
        return s

    def __call__(self, currytype):
        return currytype.apply_substitution(self)

    def __rshift__(self, other):
        """Use the >> operator to chain together substitutions."""
        res = {k: self(v) for k, v in other.items()}
        for k, v in self.items():
            if k not in other:
                res[k] = v
        return self.__class__(res)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.dict)
