import unittest
from .lambdacalculus.lambdacalculus import *
from .currytypes import *
from .currytypeassignment import *

M = Abstraction('x', 
    Application(
        Variable('f'),
        Application(
            Variable('x'),
            Variable('x')
        )
    )
)

Y = Abstraction('f', Application(M, M))

del M

class PrincipalPairTestCase(unittest.TestCase):
    def assertHasType(self, term, type_):
        _, type__ = principal_pair(term)
        self.assertTrue(unifiable(type_, type__))

    def assertCannotType(self, term):
        self.assertRaises(UnificationError, lambda: principal_pair(term))

    def testVariable(self):
        self.assertHasType(Variable('x'), TypeVariable('a'))

    def testAbstraction(self):
        self.assertHasType(
            Abstraction('x', Variable('x')), 
            ArrowType(TypeVariable('a'), TypeVariable('a'))
        )
        self.assertHasType(
            Abstraction('x', Variable('y')), 
            ArrowType(TypeVariable('a'), TypeVariable('a'))
        )
        self.assertHasType(
            Abstraction('x', Variable('y')), 
            ArrowType(TypeVariable('a'), TypeVariable('b'))
        )

    def testApplication(self):
        self.assertHasType(
            Application(Variable('a'), Variable('b')),
            TypeVariable('a')
        )
        self.assertHasType(
            Application(
                Abstraction('a', Variable('a')),
                Variable('b')
            ),
            TypeVariable('a')
        )
        self.assertHasType(
            Application(
                Abstraction('a', Abstraction('b', Variable('a'))),
                Variable('d')
            ),
            TypeVariable('a')
        )
        self.assertHasType(
            Application(
                Abstraction('a', Abstraction('b', Variable('a'))),
                Variable('d')
            ),
            ArrowType(TypeVariable('a'), TypeVariable('b'))
        )
        self.assertHasType(
            Application(
                Abstraction('a', Variable('a')),
                Abstraction('a', Variable('a'))
            ),
            ArrowType(
                ArrowType(TypeVariable('a'), TypeVariable('a')),
                ArrowType(TypeVariable('a'), TypeVariable('a'))
            )
        )

        self.assertCannotType(Application(Variable('a'), Variable('a')))
        self.assertCannotType(Y)

