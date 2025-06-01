class State():
    def __init__(self, nodeNumber, initial = False, finish = False):
        self.nodeNumber = nodeNumber
        self.initial = initial
        self.finish = finish
        self.transitions = []
        self.states = []

    def conectState(self, transition: str, state: str):
        self.transitions.append(transition)
        self.states.append(state)