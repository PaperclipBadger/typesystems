class Finalisable:
    def finalise(self):
        self._mutable = False

    def __setattr__(self, name, value):
        if not hasattr(self, '_mutable') or self._mutable:
            super().__setattr__(name, value)
        else:
            raise AttributeError("LambdaTerms are immutable once instantiated.")

