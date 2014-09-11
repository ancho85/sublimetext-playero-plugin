from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker
from tools import logHere

class CacheStatisticWriter(BaseChecker):
    """write the cache statistics after plugin usage"""

    __implements__ = IRawChecker

    name = 'cache_statistics_writer'
    msgs = {'C6666': ('cache statistics writed at log directory',
                      ('cache statistics writed at log directory'),
                      ('cache statistics writed at log directory')),
            }
    options = ()
    priority = -666
    cache = None

    def __init__(self, linter=None, cacheobj=None):
        super(CacheStatisticWriter, self).__init__(linter)
        self.cache = cacheobj

    def process_module(self, node):
        """write the cache statistics after plugin usage"""
        logHere(self.cache.getStatistics(), 'stats.log')
        lastline = sum(1 for line in node.file_stream)
        self.add_message('C6666', lastline)


from astroid.node_classes import Getattr, AssAttr, Const, If, BinOp, CallFunc, Name
from astroid.exceptions import InferenceError
from pylint.interfaces import IAstroidChecker
from pylint.checkers.utils import check_messages
from sqlparse import validateSQL

class QueryChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'playero-query-checker'
    msgs = {
            'W6602': ("query inference could not be resolved (%s)",
                                'query-inference',
                                "Query could not be resolved"),
            'E6601': ("query syntax error (%s)",
                                'query-syntax-error',
                                "Query sentence has a syntax error"),
        }
    options = ()

    queryTxt = {}

    def getAssignedTxt(self, node):
        qvalue = ""
        try:
            if type(node.value) == type(""):
                qvalue = node.value
            elif isinstance(node.value, Const):
                qvalue = node.value.value
            elif isinstance(node.value.infered()[0], Const):
                qvalue = node.value.infered()[0].value
            elif isinstance(node.value, BinOp):
                qvalue = self.getAssignedTxt(node.value.left)
            else:
                self.add_message("W6602", line=node.lineno, node=node, args=node.value)
        except InferenceError, e:
            logHere("InferenceError getAssignedTxt", e, filename="errors.log")
        except Exception, e:
            logHere("Exception getAssignedTxt", e, filename="errors.log")
        return qvalue

    def setUpQueryTxt(self, nodeTarget, value, isnew=False):
        try:
            if nodeTarget.expr.infered()[0].pytype() == "Query.Query":
                instanceName = nodeTarget.expr.name
                if isnew or instanceName not in self.queryTxt:
                    self.queryTxt[instanceName] = ""
                if not isinstance(nodeTarget.parent.parent, If):
                    self.queryTxt[instanceName] += value
                else:
                    if not isinstance(nodeTarget.parent.parent.parent, If): #First if in if-Elif-Else
                        self.queryTxt[instanceName] += value
        except InferenceError, e:
            logHere("InferenceError setUpQueryTxt", e, filename="errors.log")

    def visit_assign(self, node):
        if isinstance(node.targets[0], AssAttr):
            qvalue = self.getAssignedTxt(node)
            self.setUpQueryTxt(node.targets[0], qvalue, isnew=True)

    def visit_augassign(self, node):
        if isinstance(node.target, AssAttr):
            qvalue = self.getAssignedTxt(node)
            self.setUpQueryTxt(node.target, qvalue)

    @check_messages('query-syntax-error', 'query-inference')
    def visit_callfunc(self, node):
        if isinstance(node.func, Getattr) and node.func.attrname in ("open", "execute"):
            try:
                for x in node.infered():
                    try:
                        main = x.root().values()[0].frame()
                        if main.name == "Query":
                            name = node.func.expr.name
                            if name in self.queryTxt:
                                res = validateSQL(self.queryTxt[name])
                                if res:
                                    self.add_message("E6601", line=node.lineno, node=node, args=res)
                            else:
                                self.add_message("W6602", line=node.lineno, node=node, args=name)
                    except TypeError, e:
                        logHere("TypeError visit_callfunc", e, filename="errors.log")
            except InferenceError, e:
                logHere("InferenceError visit_callfunc", e, filename="errors.log")
