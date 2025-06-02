from graphviz import Digraph

class AutomataLR0:
    def __init__(self, productions, initial_symbol):
        self.productions = productions
        self.initial_symbol = initial_symbol
        self.states = []
        self.estados_id = {}
        self.transiciones = {}
        self.start_state = None
        self.final_states = []

    def build(self):
        self.startSymbolPrime = self.initial_symbol + "'"
        self.productions[self.startSymbolPrime] = [[self.initial_symbol]]
        I0 = { (self.startSymbolPrime, (self.initial_symbol,), 0) }
        I0 = self.closure(I0)

        # print("Building LR(0) automaton...", I0)

        self.states.append(I0)
        pendientes = [I0]
        self.estados_id[id(I0)] = 0
        
        # print("STATES:")
        # print(self.states)
        # print("PENDING:")
        # print(pendientes)
        # print("ESTADOS ID:")
        # print(self.estados_id)

        self.estado_aceptacion = None

        while pendientes:
            I = pendientes.pop(0)
            for item in I:
                nt, cuerpo, punto = item
                if nt == self.startSymbolPrime and punto == len(cuerpo):
                    self.estado_aceptacion = id(I)

            for simbolo_gramatical in self.get_grammar_symbols():
                # print(f"Simbolo: {simbolo_gramatical}")
                goto_result = self.goto(I, simbolo_gramatical)
                # print(f"goto_result: {goto_result} for simbolo: {simbolo_gramatical}")
                # print(f"goto_result: {goto_result}")


                if goto_result:
                    existente = self.find_state_index_by_content(goto_result)

                    if existente is None:
                        self.states.append(goto_result) 
                        nuevo_id = len(self.states) - 1  
                        self.estados_id[id(goto_result)] = nuevo_id 
                        pendientes.append(goto_result) 
                        destino_id = id(goto_result) 
                    else: 
                        destino_id = id(self.states[existente])
                    
                    self.transiciones[(id(I), simbolo_gramatical)] = destino_id

        # print("\n===== ESTADOS LR(0) =====")
        # for i, estado in enumerate(self.states):
        #     print(f"\nEstado {i}:")
        #     print(estado)

        # print("\n====== TRANSICIONES ======")
        # for (origen_id, simbolo), destino_id in self.transiciones.items():
        #     origen_num = self.estados_id.get(origen_id, '?')
        #     destino_num = self.estados_id.get(destino_id, '?')
        #     print(f"δ (q{origen_num}, '{simbolo}') → q{destino_num}")

        # print(self.estados_id)

        # print("\n====== ESTADOS ID ======")
        # print(self.estado_aceptacion)

    def closure(self, items):
        closure = set(items)

        newItems = True

        while newItems:
            newItems = False  
            items_nuevos = set()  

            for (_, cuerpo, punto) in closure:

                if punto < len(cuerpo): 
                    simbolo = cuerpo[punto]

                    if simbolo in self.productions:  
                        for produccion in self.productions[simbolo]:
                            item = (simbolo, tuple(produccion), 0)  
                            if item not in closure: 
                                items_nuevos.add(item) 

            if items_nuevos: 
                closure.update(items_nuevos)
                newItems = True

        return closure  

    def goto(self, I: set, X:str):
        nuevos_items = set()  

        for (nt, cuerpo, punto) in I:  
            if punto < len(cuerpo) and cuerpo[punto] == X:
                nuevo_item = (nt, cuerpo, punto + 1) 
                nuevos_items.add(nuevo_item)

        nuevos_items = self.closure(nuevos_items)
        return frozenset(nuevos_items)  

    def get_grammar_symbols(self):
        symbols = set()

        for non_terminal, rules in self.productions.items():
            symbols.add(non_terminal) 
            for rule in rules:
                symbols.update(rule)   

        return sorted(symbols)
    
    def find_state_index_by_content(self, new_state) -> int | None:
        return next((i for i, state in enumerate(self.states) if state == new_state), None)

    def graph(self):
        dot = Digraph(comment="Automata LR(0)")

        # Crear nodos de estados con sus items
        for i, estado in enumerate(self.states):
            label = f"I{i}:\n"
            for nt, cuerpo, punto in sorted(estado):
                antes = " ".join(cuerpo[:punto])
                despues = " ".join(cuerpo[punto:])
                label += f"{nt} → {antes} • {despues}\n"
            dot.node(f"I{i}", label=label, shape="box", fontname="Courier")
        
        # Crear flecha de estado de aceptación
        if self.estado_aceptacion:
            dot.node("ACCEPT", shape="doublecircle", style="filled", color="lightgray")
            dot.edge(f"I{self.estados_id[self.estado_aceptacion]}", "ACCEPT", label="$")


        # Crear transiciones
        for (origen_id, simbolo), destino_id in self.transiciones.items():
            origen_label = f"I{self.estados_id[origen_id]}"
            destino_label = f"I{self.estados_id[destino_id]}"
            dot.edge(origen_label, destino_label, label=simbolo)

        # Guardar y mostrar
        dot.render("AAAutmoataLR0/automata_LR0", format="png", cleanup=True)
        print("Automata LR(0) generado como 'automata_LR0.png'")