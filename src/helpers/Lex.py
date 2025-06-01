from typing import List, Tuple
from src.ShuntingYard.Shunting import InfixToPostfix

regex = InfixToPostfix()

class Lexer:

    def __init__(self):
        # Finals
        # rules
        self.tokens = {}
        self.tokens_definidos = set()
        # lets
        self.lets = []

        # preProcessed
        #lets
        self.preLets = []
        #rules
        self.preRules = []

    def eliminar_comentarios_multilinea(self, texto: str) -> str:
        resultado = []
        i = 0
        dentro_comentario = False
        while i < len(texto):
            if not dentro_comentario and texto[i:i+2] == '(*':
                dentro_comentario = True
                i += 2
            elif dentro_comentario and texto[i:i+2] == '*)':
                dentro_comentario = False
                i += 2
            elif dentro_comentario:
                i += 1
            else:
                resultado.append(texto[i])
                i += 1
        return ''.join(resultado)

    def eliminar_ultimo_salto(self,texto: str) -> str:
        if texto.endswith('\n'):
            return texto[:-1]
        return texto



    def indentify(self, lines: str):
        priorityRule = 0
        en_lets = True
        en_rules = False
        for line in lines:
            linea = self.eliminar_comentarios_multilinea(line)
            linea = self.eliminar_ultimo_salto(linea)
            linea = linea.strip()

            if not linea or linea.startswith("//"):
                continue 

            if linea == "\n":
                continue

            # Detectar sección de reglas
            if linea.startswith("rule "):
                en_rules = True
                en_lets = False
                continue

            if en_lets and linea.startswith("let "):
                parts = line[4:].split("=", 1)
                if len(parts) == 2:
                    nombre = parts[0].strip()
                    definicion = parts[1].strip()
                    self.preLets.append((nombre, definicion))

            elif en_rules:
                # Quitar '|' del inicio si existe
                if linea.startswith("|"):
                    linea = linea[1:].strip()

                # Buscar llaves para separar patrón y acción
                if "{" in linea and "}" in linea:
                    inicio_accion = linea.find("{")
                    fin_accion = linea.rfind("}")
                    patron = linea[:inicio_accion].strip()
                    accion = linea[inicio_accion + 1:fin_accion].strip()

                    self.preRules.append((patron, accion, priorityRule))
                    self.tokens[priorityRule] = accion
                    self.tokens_definidos.add(accion.strip())
                    priorityRule += 1

    def parseLets(self):
        nombres_let_existentes = {nombre for nombre, *_ in self.preLets}

        # Primero, añadir todos los lets originales, agregando prioridad si existe
        prioridades = {nombre: prioridad for nombre, _, prioridad in self.preRules}

        for let in self.preLets:
            nombre = let[0]
            definicion = let[1]
            if nombre in prioridades:
                self.lets.append((nombre, definicion, prioridades[nombre]))
            else:
                self.lets.append(let)

        # Luego, agregar las reglas que no estaban en lets
        for nombre, _, prioridad in self.preRules:
            if nombre not in nombres_let_existentes:
                # Agregar como nuevo let: nombre = nombre
                # if nombre.startswith("'") and nombre.endswith("'"):
                #     definicion = nombre[1:-1] 
                # else:
                #     definicion = nombre 
                # print(f"Nombre: {nombre}")
                # definicion = nombre
                # if nombre in self.OPERATORS:
                #     print("Es un operador")
                #     definicion = f"\\{nombre}"
                print("Nombre: ", nombre)
                self.lets.append((nombre, nombre, prioridad))
        

   


