#Muy mal optimizado hay varios fors que puedo hacer con un while, basicamente pierdo milisegundos pero de que sirve sirve jeje
import sys
class InfixToPostfix():

    def shutDownSistem(self, error):
        print(f"\033[31m{error}\033[0m")
        sys.exit(1)
    
    def get_precedence(self, c):
        precedence = {
            '(': 1,
            '|': 2,
            '.': 3,
            '?': 4,
            '*': 4,
            '+': 4,
            '^': 5
        }
        return precedence.get(c,6)

    def getAlphabet(self):
        return self.alphabet

    def format_reg_ex(self, regex):
        self.AllRight = True
        all_operators = ['|', '?', '+', '*', '^']
        other_operators = ['(', ')', '[', ']', '{', '}','.']
        binary_operators = ['^', '|']
        res = []
        self.alphabet = []
        
        length = len(regex)
        i = 0
        while i < length:
            c1 = regex[i]
            
            # Caracteres escapados
            if c1 == '\\':  
                if i + 1 < length:
                    isSpace = f"\\{regex[i + 1]}"
                    #print(r"\\n")
                    #if(isSpace == "\\n"):
                        #print("a")
                    res.append(f"\\{regex[i + 1]}")
                    self.alphabet.append(f"\\{regex[i + 1]}")
                    if i + 2 < len(regex):
                        if(regex[i + 2] not in ")]" and regex[i + 2] not in binary_operators and regex[i + 2] not in all_operators):
                            res.append(".")
                    i += 1  

            # Caracteres que vienen con ' ' o " ", por ejemplo '-'        
            elif c1 == "'":
                if i + 1 < length:
                    for j in range(i + 1, length):
                        if regex[j] == "'":
                            break

                    if res[-1] != "." and "#" in regex[i+1:j] and not "\\" in regex[i+1:j]:
                        res.append(".")
                    
                    caracter = regex[i + 1:j]
                    if caracter in all_operators or caracter in other_operators:
                        caracter = f"\\{caracter}"
                    res.append(caracter)



                    print(f"Esto es caracter {caracter}", "#" in caracter)
                    print(f"chi {caracter}", not "\\" in caracter)
                    
                    if not "#" in caracter:
                        self.alphabet.append(caracter)
                    else:
                        if "\\" in caracter:
                            self.alphabet.append(caracter)
                    if j + 1 < length:
                        if regex[j + 1] not in ")]" and regex[j + 1] not in binary_operators and regex[j + 1] not in all_operators:
                            res.append(".")
                    i = j

            # Parseo del +
            elif c1 == "+":
                tempRegex = ["*"]
                tempRegex.append(")")  
                flag = True
                
                openCount = 0
                closeCount = 0
                
                for c in range(1, len(res)+1):
                    currentChar = res[-c]

                    if currentChar == ")":
                        closeCount += 1
                    elif currentChar == "(":
                        openCount += 1

                    if flag:
                        tempRegex.append(currentChar)
                        
                    if openCount == closeCount and openCount > 0:   
                        flag = False
                
                tempRegex.append("(")
                tempRegex.append(".")
                tempRegex.reverse()

                if i + 1  < length:
                    if regex[i+1] not in ")]":
                        tempRegex.append(".")
                for c in tempRegex:
                    res.append(c)
                
            # Parseo del ?
            elif c1 == "?":
                tempRegex = ["|","ε",")"]

                if regex[i - 1] in ")]":
                    flag = True
                    pos = 0

                    openCount = 0
                    closeCount = 0

                    for c in range(1, len(res)+1):
                        current_char = res[-c]

                        if current_char == ')':
                            closeCount += 1
                        elif current_char == '(':
                            openCount += 1

                        if flag:
                            pos = -c

                        if openCount == closeCount and openCount > 0:
                            flag = False                 
                    
                    res.insert(pos, "(")
                else:
                    res.insert(-1, "(")

                if i + 1 < length:
                    if regex[i+1] not in ")]":
                        tempRegex.append(".")

                for c in tempRegex:
                    res.append(c)

            # Si no es ninguno puede ser un or de esta forma [a-z] o [a-z0-9] o simplemente un caracter  
            else:
            
                if i + 1 < length:
                    # Si es un or de la forma [a-z] o ['a'-'z']
                    # Entrada: [a-z] o ['a'-'z']
                    # salida: (a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)
                    if (regex[i] in "[" ):
                        j = i
                        # Empezando la respuesta
                        # ignorar todas las variables asignadas y que no se usan porque solo me servian para debbugear
                        res.append("(")
                        while regex[j+1] != "]":
                            b = regex[j + 1]
                            # Si el caracter es 'a', le lo que hay en medio de los dos ' ', por ejemplo
                            # Entrada: '\n'
                            # Salida: \n
                            if regex[j+1] == "'":
                                for k in range(j+2, length):
                                    if regex[k] == "'":
                                        break
                                    # res.append(regex[k])
                                    # self.alphabet.append(regex[k])
                                d = regex[k-1]
                                c = regex[j+2]
                                # Lo agrega a la respuesta y lo agrega al alfabeto
                                caracter = regex[j+2:k]
                                if caracter in all_operators or caracter in other_operators:
                                    caracter = f"\\{caracter}"
                                res.append(caracter)   
                                self.alphabet.append(caracter)
                                j = k
                                a = regex[j + 1]
                                # Si no ha llegado al finl, agrega un or ejemplo ['\n''\t'], arriba se leyo '\n' y ahora se leera '\t' por lo que se tiene que agregar |
                                if regex[j + 1] != "]":
                                    res.append("|")
                            
                            # Si existe un simbolo '-' significa que son todos los valores entre dos caracteres
                            elif regex[j+1] == "-":
                                # leo el primer caracter ya reconocido en la parte de arriba
                                f1 = res[-2]
                                # leo el segundo caracter a donde quiero llegar
                                f2 = regex[j+3]
                                # Creo una lista para que no agregue mas | si ya va a llegar al final
                                rango = list(range(ord(f1)+1, ord(f2)+1))
                                for i, k in enumerate(rango):
                                    res.append(chr(k))
                                    self.alphabet.append(chr(k))
                                    if i != len(rango) - 1:
                                        res.append("|")
                                j = j + 4
                                a = regex[j + 1]
                                # Si aun no termina sigue por ejemplo [a-z0-9]
                                if regex[j + 1] != "]":
                                    res.append("|")
                            else:
                                # Si no es un simbolo '-' ni un simbolo "'" es un caracter normal
                                res.append(regex[j+1])
                                self.alphabet.append(regex[j+1])
                                j += 1
                                a = regex[j + 2]
                                if regex[j + 2] != "]":
                                    res.append("|")
                            
                        res.append(")")
                            
                        i = j + 1
                    else:
                        if(regex[i] == "."):
                            c1 = "\\"+c1
                        c2 = regex[i + 1]
                        res.append(c1)
                        if c1 not in all_operators and c1 not in binary_operators and c1 not in '([' and c1 not in ')]':
                            self.alphabet.append(c1)
                    
                    if (
                        c1 not in '([' and
                        c2 not in ')]' and
                        c2 not in all_operators and
                        c1 not in binary_operators 
                    ):
                        if res and res[-1] != ".":
                            res.append('.')

                    if (c1 in ")" and c2 in "("):
                        if res and res[-1] != ".":
                            res.append('.')

                    
                    
                        
                else:
                    if (c1 == "#"):
                        if (res[-1] != "."):
                            res.append(".")
                        res.append(c1)
                    else:
                        res.append(c1)

                    if c1 not in all_operators and c1 not in binary_operators and c1 not in '([' and c1 not in ")]":
                        if c1 != "#" and c1 != ".":
                            self.alphabet.append(c1)
                    #self.alphabet.append(c1)
            
            i += 1
        ##print("".join(res))
    
        return res

    def isBalance(self, regex):
        stack = []
        i = 0
        algo = ""
        for char in regex:
            if char == "(":
                stack.append(char)
                if(i+1 < len(regex)):
                    if regex[i+1] == ")":
                        self.error = "No es valido parentesis vacios"
                        return False
            elif char == ")":
                if stack and stack[-1] == "(":
                    stack.pop()
                else:
                    return False
            
            i+= 1

        return len(stack) == 0


    def infix_to_postfix(self, regex):
        postfix = []
        stack = []
        
        self.error = ""

        if(not self.isBalance(regex)):
            error = "Esta mal Balanceada la expresion"
            if (self.error):
                error = self.error
            self.shutDownSistem(error)
        
        regex = f"({regex})#"

        postformat = self.format_reg_ex(regex)

        print("".join(postformat))

        for c in postformat:
            if c == '(':
                stack.append(c)
                #print(f"Encountered '(': Stack: {stack}")
            elif c == ')':
                while stack and stack[-1] != '(':
                    postfix.append(stack.pop())
                    ##print(f"Encountered ')': Popped from Stack to Postfix: {''.join(postfix)}, Stack: {stack}")
                if stack:
                    stack.pop() 
                #print(f"Discarded '(': Stack: {stack}")
            else:
                while (stack and stack[-1] != '(' and 
                       self.get_precedence(stack[-1]) >= self.get_precedence(c)):
                    postfix.append(stack.pop())
                    #print(f"While Loop: Popped from Stack to Postfix: {''.join(postfix)}, Stack: {stack}")
                stack.append(c)
                #print(f"Added '{c}' to Stack: {stack}")
        
        while stack:
            postfix.append(stack.pop())
            #print(f"Final Stack Popped to Postfix: {''.join(postfix)}")
        
        return postfix

 
