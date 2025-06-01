
from typing import List, Union
from collections import defaultdict

def pre_process_regex(regexs: list[tuple[str, str, int | None]]) -> str:
    if not regexs:
        return ""
    
    lets = regexs.copy()
    
    regex = ""

    for i, item in enumerate(regexs):

        if len(item) == 3:
            name, patron, priority = item
        elif len(item) == 2:
            name, patron = item
            priority = None
        else:
            continue  # o lanza error

        nuevo_patron = expand_lets(patron, lets)

        if priority is not None:
            lets[i] = (name, nuevo_patron, priority)
        else:
            lets[i] = (name, nuevo_patron)

        print("Nuevo patron: ", nuevo_patron)

        # Agrega el marcador de fin según si tiene prioridad
        if priority is not None:
            nuevo_patron += f"'#{priority}'"
        else:
            nuevo_patron += "'#'"

        # Agrega alternancia si no es el último
        if i != len(regexs) - 1:
            nuevo_patron += "|"

        regex += nuevo_patron

    return regex

# def expand_lets(value, lets: list[tuple[str, str, int | None]]):
#     for i, item in enumerate(lets):
#         # print(value)
#         if len(item) == 3:
#             key, patron, _ = item
#         elif len(item) == 2:
#             key, patron = item
        
#         value = value.replace(key, f"({patron})")

#     return value

def expand_lets(value: str, lets: list[tuple[str, str, int | None]]) -> str:
    for let in lets:
        if len(let) == 3:
            key, patron, _ = let
        else:
            key, patron = let

        i = 0
        result = ""
        in_brackets = False
        in_single_quote = False
        in_double_quote = False

        while i < len(value):
            char = value[i]

            # Control de contexto
            if char == "[":
                in_brackets = True
            elif char == "]":
                in_brackets = False
            elif char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote

            # Solo reemplazamos si no estamos dentro de un contexto literal
            if not in_brackets and not in_single_quote and not in_double_quote:
                if value[i:i+len(key)] == key:
                    # Asegurar que no estamos pegados a letras/números para evitar falsos positivos
                    prev = value[i-1] if i > 0 else ""
                    next = value[i+len(key)] if i + len(key) < len(value) else ""

                    if not prev.isalnum() and not next.isalnum():
                        result += f"({patron})"
                        i += len(key)
                        continue

            result += char
            i += 1

        value = result

    if "#" in value:
        value = value.replace("#", "\\#")

    return value

def leerArchivo(file: str) -> Union[List[str], str]:
    try:
        # script_dir = os.path.dirname(__file__)  # Directorio del script actual
        # file_path = os.path.join(script_dir, file)

        with open(file, "r", encoding="utf-8") as f:
            expresiones = f.read().split("\n")

        print(expresiones, type(expresiones))
        return expresiones
    except FileNotFoundError:
        return "El archivo no fue encontrado"
    except IOError:
        return "Error al leer el archivo"


def leerYapar(filepath: str):

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")


    tokens =set()
    producciones = defaultdict(list)
    current_non_terminal = None
    initial_symbol = None


    for line in lines:
        line = line.strip()

        if not line or line.startswith("/*") or line.startswith("//"):
            continue

        if line.startswith("%token"):
            tokens.update(line.replace("%token", "").split())
            continue

        if line.endswith(":"):
            current_non_terminal = line[:-1].strip()
            continue

        if current_non_terminal and ("|" in line or ";" in line or line):
            if ";" in line:
                line = line.replace(";", "")

            partes = [partes.strip() for partes in line.split("|")]

            for parte in partes:
                symbols = parte.split()
                if symbols:
                    if not initial_symbol:
                        initial_symbol = current_non_terminal
                    producciones[current_non_terminal].append(symbols)

    tokens = sorted(set(tokens))

    return tokens, producciones, initial_symbol


def verificar_tokens_usados_no_declarados(tokens_yapar: list[str], producciones: dict) -> list[str]:
    """
    Verifica si se están usando en las producciones tokens que no han sido declarados con %token
    ni están definidos como no terminales.

    Args:
        tokens_yalex (set): Tokens que genera el lexer (.yalex)
        tokens_yapar (list): Tokens que declara yapar con %token
        producciones (dict): Diccionario de producciones, clave = no terminal, valor = lista de listas de símbolos

    Returns:
        list: Tokens usados pero no declarados ni generados
    """
    print("Tokens declarados en YAPAR:", tokens_yapar)
    print("Producciones en YAPAR:")
    for nt, reglas in producciones.items():
        print(f"{nt}: {reglas}")
    declarados = set(tokens_yapar)
    usados = set()
    no_terminales = set(producciones.keys())

    for reglas in producciones.values():
        for produccion in reglas:
            for simbolo in produccion:
                if simbolo not in no_terminales:
                    usados.add(simbolo)

    no_declarados = usados - declarados
    return sorted(list(no_declarados))


    

def verificar_tokens(tokens_yalex: set, tokens_yapar: set) -> list:
    """
    Verifica si YAPAR tiene tokens que no están definidos en YALex.

    Args:
        tokens_yalex (set): Tokens definidos en el lexer (YALex).
        tokens_yapar (set): Tokens declarados en el parser (YAPAR).

    Returns:
        list: Lista de tokens que están en YAPAR pero no en YALex (errores).
              Si está vacía, no hay errores.
    """
    errores = tokens_yapar - tokens_yalex
    return list(errores)

