from src.Models.Node import Node
from src.ShuntingYard.Shunting import InfixToPostfix 
import graphviz
import sys

class Tree():
    def __init__(self, regex):
        self.shuntingYard = InfixToPostfix()
        self.infixToPostfix(regex)
        self.stack = []
        self.operators = ['?', '+', '*']
        self.binary_operators = ['^', '|', '.']
        print(self.regex)
        self.createObjectNode()
        self.createTree()

    def getAlphabet(self):
        return self.shuntingYard.getAlphabet()

    def getStack(self):
        return self.stack

    def infixToPostfix(self, regex):
        self.regex = self.shuntingYard.infix_to_postfix(regex)


    def createTree(self):
        self.d = graphviz.Digraph(f'AASintacticTree/SintacticTree')
        cont = 0
        self.createTreeNodes(self.stack, cont)
        self.conectTreeNodes(self.stack, 0)
        self.d.render(format='png', cleanup=False)
        #self.d.view()

    def shutDownSistem(self, error):
        print(f"\033[31m{error}\033[0m")
        sys.exit(1)

    def conectTreeNodes(self, nodes, cont = 1):
        if cont == 0:
            nodes = nodes[0]
            cont+=1
        node: Node = nodes
        if node.childs != None:
            for j in node.childs:
                node2: Node = j
                self.d.edge(node.nodeNumber, self.conectTreeNodes(node2))

        return node.nodeNumber

    def createTreeNodes(self, stack, cont):
        # print(f"Contador: {cont}")
        if cont == 0:
            stack = stack[0]
        node: Node = stack
        title = "".join(node.object)
        # print(title)
        # print(node.childs)
        # print(node.)
        #print(f"{title} Title")
        node.nodeNumber = "A"+str(cont)
        #print(node.nodeNumber)
        self.d.node(node.nodeNumber, title)
        cont+=1
       # print(d)
        if node.childs != None:
            if len(node.childs) > 1:
                cont = self.createTreeNodes(node.childs[0], cont)
                cont = self.createTreeNodes(node.childs[1], cont)
            else:
                cont = self.createTreeNodes(node.childs[0], cont)
        else:
            # print(node.object)
            if node.object[0] in self.operators or node.object[0] in self.binary_operators:
                self.shutDownSistem("No es valido el operador sin caracteres")

        return cont

    def topStack(self):
        if not self.isEmpty():
            return self.stack[-1]
        else:
            return None
        
    def isEmpty(self):
        return len(self.stack) == 0

    def createObjectNode(self):
        # cont = 0
        self.stack
        for character in self.regex:
            # print(character)
            #print(f"stack: {self.stack}")
            # if "#" in character:
            #     print(character)
            
            # print(self.stack)
            if character in self.operators and self.stack != []:
                # print(character)
                #print(f"Entro:{character}")
                c = self.stack.pop()
                node = Node([character],True,[c])
                self.stack.append(node)
            elif character in self.binary_operators and self.stack != []:
                # print(character)
                if(not self.topStack()):
                    self.shutDownSistem("No esta correctamente ingresada la expresion")
                r = self.stack.pop()
                if(not self.topStack()):
                    self.shutDownSistem("No esta correctamente ingresada la expresion")
                l = self.stack.pop()
                node = Node([character], True, [l,r])
                self.stack.append(node)
            else:
                self.stack.append(Node([character], False, None))
            
            # print(f"Contador: {cont}")
            # cont+=1