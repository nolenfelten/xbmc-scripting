

import xbmc,xbmcgui, time, sys, os
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
        self.readstatus = []
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        try:focusid = self.getFocusId()
        except:focusid = 0
        if (50 <= focusid <= 59):
         #   self.deletemail(self.getCurrentListPosition(),1)
            self.openemail(self.getCurrentListPosition())
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
        myemail = email.message_from_string(self.emaillist[selected].split("|")[0])
        if myemail.is_multipart():
            for part in myemail.walk():
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    self.getControl(67).setText(self.parse_email(part.get_payload()))
                    break
        else:self.getControl(67).setText(self.parse_email(myemail.get_payload()))

    def openemail(self, pos):
        #open dialog here
        item = self.emaillist[pos]
        f = open(self.ibfolder + item.split("|")[1] + ".sss", "r")
        myfile = f.read().split("|")[1]
        f.close()
        f = open(self.ibfolder + item.split("|")[1] + ".sss", "w")
        f.write("1|" + myfile)
        f.close()
        if item.split("|")[2] == "0":icon = "XBemailread.png"
        else:icon = "XBemailreadattach.png"
        self.getListItem(pos).setThumbnailImage(icon)
    
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
        w = Checkemail(self.ibsettings,self.inbox,self.account,self.language,False)
        w.checkemail()
        self.newlist = w.newlist
        self.servsize = w.serversize
        self.inboxsize = w.inboxsize
        if len(self.newlist) != 0:
            self.serversize = w.serversize
            self.inboxsize = w.inboxsize
            self.getControl(81).setLabel(self.language(257) + self.getsizelabel(self.serversize))
            self.getControl(82).setLabel(self.language(258) + self.getsizelabel(self.inboxsize))                 
            self.updatelist()
        del w

    def deletemail(self, pos, setting):
        w = Checkemail(self.ibsettings,self.inbox,self.account,self.language,True)
        w.deletemail(pos,setting)
        self.serversize = w.serversize
        self.inboxsize = w.inboxsize
        if self.serversize != 0:
            self.getControl(81).setLabel(self.language(257) + self.getsizelabel(self.serversize))
        else:self.getControl(81).setLabel(self.language(257) + self.language(259))
        if self.inboxsize != 0:
            self.getControl(82).setLabel(self.language(258) + self.getsizelabel(self.inboxsize))
        else:
            self.getControl(82).setLabel(self.language(258) + self.language(259))
            self.setinboxempty()                
        del w
        if setting != 1:
            self.removeItem(pos)
            self.emaillist.pop(pos)


    def setinboxempty(self):
        self.getControl(82).setLabel("")
        self.addItem(self.language(256))
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
                if myline[1] == "Account Name":
                    accountname = myline[2]
                    popname = myline[3]
                    if accountname != self.ibsettings.getSetting("Account Name") or popname != self.ibsettings.getSetting("POP Server"):
                        f.close()
                        self.removefiles(self.ibfolder)
                        self.buildemlist()
                        return
                elif myline[1] == "Server Size":
                    if int(myline[2]) != 0:
                        self.getControl(81).setLabel(self.language(257) + self.getsizelabel(int(myline[2])))
                    else:self.getControl(81).setLabel(self.language(257) + self.language(259))
                elif myline[1] == "Inbox Size":
                    if int(myline[2]) != 0:
                        self.getControl(82).setLabel(self.language(258) + self.getsizelabel(int(myline[2])))
                    else:
                        self.setinboxempty()
                        self.getControl(82).setLabel(self.language(258) + self.language(259))
                        return
                else:
                    if myline[0] != "-":
                        self.list.append(theline)
            f.close()
            if len(self.list) == 0:self.setinboxempty()
            else:self.createlist()

    def removefiles(self,mydir):
        for root, dirs, files in os.walk(mydir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

    def getsizelabel (self, size):
        if size >= 1024:
            size = size/1024.0
            sizeext = "KB"
            if size >= 1024:
                size = size/1024.0
                sizeext = "MB"
        else:sizeext = "bytes"
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
            f = open(self.ibfolder + item.split("|")[0] + ".sss", "r")
            myfile = f.read()
            myemail = email.message_from_string(myfile.split("|")[1])
            self.emaillist.insert(0,myfile.split("|")[1] + "|" + item.split("|")[0] + "|" + item.split("|")[1])
            f.close()
            attachstatus = item.split("|")[1]
            if attachstatus == "0":icon = "XBnewemailnotread.png"
            else:icon="XBnewattachemailnotread.png"
            self.addItem(xbmcgui.ListItem(myemail.get('subject'),myemail.get('From'),icon,icon),0)
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
            myfile = f.read()
            myemail = email.message_from_string(myfile.split("|")[1])
            self.emaillist.insert(0,myfile.split("|")[1] + "|" + myitem[2] + "|" + myitem[3])
            f.close()
            readstatus = myfile.split("|")[0]
            attachstatus = myitem[3]
            if readstatus == "0" and attachstatus == "0":icon="XBemailnotread.png"
            if readstatus == "0" and attachstatus == "1":icon="XBemailnotreadattach.png"
            if readstatus == "1" and attachstatus == "0":icon="XBemailread.png"
            if readstatus == "1" and attachstatus == "1":icon="XBemailreadattach.png"
            self.addItem(xbmcgui.ListItem(self.parsesubject(myemail.get('subject')),myemail.get('From'),icon,icon),0)
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
