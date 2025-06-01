from collections import defaultdict

class SLR:
    def __init__(self, productions, nonTerminals , states, transitions, states_id, accStates, primeSymbol, follow, terminales):
        self.action_table = defaultdict(dict)
        self.goto_table = defaultdict(dict)
        self.states = []
        self.productions = productions
        self.nonTerminals = nonTerminals
        self.states = states
        self.transitions = transitions
        self.states_id = states_id
        self.accStates = accStates
        self.primeSymbol = primeSymbol
        self.follow = follow
        self.terminales = terminales

    def build_slr_tables(self):
        # print("\n====== TRANSICIONES ======")
        for (origen_id, simbolo), destino_id in self.transitions.items():
            # origen_num = estados_id.get(origen_id, '?')
            # destino_num = estados_id.get(destino_id, '?')
            # print(f"δ (q{origen_num}, '{simbolo}') → q{destino_num}")

            origen = self.states_id[origen_id]
            destino = self.states_id[destino_id]

            #goto
            if simbolo in self.nonTerminals:
                self.goto_table[origen][simbolo] = destino

            #action
            else: 
                # shift, caso a, A → α·aβ
                self.action_table[origen][simbolo] = f's{destino}' 
        

        
        producciones_numeradas =[]
        for lhs, reglas in self.productions.items():
            for regla in reglas: 
                producciones_numeradas.append((lhs, regla))


        for estado_idx, items in enumerate(self.states):

            for nt, cuerpo, punto in items: 
                if punto == len(cuerpo): 
                    
                    if nt == self.primeSymbol:

                        self.action_table[estado_idx]['$'] = 'acc'

                    else: 

                        for num, (lhs, rhs) in enumerate(producciones_numeradas):
                            if lhs == nt and list(cuerpo) == rhs:

                                for simbolo in self.follow[nt]:
                                    if simbolo in self.action_table[estado_idx]:
                                        print("conflicto de en action[{estado_idx}][{simbolo}] ")
                                        break
                                    else:
                                        self.action_table[estado_idx][simbolo] = f'r{num}'

    def imprimirTablas(self):
        # Encabezado
        print("\n")
        header = f"{'STATE':^6}|" + "".join(f"{t:^6}|" for t in self.terminales) + "||" + "".join(f"{nt:^6}|" for nt in self.nonTerminals)
        
        print(header)
        print("-" * len(header))

        # Filas
        all_states = sorted(set(self.action_table.keys()) | set(self.goto_table.keys()))
        for state in all_states:
            fila = f"{state:^6}|"
            for t in self.terminales:
                fila += f"{self.action_table.get(state, {}).get(t, ''):^6}|"
            fila += "||"
            for nt in self.nonTerminals:
                fila += f"{self.goto_table.get(state, {}).get(nt, ''):^6}|"
            print(fila)

    def parse(self, tokens):
        stack = [0]
        index = 0
        tokens.append('$')

        producciones_numeradas = []
        for lhs, reglas in self.productions.items():
            for regla in reglas:
                producciones_numeradas.append((lhs, regla))

        print("\n--- Inicio del Parsing ---")
        print(f"Tokens de entrada: {tokens}")

        while True:
            estado_actual = stack[-1]
            simbolo_actual = tokens[index]

            accion = self.action_table.get(estado_actual, {}).get(simbolo_actual)

            if not accion:
                print(f"Error sintáctico: no hay acción definida para estado {estado_actual} con símbolo '{simbolo_actual}'")
                return False

            print(f"---[Estado {estado_actual}] Acción: {accion} con símbolo '{simbolo_actual}'")

            if accion.startswith('s'):
                nuevo_estado = int(accion[1:])
                stack.append(nuevo_estado)
                index += 1
                print(f"→ Shift a estado {nuevo_estado}")

            elif accion.startswith('r'):
                num = int(accion[1:])
                lhs, rhs = producciones_numeradas[num]
                for _ in rhs:
                    stack.pop()
                estado_actual = stack[-1]
                goto_estado = self.goto_table[estado_actual][lhs]
                stack.append(goto_estado)
                print(f"← Reduce usando producción: {lhs} → {' '.join(rhs)}")
                print(f"→ Ir al estado {goto_estado} (goto)")

            elif accion == 'acc':
                print("Cadena aceptada por el analizador sintáctico.")
                return True

            else:
                print(f"Acción inválida: {accion}")
                return False
