from src.helpers.Utils import leerYapar, verificar_tokens, verificar_tokens_usados_no_declarados
from src.helpers.first import First
from src.helpers.follow import Follow
from src.AutomataLR0.automata import AutomataLR0
from src.SLRParsing.SLR import SLR

from src.helpers.Lex import Lexer
from src.helpers.Utils import pre_process_regex
from src.Automata.Automata import Create_automata

import sys
    

lex = Lexer()
aut = Create_automata()

def leer_yalex(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lex.indentify(lines)

leer_yalex("data/inputs/tyal/hardYalex.yal")

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

            

            if c not in aut.ddfa.alphabet:
                if c in special_characters:
                    scape = replace_characters[c]
                else:
                    scape = f"\\{c}"
                    
                if scape in aut.ddfa.alphabet:
                    c = scape
                else:
                    break

            trans_actual = aut.ddfa.transitions[current_state]["transitions"]
            if c in trans_actual:
                if c == '\\n':
                    line_number += 1
                next_state = trans_actual[c]
                current_state = next_state

                if aut.ddfa.transitions[current_state]["accept"]:
                    accion_info = aut.ddfa.transitions[current_state].get("action", "")
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
            # tokens_encontrados.append((accion_aceptada, lexema_aceptado))
            i = posicion_aceptada
        else:
            error_char = input_string[i]
            tokens_linea_actual.append((f"ERROR(line {line_number})", error_char))
            # tokens_encontrados.append((f"ERROR(line {line_number})", error_char))
            i += 1

    if tokens_linea_actual:
        tokens_encontrados.append(tokens_linea_actual)

    return tokens_encontrados


with open("data/inputs/entradafacil.txt", "r", encoding="utf-8") as f:
    data = f.read()
resultado = run_lexer(data)

print("==== RESULTADO DEL LEXER ====")
linea = 1
for lines in resultado:
    print(f"Linea {linea}:")
    for token, lexema in lines:
        print(f"{token} -> {lexema}")
    linea += 1

# for token, lexema in resultado:
#     print(f"{token} -> {lexema}")

print("\n==== SINTACTICO ====")

tokensYalex = [t[0] for linea in resultado for t in linea] #[t[0] for t in resultado]
# tokensYalex = [t[0] for t in resultado]

print(tokensYalex)


# archivo = "./testfile2.yalp"
archivo = "./data/inputs/tyapar/easy.yalp"
tokens, producciones, initial_symbol = leerYapar(archivo)

# print(tokens)
# print(producciones)
# print(lex.tokens_definidos)

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

# if automata.estado_aceptacion:
#         if '$' not in terminales: 
#             terminales.append('$')

# slr.imprimirTablas()

print("SLR Tables:")
print(slr.goto_table)
print("\n\n")
print(slr.productions)
print("\n\n")
print(slr.primeSymbol)

print("\n\n")
skip = ["COMENTARIO", "COMENTARIO_MULTILINEA", ""]
for lines in resultado:
    print(lines)
    toParse = [t[0] for t in lines if t[0] not in skip]

    if toParse:
        print(toParse)
        slr.parse(toParse)
    print("\n\n")

# print(tokensYalex)
# slr.parse(tokensYalex)



