import unittest
from .currytypes import *

class UnifiTestCase(unittest.TestCase):
    def assertUnifiable(self, *args):
        self.assertTrue(unifiable(*args))
        s = unify(*args)
        self.assertTrue(all(s(a) == s(args[0]) for a in args))

    def assertNotUnifiable(self, *args):
        self.assertFalse(unifiable(*args))
        self.assertRaises(UnificationError, lambda: unify(*args))

    def testVariable(self):
        self.assertUnifiable(TypeVariable('a'), TypeVariable('b'))
        self.assertUnifiable(TypeVariable('a'), TypeVariable('a'))

    def testConstant(self):
        self.assertUnifiable(TypeVariable('a'), ConstantType('A'))
        self.assertUnifiable(TypeVariable('a'), ConstantType('B'))
        self.assertUnifiable(ConstantType('A'), ConstantType('A'))
        self.assertNotUnifiable(ConstantType('A'), ConstantType('B'))

    def testArrow(self):
        self.assertUnifiable(
            ArrowType(TypeVariable('a'), TypeVariable('b')),
            ArrowType(TypeVariable('c'), TypeVariable('d')),
        )
        self.assertUnifiable(
            ArrowType(TypeVariable('a'), TypeVariable('b')),
            ArrowType(TypeVariable('a'), TypeVariable('a')),
        )
        self.assertUnifiable(
            ArrowType(TypeVariable('a'), TypeVariable('b')),
            ArrowType(TypeVariable('b'), TypeVariable('a')),
        )
        self.assertUnifiable(
            TypeVariable('a'),
            ArrowType(TypeVariable('b'), TypeVariable('c'))
        )
        self.assertNotUnifiable(
            TypeVariable('a'),
            ArrowType(TypeVariable('a'), TypeVariable('c'))
        )
        self.assertUnifiable(
            ArrowType(TypeVariable('b'), TypeVariable('c')),
            TypeVariable('a')
        )
        self.assertNotUnifiable(
            ArrowType(TypeVariable('a'), TypeVariable('c')),
            TypeVariable('a')
        )

    def testManyArgs(self):
        self.assertUnifiable(*[TypeVariable(a) for a in ('a', 'b', 'c', 'd')])
        self.assertUnifiable(*[ArrowType(TypeVariable(a), TypeVariable(b))
                               for a, b in (('a','b'), ('a','c'), ('b','c'))])

