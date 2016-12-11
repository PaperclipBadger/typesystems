# -*- coding: utf-8 -*-
import unittest
from .lambdacalculus import *
from .lexparse import parse

class LexParseTestCase(unittest.TestCase):
    def testVariable(self):
        self.assertEqual(parse('y'), Variable('y'))
        self.assertEqual(parse('(y)'), Variable('y'))

    def testUnicodeVariable(self):
        self.assertEqual(parse('γ'), Variable('γ'))

    def testApplication(self):
        self.assertEqual(parse('xy'), Application(Variable('x'), Variable('y')))
        self.assertEqual(
            parse('xyz'), 
            Application(
                Application(Variable('x'), Variable('y')),
                Variable('z')
            )
        )
        self.assertEqual(
            parse('x(yz)'),
            Application(
                Variable('x'),
                Application(Variable('y'), Variable('z'))
            )
        )

    def testAbstraction(self):
        self.assertEqual(parse(r'\x.y'), Abstraction('x', Variable('y')))
        self.assertEqual(parse(r'(\x.y)'), Abstraction('x', Variable('y')))
        self.assertEqual(
            parse(r'\xy.z'), 
            Abstraction('x', Abstraction('y', Variable('z')))
        )
