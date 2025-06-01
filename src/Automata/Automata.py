from src.ShuntingYard.Shunting import InfixToPostfix
from src.SintacticTree.Tree import Tree
from src.DirectDFA.DirectDFA import DirectDFA

class Create_automata():

    def __init__(self):
        self.shunting = InfixToPostfix()
        # self.directDFA = DirectDFA()
        self.ddfa = None


    def getDFA(self):
        return self.transitions


    def convertRegex(self, regex, tokens):
        # Preprocesar lets
        tree = Tree(regex)

        alphabet = tree.getAlphabet()
        
        # Esto es solo para hacer unicos los valores
        alphabet = set(alphabet)
        alphabet = list(alphabet)

        print(alphabet)

        stack = tree.getStack()

        # ddfa = DirectDFA(stack, alphabet, tokens)


        # print(len(ddfa.transitions))

        # for key, value in ddfa.transitions.items():
        #     if key == ():
        #         print("Estado inicial: ", value)

        # print(list(ddfa.transitions.keys()))


        # print(len(ddfa.transitions))

        # minidfa = GenericMiniDFA(ddfa.transitions, ddfa.acceptStates, ddfa.noAcceptStates, alphabet, 0)

        # print(minidfa.miniStates)

        # print(len(minidfa.miniStates))

        # print(alphabet)

        # print("RECONOCER")

        # algo = ddfa.recognize("# Que pedo tranza que dice")
        # algo = ddfa.recognize('"""  QUE PEDO ESTO ES UN COMENTARIO MULTILinea   """')
        # algo = ddfa.recognize("importsys")

        # print("Encontrado: ",algo)
        # eval(algo)


        self.ddfa = DirectDFA(stack, alphabet, tokens)

        # self.ddfa.recognize()

        # print(postfix)