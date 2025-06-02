# sintactic.py – Analizador SLR(1) generado automáticamente
import sys

ACTION = {'0:IDENTIFICADOR': 's1', '1:ASSIGN': 's3', '3:IDENTIFICADOR': 's4', '3:NUMBER': 's5', '6:MINUS': 's8', '6:PLUS': 's9', '6:$': 'r0', '8:IDENTIFICADOR': 's4', '8:NUMBER': 's5', '9:IDENTIFICADOR': 's4', '9:NUMBER': 's5', '2:$': 'acc', '4:$': 'r5', '4:PLUS': 'r5', '4:MINUS': 'r5', '5:$': 'r4', '5:PLUS': 'r4', '5:MINUS': 'r4', '7:$': 'r3', '7:MINUS': 'r3', '7:PLUS': 'r3', '10:$': 'r2', '10:MINUS': 'r2', '10:PLUS': 'r2', '11:$': 'r1', '11:MINUS': 'r1', '11:PLUS': 'r1'}

GOTO   = {'0:operacion': 2, '3:expression': 6, '3:term': 7, '8:term': 10, '9:term': 11}

PRODUCTIONS = [('operacion', 3), ('expression', 3), ('expression', 3), ('expression', 1), ('term', 1), ('term', 1), ("operacion'", 1)]
START_SYMBOL = 'operacion'


def parse(tokens):
    tokens = list(tokens) + [('$', '$', -1)]
    stack  = [0]
    idx    = 0
    errs   = []
    while True:
        state = stack[-1]
        tok, lex, line = tokens[idx]
        act = ACTION.get(f"{state}:{tok}")
        if act is None:
            errs.append(f"Error de sintaxis en línea {line}: token '{tok}' inesperado")
            return False, errs
        if act == 'acc':
            return True, errs
        if act.startswith('s'):
            stack.extend([tok, int(act[1:])])
            idx += 1
            continue
        if act.startswith('r'):
            n = int(act[1:])
            head, blen = PRODUCTIONS[n]
            for _ in range(blen * 2):
                stack.pop()
            goto_state = GOTO.get(f"{stack[-1]}:{head}")
            if goto_state is None:
                errs.append(f"Sin GOTO para {head} desde estado {stack[-1]}")
                return False, errs
            stack.extend([head, goto_state])
            continue
