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
    if type=='string': return str(GetNodeValue(pnode,'value'))
    if type=='float': return float(GetNodeValue(pnode,'value'))
    if type=='int': return int(GetNodeValue(pnode,'value'))
    if type=='boolean':
        val=GetNodeValue(pnode,'value').lower();
        return (not((val=='false') or (val=='0')))
    if type=='select': return int(GetNodeValue(pnode,'value'))
    if type[0:4]=='list':
        options=GetSelectOptions(pnode, type[5:])
        return options

    return "unknown type:"+str(GetNodeValue(pnode,'value'))

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
            else:
                options.append(str(GetNodeText(child)))

    return options

def createXML_Document():
    doc = xml.dom.minidom.Document()
    docElement = doc.createElement("settings")
    docElement.setAttribute("name", "Poker Timer II")
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

def returnString(v):
    s = str('%.2f' % v)
    if s[-3:] == ".00":
        s = s[:-3]
    return s

def savePadSettings(padsettings, settingsfile):
    doc, docElement = createXML_Document()

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "ScriptTitle", "string")
    cNode = add_cNode(doc, pNode, padsettings['ScriptTitle'])

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "PadImageName", "string")
    cNode = add_cNode(doc, pNode, padsettings['PadImageName'])

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "padSize", "int")
    cNode = add_cNode(doc, pNode, str(padsettings['padSize']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "animate", "boolean")
    cNode = add_cNode(doc, pNode, str(padsettings['animate']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "autoHide", "boolean")
    cNode = add_cNode(doc, pNode, str(padsettings['autoHide']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "autoHideTime", "int")
    cNode = add_cNode(doc, pNode, str(padsettings['autoHideTime']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "padOffsetX", "int")
    cNode = add_cNode(doc, pNode, str(padsettings['padOffsetX']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "padOffsetY", "int")
    cNode = add_cNode(doc, pNode, str(padsettings['padOffsetY']))

    writeFile(settingsfile, doc)
    doc.unlink()

def saveSettings(settings, settingsfile):

    doc, docElement = createXML_Document()

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "EndTournamentAlarm", "string")
    cNode = add_cNode(doc, pNode, settings['EndTournamentAlarm'])
    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "EndTournamentAlarmTime", "int")
    cNode = add_cNode(doc, pNode, returnString(settings['EndTournamentAlarmTime']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "EndLevelAlarm", "string")
    cNode = add_cNode(doc, pNode, settings['EndLevelAlarm'])
    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "EndLevelAlarmTime", "int")
    cNode = add_cNode(doc, pNode, returnString(settings['EndLevelAlarmTime']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "StartLevelAlarm", "string")
    cNode = add_cNode(doc, pNode, settings['StartLevelAlarm'])
    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "StartLevelAlarmTime", "int")
    cNode = add_cNode(doc, pNode, returnString(settings['StartLevelAlarmTime']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "WarningAlarm", "string")
    cNode = add_cNode(doc, pNode, settings['WarningAlarm'])
    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "WarningAlarmTime", "int")
    cNode = add_cNode(doc, pNode, returnString(settings['WarningAlarmTime']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "LEVEL_TIME", "list int")
    for c in range(1,21):
        cNode = add_cNode(doc, pNode, str(settings['LEVEL_TIME'][c]))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "WARNING_TIME", "int")
    cNode = add_cNode(doc, pNode, str(settings['WARNING_TIME']))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "ANTE", "list int")
    for c in range(1,21):
        s = returnString(settings['ANTE'][c])
        cNode = add_cNode(doc, pNode, s)

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "SM_BLIND", "list int")
    for c in range(1,21):
        s = returnString(settings['SM_BLIND'][c])
        cNode = add_cNode(doc, pNode, s)

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "BIG_BLIND", "list int")
    for c in range(1,21):
        s = returnString(settings['BIG_BLIND'][c])
        cNode = add_cNode(doc, pNode, s)

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "BREAK_TIME", "list int")
    for c in range(1,21):
        cNode = add_cNode(doc, pNode, str(settings['BREAK_TIME'][c]))

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "CHIP_AMT", "list int")
    for c in range(1,6):
        s = returnString(settings['CHIP_AMT'][c])
        cNode = add_cNode(doc, pNode, s)

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "CHIP_IMAGE", "list")
    for c in range(1,6):
        cNode = add_cNode(doc, pNode, settings['CHIP_IMAGE'][c])

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "CHIP_TABLE", "list int")
    for c in range(1,14):
        s = returnString(settings['CHIP_TABLE'][c])
        cNode = add_cNode(doc, pNode, s)

    pNode = add_pNode(doc, docElement)
    set_pNode(pNode, "BLIND_TABLE", "list int")
    for c in range(1,31):
        s = returnString(settings['BLIND_TABLE'][c])
        cNode = add_cNode(doc, pNode, s)

    writeFile(settingsfile, doc)
    doc.unlink()

def writeFile(settingsfile, doc):
    f = file(settingsfile,'w')
    try:
        xml.dom.ext.PrettyPrint(doc, f)
    finally:
        f.close()
