"""Basic compiler for lambda calculus."""
import ply.lex as lex

tokens = ('VARIABLE',)
literals = [ '(', ')', '\\', '.' ]

t_VARIABLE     = r'[a-z]'

t_ignore = ' \t\r\n'

def t_error(t):
    raise Exception('Illegal character {:s}'.format(repr(t.value)))

lexer = lex.lex()

import ply.yacc as yacc

precedence = (
    ('right', 'ABSTRACTION'),
    ('left', 'APPLICATION')
)

def p_term(p):
    """term : VARIABLE
            | '(' term ')'
            | '\\\\' variables '.' term %prec ABSTRACTION
            | term term                %prec APPLICATION
    """
    pass

def p_variables(p):
    """variables : VARIABLE
                 | variables VARIABLE"""
    pass

def p_error(p):
    raise Exception('Syntax error!')

parser = yacc.yacc()

result = parser.parse(input('Write a lambda expression: '))
print(result)

