

import xbmc,xbmcgui, time, sys, os, traceback
import XinBox_Util, email, re
from XinBox_Settings import Settings
from XinBox_EmailEngine import Email
import XinBox_Email
import XinBox_Compose
from os.path import join, exists, basename
from os import mkdir, remove, listdir
SETTINGDIR = "P:\\script_data\\XinBox\\"
ACCOUNTSDIR = "P:\\script_data\\XinBox\\Accounts\\"
from sgmllib import SGMLParser

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,lang=False,theinbox=False,account=False,title=False):
        self.srcpath = strFallbackPath
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
        self.updatesizelabel()
        
    def setupvars(self):
        self.animating = False
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
        if not self.animating:
            try:focusid = self.getFocusId()
            except:focusid = 0
            if (50 <= focusid <= 59):
                self.openemail(self.getCurrentListPosition())
            elif controlID == 65:
                self.close()
            elif controlID == 61:
                self.checkfornew()
            elif controlID == 62:
                self.sendemail()
            elif controlID == 63:
                self.cleaninbox()
            elif controlID == 66:pass
             #   self.opendrafts()

    def cleaninbox(self):
        dialog = xbmcgui.Dialog()
        if dialog.ok(self.language(210) + self.inbox, self.language(276)):  
            self.removefiles(self.ibfolder)
            self.clearList()
            self.onInit()
            return
  
    def onAction( self, action ):
        if not self.animating:
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
        w = XinBox_Email.GUI("XinBox_EmailDialog.xml",self.srcpath,"DefaultSkin",0,emailsetts=item,lang=self.language)
        w.doModal()
        returnval = w.returnvalue
        del w
        if returnval != "-":
            self.deletemail(pos, returnval)

    def sendemail(self, draft=["","","","","",None]):
        w = XinBox_Compose.GUI("XinBox_Compose.xml",self.srcpath,"DefaultSkin",0,inboxsetts=self.ibsettings,lang=self.language,inboxname=self.inbox,mydraft=draft,ibfolder=self.ibfolder)
        w.doModal()
        returnval = w.returnvalue
        print "return val = " + str(returnval)
        print "draft = " + str(draft)
        del w
        if returnval != 0:
            w = Email(self.ibsettings,self.inbox,self.account,self.language)
            w.sendemail(returnval[0],returnval[3],returnval[4],returnval[5],returnval[1],returnval[2])
            del w
        self.getControl(66).setEnabled(self.checkdrafts())


    def opendrafts(self):
        dialog = XinBox_Drafts("XinBox_Drafts.xml",self.srcpath,"DefaultSkin",ibfolder=self.ibfolder)
        dialog.doModal()
        returnval = dialog.returnval
        del dialog
        if returnval != 0:
            self.sendemail(returnval)


    def checkdrafts(self):
        try:
            f = open(self.ibfolder + "drafts.xib", "r")
            myfile = f.read()
            f.close()
            for draft in myfile.split("<>"):
                if draft != "":return True
            return False
        except:return False
        
    
    def parse_email(self, email):
        parser = html2txt()
        parser.reset()
        parser.feed(email)
        parser.close()
        return parser.output()
    
    def setupcontrols(self):
        self.getControl(66).setLabel("Drafts")
        self.getControl(66).setEnabled(self.checkdrafts())
        self.getControl(80).setLabel(self.inbox)
        self.getControl(61).setLabel(self.language(250))
        self.getControl(62).setLabel(self.language(251))
        self.getControl(63).setLabel(self.language(275))
        self.getControl(64).setLabel(self.language(252))
        self.getControl(65).setLabel(self.language(65))
        


    def checkfornew(self):
        w = Email(self.ibsettings,self.inbox,self.account,self.language)
        w.checkemail()
        newlist = w.newlist
        self.serversize = w.serversize
        self.inboxsize = w.inboxsize
        del w
        self.updatesizelabel()
        if len(newlist) != 0:
            self.updatelist(newlist)
        

    def updatesizelabel(self):
        if self.theservsize == False:
            self.getControl(81).setLabel(self.language(257) + self.getsizelabel(self.serversize))
        else:
            self.getControl(81).setEnabled(self.checksize(int(self.serversize),self.theservsize))
            self.getControl(81).setLabel(self.language(257) + self.getsizelabel(int(self.serversize)) + "/" + str(self.theservsize) +"MB")
        if self.ibxsize == False:
            self.getControl(82).setLabel(self.language(258) + self.getsizelabel(self.inboxsize))
        else:
            self.getControl(82).setEnabled(self.checksize(int(self.inboxsize),self.ibxsize))
            self.getControl(82).setLabel(self.language(258) + self.getsizelabel(int(self.inboxsize))+ "/" + str(self.ibxsize) + "MB")

    def deletemail(self, pos, setting):
        w = Email(self.ibsettings,self.inbox,self.account,self.language,True)
        w.deletemail(pos,setting)
        self.serversize = w.serversize
        self.inboxsize = w.inboxsize                
        del w
        self.updatesizelabel()
        if setting != 1:
            self.removeItem(pos)
            self.guilist.pop(pos)
            if len(self.guilist) != 0:
                self.printEmail(self.getCurrentListPosition())
            else:self.setinboxempty()
        else:
            orig = self.guilist[pos]
            new = [orig[0],orig[1],orig[2],orig[3],orig[4],orig[5],"-"]
            self.guilist.pop(pos)
            self.guilist.insert(pos, new)

    def setinboxnotemtpy(self):
        self.getControl(50).setEnabled(True)
        self.clearList()


    def setinboxempty(self):
        self.inboxsize = 0
        self.addItem(self.language(256))
        self.getControl(50).setEnabled(False)
        self.setFocusId(61)
        self.getControl(67).setText("")
        self.updatesizelabel()


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
        if size == 0:
            return self.language(259)
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
            self.guilist.insert(0,[item[0],myemail,item[1],readstatus,item[2],item[3],item[4]])
            if item[1] == 0:icon="XBnewemailnotread.png"
            else:icon="XBnewattachemailnotread.png"
            self.addItem(xbmcgui.ListItem(self.parsesubject(myemail.get('subject')).replace("\n",""),myemail.get('From').replace("\n",""),icon,icon),0)
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
        try:
            if not exists(self.ibfolder + "emid.xib"):
                self.serversize = 0
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
                if myline[1] == "Account Name":
                    self.accountname = myline[2]
                    popname = myline[3]
                    if self.accountname != self.ibsettings.getSetting("Account Name") or popname != self.ibsettings.getSetting("POP Server"):
                        self.serversize = 0
                        self.removefiles(self.ibfolder)
                        break
                elif myline[1] == "Server Size":self.serversize = int(myline[2])
                elif myline[1] == "Inbox Size":self.inboxsize = int(myline[2])
                else:
                    if myline[0] != "-":
                        f = open(self.ibfolder + myline[2] + ".sss", "r")
                        myfile = f.read()
                        f.close()
                        myemail = email.message_from_string(myfile.split("|")[1])
                        readstatus = int(myfile.split("|")[0])
                        attachstat = int(myline[3])
                                            #"sssfilenam, email, attachstat, readstat,  time,     date,    emailid
                        self.guilist.insert(0,[myline[2],myemail,attachstat,readstatus,myline[4],myline[5],myline[1]])
                        icon=self.geticon(attachstat,readstatus)
                        self.addItem(xbmcgui.ListItem(self.parsesubject(myemail.get('subject')).replace("\n",""),myemail.get('From').replace("\n",""),icon,icon),0)
            if len(self.guilist) == 0:self.setinboxempty()
            dialog.close()
        except:traceback.print_exc()

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

class XinBox_Drafts(xbmcgui.WindowXMLDialog):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,ibfolder=False):
        self.ibfolder = ibfolder
        self.control_action = XinBox_Util.setControllerAction()
        self.animating = False
        self.returnval = 0

    def onInit(self):
        self.animating = True
        xbmc.executebuiltin("Skin.SetBool(draftlist)")
        time.sleep(0.8)
        self.animating = False
        self.getdrafts()
        self.setFocusId(50)

    def onAction(self, action):
        if not self.animating:
            button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
            actionID   =  action.getId()
            try:focusid = self.getFocusId()
            except:focusid = 0
            try:control = self.getFocus()
            except: control = 0
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.animating = True
                xbmc.executebuiltin("Skin.ToggleSetting(draftlist)")
                time.sleep(0.8)
                self.animating = False
                self.close()

    def onClick(self, controlID):
        if not self.animating:
            if controlID == 50:
                self.animating = True
                self.returnval = self.draftlist[self.getCurrentListPosition()]
                xbmc.executebuiltin("Skin.ToggleSetting(draftlist)")
                time.sleep(0.8)
                self.animating = False
                self.close()

    def onFocus(self, controlID):
        pass

    def getdrafts(self):
       try:
           self.draftlist = []
           f = open(self.ibfolder + "drafts.xib", "r")
           myfile = f.read()
           f.close()
           for draft in myfile.split("<>"):
               if draft != "":
                   mydraft = draft.split("|")
                   attachments = mydraft[5].split(",")
                   myattachments = []
                   for attach in attachments:
                       if attach != "":myattachments.append([basename(attach),attach])
                   self.draftlist.append([mydraft[0],mydraft[1],mydraft[2],mydraft[3],mydraft[4],myattachments])
                   self.addItem(xbmcgui.ListItem("To: " + mydraft[0],"Subject: " + mydraft[3],"",""))
       except:traceback.print_exc()
    
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


