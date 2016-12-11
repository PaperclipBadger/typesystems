import unittest
from .lambdacalculus import *

S = Abstraction('x', Abstraction('y', Abstraction('z',
    Application(
        Application(Variable('x'), Variable('z')),
        Application(Variable('y'), Variable('z'))
    )
)))

K = Abstraction('x', Abstraction('y', Variable('x')))
TRUE = K
FALSE = Abstraction('x', Abstraction('y', Variable('y')))
ONE = Abstraction('f', Abstraction('x', 
    Application(Variable('f'), Variable('x'))
))
TWO = Abstraction('f', Abstraction('x', 
    Application(Variable('f'), Application(Variable('f'), Variable('x')))
))
THREE = Abstraction('f', Abstraction('x', 
    Application(Variable('f'), 
        Application(Variable('f'), 
            Application(Variable('f'), Variable('x'))
        )
    )
))
ADD = Abstraction('m', Abstraction('n', Abstraction('f', Abstraction('x',
    Application(
        Application(
            Variable('m'),
            Variable('f'),
        ),
        Application(
            Application(
                Variable('n'),
                Variable('f'),
            ),
            Variable('x')
        )
    )
))))

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
        self.assertRedex(Application(self.valid_redex, Variable('w')))
        self.assertRedex(Application(Variable('w'), self.valid_redex))

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

    def testEventual(self):
        term = Application(S, K)
        while term.is_redex:
            term = term.reduce()
        self.assertTrue(term.alpha_eq(FALSE))

        term = Application(Application(ADD, ONE), TWO)
        while term.is_redex:
            term = term.reduce()
        self.assertTrue(term.alpha_eq(THREE))

class AlphaEquivalenceTestCase(unittest.TestCase):
    def assertAlphaEq(self, t0, t1, sub):
        self.assertTrue(t0.alpha_eq(t1))
        res, sub_ = t0.alpha_eq(t1)
        self.assertTrue(res)
        sub = {Variable(k): Variable(v) for k, v in sub.items()}
        self.assertEqual(sub_, sub)

    def assertNotAlphaEq(self, t0, t1):
        self.assertFalse(t0.alpha_eq(t1))
        res, sub_ = t0.alpha_eq(t1)
        self.assertFalse(res)
        self.assertIs(sub_, None)

    def testVariable(self):
        self.assertNotAlphaEq(Variable('x'), Variable('y'))

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
        # \fx.f(e(ex)) != \fx.f(f(fx))
        self.assertNotAlphaEq(
            Abstraction('f', Abstraction('x', 
                Application(Variable('f'), Application(Variable('e'),
                    Variable('x')
                ))
            )),
            Abstraction('f', Abstraction('x', 
                Application(Variable('f'), Application(Variable('f'),
                    Variable('x')
                ))
            ))
        ) 

    def testAplication(self):
        self.assertNotAlphaEq(
            Application(Variable('w'), Variable('x')),
            Application(Variable('y'), Variable('z')),
        )
        self.assertAlphaEq(
            Application(Abstraction('x', Variable('x')), Variable('y')),
            Application(Abstraction('z', Variable('z')), Variable('y')),
            {'x': 'z'}
        )

    def testSubstitution(self):
        a = Application(Abstraction('x', Variable('y')), Variable('z'))
        b = Application(Abstraction('a', Variable('y')), Variable('z'))
        s = {'x': 'a'}
        s_ = {Variable(k): Variable(v) for k, v in s.items()}
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
