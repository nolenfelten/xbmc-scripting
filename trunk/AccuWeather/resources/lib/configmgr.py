import xml.dom.minidom
import xml.dom.ext

NODE_ELEMENT=1
NODE_ATTRIBUTE=2
NODE_TEXT=3
NODE_CDATA_SECTION=4


def GetNodeText(node):
    dout=''
    for tnode in node.childNodes:
        if (tnode.nodeType==NODE_TEXT)|(tnode.nodeType==NODE_CDATA_SECTION):
            dout=dout+tnode.nodeValue
    return dout.encode("iso-8859-1")

def GetNodeValue(node,tag=None): #helper function for xml reading
    if tag is None: return GetNodeText(node)
    nattr=node.attributes.getNamedItem(tag)
    if not (nattr is None): return nattr.value.encode("iso-8859-1")
    for child in node.childNodes:
        if child.nodeName==tag:
            return GetNodeText(child)
    return None

def GetParamValue(pnode):
    type=GetNodeValue(pnode,"type")
    if type=='int': return int(GetNodeValue(pnode,'value'))
    elif type=='float': return float(GetNodeValue(pnode,'value'))
    elif type=='bool':
        val=GetNodeValue(pnode,'value').lower();
        return (not((val=='false') or (val=='0')))
    elif type=='select': return int(GetNodeValue(pnode,'value'))
    elif type[0:4]=='list':
        options=GetSelectOptions(pnode, type[5:])
        return options
    else:
      return str(GetNodeValue(pnode,'value'))

    #return "unknown type:"+str(GetNodeValue(pnode,'value'))

def ReadSettings(settingsfile):
    dom = xml.dom.minidom.parse(settingsfile)
    params=dom.getElementsByTagName("setting")
    settings={}
    for param in params:
        id=GetNodeValue(param,'id')
        settings[id]=GetParamValue(param)
    return settings

def GetSelectOptions(pnode, type = 'string'):
    options=[]
    for child in pnode.childNodes:
        if child.nodeName=='value':
            if type=='int':
                options.append(int(GetNodeText(child)))
            elif type=='float':
                options.append(float(GetNodeText(child)))
            elif type=='bool':
                val=GetNodeText(child).lower();
                options.append((not((val=='false') or (val=='0'))))
            else:
                options.append(str(GetNodeText(child)))

    return options

def createXML_Document(ScriptTitle):
    doc = xml.dom.minidom.Document()
    docElement = doc.createElement("settings")
    docElement.setAttribute("name", ScriptTitle)
    doc.appendChild(docElement)
    return doc, docElement

def add_pNode(doc, docElement):
    pNode = doc.createElement("setting")
    docElement.appendChild(pNode)
    return pNode

def add_cNode(doc, pNode, value):
    cNode = doc.createElement("value")
    pNode.appendChild(cNode)
    v = doc.createTextNode(value)
    cNode.appendChild(v)
    return cNode

def set_pNode(pNode, idValue, idType):
    pNode.setAttribute("id", idValue)
    pNode.setAttribute("type", idType)

def saveDefaults(settings, settingsfile, settingstitle):

    doc, docElement = createXML_Document(settingstitle)

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "URL_Location", "str")
    cNode = add_cNode(doc, pNode, settings['URL_Location'])

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "defaultMap_Category", "int")
    cNode = add_cNode(doc, pNode, str(settings['defaultMap_Category']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "defaultMap_Level", "int")
    cNode = add_cNode(doc, pNode, str(settings['defaultMap_Level']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "defaultMap_Type", "int")
    cNode = add_cNode(doc, pNode, str(settings['defaultMap_Type']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "location", "str")
    cNode = add_cNode(doc, pNode, settings['location'])

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "defaults", "list")
    for item in settings['defaults'][:]:
        cNode = add_cNode(doc, pNode, item)

    writeFile(settingsfile, doc)
    doc.unlink()

def writeFile(settingsfile, doc):
    f = file(settingsfile,'w')
    try:
        xml.dom.ext.PrettyPrint(doc, f)
    finally:
        f.close()

