from xml.sax import handler
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces

###RECORD###

def parseRecordXML(filename):
    parser = make_parser()
    parser.setFeature(feature_namespaces, 0)
    dh = XMLRecordHandler()
    parser.setContentHandler(dh)
    parser.parse(open(filename, "r"))
    return dh

class XMLRecordHandler(handler.ContentHandler):

    def __init__(self):
        self.fields = {}
        self.details = {}
        self.isPersistent = True
        self.inheritance = ""

    def startElement(self, name, attrs):
        if name not in ("record","detailrecord","reportwindow","routinewindow"):
            if attrs.has_key("name"):
                fieldname = str(attrs.get("name",""))
                fieldtype = str(attrs.get("type"))
                self.fields[fieldname] = fieldtype
                if fieldtype == "detail":
                    self.details[fieldname] = str(attrs.get("recordname"))
        else:
            if attrs.has_key("inherits"):
                self.inheritance = str(attrs.get("inherits"))
            elif attrs.has_key("persistent"):
                self.isPersistent = bool(attrs.get("persistent"))

    def endElement(self, name):
        pass

###SETTINGS###
def parseSettingsXML(filename):
    parser = make_parser()
    parser.setFeature(feature_namespaces, 0)
    dh = XMLSettingsHandler()
    parser.setContentHandler(dh)
    parser.parse(open(filename, "r"))
    return dh

class XMLSettingsHandler(handler.ContentHandler):

    def __init__(self):
        self.scriptdirs = []
        self.sd = []
        for i in range(255):
            self.sd.append(None)

    def startElement(self, name, attrs):
        if name == "scriptdir":
            self.sd[int(attrs.get('level', 0))] = self.unicodeToStr(attrs.get('path', None))

    def endDocument(self):
        for i in self.sd:
            if i:
                self.scriptdirs.append(i)

    def unicodeToStr(self, value):
        res = ""
        try:
            res = str(value)
        except:
            res = repr(value)
        return res
