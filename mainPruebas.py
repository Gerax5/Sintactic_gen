import sys
import argparse
import os

from src.helpers.Lex import Lexer
from src.helpers.Utils import pre_process_regex
from src.Automata.Automata import Create_automata

def generar_analizador_lexico(nombre_archivo_salida, dfa_transitions, alfabeto, acciones):
    with open(nombre_archivo_salida, 'w', encoding='utf-8') as out:
        out.write("# Analizador léxico generado automáticamente\n")
        out.write("import sys\n\n")
        out.write("# Tabla de transiciones del DFA\n")
        out.write(f"transitions = {repr(dfa_transitions)}\n\n")
        out.write(f"alphabet = {repr(list(alfabeto))}\n\n")
        out.write(f"actions = {repr(acciones)}\n\n")

        out.write(r'''
def run_lexer(input_string):
    initial_state = None
    for st, info in transitions.items():
        if info.get("initial", False):
            initial_state = st
            break
    if initial_state is None:
        raise Exception("No se encontró un estado inicial en el DFA")

    tokens_encontrados = []
    current_state = initial_state

    line_number = 1
    i = 0
    lexema_actual = ""
    longitud = len(input_string)

    replace_characters = {
        "\n": "\\n",
        "\t": "\\t",
        "\r": "\\r"
    }
    special_characters = list(replace_characters.keys())

    while i < longitud:
        c = input_string[i]
        lexema_actual += c

        if c == '\n':
            line_number += 1

        if c not in alphabet:
            if c in special_characters:
                scape = replace_characters[c]
            else:
                scape = f"\\{c}"
            if scape in alphabet:
                c = scape
            else:
                tokens_encontrados.append((f"ERROR(line {line_number})", lexema_actual))
                lexema_actual = ""
                current_state = initial_state
                i += 1
                continue

        trans_actual = transitions[current_state]["transitions"]
        if c in trans_actual:
            next_state = trans_actual[c]
            current_state = next_state
            i += 1
        else:
            if transitions[current_state]["accept"]:
                accion_info = transitions[current_state].get("action", None)
                accion = ""

                if isinstance(accion_info, dict):
                    accion = accion_info.get("action", "")
                elif isinstance(accion_info, list):
                    accion_ordenada = sorted(
                        [a for a in accion_info if isinstance(a, dict) and "priority" in a],
                        key=lambda x: x["priority"]
                    )
                    if accion_ordenada:
                        accion = accion_ordenada[0]["action"]
                elif isinstance(accion_info, str):
                    accion = accion_info

                lexema_valido = lexema_actual[:-1]

                if accion.strip():
                    tokens_encontrados.append((accion, lexema_valido))

                lexema_actual = ""
                current_state = initial_state
            else:
                tokens_encontrados.append((f"ERROR(line {line_number})", lexema_actual))
                lexema_actual = ""
                current_state = initial_state
                i += 1

    if transitions[current_state]["accept"]:
        accion_info = transitions[current_state].get("action", None)
        accion = ""

        if isinstance(accion_info, dict):
            accion = accion_info.get("action", "")
        elif isinstance(accion_info, list):
            accion_ordenada = sorted(
                [a for a in accion_info if isinstance(a, dict) and "priority" in a],
                key=lambda x: x["priority"]
            )
            if accion_ordenada:
                accion = accion_ordenada[0]["action"]
        elif isinstance(accion_info, str):
            accion = accion_info

        if accion.strip():
            tokens_encontrados.append((accion, lexema_actual))
    elif lexema_actual != "":
        tokens_encontrados.append((f"ERROR(line {line_number})", lexema_actual))

    return tokens_encontrados


if __name__ == "__main__":
    data = sys.stdin.read()
    resultado = run_lexer(data)
    for token, lexema in resultado:
        print(f"{token} -> {lexema}")
''')

    print(f"✅ Analizador léxico generado correctamente en: {nombre_archivo_salida}")


def main():
    parser = argparse.ArgumentParser(description="Generador de Analizadores Léxicos")
    parser.add_argument("yalex_file", help="Archivo de especificación YALex")
    parser.add_argument("-o", "--output", default="thelexer.py",
                        help="Nombre del archivo de salida para el analizador léxico")
    args = parser.parse_args()

    yalex_path = args.yalex_file
    out_file = args.output

    if not os.path.isfile(yalex_path):
        print(f"❌ Error: No se encontró el archivo {yalex_path}")
        sys.exit(1)

    # Leer y parsear la especificación YALex
    lex = Lexer()
    with open(yalex_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lex.indentify(lines)

    # Procesar las secciones "let"
    lex.parseLets()

    # Construir la expresión regular combinada
    regex = pre_process_regex(lex.lets)

    # Generar el DFA
    automata = Create_automata()
    automata.convertRegex(regex, lex.tokens)

    dfa_transitions = automata.ddfa.getTransitions()
    alfabeto = automata.ddfa.alphabet
    acciones = lex.tokens

    # Generar archivo Python del analizador léxico
    generar_analizador_lexico(out_file, dfa_transitions, alfabeto, acciones)


if __name__ == "__main__":
    main()
