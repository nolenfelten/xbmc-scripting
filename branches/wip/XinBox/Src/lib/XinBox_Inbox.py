

import xbmc,xbmcgui, time, sys, os, traceback
import XinBox_Util, email, re
from XinBox_Settings import Settings
from XinBox_EmailEngine import Email
import XinBox_Email
import XinBox_Compose
import XinBox_InfoDialog
import XinBox_Contacts
from os.path import join, exists, basename
from os import mkdir, remove, listdir
from sgmllib import SGMLParser

SETTINGDIR = XinBox_Util.__settingdir__
ACCOUNTSDIR = XinBox_Util.__accountsdir__
TEMPFOLDER = XinBox_Util.__tempdir__

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
        self.loadsettings()
        self.setupvars()
        xbmcgui.lock()
        self.setupcontrols()
        xbmcgui.unlock()
        self.reademid()
        self.updatesizelabel()
        
    def setupvars(self):
        self.chicon = []
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
                self.change = True
                self.openemail(self.getCurrentListPosition())
            elif controlID == 61:
                self.checkfornew()
            elif controlID == 62:
                self.sendemail()
            elif controlID == 63:
                self.cleaninbox()
            elif controlID == 64:
                self.exitme()
            elif controlID == 65:
                self.launchmycontacts()

    def exitme(self):
        self.animating = True
        self.updateicons()
        self.removefiles(TEMPFOLDER)
        self.animating = False
        self.close()

    def cleaninbox(self):
        dialog = xbmcgui.Dialog()
        if dialog.yesno(self.language(210) + self.inbox, self.language(276),self.language(277)):  
            self.removefiles(self.ibfolder)
            self.clearList()
            self.setinboxempty()
            dialog.ok(self.language(49),self.language(278))
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
                self.exitme()
            elif (50 <= focusid <= 59):
                if ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title' ):
                    self.launchinfo(136,self.language(225))
                elif ( button_key == 'Keyboard Ctrl Button' or button_key == 'B Button'):
                    self.addcontact(self.getCurrentListPosition())
                else:self.printEmail(self.getCurrentListPosition())
            elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title' ):
                if focusid == 61:
                    self.launchinfo(132,self.language(250))
                elif focusid == 62:
                    self.launchinfo(133,self.language(251))
                elif focusid == 63:
                    self.launchinfo(134,self.language(275))
                elif focusid == 64:
                    self.launchinfo(128,self.language(65))
                    
    def getem(self, myfrom):
        myre = re.search('<([^>]*)>',myfrom)
        if myre == None:
            return myfrom
        else:return myre.group(1)

    def getcon(self, myfrom, contactemail):
        myre = myfrom.replace("<" + contactemail + ">","").replace('"','').strip()
        if myre == myfrom or myre == "":return self.editcontactname(contactemail.split("@")[0])
        else:
            if myre in self.contacts:
                dialog = xbmcgui.Dialog()
                dialog.ok(self.language(93), self.language(373))
                return self.editcontactname(myre)
            else:return myre

    def editcontactname(self, default):
        value = self.showKeyboard(self.language(372),default)
        if value != False and value != "":
            if value in self.contacts:
                dialog = xbmcgui.Dialog()
                dialog.ok(self.language(93), self.language(373))
                return False
            else:return value
        else:return False

    def buildcontactlist(self):
        self.contacts  = []
        for set in self.accountsettings.getSetting("Contacts")[1]:
            self.contacts.append(set[0])

    def addcontact(self, pos):
        self.buildcontactlist()
        contact = self.getListItem(pos).getLabel2()
        contactemail = self.getem(contact)
        contname = self.getcon(contact,contactemail)
        if contname != False:
            self.accountsettings.addSettingInList("Contacts",contname,contactemail,"text")
            self.settings.saveXMLfromArray()
            dialog = xbmcgui.Dialog()
            dialog.ok(self.language(49), self.language(378))            
                    
    def launchinfo(self, focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.srcpath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        value = dialog.value
        del dialog
        return value

                    
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
        self.guilist.pop(pos)
        self.guilist.insert(pos, [item[0],item[1],item[2],1,item[4],item[5],item[6]])
        if item[3] != 1:
            self.chicon.append(str(self.getListSize() - 1 - pos))
            if item[2] == 0:icon = "XBemailread.png"
            else:icon = "XBemailreadattach.png"
            self.getListItem(pos).setThumbnailImage(icon)
        w = XinBox_Email.GUI("XinBox_EmailDialog.xml",self.srcpath,"DefaultSkin",0,emailsetts=item,lang=self.language)
        w.doModal()
        returnval = w.returnvalue
        replyvalue = w.replyvalue
        del w
        if replyvalue != 0:
            self.sendemail(replyvalue)
        if returnval != "-":
            self.deletemail(pos, returnval)

    def updateicons(self):
        if exists(self.ibfolder + "emid.xib"):
            dialog = xbmcgui.DialogProgress()
            dialog.create(self.language(210) + self.inbox, self.language(282))
            writelist = []
            f = open(self.ibfolder + "emid.xib", "r")
            for line in f.readlines():
                myarray = False
                theline = line.strip("\n")
                myline = theline.split("|")
                if myline[0] != "-":
                    if myline[0] in self.chicon:
                        writelist.append(myline[0] + "|" + myline[1] + "|" + myline[2] + "|" + myline[3]+ "|" + myline[4]+ "|" + myline[5] + "|1|0\n")
                    else:writelist.append(myline[0] + "|" + myline[1] + "|" + myline[2] + "|" + myline[3]+ "|" + myline[4]+ "|" + myline[5] + "|" + myline[6]+ "|0\n")
                else:writelist.append(line)
            f.close()
            f = open(self.ibfolder + "emid.xib", "w")
            f.writelines(writelist)
            f.close()
            dialog.close()

    def sendemail(self, draft=["","","","","",None]):
        try:
            w = XinBox_Compose.GUI("XinBox_Compose.xml",self.srcpath,"DefaultSkin",0,inboxsetts=self.ibsettings,lang=self.language,inboxname=self.inbox,mydraft=draft,ibfolder=self.ibfolder,account=self.account,setts=self.settings)
            w.doModal()
            returnval = w.returnvalue
            del w
            if returnval != 0:
                print "hey oh"
                w = Email(self.ibsettings,self.inbox,self.account,self.language)
                w.sendemail(returnval[0],returnval[3],returnval[4],returnval[5],returnval[1],returnval[2])
                del w
        except:traceback.print_exc()


    def launchmycontacts(self):
        w = XinBox_Contacts.GUI("XinBox_Contacts.xml",self.srcpath,"DefaultSkin",0,accountname=self.account,setts=self.settings,lang=self.language)
        w.doModal()
        returnval = w.returnval
        del w
        if returnval != 0:
            self.sendemail([returnval,"","","","",[]])
    
    def parse_email(self, email):
        email = email.replace("\t","")
        parser = html2txt()
        parser.reset()
        parser.feed(email)
        parser.close()
        return parser.output()
    
    def setupcontrols(self):
        self.getControl(80).setLabel(self.inbox)
        self.getControl(61).setLabel(self.language(250))
        self.getControl(62).setLabel(self.language(251))
        self.getControl(63).setLabel(self.language(275))
        self.getControl(64).setLabel(self.language(65))
        self.getControl(65).setLabel(self.language(370))
        


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
            new = [orig[0],orig[1],orig[2],orig[3],orig[4],orig[5],"-",]
            self.guilist.pop(pos)
            self.guilist.insert(pos, new)

    def setinboxnotemtpy(self):
        self.getControl(50).setEnabled(True)
        self.clearList()


    def setinboxempty(self):
        self.guilist = []
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
            myemail = email.message_from_string(f.read())
            f.close()
            self.guilist.insert(0,[item[0],myemail,item[1],0,item[2],item[3],item[4]])
            if item[1] == 0:icon="XBnewemail.png"
            else:icon="XBnewattachemail.png"
            self.addItem(xbmcgui.ListItem(self.parsesubject(myemail.get('subject')).replace("\n",""),myemail.get('From').replace("\n",""),icon,icon),0)
        dialog.close()

    def geticon(self,attstat, readstat, newstatus):
        if newstatus == 0:
            if attstat == 0 and readstat == 0:return "XBemailnotread.png"
            elif attstat == 0 and readstat == 1:return "XBemailread.png"
            elif attstat == 1 and readstat == 0:return "XBemailnotreadattach.png"
            elif attstat == 1 and readstat == 1:return "XBemailreadattach.png"
        else:
            if attstat == 0:return "XBnewemail.png"
            else:return "XBnewattachemail.png"
  
    def parsesubject(self, subject):
        if subject == "":
            return self.language(255)
        else:return subject

    def reademid(self):
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
                    myemail = email.message_from_string(f.read())
                    f.close()
                    readstatus = int(myline[6])
                    newstatus = int(myline[7])
                    attachstat = int(myline[3])
                    self.guilist.insert(0,[myline[2],myemail,attachstat,readstatus,myline[4],myline[5],myline[1]])
                    icon=self.geticon(attachstat,readstatus, newstatus)
                    self.addItem(xbmcgui.ListItem(self.parsesubject(myemail.get('subject')).replace("\n",""),myemail.get('From').replace("\n",""),icon,icon),0)
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

    def showKeyboard(self, heading,default=""):
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return False
    
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


