# -*- coding: utf-8 -*-
import os
import sys
import imp
import ntpath
import cPickle

HERE = os.path.dirname(os.path.abspath(__file__))

def latinToAscii(unicrap):
    """This takes a UNICODE string and replaces Latin-1 characters with
        something equivalent in 7-bit ASCII. It returns a plain ASCII string.
        This function makes a best effort to convert Latin-1 characters into
        ASCII equivalents. It does not just strip out the Latin-1 characters.
        All characters in the standard 7-bit ASCII range are preserved.
        In the 8th bit range all the Latin-1 accented letters are converted
        to unaccented equivalents. Most symbol characters are converted to
        something meaningful. Anything not converted is deleted.
    """
    xlate = {0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A',
        0xc6:'Ae', 0xc7:'C',
        0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
        0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
        0xd0:'Th', 0xd1:'N',
        0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
        0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U',
        0xdd:'Y', 0xde:'th', 0xdf:'ss',
        0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a',
        0xe6:'ae', 0xe7:'c',
        0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
        0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
        0xf0:'th', 0xf1:'n',
        0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o',
        0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u',
        0xfd:'y', 0xfe:'th', 0xff:'y' #,
        """0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
        0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
        0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
        0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
        0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
        0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
        0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>',
        0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
        0xd7:'*', 0xf7:'/',
        0x0A:'', #New Line
        0x0D:'', #Carriage Return
        0xA0:'', #Non-breaking space ??
        0x00:'', #Null
        0x09:'', #Horizontal Tab
        0x0b:'' #Vertical Tab """
        }
    return ''.join(xlate.get(ord(i), str(i) if ord(i) < 0x80 else '') for i in unicrap)

def logHere(*args, **kwargs):
    filename = kwargs.get("filename", "log.log")
    logfile = os.path.join(HERE, '..', 'logs', filename)
    f = file(logfile, "a")
    f.writelines("%s  " % str(arg) for arg in args)
    f.write("%s" % "\n" * (kwargs.get("whitespace", 0) + 1))

def hashIt(param, unhash=False):
    if unhash:
        return cPickle.loads(param)
    return cPickle.dumps(param, 2) #binary format

def filenameFromPath(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def embeddedImport(modulename):
    return imp.load_source(modulename, os.path.join(HERE, "..", "corepy", "embedded", "%s.py" % modulename))

def includeZipLib(zipfile):
    sys.path.insert(0, os.path.join(HERE, "..", "libs", zipfile))

def xmlValue(xtype):
    return {"string": "''",
            "boolean": True,
            "integer": 0,
            "value": 666.0,
            "memo": "''",
            "set": "''",
            "detail": "''",
            "none": None,
            "date": "date(2000, 01, 01)",
            "time": "time(1, 0, 0)",
            "internalid": 111,
            "blob": "''"
            }[str(xtype).lower()]

def escapeAnyToString(text):
    integers = tuple((x, "0%s") for x in ['%d', '%i', '%o', '%u', '%x', '%X'])
    decimals = tuple((x, "0%s") for x in ['%e', '%E', '%f', '%F', '%g', '%G'])
    strings  = tuple((x, "%s") for x in ['%c', '%r'])
    for k, v in integers:
        text = text.replace(k, v)
    for k, v in decimals:
        text = text.replace(k, v)
    for k, v in strings:
        text = text.replace(k, v)
    return text

def isNumber(text):
    try:
        float(text)
        return True
    except TypeError:
        return False
    except ValueError:
        return False

indent = ""
def debug(fn):
    import inspect
    varList, _, _, default = inspect.getargspec(fn)
    d = {}
    if default is not None:
        d = dict((varList[-len(default):][i], v) for i, v in enumerate(default))
    def f(*argt, **argd):
        global indent
        indent += "    "
        logHere(indent, ('Enter %s' % fn).center(100, '='), filename="debug.log")
        d.update(dict((varList[i], v) for i, v in enumerate(argt)))
        d.update(argd)
        for c in d.iteritems():
            logHere(indent, '%s = %s' % c, filename="debug.log")
        ret = fn(*argt, **argd)
        logHere(indent, 'return:', filename="debug.log")
        if type(ret) == str:
            logHere(indent, ret.replace("\n", "%s\n" % indent), filename="debug.log")
        else:
            logHere(indent, ret, filename="debug.log")
        logHere(indent, ('Exit %s' % fn).center(100, '='), filename="debug.log")
        indent = indent[:-4]
        return ret
    return f
