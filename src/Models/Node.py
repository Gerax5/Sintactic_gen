class Node():
    def __init__(self, object: list, isOperator: bool, childs: list["Node"] | None):
        self.object = object
        self.isOpeator = isOperator
        self.childs = childs
        self.nodeNumber = 0

        #Direct DFA
        self.leafNumber: None | int = None
        self.firstPosition: set = {}
        self.lastPosition: set = {}
        self.nullable: bool = False 


    def getObject(self):
        return self.object
    
    def getIsOperator(self):
        return self.isOpeator
    
    def getChilds(self):
        return self.childs

    def getNodeNumber(self):
        return self.nodeNumber
    
