import xbmc, xbmcgui
import sys, traceback
import os.path
from xml.dom.minidom import parse, parseString
import time
group=[]
def GetNodeText(node):
	dout=''
	for tnode in node.childNodes:
		if (tnode.nodeType==NODE_TEXT)|(tnode.nodeType==NODE_CDATA_SECTION):
			dout=dout+tnode.nodeValue
	return dout.encode("iso-8859-1")

def GetNodeValue(node,tag=None): #xml reading
	if tag is None: return GetNodeText(node)
	nattr=node.attributes.getNamedItem(tag)
	if not (nattr is None): return nattr.value.encode("iso-8859-1")
	for child in node.childNodes:
		if child.nodeName==tag:
			return GetNodeText(child)
	return None
    
def hidegroup(self,group):
    tmpgroup=[]

    exec ("for i in self." + group + "group: tmpgroup.append(i)")

    for i in tmpgroup:
        try:
            exec ("self." + i + ".setVisible(False)")
        except:
             print "hide error"

def showgroup(self,group):
    tmpgroup=[]

    exec ("for i in self." + group + "group: tmpgroup.append(i)")

    for i in tmpgroup:
         try:
             exec ("self." + i + ".setVisible(True)")
         except:
            print "show error"
def skin(self,ospath,skin):
                        

                        w=self.getWidth()
                        h=self.getHeight()
                        dom = parse(ospath + skin)
                    
                        params=dom.getElementsByTagName("item")
                        for i in params:
                            Name ="self." + str(GetNodeValue(i,'name'))
                            type1 =str(GetNodeValue(i,'type'))
                            loc1=str(GetNodeValue(i,'location'))
                            path=str(GetNodeValue(i,'path'))
                            label=(GetNodeValue(i,'label'))
                            focusTexture=(GetNodeValue(i,'focusTexture'))
                            noFocusTexture=(GetNodeValue(i,'noFocusTexture'))
                            textXOffset=(GetNodeValue(i,'textXOffset'))
                            textYOffset=(GetNodeValue(i,'textYOffset'))
                            alignment=(GetNodeValue(i,'alignment'))
                            font=(GetNodeValue(i,'font'))
                            textColor=(GetNodeValue(i,'textColor'))
                            disabledColor=(GetNodeValue(i,'disabledColor'))
                            checkWidth=(GetNodeValue(i,'checkWidth'))
                            checkHeight=(GetNodeValue(i,'checkHeight'))
                            hasPath=(GetNodeValue(i,'hasPath'))
                            
                            if label == None:
                                label=""                    
                            if focusTexture == None:
                                focusTexture=""
                            if noFocusTexture == None:
                                noFocusTexture=""
                            if textXOffset == None:
                                textXOffset=""
                            if textYOffset == None:
                                textYOffset=""
                            if alignment== None:
                                alignment=""
                            if font == None:
                                font="font13"
                            if textColor  == None:
                                textColor = "0xffffffff"
                            if disabledColor == None:
                                disabledColor=""
                            if checkWidth==None:
                                checkWidth=str(10)
                            if checkHeight== None:
                                checkHeight=str(10)
                            if hasPath == None:
                                hasPath="" 
                            loc=[]
                            
                            exec ("loc = " + loc1)


                          
                            
                            if str(type1) == "ControlImage":


                                exec  (Name + "= xbmcgui." + str(type1) + "(" + str(loc[0]) + "," + str(loc[1]) + "," + str(loc[2]) + "," + str(loc[3]) + ",'" + ospath + "\\"+ path + "' )" )
                                


                            if str(type1) == "ControlList":
                                exec  (Name + "= xbmcgui." + str(type1) + "(" + str(loc[0]) + "," + str(loc[1]) + "," + str(loc[2]) + "," + str(loc[3]) + ",'" + font + "','" + textColor + "')" )


                            if str(type1) == "ControlButton":
                                exec  (Name + "= xbmcgui." + str(type1) + "(" + str(loc[0]) + "," + str(loc[1]) + "," + str(loc[2]) + "," + str(loc[3]) + ",'" + label + "' )" )

                                
                            if str(type1) == "ControlCheckMark":
                                exec  (Name + "= xbmcgui." + str(type1) + "(" + str(loc[0]) + "," + str(loc[1]) + "," + str(loc[2]) + "," + str(loc[3]) + ",'" + label + "')" )

                                
                            if str(type1) == "ControlFadeLabel":
                                exec  (Name + "= xbmcgui." + str(type1) + "(" + str(loc[0]) + "," + str(loc[1]) + "," + str(loc[2]) + "," + str(loc[3]) + ",'" + font + "','" + textColor + "')" )

                                
                            if str(type1) == "ControlLabel":
                                exec  (Name + "= xbmcgui." + str(type1) + "(" + str(loc[0]) + "," + str(loc[1]) + "," + str(loc[2]) + "," + str(loc[3])  + ",'" + label + "','" + font + "','" + textColor + "')" )


                            if str(type1) == "ControlTextBox":
                                exec  (Name + "= xbmcgui." + str(type1) + "(" + str(loc[0]) + "," + str(loc[1]) + "," + str(loc[2]) + "," + str(loc[3]) +",'" + font + "','" + textColor + "')" )


                            exec ("self.addControl(" + Name +")")

                        

                        
                        movem=dom.getElementsByTagName("move")
                        for i in movem:
                                name =str(GetNodeValue(i,'name'))
                                up =(GetNodeValue(i,'onup'))
                                dwn =(GetNodeValue(i,'ondown'))
                                lft =(GetNodeValue(i,'onleft'))
                                rgh =(GetNodeValue(i,'onright'))
                                if not up == None:
                                    exec ("self." + name + ".controlUp(self." + up +")")
                                if not dwn == None:
                                    exec ("self." + name + ".controlDown(self." + dwn +")")
                                if not lft == None:
                                    exec ("self." + name + ".controlLeft(self." + lft +")")
                                if not rgh == None:
                                    exec ("self." + name + ".controlRight(self." + rgh +")")
                      
                        foc=dom.getElementsByTagName("focus")
                        try:
                            name =str(GetNodeValue(foc[0],'name'))
                        except:
                            pass
                        try :
                            exec ("self.setFocus(self." + name + ")")
                        except:
                            pass

                
                        groups=dom.getElementsByTagName("Group")
                        for i in groups:
                            item =str(GetNodeValue(i,'item'))
                            id =str(GetNodeValue(i,'id'))
                            try :
                                exec ("if self."+ str(id) + "group == None:" + str(id) + "group =[]")
                            except:

                                exec ("self." + str(id) + "group =[]")
                            exec("self." + str(id) + "group.append('" + item + "')")
                     
                                 
                        
