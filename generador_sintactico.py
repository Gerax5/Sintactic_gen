from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Tuple

from src.helpers.Utils import (
    leerYapar,
    verificar_tokens,
    verificar_tokens_usados_no_declarados,
)
from src.helpers.first import First
from src.helpers.follow import Follow
from src.AutomataLR0.automata import AutomataLR0
from src.SLRParsing.SLR import SLR


def _compact(state: int, sym: str) -> str:
    return f"{state}:{sym}"

def _expand(key: str) -> Tuple[int, str]:
    st, sym = key.split(":", 1)
    return int(st), sym

def _flatten_tables(action_nested: dict, goto_nested: dict):
    action, goto = {}, {}
    for st, trans in action_nested.items():
        for sym, act in trans.items():
            action[(st, sym)] = act
    for st, trans in goto_nested.items():
        for sym, dst in trans.items():
            goto[(st, sym)] = dst
    return action, goto

# ---------------------------------------------------------------------------
# Generador de sintactic.py
# ---------------------------------------------------------------------------

def generar_parser(
    output_path: Path,
    action_table: dict,
    goto_table: dict,
    productions: List[Tuple[str, List[str]]],
    start_symbol: str,
):
    # 1) aplanar tablas
    action_flat = dict(action_table)
    goto_flat = dict(goto_table)

    # 2) simplificar producciones → (head, |body|)
    prods_simple = dict(productions)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("""# sintactic.py – Analizador SLR(1) generado automáticamente\n""")
        f.write("# *Archivo autónomo; no requiere las librerías del generador.*\n\n")
        f.write("import sys\nfrom collections import deque\n\n")

        f.write("# ACTION: (estado, token) -> acción ('sN' / 'rM' / 'acc')\n")
        f.write(f"ACTION = {repr(action_flat)}\n\n")
        f.write("# GOTO: (estado, NoTerminal) -> estado\n")
        f.write(f"GOTO = {repr(goto_flat)}\n\n")

        f.write(f"PRODUCTIONS = {repr(prods_simple)}\n")
        f.write(f"START_SYMBOL = {repr(start_symbol)}\n\n")

        # Algoritmo de parsing
        f.write(textwrap.dedent(
            '''
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
            '''
        ))
    print(f"Analizador sintáctico generado en {output_path}")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='Generador SLR(1)')
    ap.add_argument('yapar_file')
    ap.add_argument('-l', '--yal_file')
    ap.add_argument('-o', '--output', default='sintactic.py')
    args = ap.parse_args()

    yapar = Path(args.yapar_file)
    if not yapar.is_file():
        print('❌ No se encontró', yapar); sys.exit(1)

    # Parsear gramática
    tokens_decl, prod_dict, start = leerYapar(str(yapar))

    if args.yal_file:
        from src.helpers.Lex import Lexer
        from src.helpers.Utils import pre_process_regex
        from src.Automata.Automata import Create_automata
        lex = Lexer(); lex.indentify(Path(args.yal_file).read_text(encoding='utf-8').splitlines())
        lex.parseLets(); regex = pre_process_regex(lex.lets)
        Create_automata().convertRegex(regex, lex.tokens)  # sólo para poblar tokens_definidos
        missing = verificar_tokens(lex.tokens_definidos, set(tokens_decl))
        if missing:
            print('Tokens del parser no existen en lexer:', missing)

    if (u := verificar_tokens_usados_no_declarados(tokens_decl, prod_dict)):
        print('Tokens usados sin declarar en YAPAR:', u)

    # FIRST/FOLLOW + LR(0) + tablas SLR
    first = First(prod_dict)
    follow = Follow(prod_dict, first.first, start)
    aut = AutomataLR0(prod_dict, start); aut.build();
    try: aut.graph()
    except: pass
    slr = SLR(prod_dict, list(prod_dict.keys()), aut.states, aut.transiciones,
              aut.estados_id, aut.estado_aceptacion, aut.startSymbolPrime,
              follow.follow_set, sorted(set(tokens_decl)))
    slr.build_slr_tables()

    generar_parser(Path(args.output), slr.action_table, slr.goto_table, slr.productions, slr.primeSymbol)

if __name__ == '__main__':
    main()