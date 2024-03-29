

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
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,lang=False,theinbox=False,account=False,title=False,mmflag=0):
        self.init = 0
        self.mmflag = mmflag
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
        if self.init == 0:
            self.init = 1
            self.loadsettings()
            self.setupvars()
            self.setupcontrols()
            self.emaillistprepare()
            self.updatesizelabel()
        xbmcgui.unlock()
        self.checkauto()

    def checkauto(self):
        if self.accountsettings.getSetting("Auto Check") == "True":
            self.checkfornew()
        
    def setupvars(self):
        self.exitflag = 0
        self.removeme = []
        self.emnotread = 0
        self.nwmail = 0
        self.chicon = []
        self.markunread = []
        self.animating = False
        self.guilist = []
        self.control_action = XinBox_Util.setControllerAction()
        if self.accountsettings.getSetting("XinBox Promote") == "True":
            self.promote = True
        else:self.promote = False
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
                self.exitflag = 1
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
            self.emnotread = 0
            self.nwmail = 0
            dialog.ok(self.language(49),self.language(278))
            return

    def setupcontrols(self):
        self.getControl(80).setLabel(self.inbox)
        self.getControl(61).setLabel(self.language(250))
        self.getControl(62).setLabel(self.language(251))
        self.getControl(63).setLabel(self.language(275))
        self.getControl(64).setLabel(self.language(65))
        self.getControl(65).setLabel(self.language(370))
        
    def onAction( self, action ):
        if not self.animating:
            button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
            actionID   =  action.getId()
            try:focusid = self.getFocusId()
            except:focusid = 0
            try:control = self.getFocus()
            except: control = 0
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu' ):
                if self.mmflag == 1:
                    self.exitflag = 1
                self.exitme()
            elif (50 <= focusid <= 59):
                if ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Info' ):
                    self.launchinfo(136,self.language(225))
                elif ( button_key == 'Keyboard TAB Button' or button_key == 'White Button' or button_key == 'Remote Display'):
                    self.addcontact(self.getCurrentListPosition())
                elif ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Title'):
                    self.deletemail(self.getCurrentListPosition(), 0)
                else:self.printEmail(self.getCurrentListPosition())
            elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Info' ):
                if focusid == 61:
                    self.launchinfo(132,self.language(250))
                elif focusid == 62:
                    self.launchinfo(133,self.language(251))
                elif focusid == 63:
                    self.launchinfo(134,self.language(275))
                elif focusid == 64:
                    self.launchinfo(128,self.language(65))
                elif focusid == 65:
                    self.launchinfo(156,self.language(370))
                    
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
        f = open(self.ibfolder + self.guilist[selected][0] + ".sss", "r")                
        myemail = email.message_from_string(f.read())
        f.close()
        self.curremail = myemail
        if myemail.is_multipart():
            for part in myemail.walk():
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    self.getControl(67).setText(self.parse_email(part.get_payload()))
                    break
        else:self.getControl(67).setText(self.parse_email(myemail.get_payload()))
        

    def openemail(self, pos):
        try:
            item = self.guilist[pos]
            self.guilist.pop(pos)
            self.guilist.insert(pos, [item[0],item[1],item[2],1,item[4],item[5],item[6],item[7]])
            if item[3] != 1:
                self.chicon.append(item[0])
                if item[2] == 0:icon = "XBemailread.png"
                else:icon = "XBemailreadattach.png"
                self.getListItem(pos).setThumbnailImage(icon)
                if item[7] == 1:
                    self.nwmail -= 1
                else:self.emnotread -= 1
                self.updatesizelabel()
            w = XinBox_Email.GUI("XinBox_EmailDialog.xml",self.srcpath,"DefaultSkin",0,emailsetts=item,lang=self.language,myemail=self.curremail)
            w.doModal()
            returnval = w.returnvalue
            replyvalue = w.replyvalue
            unreadvalue = w.unreadvalue
            del w
            if replyvalue != 0:
                self.sendemail(replyvalue)
            elif returnval != "-":
                self.deletemail(pos, returnval)
            elif unreadvalue == 1:
                self.guilist.pop(pos)
                self.guilist.insert(pos, [item[0],item[1],item[2],0,item[4],item[5],item[6],item[7]])
                self.emnotread += 1
                if item[2] == 0:icon = "XBemailnotread.png"
                else:icon = "XBemailnotreadattach.png"
                self.markunread.append(item[0])
                self.getListItem(pos).setThumbnailImage(icon)
                self.updatesizelabel()
        except:traceback.print_exc()

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
                    if myline[2] in self.removeme:pass
                    if myline[2] in self.markunread:
                        writelist.append(myline[0] + "|" + myline[1] + "|" + myline[2] + "|" + myline[3]+ "|" + myline[4]+ "|" + myline[5] + "|0|0|" + myline[8] + "|" + myline[9] + "\n")
                    elif myline[2] in self.chicon:        
                        writelist.append(myline[0] + "|" + myline[1] + "|" + myline[2] + "|" + myline[3]+ "|" + myline[4]+ "|" + myline[5] + "|1|0|" + myline[8] + "|" + myline[9] + "\n")
                    else:writelist.append(myline[0] + "|" + myline[1] + "|" + myline[2] + "|" + myline[3]+ "|" + myline[4]+ "|" + myline[5] + "|" + myline[6]+ "|0|" + myline[8]+ "|" + myline[9]+ "\n")
                else:writelist.append(line)
            f.close()
            f = open(self.ibfolder + "emid.xib", "w")
            f.writelines(writelist)
            f.close()
            dialog.close()

    def sendemail(self, draft=["","","","","",None]):
        w = XinBox_Compose.GUI("XinBox_Compose.xml",self.srcpath,"DefaultSkin",0,inboxsetts=self.ibsettings,lang=self.language,inboxname=self.inbox,mydraft=draft,ibfolder=self.ibfolder,account=self.account,setts=self.settings)
        w.doModal()
        returnval = w.returnvalue
        del w
        if returnval != 0:
            w = Email(self.ibsettings,self.inbox,self.account,self.language)
            w.sendemail(returnval[0],returnval[3],returnval[4],returnval[5],returnval[1],returnval[2],self.promote)
            del w

    def launchmycontacts(self):
        w = XinBox_Contacts.GUI("XinBox_Contacts.xml",self.srcpath,"DefaultSkin",0,accountname=self.account,setts=self.settings,lang=self.language)
        w.doModal()
        returnval = w.returnval
        del w
        if returnval != 0:
            self.sendemail([returnval,"","","","",[]])

    def parse_email(self, email):
        email = email.decode("quopri_codec")
        parser = html2txt()
        parser.reset()
        parser.feed(email)
        parser.close()
        return parser.output()
        
    def checkfornew(self):
        w = Email(self.ibsettings,self.inbox,self.account,self.language,False,self.accountsettings.getSetting("Email Dialogs"))
        w.checkemail()
        newlist = w.newlist
        self.serversize = w.serversize
        self.inboxsize = w.inboxsize
        del w
        if len(newlist) != 0:
            self.updatelist(newlist)
        self.updatesizelabel()
        
    def updatesizelabel(self):
        if len(self.guilist) != 0:
            self.getControl(83).setLabel(self.language(283) + str(self.nwmail) + " " + self.language(284) + str(self.emnotread) + " " + self.language(285) + " " + str(self.getListSize()))
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
        if setting != 1:
            self.removeItem(pos)
            if self.guilist[pos][3] == 0:
                if self.guilist[pos][7] == 0:
                    self.emnotread -= 1
                else:self.nwmail -= 1
            self.guilist.pop(pos)
            if len(self.guilist) != 0:
                self.updatesizelabel()
                self.printEmail(self.getCurrentListPosition())
            else:self.setinboxempty()
        else:
            orig = self.guilist[pos]
            new = [orig[0],orig[1],orig[2],orig[3],orig[4],orig[5],"-",orig[7]]
            self.guilist.pop(pos)
            self.guilist.insert(pos, new)
            self.updatesizelabel()

    def setinboxnotemtpy(self):
        self.getControl(50).setEnabled(True)
        self.clearList()


    def setinboxempty(self):
        self.getControl(83).setLabel(self.language(283) + "0 " + self.language(284) + "0 " + self.language(285) + "0")
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
        xbmcgui.lock()
        for i,item in enumerate(newlist):
            dialog.update((i*100)/len(newlist),self.language(254),"")
            self.guilist.insert(0,[item[0],item[5],item[1],0,item[2],item[3],item[4],1])
            icon = self.geticon(item[1],0,1)
            try:
                self.addItem(xbmcgui.ListItem(item[5][0],item[5][1],icon,icon),0)
            except:self.addItem("In-Compatible Subject or From Header")
        xbmcgui.unlock()
        dialog.close()

    def geticon(self,attstat, readstat, newstatus):
        if newstatus == 0:
            if attstat == 0 and readstat == 0:
                self.emnotread += 1
                return "XBemailnotread.png"
            elif attstat == 0 and readstat == 1:return "XBemailread.png"
            elif attstat == 1 and readstat == 0:
                self.emnotread += 1
                return "XBemailnotreadattach.png"
            elif attstat == 1 and readstat == 1:return "XBemailreadattach.png"
        else:
            if attstat == 0:
                self.nwmail += 1
                return "XBnewemail.png"
            else:
                self.nwmail += 1
                return "XBnewattachemail.png"

    def emaillistprepare(self):
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
                        if exists(self.ibfolder + myline[2] + ".sss"):
                            self.guilist.insert(0,[myline[2],[myline[8],myline[9]],int(myline[3]),int(myline[6]),myline[4],myline[5],myline[1],int(myline[7])])
            dialog.close()                                      #subject and from
            if len(self.guilist) == 0:self.setinboxempty()
            else:self.additems(self.guilist)
        except:traceback.print_exc()

    def additems(self, mylist):
        for item in mylist:
            icon=self.geticon(int(item[2]),int(item[3]), int(item[7]))
            self.addItem(xbmcgui.ListItem(item[1][0],item[1][1],icon,icon))

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


