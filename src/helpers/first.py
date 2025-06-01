def isTerminal(simbolo: str, producciones: dict) -> bool:
        return simbolo not in producciones and simbolo != "ε" 

class First:

    def __init__(self, grammar: dict):
        self.grammar = grammar
        self.first = {}
        for key in grammar:
            self.calculate_first(key)

    def calculate_first(self, character: str):
        
        if character in self.first:
            return self.first[character]
        
        if isTerminal(character, self.grammar):
            return character
        
        for prod in self.grammar[character]:
            
            self.first[character] = self.first.get(character, set())
            i = 0
            while i < len(prod):
                cur_char: str = prod[i]

                if isTerminal(cur_char, self.grammar):
                    self.first[character].add(prod[i])
                    break

                self.first[character].update(self.calculate_first(cur_char))

                if "ε" not in self.first[character]:
                    break

                i += 1
        
        return self.first[character]

