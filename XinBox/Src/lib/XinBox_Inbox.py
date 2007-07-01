

import xbmc,xbmcgui, time, sys, os, traceback
import XinBox_Util, email, re
from XinBox_Settings import Settings
from XinBox_EmailEngine import Checkemail
from os.path import join, exists
from os import mkdir, remove
SETTINGDIR = "P:\\script_data\\XinBox\\"
ACCOUNTSDIR = "P:\\script_data\\XinBox\\Accounts\\"
from sgmllib import SGMLParser    

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,lang=False,theinbox=False,account=False,title=False):
        self.language = lang
        self.inbox = theinbox
        self.account = account
        self.title = title
        self.ibfolder = join(ACCOUNTSDIR,str(hash(self.account)),str(hash(self.inbox))) + "\\"

    def loadsettings(self):
        self.settings = Settings("XinBox_Settings.xml",self.title,"")
        self.accountsettings = self.settings.getSettingInListbyname("Accounts",self.account)
        self.ibsettings = self.accountsettings.getSettingInListbyname("Inboxes",self.inbox)
 
    def onInit(self):
        xbmcgui.lock()
        self.loadsettings()
        self.setupvars()
        self.setupcontrols()
        xbmcgui.unlock()
        self.buildemlist()
        
    def setupvars(self):
        self.emaillist = []
        self.control_action = XinBox_Util.setControllerAction()
        self.iboxempty = True
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        try:focusid = self.getFocusId()
        except:focusid = 0
        if (50 <= focusid <= 59):
            self.deletemail(self.getCurrentListPosition(),0)
        if controlID == 64:
            self.close()
        elif controlID == 61:
            self.checkfornew()
  
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.close()
        elif (50 <= focusid <= 59):
            self.printEmail(self.getCurrentListPosition())

    def printEmail(self, selected):
        if self.emaillist[selected].is_multipart():
            for part in self.emaillist[selected].walk():
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    self.getControl(67).setText(self.parse_email(part.get_payload()))
                    break
        else:self.getControl(67).setText(self.parse_email(self.emaillist[selected].get_payload()))

    
    def parse_email(self, email):
        parser = html2txt()
        parser.reset()
        parser.feed(email)
        parser.close()
        return parser.output()
    
    def setupcontrols(self):
        self.getControl(80).setLabel(self.inbox)
        self.getControl(61).setLabel(self.language(250))
        self.getControl(62).setLabel(self.language(251))
        self.getControl(63).setLabel(self.language(252))
        self.getControl(64).setLabel(self.language(65))

    def checkfornew(self):
        try:
            w = Checkemail(self.ibsettings,self.inbox,self.account,self.language,False)
            w.checkemail()
            self.newlist = w.newlist
            self.servsize = w.serversize
            if len(self.newlist) != 0:
                self.serversize = w.serversize
                self.inboxsize = w.inboxsize
                self.getControl(81).setLabel(self.getsizelabel(self.serversize))
                self.getControl(82).setLabel(self.getsizelabel(self.inboxsize))                 
                self.updatelist()
            del w
        except:traceback.print_exc()

    def deletemail(self, pos, setting):
        try:
            w = Checkemail(self.ibsettings,self.inbox,self.account,self.language,True)
            w.deletemail(pos,setting)
            self.serversize = w.serversize
            self.inboxsize = w.inboxsize
            self.getControl(81).setLabel(self.getsizelabel(self.serversize))
            if self.inboxsize != 0:
                self.getControl(82).setLabel(self.getsizelabel(self.inboxsize))
            else:self.setinboxempty()                
            del w
            self.removeItem(pos)
        except:traceback.print_exc()


    def setinboxempty(self):
        self.getControl(82).setLabel("")
        self.addItem("Inbox Empty")
        self.iboxempty = True
        self.getControl(50).setEnabled(False)
        self.setFocusId(61)
        self.getControl(67).setText("")

    def buildemlist(self):
        if not exists(self.ibfolder + "emid.xib"):
            self.setinboxempty()
            return
        else:
            self.list = []
            f = open(self.ibfolder + "emid.xib", "r")
            for line in f.readlines():
                theline = line.strip("\n")
                myline = theline.split("|")
                print "myline = " + str(myline)
                if myline[1] == "Account Name":
                    accountname = myline[2]
                    popname = myline[3]
                    if accountname != self.ibsettings.getSetting("Account Name") or popname != self.ibsettings.getSetting("POP Server"):
                        f.close()
                        self.removefiles(self.ibfolder)
                        self.buildemlist()
                        return
                elif myline[1] == "Server Size":
                    self.getControl(81).setLabel(self.getsizelabel(int(myline[2])))
                elif myline[1] == "Inbox Size":
                    self.getControl(82).setLabel(self.getsizelabel(int(myline[2])))
                else:
                    if myline[0] != "-":
                        self.list.append(theline)
            f.close()
            if len(self.list) == 0:
                self.addItem("Inbox Empty")
                self.getControl(50).setEnabled(False)
            else:self.createlist()

    def removefiles(self,mydir):
        for root, dirs, files in os.walk(mydir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

    def getsizelabel (self, size):
        if size >= 1024:
            size = size/1024.0
            sizeext = "KB"
            self.xbsizeb = size
            if size >= 1024:
                size = size/1024.0
                sizeext = "MB"
        else:
            self.xbsizeb = 0
            sizeext = "bytes"
        return "%.1f %s" % (size,  sizeext)  
   
    def updatelist(self):
        if self.iboxempty:
            self.iboxempty = False
            self.getControl(50).setEnabled(True)
            self.clearList()
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create(self.language(210) + self.inbox, self.language(254))
        for i,item in enumerate(self.newlist):
            self.dialog.update((i*100)/len(self.newlist),self.language(254),"")
            f = open(self.ibfolder + item + ".sss", "r")
            myemail = email.message_from_string(f.read())
            self.emaillist.insert(0,myemail)
            f.close()
            self.addItem(xbmcgui.ListItem(myemail.get('subject'),myemail.get('From'),"XBnewemailnotread.png","XBnewemailnotread.png"),0)
        self.dialog.close()

    def createlist(self):
        self.iboxempty = False
        self.getControl(50).setEnabled(True)
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create(self.language(210) + self.inbox, self.language(253))
        for i,item in enumerate(self.list):
            self.dialog.update((i*100)/len(self.list),self.language(253),"")
            myitem = item.split("|")
            f = open(self.ibfolder + myitem[2] + ".sss", "r")
            myemail = email.message_from_string(f.read())
            self.emaillist.insert(0,myemail)
            f.close()
            self.addItem(xbmcgui.ListItem(self.parsesubject(myemail.get('subject')),myemail.get('From'),"XBemailnotread.png","XBemailnotread.png"),0)
        self.dialog.close()

    def parsesubject(self, subject):
        if subject == "":
            return self.language(255)
        else:return subject

class html2txt(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.pieces = []

    def handle_data(self, text):
        self.pieces.append(text)

    def handle_entityref(self, ref):
        if ref=='amp':
            self.pieces.append("&")

    def output(self):
        return " ".join(self.pieces)        
