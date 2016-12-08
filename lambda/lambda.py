"""Basic compiler for lambda calculus."""
import ply.lex as lex

tokens = ('VARIABLE',)
literals = [ '(', ')', '\\', '.', '@' ]

t_VARIABLE     = r'[a-z]'

t_ignore = ' \t\r\n'

def t_error(t):
    raise Exception('Illegal character {:s}'.format(repr(t.value)))

lexer = lex.lex()

import ply.yacc as yacc
from abc import ABC, abstractmethod, abstractproperty
linesep = '\n'

def padlines(lines, pad):
    return linesep.join(pad + line for line in lines.split(linesep))

class Variable:
    def __init__(self, symbol):
        self.symbol = symbol
    def __repr__(self):
        return '<Variable {}>'.format(self.symbol)

class Abstraction:
    def __init__(self, bound_symbol, term):
        self.bound_symbol = bound_symbol
        self.term = term
    def __repr__(self):
        return '<Abstraction {} {}>'.format(self.bound_symbols, self.term)
    def __str__(self):
        return """Abstraction on {}
{}""".format(self.bound_symbol, padlines(str(self.term), '| '))

class Application:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return '<Application {} {}>'.format(self.left, self.right)
    def __str__(self):
        return """Application
{}
{}""".format(padlines(str(self.left), '| '), padlines(str(self.right), '| '))


precedence = (
    ('nonassoc', 'Abstraction'),
    ('nonassoc', '\\'),
    ('left', '('),
    ('right', ')'),
    ('left', 'VARIABLE'),
    ('left', 'Application'),
)

def p_term_variable(p):
    "term : VARIABLE"
    p[0] = Variable(p[1])

def p_term_brackets(p):
    "term : '(' term ')'"
    p[0] = p[2]

def p_term_application(p):
    "term : term term %prec Application"
    p[0] = Application(p[1], p[2])

def p_term_abstraction(p):
    "term : '\\\\' variables '.' term %prec Abstraction"
    for i in reversed(p[2]):
        p[4] = Abstraction(i, p[4])
    p[0] = p[4]

def p_variables(p):
    """variables : VARIABLE
                 | variables VARIABLE"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_error(p):
    raise Exception('Syntax error!')

parser = yacc.yacc()

while True:
    result = parser.parse(input('Write a lambda expression: '))
    print(result)

