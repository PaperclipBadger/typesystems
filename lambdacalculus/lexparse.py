"""Lexer and parser for lambda calculus."""
import ply.lex as lex
import ply.yacc as yacc

from .lambdacalculus import *

# ============================= LEXER ==================================

tokens = ('VARIABLE',)
literals = [ '(', ')', '\\', '.', '@' ]
t_VARIABLE = r'[^\W\d_]'
t_ignore = ' \t\r\n'

def t_error(t):
    raise Exception('Illegal character {:s}'.format(repr(t.value)))

lexer = lex.lex()


# ============================= PARSER =================================


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

def parse(source):
    """Parses a lambda calculus term."""
    return parser.parse(source)
