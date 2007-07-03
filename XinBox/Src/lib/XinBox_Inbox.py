

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
        self.reademid()
        
    def setupvars(self):
        self.guilist = []
        self.control_action = XinBox_Util.setControllerAction()
        if self.ibsettings.getSetting("SERV Inbox Size") != "0":
            self.theservsize = int(self.ibsettings.getSetting("SERV Inbox Size"))
        else:self.theservsize = False
        if self.ibsettings.getSetting("XinBox Inbox Size") != "0":
            self.ibxsize = int(self.ibsettings.getSetting("XinBox Inbox Size"))
        else:self.ibxsize = False
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        try:focusid = self.getFocusId()
        except:focusid = 0
        if (50 <= focusid <= 59):
           # self.deletemail(self.getCurrentListPosition(),0)
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
        myemail = self.guilist[selected][1]
        if myemail.is_multipart():
            for part in myemail.walk():
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    self.getControl(67).setText(self.parse_email(part.get_payload()))
                    break
        else:self.getControl(67).setText(self.parse_email(myemail.get_payload()))

    def openemail(self, pos):
        #open dialog here
        item = self.guilist[pos]
        f = open(self.ibfolder + item[0] + ".sss", "r")
        myfile = f.read().split("|")[1]
        f.close()
        f = open(self.ibfolder + item[0] + ".sss", "w")
        f.write("1|" + myfile)
        f.close()
        if item[2] == 0:icon = "XBemailread.png"
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
        newlist = w.newlist
        self.servsize = w.serversize
        self.inboxsize = w.inboxsize
        del w
        if len(newlist) != 0:
            self.updatelist(newlist)
                

    def deletemail(self, pos, setting):
        w = Checkemail(self.ibsettings,self.inbox,self.account,self.language,True)
        w.deletemail(pos,setting)
        self.serversize = w.serversize
        self.inboxsize = w.inboxsize                
        del w
        if setting != 1:
            self.removeItem(pos)
            self.guilist.pop(pos)
            if len(self.guilist) != 0:
                self.printEmail(self.getCurrentListPosition())
            else:self.setinboxempty()

    def setinboxnotemtpy(self):
        self.getControl(50).setEnabled(True)
        self.clearList()
        self.setFocusId(50)


    def setinboxempty(self):
        self.addItem(self.language(256))
        self.getControl(50).setEnabled(False)
        self.setFocusId(61)
        self.getControl(67).setText("")


    def checksize(self,currsize, limit):
        limbytes = float(limit*1048576)
        if (float(currsize/limbytes)*100) >= 90:
            return False
        else:return True
                                            
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
   
    def updatelist(self, newlist):
        dialog = xbmcgui.DialogProgress()
        dialog.create(self.language(210) + self.inbox, self.language(254))
        if len(self.guilist) == 0: self.setinboxnotemtpy()
        for i,item in enumerate(newlist):
            dialog.update((i*100)/len(newlist),self.language(254),"")
            f = open(self.ibfolder + item[0] + ".sss", "r")
            myfile = f.read()
            f.close()
            myemail = email.message_from_string(myfile.split("|")[1])
            readstatus = int(myfile.split("|")[0])
            self.guilist.insert(0,[item[0],myemail,item[1],readstatus,item[2],item[3]])
            if item[1] == 0:icon="XBnewemailnotread.png"
            else:icon="XBnewattachemailnotread.png"
            self.addItem(xbmcgui.ListItem(self.parsesubject(myemail.get('subject')),myemail.get('From'),icon,icon),0)
        dialog.close()

    def geticon(self,attstat, readstat):
        if attstat == 0 and readstat == 0:return "XBemailnotread.png"
        elif attstat == 0 and readstat == 1:return "XBemailread.png"
        elif attstat == 1 and readstat == 0:return "XBemailnotreadattach.png"
        elif attstat == 1 and readstat == 1:return "XBemailreadattach.png"        
  
    def parsesubject(self, subject):
        if subject == "":
            return self.language(255)
        else:return subject

    def reademid(self):
        if not exists(self.ibfolder + "emid.xib"):
            self.setinboxempty()
            return
        dialog = xbmcgui.DialogProgress()
        dialog.create(self.language(210) + self.inbox, self.language(253))
        f = open(self.ibfolder + "emid.xib", "r")
        lines = f.readlines()
        f.close()
        for i,line in enumerate(lines):
            dialog.update((i*100)/len(lines),self.language(253),"")
            theline = line.strip("\n")
            myline = theline.split("|")
            if myline[1] == "Account Name":self.accountname = myline[2]
            elif myline[1] == "Server Size":self.serversize = myline[2]
            elif myline[1] == "Inbox Size":self.inboxsize = myline[2]
            else:
                if myline[0] != "-":
                    f = open(self.ibfolder + myline[2] + ".sss", "r")
                    myfile = f.read()
                    f.close()
                    myemail = email.message_from_string(myfile.split("|")[1])
                    readstatus = int(myfile.split("|")[0])
                    attachstat = int(myline[3])
                                        #"sssfilenam,  email,   attachstat,   readstat,    time,   date
                    self.guilist.insert(0,[myline[2],myemail,attachstat,readstatus,myline[4],myline[5]])
                    icon=self.geticon(attachstat,readstatus)
                    self.addItem(xbmcgui.ListItem(self.parsesubject(myemail.get('subject')),myemail.get('From'),icon,icon),0)
        if len(self.guilist) == 0:self.setinboxempty()
        dialog.close()

    def checkifonserv(self,pos):
        f = open(self.ibfolder + "emid.xib", "r")
        for line in f.readlines():
            theline = line.strip("\n")
            myline = theline.split("|")
            if myline[1] != "Account Name" and myline[1] != "Server Size" and myline[1] != "Inbox Size":
                if int(myline[0]) == pos:
                    if myline[1] == "-":
                        f.close()
                        return False
                    else:
                        f.close()
                        return True
                 
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
