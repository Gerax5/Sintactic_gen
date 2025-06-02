from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

from src.helpers.Utils import leerYapar, verificar_tokens, verificar_tokens_usados_no_declarados
from src.helpers.first import First
from src.helpers.follow import Follow
from src.AutomataLR0.automata import AutomataLR0
from src.SLRParsing.SLR import SLR

def _compact_key(state: int, symbol: str) -> str:
    return f"{state}:{symbol}"

def _expand_key(key: str) -> Tuple[int, str]:
    st, sym = key.split(":", 1)
    return int(st), sym

def _serializar_tablas(action: dict, goto: dict):
    if all(isinstance(k, int) for k in action.keys()):
        action = {(s, a): v for s, d in action.items() for a, v in d.items()}
        goto = {(s, nt): v for s, d in goto.items() for nt, v in d.items()}

    action_ser = {_compact_key(s, a): act for (s, a), act in action.items()}
    goto_ser   = {_compact_key(s, nt): dst for (s, nt), dst in goto.items()}
    return action_ser, goto_ser

def _simplify_productions(prod_list):
    simplified = []
    for prod in prod_list:
        if isinstance(prod, (tuple, list)) and len(prod) == 2:
            head, body = prod
        elif hasattr(prod, "head") and hasattr(prod, "body"):
            head, body = prod.head, prod.body
        elif isinstance(prod, str):
            if "->" in prod:
                head, rhs = prod.split("->", 1)
                head = head.strip()
                body = rhs.strip().split()
            else:
                head, body = prod.strip(), []
        else:
            raise TypeError(f"Formato de producción no reconocido: {prod}")
        if not isinstance(body, (list, tuple)):
            body = str(body).split()
        simplified.append((head, len(body)))
    return simplified

def generar_parser(out: Path, action_tbl: dict, goto_tbl: dict, prod_list, start_symbol: str):
    ACTION_SER, GOTO_SER = _serializar_tablas(action_tbl, goto_tbl)
    prods_simplified     = _simplify_productions(prod_list)

    usados = [int(v[1:]) for v in ACTION_SER.values() if v.startswith("r")]
    if usados and max(usados) >= len(prods_simplified):
        raise ValueError(f"Se requieren al menos {max(usados)+1} producciones, pero solo hay {len(prods_simplified)}")

    with out.open("w", encoding="utf-8") as f:
        f.write("# sintactic.py – Analizador SLR(1) generado automáticamente\n")
        f.write("import sys\n\n")
        f.write(f"ACTION = {repr(ACTION_SER)}\n\n")
        f.write(f"GOTO   = {repr(GOTO_SER)}\n\n")
        f.write(f"PRODUCTIONS = {repr(prods_simplified)}\n")
        f.write(f"START_SYMBOL = {repr(start_symbol)}\n\n")
        f.write(
                '''
def parse(tokens):
    tokens = list(tokens) + [('$', '$', -1)]
    stack  = [0]
    idx    = 0
    errs   = []
    while True:
        state = stack[-1]
        tok, lex, line = tokens[idx]
        act = ACTION.get(f\"{state}:{tok}\")
        if act is None:
            errs.append(f\"Error de sintaxis en línea {line}: token '{tok}' inesperado\")
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
            goto_state = GOTO.get(f\"{stack[-1]}:{head}\")
            if goto_state is None:
                errs.append(f\"Sin GOTO para {head} desde estado {stack[-1]}\")
                return False, errs
            stack.extend([head, goto_state])
            continue
''')

    print("sintactic.py generado con éxito en:", out)

def _ordenar_producciones(diccionario: dict[str, list[list[str]]]) -> list[tuple[str, list[str]]]:
    return [(head, cuerpo) for head, cuerpos in diccionario.items() for cuerpo in cuerpos]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("yapar_file")
    p.add_argument("-l", "--yal_file")
    p.add_argument("-o", "--output", default="sintactic.py")
    ns = p.parse_args()

    yapar_path = Path(ns.yapar_file)
    tokens_yap, prod_dict, start_sym = leerYapar(str(yapar_path))

    # FIRST/FOLLOW
    first  = First(prod_dict)
    follow = Follow(prod_dict, first.first, start_sym)

    # Automata + tablas
    auto = AutomataLR0(prod_dict, start_sym)
    auto.build()

    slr = SLR(prod_dict, list(prod_dict), auto.states, auto.transiciones,
              auto.estados_id, auto.estado_aceptacion, auto.startSymbolPrime,
              follow.follow_set, sorted(set(tokens_yap)))
    slr.build_slr_tables()

    productions_ordered = _ordenar_producciones(prod_dict)

    generar_parser(Path(ns.output), slr.action_table, slr.goto_table, productions_ordered, start_sym)


if __name__ == "__main__":
    main()