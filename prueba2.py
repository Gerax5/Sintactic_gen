from src.helpers.Utils import leerYapar, verificar_tokens, verificar_tokens_usados_no_declarados
from src.helpers.first import First
from src.helpers.follow import Follow
from src.AutomataLR0.automata import AutomataLR0
from src.SLRParsing.SLR import SLR

from src.helpers.Lex import Lexer
from src.helpers.Utils import pre_process_regex
from src.Automata.Automata import Create_automata

import sys


def processProd(prod: str):
    tokens = []
    i = 0
    while i < len(prod):

        if prod[i].islower():
            buffer = prod[i]
            i += 1
            while i < len(prod) and prod[i].islower():
                buffer += prod[i]
                i += 1
            tokens.append(buffer)

        elif prod[i].isupper():
            buffer = prod[i]
            i += 1

            while i < len(prod) and prod[i] == "'":
                buffer += prod[i]
                i += 1
            tokens.append(buffer)
        elif prod[i] == "'":

            tokens.append("'")
            i += 1
        else:
            tokens.append(prod[i])
            i += 1
    return tokens

def leerArchivo(file: str):
    transitions = {}
    inital_symbol = ""
    try:
        with open(file, "r", encoding="utf-8") as f:
            expresiones = f.read().split("\n")
            for expr in expresiones:
                expr = expr.strip()
                if not expr:
                    continue  # Saltar líneas vacías

                if "->" not in expr:
                    continue  # Saltar líneas mal formadas

                production = expr.split("->")
                left = production[0].strip()
                rights = [x.strip() for x in production[1].split("|")]

                if inital_symbol == "":
                    inital_symbol = left

                if left not in transitions:
                    transitions[left] = []

                transitions[left].extend(rights)

        # Procesar producciones con processProd
        for key, value in transitions.items():
            prod = []
            for p in value:
                prod.append(processProd(p))
            transitions[key] = prod

        print("Producciones: ", transitions)
        return inital_symbol, transitions

    except FileNotFoundError:
        return "El archivo no fue encontrado"
    except IOError:
        return "Error al leer el archivo"
    

lex = Lexer()
aut = Create_automata()

def leer_yalex(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lex.indentify(lines)

leer_yalex("data/inputs/tyal/easyYalex.yal")

lex.parseLets()

regex = pre_process_regex(lex.lets)

aut.convertRegex(regex, lex.tokens)

def run_lexer(input_string):
    initial_state = None
    for st, info in aut.ddfa.transitions.items():
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

        if c not in aut.ddfa.alphabet:
            if c in special_characters:
                scape = replace_characters[c]
            else:
                scape = f"\\{c}"
            if scape in aut.ddfa.alphabet:
                c = scape
            else:
                tokens_encontrados.append((f"ERROR(line {line_number})", lexema_actual))    
                lexema_actual = ""
                current_state = initial_state
                i += 1
                continue

        trans_actual = aut.ddfa.transitions[current_state]["transitions"]
        if c in trans_actual:
            next_state = trans_actual[c]
            current_state = next_state
            i += 1
        else:
            if aut.ddfa.transitions[current_state]["accept"]:
                accion_info = aut.ddfa.transitions[current_state].get("action", None)
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

    if aut.ddfa.transitions[current_state]["accept"]:
        accion_info = aut.ddfa.transitions[current_state].get("action", None)
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


with open("data/inputs/entradafacil.txt", "r", encoding="utf-8") as f:
    data = f.read()
resultado = run_lexer(data)
for token, lexema in resultado:
    print(f"{token} -> {lexema}")

tokensYalex = [t[0] for t in resultado]

print(tokensYalex)


archivo = "./testfile2.yalp"
tokens, producciones, initial_symbol = leerYapar(archivo)

print(tokens)
print(producciones)
print(lex.tokens_definidos)

print(verificar_tokens_usados_no_declarados(tokens, producciones)) # Verifica en el yapar tokens que no han sido declarados y fueron usados

print(verificar_tokens(lex.tokens_definidos, set(tokens))) # verifica que los tokens del yapar existan en el lexer


# archivo = "./cfg.txt"
# inital_symbol, transitions = leerArchivo(archivo)
# print("==== EXPRESIONES ====")
# print(expreision)
# print("\n==== TOKENS ====")
# print(tokens)
# print(producciones)

no_terminales = list(producciones.keys())
terminales = sorted(set(tokens))

# # print("\n==== PRODUCCIONES ====")
# # print(no_terminales, terminales)

first = First(producciones)
# # print("\n==== FIRST ====")
# # print(first.first)

follow = Follow(producciones, first.first, initial_symbol)
# # print("\n==== FOLLOW ====")
# # print(follow.follow_set)

# # algo = AutomataLR0(producciones, initial_symbol)
automata = AutomataLR0(producciones, initial_symbol)

automata.build()

automata.graph()

slr = SLR(producciones, no_terminales, automata.states, 
          automata.transiciones, automata.estados_id, automata.estado_aceptacion, 
          automata.startSymbolPrime, follow.follow_set, terminales)

slr.build_slr_tables()

if automata.estado_aceptacion:
        if '$' not in terminales: 
            terminales.append('$')

slr.imprimirTablas()


slr.parse(tokensYalex)




