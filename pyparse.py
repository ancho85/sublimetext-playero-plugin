import ast
import os
from cache import cache

@cache.store
def parseScript(filefullpath):
    f = open(filefullpath, "r")
    lines = f.read().splitlines() #best handling for CR LF and LF
    f.close()
    fixed = "\n".join([line.rstrip() for line in lines]) #force \n for each line
    parse = PyParse()
    try:
        nodes = ast.parse(fixed, mode="exec")
        parse.visit(nodes)
    except SyntaxError:
        pass
    return parse

class PyParse(ast.NodeVisitor):

    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.attributes = set()
        self.methods = set()
        self.classes = set()
        self.names = set()
        self.inheritance = {}

    def generic_visit(self, node):
        #print type(node).__name__
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Module(self, node):
        self.generic_visit(node)

    def visit_Name(self, node):
        self.names.add(node.id)
        #print "name level", node.id

    def visit_ClassDef(self, node):
        #print "class level", node.name
        self.classes.add(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.methods.add(node.name)
        #print "function level", node.name

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            self.attributes.add(node.targets[0].id)
        self.generic_visit(node)
        #print "assign level", node.targets[0].id

    def visit_Call(self, node):
        for key, value in ast.iter_fields(node):
            if key == 'func':
                #print "call FUNCTION", key, "value id:", value.id
                #self.visit(value)
                pass
            elif value:
                if isinstance(value[0],ast.Str):
                    currentClass = value[0].s
                    self.inheritance[currentClass] = ""
                    self.subnodeVisit(value, currentClass)

    def subnodeVisit(self, node, current):
        if isinstance(node, list):
            for item in node:
                if isinstance(item, ast.Str):
                    if item.s != current:
                        self.inheritance[current] = item.s
                else:
                    pass # probably ast.Name instance. __file__

@cache.store
def parseExecLine(txtLine, mode="single"): #eval
    parse = PyExecLineParse()
    try:
        nodes = ast.parse(txtLine, mode=mode)
        parse.visit(nodes)
    except SyntaxError, e:
        parse.errors = e
    return parse

class PyExecLineParse(ast.NodeVisitor):

    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.importfrom = ""
        self.importwhat = ""
        self.alias = None
        self.targets = []
        self.values = []
        self.errors = None

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ImportFrom(self, node):
        self.importfrom = node.module
        self.importwhat = node.names[0].name
        self.alias = node.names[0].asname

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            self.targets = [node.targets[0].id]
        elif isinstance(node.targets[0], ast.Tuple):
            for t in [tar for tar in node.targets[0].elts if isinstance(tar, ast.Name)]:
                self.targets.append(t.id)
        #self.values = node.value



if __name__ == "__main__":
    filepath = "e:/Develop/desarrollo/python/ancho/workspace/Playero/extra/StdPY/records/Invoice.py"
    if (os.name == "posix"):
        filepath = "/home/ancho/Develop/Playero/standard/records/Invoice.py"
    par = parseScript(filepath)
    """print "---attributes---"
    for a in par.attributes:
        print a
    print "---methods---"
    for b in par.methods:
        print b
    print "---inheritance---"
    for k in par.inheritance:
        print k, par.inheritance[k]"""
