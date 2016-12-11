import unittest
from .lambdacalculus import *

class IsRedexTestCase(unittest.TestCase):
    valid_redex = Application(Abstraction('x', Variable('x')), Variable('y'))

    def assertRedex(self, term):
        self.assertTrue(term.is_redex)
        term.reduce()  # check this doesn't raise

    def assertNotRedex(self, term):
        self.assertFalse(term.is_redex)
        self.assertRaises(NotReduceable, term.reduce)

    def testVariable(self):
        self.assertNotRedex(Variable('x'))

    def testAbstraction(self):
        self.assertNotRedex(Abstraction('x', Variable('x')))
        self.assertRedex(Abstraction('w', self.valid_redex))

    def testApplication(self):
        self.assertNotRedex(Application(Variable('x'), Variable('y')))
        self.assertRedex(self.valid_redex)
        self.assertRedex(Application(self.valid_redex, Variable('x')))
        self.assertRedex(Application(Variable('x'), self.valid_redex))

class ReductionTestCase(unittest.TestCase):
    valid_redex = Application(Abstraction('x', 
        Application(Variable('x'), Variable('z'))
    ), Variable('y'))
    valid_redex_reduction = Application(Variable('y'), Variable('z'))
    invalid_redex = Variable('w')

    def testApplication(self):
        self.assertEqual(self.valid_redex.reduce(), self.valid_redex_reduction)

    def testContextualClosure(self):
        self.assertEqual(
            Application(self.valid_redex, self.valid_redex).reduce(),
            Application(self.valid_redex_reduction, self.valid_redex)
        )
        self.assertEqual(
            Application(self.invalid_redex, self.valid_redex).reduce(),
            Application(self.invalid_redex, self.valid_redex_reduction)
        )
        self.assertEqual(
            Abstraction('w', self.valid_redex).reduce(),
            Abstraction('w', self.valid_redex_reduction)
        )

class AlphaEquivalenceTestCase(unittest.TestCase):
    def assertAlphaEq(self, t0, t1, sub):
        self.assertTrue(t0.alpha_eq(t1))
        res, sub_ = t0.alpha_eq(t1)
        self.assertTrue(res)
        sub = dict((Variable(k), Variable(v)) for k, v in sub.items())
        self.assertEqual(sub_, sub)

    def assertNotAlphaEq(self, t0, t1):
        self.assertFalse(t0.alpha_eq(t1))
        res, sub_ = t0.alpha_eq(t1)
        self.assertFalse(res)
        self.assertIs(sub_, None)

    def testVariable(self):
        self.assertAlphaEq(Variable('x'), Variable('y'), {'x': 'y'})

    def testAbstraction(self):
        self.assertAlphaEq(
            Abstraction('x', Variable('x')),
            Abstraction('y', Variable('y')),
            {'x': 'y'}
        )
        self.assertNotAlphaEq(
            Abstraction('x', Variable('x')),
            Abstraction('x', Variable('y')),
        )

    def testAplication(self):
        self.assertAlphaEq(
            Application(Variable('w'), Variable('x')),
            Application(Variable('y'), Variable('z')),
            {'w': 'y', 'x': 'z'}
        )
        self.assertAlphaEq(
            Application(Variable('x'), Variable('y')),
            Application(Variable('y'), Variable('x')),
            {'x': 'y', 'y': 'x'}
        )
        self.assertNotAlphaEq(
            Application(Variable('x'), Variable('x')),
            Application(Variable('y'), Variable('x'))
        )
        self.assertNotAlphaEq(
            Application(Variable('x'), Variable('x')),
            Application(Variable('x'), Variable('y'))
        )

    def testSubstitution(self):
        a = Application(Abstraction('x', Variable('y')), Variable('z'))
        b = Application(Abstraction('a', Variable('b')), Variable('c'))
        s = {'x': 'a', 'y': 'b', 'z': 'c'}
        s_ = dict((Variable(k), Variable(v)) for k, v in s.items())
        self.assertAlphaEq(a, b, s)
        self.assertEqual(a.apply_alpha_substitution(s_), b)

class EqualityTestCase(unittest.TestCase):
    def testVariable(self):
        self.assertEqual(Variable('x'), Variable('x'))
        self.assertNotEqual(Variable('x'), Variable('y'))

    def testAbstraction(self):
        self.assertEqual(
            Abstraction('x', Variable('x')),
            Abstraction('x', Variable('x'))
        )
        self.assertNotEqual(
            Abstraction('x', Variable('x')),
            Abstraction('x', Variable('y'))
        )
        self.assertNotEqual(
            Abstraction('x', Variable('x')),
            Abstraction('y', Variable('x'))
        )
        self.assertNotEqual(
            Abstraction('x', Variable('x')),
            Abstraction('y', Variable('y'))
        )

    def testApplication(self):
        self.assertEqual(
            Application(Variable('x'), Variable('x')),
            Application(Variable('x'), Variable('x'))
        )
        self.assertNotEqual(
            Application(Variable('x'), Variable('x')),
            Application(Variable('x'), Variable('y'))
        )
        self.assertNotEqual(
            Application(Variable('x'), Variable('x')),
            Application(Variable('y'), Variable('x'))
        )
        self.assertNotEqual(
            Application(Variable('x'), Variable('x')),
            Application(Variable('y'), Variable('y'))
        )

class strTestCase(unittest.TestCase):
    def testVariable(self):
        self.assertEqual(str(Variable('x')), 'x')
        self.assertEqual(str(Variable('x_1')), '(x_1)')

    def testAbstraction(self):
        self.assertEqual(str(Abstraction('x', Variable('x'))), r'\x.x')
        self.assertEqual(
            str(Abstraction('x', Abstraction('y', 
                Abstraction('z', Variable('x'))
            ))), 
            r'\xyz.x'
        )

    def testApplication(self):
        self.assertEqual(str(Application(Variable('x'), Variable('y'))), 'xy')
        self.assertEqual(
            str(Application(
                Application(Variable('x'), Variable('y')),
                Variable('z')
            )), 
            'xyz'
        )
        self.assertEqual(
            str(Application(
                Variable('x'),
                Application(Variable('y'), Variable('z'))
            )), 
            'x(yz)'
        )
        self.assertEqual(
            str(Application(
                Abstraction('x', Variable('x')),
                Variable('y')
            )), 
            r'(\x.x)y'
        )
        self.assertEqual(
            str(Application(
                Variable('y'),
                Abstraction('x', Variable('x')),
            )), 
            r'y(\x.x)'
        )
