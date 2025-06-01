from src.helpers.first import isTerminal

class Follow:

    def __init__(self, grammar, first, initial_symbol):
        self.grammar = grammar
        self.initial_symbol = initial_symbol
        self.first = first
        self.follow_set = {non_terminal: set() for non_terminal in grammar}
        self.follow_set[initial_symbol].add("$")
        self.calculate_follow()

    def calculate_follow(self):
        changed = True
        while changed:
            changed = False
            for head in self.grammar:
                for production in self.grammar[head]:
                    for i, symbol in enumerate(production):
                        if not isTerminal(symbol, self.grammar):
                           
                            beta = production[i+1:]

                            # FIRST(β) - {ε}
                            first_of_beta = self.first_of_sequence(beta)
                            before = len(self.follow_set[symbol])
                            self.follow_set[symbol].update(first_of_beta - {'ε'})

                            # Si ε ∈ FIRST(β) o no hay β, añade FOLLOW(head)
                            if 'ε' in first_of_beta or not beta:
                                self.follow_set[symbol].update(self.follow_set[head])

                            if len(self.follow_set[symbol]) > before:
                                changed = True

    def first_of_sequence(self, seq):
        result = set()
        for s in seq:
            if isTerminal(s, self.grammar):
                result.add(s)
                return result
            result.update(self.first[s] - {'ε'})
            if 'ε' not in self.first[s]:
                return result
        result.add('ε')
        return result
