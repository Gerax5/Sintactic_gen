# sintactic.py – Analizador SLR(1) generado automáticamente
# *Archivo autónomo; no requiere las librerías del generador.*

import sys
from collections import deque

# ACTION: (estado, token) -> acción ('sN' / 'rM' / 'acc')
ACTION = {(0, 'IDENTIFICADOR'): 's1', (1, 'ASSIGN'): 's3', (3, 'IDENTIFICADOR'): 's4', (3, 'NUMBER'): 's5', (6, 'MINUS'): 's8', (6, 'PLUS'): 's9', (6, '$'): 'r0', (8, 'IDENTIFICADOR'): 's4', (8, 'NUMBER'): 's5', (9, 'IDENTIFICADOR'): 's4', (9, 'NUMBER'): 's5', (2, '$'): 'acc', (4, '$'): 'r5', (4, 'MINUS'): 'r5', (4, 'PLUS'): 'r5', (5, '$'): 'r4', (5, 'MINUS'): 'r4', (5, 'PLUS'): 'r4', (7, 'PLUS'): 'r3', (7, 'MINUS'): 'r3', (7, '$'): 'r3', (10, 'PLUS'): 'r2', (10, 'MINUS'): 'r2', (10, '$'): 'r2', (11, 'PLUS'): 'r1', (11, 'MINUS'): 'r1', (11, '$'): 'r1'}

# GOTO: (estado, NoTerminal) -> estado
GOTO = {(0, 'operacion'): 2, (3, 'expression'): 6, (3, 'term'): 7, (8, 'term'): 10, (9, 'term'): 11}

PRODUCTIONS = [('o', 1), ('e', 1), ('t', 1), ('o', 1)]
START_SYMBOL = 'operacion'


def parse(token_stream):
    tokens = list(token_stream) + [('$', '$', -1)]
    stack = [0]
    i = 0
    errors = []
    while True:
        state = stack[-1]
        tok, lex, line = tokens[i]
        act = ACTION.get((state, tok))
        if act is None:
            errors.append(f"Error de sintaxis en la línea {line if line!=-1 else '?'}: se encontró '{tok}'.")
            return False, errors
        if act == 'acc':
            return True, errors
        if act.startswith('s'):
            stack.extend([tok, int(act[1:])])
            i += 1
            continue
        if act.startswith('r'):
            prod = int(act[1:])
            head, blen = PRODUCTIONS[prod]
            for _ in range(blen*2):
                stack.pop()
            goto_state = GOTO.get((stack[-1], head))
            if goto_state is None:
                errors.append(f"Sin transición GOTO para {head} desde {stack[-1]}")
                return False, errors
            stack.extend([head, goto_state])
            continue
        errors.append(f"Acción desconocida: {act}")
        return False, errors
