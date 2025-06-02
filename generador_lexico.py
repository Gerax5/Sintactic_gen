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
    tokens_linea_actual = []
    line_number = 1
    i = 0
    longitud = len(input_string)

    replace_characters = {
        "\n": "\\n",
        "\t": "\\t",
        "\r": "\\r",
        " ": " "
    }
    special_characters = list(replace_characters.keys())

    while i < longitud:
        while i < longitud and input_string[i].isspace():
            if input_string[i] == '\n':
                line_number += 1
                if tokens_linea_actual:
                    tokens_encontrados.append(tokens_linea_actual)
                    tokens_linea_actual = []
            i += 1
        
        if i >= longitud:
            break


        current_state = initial_state
        lexema_actual = ""
        accion_aceptada = None
        lexema_aceptado = ""
        posicion_aceptada = -1

        j = i
        while j < longitud:
            c = input_string[j]
            lexema_actual += c

            

            if c not in alphabet:
                if c in special_characters:
                    scape = replace_characters[c]
                else:
                    scape = f"\\{c}"
                    
                if scape in alphabet:
                    c = scape
                else:
                    break

            trans_actual = transitions[current_state]["transitions"]
            if c in trans_actual:
                if c == '\\n':
                    line_number += 1
                next_state = trans_actual[c]
                current_state = next_state

                if transitions[current_state]["accept"]:
                    accion_info = transitions[current_state].get("action", "")
                    if isinstance(accion_info, dict):
                        accion_aceptada = accion_info.get("action", "")
                    elif isinstance(accion_info, str):
                        accion_aceptada = accion_info
                    lexema_aceptado = lexema_actual
                    posicion_aceptada = j + 1
                j += 1
            else:
                break

        if accion_aceptada and accion_aceptada.strip():
            tokens_linea_actual.append((accion_aceptada, lexema_aceptado))
            i = posicion_aceptada
        else:
            error_char = input_string[i]
            tokens_linea_actual.append((f"ERROR(line {line_number})", error_char))
            i += 1
                  
    if tokens_linea_actual:
        tokens_encontrados.append(tokens_linea_actual)

    return tokens_encontrados



if __name__ == "__main__":
    data = sys.stdin.read()
    resultado = run_lexer(data)
    for token, lexema in resultado:
        print(f"{token} -> {lexema}")
''')

    print(f"Analizador léxico generado en: {nombre_archivo_salida}")


def main():
    parser = argparse.ArgumentParser(description="Generador de Analizadores Léxicos")
    parser.add_argument("yalex_file", help="Archivo de especificación YALex")
    parser.add_argument("-o", "--output", default="thelexer.py",
                        help="Nombre del archivo de salida para el analizador léxico")
    args = parser.parse_args()

    yalex_path = args.yalex_file
    out_file = args.output

    if not os.path.isfile(yalex_path):
        print(f"Error: No se encontró el archivo {yalex_path}")
        sys.exit(1)

    # 1. Leer y parsear YALex
    lex = Lexer()
    with open(yalex_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lex.indentify(lines)

    # 2. Procesar "let"
    lex.parseLets()

    # 3. Construir expresión regular
    regex = pre_process_regex(lex.lets)

    # 4. Construir DFA
    automata = Create_automata()
    automata.convertRegex(regex, lex.tokens)

    dfa_transitions = automata.ddfa.getTransitions()
    alfabeto = automata.ddfa.alphabet
    acciones = lex.tokens

    # 5. Generar analizador léxico con run_lexer
    generar_analizador_lexico(out_file, dfa_transitions, alfabeto, acciones)


if __name__ == "__main__":
    main()
