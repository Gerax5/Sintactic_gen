# sintactic.py – Analizador SLR(1) generado automáticamente
# *Archivo autónomo; no requiere las librerías del generador.*

import sys
from collections import deque

# ACTION: (estado, token) -> acción ('sN' / 'rM' / 'acc')
ACTION = {0: {'IDENTIFICADOR': 's1'}, 1: {'ASSIGN': 's3'}, 3: {'IDENTIFICADOR': 's4', 'NUMBER': 's5'}, 6: {'MINUS': 's8', 'PLUS': 's9', '$': 'r0'}, 8: {'IDENTIFICADOR': 's4', 'NUMBER': 's5'}, 9: {'IDENTIFICADOR': 's4', 'NUMBER': 's5'}, 2: {'$': 'acc'}, 4: {'$': 'r5', 'MINUS': 'r5', 'PLUS': 'r5'}, 5: {'$': 'r4', 'MINUS': 'r4', 'PLUS': 'r4'}, 7: {'$': 'r3', 'MINUS': 'r3', 'PLUS': 'r3'}, 10: {'$': 'r2', 'MINUS': 'r2', 'PLUS': 'r2'}, 11: {'$': 'r1', 'MINUS': 'r1', 'PLUS': 'r1'}}

# GOTO: (estado, NoTerminal) -> estado
GOTO = {0: {'operacion': 2}, 3: {'expression': 6, 'term': 7}, 8: {'term': 10}, 9: {'term': 11}}

PRODUCTIONS = {'operacion': [['IDENTIFICADOR', 'ASSIGN', 'expression']], 'expression': [['expression', 'PLUS', 'term'], ['expression', 'MINUS', 'term'], ['term']], 'term': [['NUMBER'], ['IDENTIFICADOR']], "operacion'": [['operacion']]}
START_SYMBOL = "operacion'"


def parse(token_stream):
    tokens = list(token_stream) + [('$', '$', -1)]
    stack = [0]
    i = 0
    errors = []
    producciones_numeradas = []
    for lhs, reglas in PRODUCTIONS.items():
        for regla in reglas:
            producciones_numeradas.append((lhs, regla))

    while True:
        state = stack[-1]
        tok, lex, line = tokens[i]
        act = ACTION.get(int(state), {}).get(tok)
        if act is None:
            errors.append(f"Error de sintaxis en la línea {line if line!=-1 else '?'}: token inesperado '{tok}' (lexema: '{lex}').")
            return False, errors
        if act == 'acc':
            return True, errors
        if act.startswith('s'):
            # stack.extend([tok, int(act[1:])])
            stack.append(act[1:])  # Agregar solo el estado, no el token
            i += 1
            continue
        if act.startswith('r'):
            prod = int(act[1:])
            head, blen = producciones_numeradas[prod]
            for _ in blen:
                stack.pop()
            newState = int(stack[-1])
            goto_state = GOTO[newState][head]
            if goto_state is None:
                errors.append(f"Error interno del analizador: no se encontró una transición válida (GOTO) para el símbolo {head} desde {stack[-1]}")
                return False, errors
            stack.append(goto_state)
            continue
        errors.append(f"Acción desconocida: {act}")
        return False, errors
