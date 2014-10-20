import ast
import os
from cache import cache
from tools import logHere

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
        self.attributes = {}
        self.methods = set()
        self.classes = set()
        self.names = set()
        self.inheritance = {}
        self.defaults = {}

    def visit_Name(self, node):
        self.names.add(node.id)

    def visit_ClassDef(self, node):
        self.classes.add(node.name)
        baseid = None
        if len(node.bases):
            if isinstance(node.bases[0], ast.Name):
                baseid = node.bases[0].id
            elif isinstance(node.bases[0], ast.Attribute):
                baseid = node.bases[0].value.id
        if node.name not in self.inheritance:
            self.inheritance[node.name] = baseid
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.methods.add(node.name)
        if node.name == "defaults":
            self.funcDefDefaults(node)
        elif node.name in ("__init__", "run"):
            self.funcDefStarters(node)

    def funcDefDefaults(self, node):
        for elm in node.body:
            if isinstance(elm, ast.Assign):
                target = elm.targets[0]
                if isinstance(target, ast.Name):
                    instname = self.getAstValue(target)
                    if self.getAstValue(elm.value) == "getRecord":
                        self.defaults[instname] = {}
                elif isinstance(target, ast.Attribute):
                    instname = self.getAstValue(target.value)
                    if instname in self.defaults:
                        self.defaults[instname][target.attr] = self.getAstValue(elm.value)
        new = {}
        for insts in self.defaults: #each instantiator name have a dict with attributeName/value pair
            new.update(self.defaults[insts])
        self.defaults = new

    def funcDefStarters(self, node):
        for elm in node.body:
            if isinstance(elm, ast.Assign):
                target = elm.targets[0]
                if isinstance(target, ast.Attribute):
                    if self.getAstValue(target.value) == "self":
                        self.attributes[target.attr] = self.getAstValue(elm.value)

    def visit_Assign(self, node):
        target = node.targets[0]
        if isinstance(target, ast.Name):
            attrname = target.id
            self.attributes[attrname] = self.getAstValue(node.value)
        elif isinstance(target, ast.Tuple):
            self.attributes.update((self.getAstValue(x), self.getAstValue(node.value)) for x in target.elts)
        elif isinstance(target, ast.Subscript):
            self.attributes[self.getAstValue(target.value)] = self.getAstValue(node.value)
        #elif isinstance(target, ast.Attribute):
        #    self.attributes[target.attr] = self.getAstValue(node.value)
        self.generic_visit(node)

    def visit_Call(self, node):
        for key, value in ast.iter_fields(node):
            if key == 'func':
                pass
            elif value:
                if isinstance(value[0], ast.Str):
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
                    pass

    def getAstValue(self, node):
        res = None
        if isinstance(node, ast.Num):
            res = node.n
        elif isinstance(node, ast.Str):
            res = "'%s'" % node.s
        elif isinstance(node, ast.List):
            res = []
        elif isinstance(node, ast.Dict):
            res = {}
        elif isinstance(node, ast.Call):
            if hasattr(node.func, "id"):
                res = node.func.id
            elif hasattr(node.func, "attr"):
                res = node.func.attr
        elif isinstance(node, ast.Name):
            res = node.id
        elif isinstance(node, ast.Tuple):
            res = ()
            for elm in node.elts:
                res = self.getAstValue(elm)
        elif isinstance(node, ast.Attribute):
            res = self.getAstValue(node.value)
        return res

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
        self.targets = {}
        self.values = {}
        self.errors = None

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ImportFrom(self, node):
        self.importfrom = node.module
        self.importwhat = node.names[0].name
        self.alias = node.names[0].asname

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            self.targets[0] = node.targets[0].id
            self.values[0] = node.value
        #elif isinstance(node.targets[0], ast.Tuple):
        #    for t in [tar for tar in node.targets[0].elts if isinstance(tar, ast.Name)]:
        #        self.targets.append(t.id)



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
