from src.Models.Node import Node
from graphviz import Digraph

class DirectDFA:
    OPERATORS = ["*"]
    BINARY_OPERATORS = ["^", "|", "."]

    def __init__(self, stack: list[Node], alphabet: list[str], tokens: set, fileNumber = 0):
        # Initialize the variables
        self.fileNumber = fileNumber
        self.alphabet = alphabet
        self.actions = tokens
        self.currentLeafNumber = 0

        self.acceptStates = []
        self.noAcceptStates = []

        # Initialize the tree
        self.leaves = {}
        seed = stack[0]
        self.enumerateLeaves(seed)
        self.setNullable(seed)
        self.setFirstPosition(seed)
        self.setLastPosition(seed)
        self.setFollowPosition(seed)

        # make the transition table
        self.transitions = {}
        self.stateNumber = 0
        self.generateTransitionTable(seed)
        self.setAcceptStates()
        self.limpiar_estado_vacio()

        # for key in self.transitions:
        #     print(key, self.transitions[key])

        # Create the graph
        self.createGraph()

    def enumerateLeaves(self, node: Node):
        if node.getIsOperator():
            object = "".join(node.getObject())
            if object in self.BINARY_OPERATORS: 
                self.enumerateLeaves(node.getChilds()[0])
                self.enumerateLeaves(node.getChilds()[1])
            else:
                self.enumerateLeaves(node.getChilds()[0])
        else:
            leaf = "".join(node.getObject())
            if leaf != "ε":
                node.leafNumber = self.currentLeafNumber
                self.currentLeafNumber += 1
                if leaf == "#":
                    self.leaves.setdefault(leaf, []).append(node.leafNumber)
                else:
                    if "#" in leaf:
                        if not "\\" in leaf:
                            self.leaves[leaf] = node.leafNumber
                        else:
                            self.leaves[node.leafNumber] = {
                                "letter": leaf,
                                "followPosition": set()
                            }
                    else:
                        self.leaves[node.leafNumber] = {
                            "letter": leaf,
                            "followPosition": set()
                        }

            # print(node.getObject(), node.leafNumber)

    def setNullable(self, node: Node):
        if node.getIsOperator():
            object = "".join(node.getObject())
            if object in self.BINARY_OPERATORS:
                self.setNullable(node.getChilds()[0])
                self.setNullable(node.getChilds()[1])
                if object == "|":
                    node.nullable = node.getChilds()[0].nullable or node.getChilds()[1].nullable
                elif object == ".":
                    node.nullable = node.getChilds()[0].nullable and node.getChilds()[1].nullable
            elif object in self.OPERATORS:
                self.setNullable(node.getChilds()[0])
                node.nullable = True
        else:
            if "".join(node.getObject()) == "ε":
                node.nullable = True
            else:
                node.nullable = False

        # print("Nullable", node.getObject(), node.nullable, node.leafNumber)

    def setFirstPosition(self, node: Node):
        if node.getIsOperator():
            object = "".join(node.getObject())
            if object in self.BINARY_OPERATORS:
                self.setFirstPosition(node.getChilds()[0])
                self.setFirstPosition(node.getChilds()[1])
                if object == "|":
                    node.firstPosition = node.getChilds()[0].firstPosition.union(node.getChilds()[1].firstPosition)
                elif object == ".":
                    if node.getChilds()[0].nullable:
                        node.firstPosition = node.getChilds()[0].firstPosition.union(node.getChilds()[1].firstPosition)
                    else:
                        node.firstPosition = node.getChilds()[0].firstPosition
            elif object in self.OPERATORS:
                self.setFirstPosition(node.getChilds()[0])
                node.firstPosition = node.getChilds()[0].firstPosition
        else:
            if "".join(node.getObject()) == "ε":
                node.firstPosition = set()
            else:
                node.firstPosition = {node.leafNumber}

        # print("first", node.getObject(), node.firstPosition ,node.nullable, node.leafNumber)

    def setLastPosition(self, node: Node):
        if node.getIsOperator():
            object = "".join(node.getObject())
            if object in self.BINARY_OPERATORS:
                self.setLastPosition(node.getChilds()[0])
                self.setLastPosition(node.getChilds()[1])
                if object == "|":
                    node.lastPosition = node.getChilds()[0].lastPosition.union(node.getChilds()[1].lastPosition)
                elif object == ".":
                    if node.getChilds()[1].nullable:
                        node.lastPosition = node.getChilds()[0].lastPosition.union(node.getChilds()[1].lastPosition)
                    else:
                        node.lastPosition = node.getChilds()[1].lastPosition
            elif object in self.OPERATORS:
                self.setLastPosition(node.getChilds()[0])
                node.lastPosition = node.getChilds()[0].lastPosition
        else:
            if "".join(node.getObject()) == "ε":
                node.lastPosition = set()
            else:
                node.lastPosition = {node.leafNumber}


        # print("last", node.getObject(), node.firstPosition, node.lastPosition,node.nullable, node.leafNumber)

    def setFollowPosition(self, node: Node):
        if node.getIsOperator():
            object = "".join(node.getObject())
            if object in self.BINARY_OPERATORS:
                self.setFollowPosition(node.getChilds()[0])
                self.setFollowPosition(node.getChilds()[1])
                if object == ".":
                    for i in node.getChilds()[0].lastPosition:
                        if i in self.leaves:
                            self.leaves[i]["followPosition"] = self.leaves[i]["followPosition"].union(node.getChilds()[1].firstPosition)
                        # self.leaves[i]["followPosition"] =  self.leaves[i]["followPosition"].union(node.getChilds()[1].firstPosition)
            elif object in self.OPERATORS:
                self.setFollowPosition(node.getChilds()[0])
                for i in node.getChilds()[0].lastPosition:
                    self.leaves[i]["followPosition"] = self.leaves[i]["followPosition"].union(node.firstPosition)


        # print("follow", node.getObject(), node.firstPosition, node.lastPosition, node.nullable, node.leafNumber)

    def getStateName(self):
        state = f"S{self.stateNumber}"
        self.stateNumber += 1
        return state

    def generateTransitionTable(self, seed: Node):
        firstState = tuple(seed.firstPosition)
        self.transitions[firstState] = {
            "name": self.getStateName(),
            "state": firstState,
            "initial": True,
            "accept": False,
            "transitions": {}
        }

        stack = [firstState]

        while len(stack) > 0:
            currentState = stack.pop()
            transitions = self.transitions[currentState]["transitions"]
            for letter in self.alphabet:
                nextState = set()
                for i in currentState:
                    if i in self.leaves:
                        if letter in self.leaves[i]["letter"]:
                            nextState = nextState.union(self.leaves[i]["followPosition"])
                nextState = tuple(nextState)
                if nextState not in self.transitions:
                    self.transitions[nextState] = {
                        "name": self.getStateName(),
                        "state": nextState,
                        "accept": False,
                        "transitions": {}
                    }
                    stack.append(nextState)
                transitions[letter] = self.transitions[nextState]["state"]

        # for i in self.transitions:
        #     print(self.transitions[i])

    def setAcceptStates(self):
        for i in self.transitions:
            state = self.transitions[i]
            acciones_candidatas = []

            for j in state["state"]:
                for hoja in self.leaves:
                    valor = self.leaves[hoja]

                    if isinstance(valor, int):
                        posiciones = [valor]
                    elif isinstance(valor, list):
                        posiciones = valor
                    else:
                        continue

                    if j in posiciones:
                        if isinstance(hoja, str) and hoja.startswith("#"):
                            state["accept"] = True
                            if len(hoja) > 1 and hoja[1:].isdigit():
                                accion_index = int(hoja[1:])
                                if accion_index in self.actions:
                                    nueva_accion = {
                                        "action": self.actions[accion_index],
                                        "priority": accion_index
                                    }
                                    acciones_candidatas.append(nueva_accion)
                        break

            if acciones_candidatas:
                accion_prioritaria = min(acciones_candidatas, key=lambda x: x["priority"])
                state["action"] = accion_prioritaria



    def limpiar_estado_vacio(self):
        # 1. Eliminar el estado vacío
        if () in self.transitions:
            del self.transitions[()]

        # 2. Eliminar transiciones a ese estado
        for state in self.transitions.values():
            trans = state.get("transitions", {})
            trans_clean = {k: v for k, v in trans.items() if v != ()}
            state["transitions"] = trans_clean

    def getInitialState(self):
        for i in self.transitions:
            if self.transitions[i]["initial"]:
                return self.transitions[i]["state"]
            
    def createGraph(self):
        self.diagram = Digraph()
        self.diagram.node("start", "inicio", shape='point', width='0')

        for state in self.transitions:
            if state != ():
                if self.transitions[state]["accept"]:
                    self.acceptStates.append(state)
                    self.diagram.node(self.transitions[state]["name"], self.transitions[state]["name"], shape='doublecircle')
                else:
                    self.noAcceptStates.append(state)
                    self.diagram.node(self.transitions[state]["name"], self.transitions[state]["name"], shape='circle')

        for state in self.transitions:
            if state != ():
                for letter in self.alphabet:
                    if letter in self.transitions[state]["transitions"]:
                        nextState = self.transitions[state]["transitions"][letter]
                        if nextState != ():
                            self.diagram.edge(self.transitions[state]["name"], self.transitions[nextState]["name"], label=letter)

        self.diagram.edge("start",self.transitions[self.getInitialState()]["name"])

        self.diagram.render(f'AAImageAutomataDirectDFA/DirectDFA{self.fileNumber}', format='png', cleanup=False)

    def getTransitions(self):
        return self.transitions

    def recognize(self, string: str):
        print(f"\033[32mExpresion a evaluar en DFA con construccion directa : {string}\033[0m")
        currentState = self.getInitialState()
        print(f"\033[32mEstado inicial: {self.transitions[currentState]['name']}\033[0m")
        for letter in string:
            if letter not in self.alphabet:
                print(letter)
                if f"\\{letter}" in self.alphabet:
                    currentState = self.transitions[currentState]["transitions"][f"\\{letter}"]
                    print(f"\033[32mEstado actual: {self.transitions[currentState]['name']}\033[0m")
                else:
                    print(f"\033[31mLa letra {letter} no esta en el alfabeto\033[0m")
                    return "Caracter no valido"
            else:
                currentState = self.transitions[currentState]["transitions"][letter]
                print(f"\033[32mEstado actual: {self.transitions[currentState]['name']}\033[0m")

        if self.transitions[currentState]["accept"]:
            acciones = self.transitions[currentState]["action"]

            if isinstance(acciones, list):
                # Si todas las acciones son diccionarios con clave "priority"
                if all(isinstance(a, dict) and "priority" in a for a in acciones):
                    # Elegir la de mayor peso (menor número de prioridad)
                    accion_prioritaria = min(acciones, key=lambda x: x["priority"])
                    return accion_prioritaria["action"]
                else:
                    # Si no tienen prioridad (solo tienen 'action')
                    return acciones[0]["action"]
            else:
                return acciones["action"] if isinstance(acciones, dict) else acciones
        else:
            return "token no reconocido"
            
    

        
        
