

import xbmc,xbmcgui, time, sys, os
import XinBox_Util
import XinBox_InfoDialog
from XinBox_EmailEngine import TestInbox

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,accountsetts=False,theinbox=False,lang=False):
        self.srcpath = strFallbackPath
        self.language = lang
        self.inbox = theinbox
        self.accountSettings = accountsetts
        if self.inbox == "":
            self.newinbox = True
        else:self.newinbox = False
        self.settings = self.getinboxsettings(self.inbox)
        self.inboxlist = self.buildinboxdict(self.accountSettings)

    def buildinboxdict(self,accountsettings):
        inboxes = []
        for set in accountsettings.getSetting("Inboxes")[1]:
            inboxes.append(set[0])
        return inboxes

    def getinboxsettings(self,inbox):
        return self.accountSettings.getSettingInListbyname("Inboxes",inbox)
    
    def onInit(self):
        xbmcgui.lock()
        self.setupvars()
        self.setupcontrols()
        self.builsettingsList()
        self.unsaveddef = self.defaultinbox
        self.setupcompsetts()
        xbmcgui.unlock()

    def setupcompsetts(self):
        self.checksettings = str(self.settings.settings)
        self.defibox = self.defaultinbox

    def checkforchanges(self):
        if str(self.settings.settings)!= self.checksettings:
            self.settchanged = "True"
        elif self.defibox != self.defaultinbox:
            self.settchanged = "True"

    def setupvars(self):
        self.settchanged = "False"
        self.renameme = []
        self.servers = XinBox_Util.getpresetservers()
        self.control_action = XinBox_Util.setControllerAction()
        self.settnames ={
        1 : "Email Address",
        2 : "POP Server",
        3 : "SMTP Server",
        4 : "Account Name",
        5 : "Account Password",
        6 : "SERV Inbox Size",
        7 : "XinBox Inbox Size",
        8 : "Keep Copy Emails",
        9 : "Email Notification",
        10 : "Default Inbox",
        11 : "Mini Mode Enabled"
        }
        if self.accountSettings.getSetting("Default Inbox") == self.inbox:
            self.defaultinbox = True
        else:self.defaultinbox = False
        self.keepemails = self.settings.getSetting("Keep Copy Emails")
        self.popssl = self.settings.getSetting("POP SSL")
        self.smtpssl = self.settings.getSetting("SMTP SSL")
        self.mmenabled = self.settings.getSetting("Mini Mode Enabled")
        if self.popssl == "0":
            self.popdefault = False
            self.getControl(104).setSelected(self.popdefault)
            self.getControl(104).setLabel(self.language(90))
        else:
            self.popdefault = True
            self.getControl(104).setLabel(self.popssl)
        if self.smtpssl == "0":
            self.smtpdefault = False
            self.getControl(105).setLabel(self.language(90))
        else:
            self.smtpdefault = True
            self.getControl(105).setLabel(self.smtpssl)
        if self.keepemails == "True":
            self.keepemails = True
        else:self.keepemails = False
        if self.mmenabled == "True":
            self.mmenabled = True
        else:self.mmenabled = False

    def setupcontrols(self):
        self.getControl(82).setLabel(self.language(20))
        self.getControl(83).setLabel(self.language(21))
        self.getControl(61).setLabel(self.language(89))
        self.getControl(108).setSelected(self.mmenabled)
        self.getControl(106).setSelected(self.keepemails)
        self.getControl(105).setSelected(self.smtpdefault)
        self.getControl(104).setSelected(self.popdefault)
        self.getControl(107).setSelected(self.defaultinbox)
        if self.newinbox:
            self.getControl(62).setLabel(self.language(61))
        else:self.getControl(62).setLabel(self.language(242))
        if self.newinbox:
            self.getControl(62).setEnabled(False)
            self.getControl(80).setLabel(self.language(80))
            self.getControl(104).setLabel(self.language(90))
            self.getControl(105).setLabel(self.language(90))
        else:
            self.getControl(62).setEnabled(True)
            self.getControl(80).setLabel(self.language(81))
            self.getControl(81).setLabel(self.inbox)

    def builsettingsList(self):
        self.addItem(self.SettingListItem(self.language(82), self.inbox))
        self.addItem(self.SettingListItem(self.language(96), self.settings.getSetting("Email Address")))
        self.addItem(self.SettingListItem(self.language(83), self.settings.getSetting("POP Server")))
        self.addItem(self.SettingListItem(self.language(84), self.settings.getSetting("SMTP Server")))
        self.addItem(self.SettingListItem(self.language(85), self.settings.getSetting("Account Name")))
        if self.settings.getSetting("Account Password") == "-":
            self.addItem(self.SettingListItem(self.language(86), ""))
        else:self.addItem(self.SettingListItem(self.language(86), '*' * len(self.settings.getSetting("Account Password").decode("hex"))))
        self.addItem(self.SettingListItem(self.language(87), self.settings.getSetting("SERV Inbox Size")))
        self.addItem(self.SettingListItem(self.language(88), self.settings.getSetting("XinBox Inbox Size")))
        self.addItem(self.SettingListItem(self.language(97),""))
        self.addItem(self.SettingListItem(self.language(240),self.settings.getSetting("Email Notification")))
        self.addItem(self.SettingListItem(self.language(243),""))
        self.addItem(self.SettingListItem(self.language(350),""))
        
    def SettingListItem(self, label1,label2):
        if label2 == "-":
            return xbmcgui.ListItem(label1,"","","")
        elif label2 == "0":
            return xbmcgui.ListItem(label1,self.language(98),"","")
        return xbmcgui.ListItem(label1,label2,"","")

        
    def onFocus(self, controlID):
        pass

    def updatesizes(self, value, curPos, curName2=None):
        if value == "0":
            self.getListItem(curPos).setLabel2(self.language(98))
            self.settings.setSetting(self.settnames[curPos],"0")
        elif value != curName2:
            self.getListItem(curPos).setLabel2(value)
            self.settings.setSetting(self.settnames[curPos],value)        
    
    def onClick(self, controlID):
        if ( controlID == 51):
            curPos  = self.getCurrentListPosition()
            curItem = self.getListItem(curPos)
            curName = curItem.getLabel()
            curName2 = curItem.getLabel2()
            if curPos == 5:
                value = self.showKeyboard(self.language(66) % curName,"",1)
                if value != False:
                    if value == "":
                        curItem.setLabel2("")
                        self.settings.setSetting(self.settnames[curPos],"-")
                    else:
                        curItem.setLabel2('*' * len(value))
                        self.settings.setSetting(self.settnames[curPos],value.encode("hex"))
            elif curPos == 6 or curPos == 7:
                dialog = xbmcgui.Dialog()
                value = dialog.numeric(0, self.language(66) % curName, curName2)
                self.updatesizes(value,curPos,curName2)
            elif curPos == 8:
                self.keepemails = not self.keepemails
                self.getControl(106).setSelected(self.keepemails)
                self.settings.setSetting(self.settnames[curPos],str(self.keepemails))
            elif curPos == 10:
                self.defaultinbox = not self.defaultinbox
                self.getControl(107).setSelected(self.defaultinbox)
            elif curPos == 11:
                self.mmenabled = not self.mmenabled
                self.getControl(108).setSelected(self.mmenabled)
                self.settings.setSetting(self.settnames[curPos],str(self.mmenabled))
            elif curPos == 9:
                dialog = xbmcgui.Dialog()
                value = dialog.browse(1, self.language(241), "files","",False,False,self.settings.getSetting("Email Notification"))
                if value != self.settings.getSetting("Email Notification"):
                    curItem.setLabel2(value)
                    self.settings.setSetting(self.settnames[curPos],value)
            else:
                value = self.showKeyboard(self.language(66) % curName,curName2)
                if value != False and value != "" and value !=curName2:
                        if curPos == 0:
                            if value in self.inboxlist:
                                self.launchinfo(94,"",self.language(93))
                            else:
                                self.renameme = [curName2,value]
                                self.accountSettings.setSettingnameInList("Inboxes",curName2,value)
                                self.settings.setSetting("Inbox Hash",str(hash(value)))
                                self.inboxlist = self.buildinboxdict(self.accountSettings)
                                self.inbox = value
                                self.getControl(62).setEnabled(True)
                                curItem.setLabel2(value)
                        elif curPos == 1:
                            self.settings.setSetting(self.settnames[curPos],value)
                            curItem.setLabel2(value)
                            if "@" in value:
                                server = value.split("@")[1]
                                name = value.split("@")[0]
                                self.settings.setSetting("Account Name",name)
                                self.getListItem(4).setLabel2(name)
                                if self.servers.has_key(server):
                                    self.settings.setSetting("POP Server",self.servers[server][0])
                                    self.getListItem(2).setLabel2(self.servers[server][0])
                                    self.settings.setSetting("SMTP Server",self.servers[server][1])
                                    self.getListItem(3).setLabel2(self.servers[server][1])
                                    self.updatessl(91,"",self.servers[server][2])
                                    self.updatessl(92,"",self.servers[server][3])
                                    self.updatesizes(self.servers[server][4],6)
                        else:
                            self.settings.setSetting(self.settnames[curPos],value)
                            curItem.setLabel2(value)
        elif ( controlID == 61):
            w = TestInbox(self.settings,self.language,self.srcpath)
            w.testinput()
            del w
        elif ( controlID == 62):
            self.checkforchanges()
            if self.defaultinbox:
                self.accountSettings.setSetting("Default Inbox", self.inbox)
            else:
                if self.accountSettings.getSetting("Default Inbox") == self.inbox:
                    self.accountSettings.setSetting("Default Inbox", "-")
            self.closeme(1)


    def closeme(self,ID):
        if ID == 0:self.returnID = 0
        else:self.returnID = 1
        self.close()
        
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.settchanged = "False"
            self.closeme(0)
        elif ( button_key == 'Keyboard Right Arrow' or button_key == 'DPad Right' or button_key == 'Remote Right' ):
            if focusid == 51:
                if self.getCurrentListPosition() == 2:
                    self.updatessl(91,self.popssl)
                elif self.getCurrentListPosition() == 3:
                    self.updatessl(92,self.smtpssl)
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title' ):
            if focusid == 51:
                if self.getCurrentListPosition() != 9 and self.getCurrentListPosition() != 10:
                    self.launchinfo(113 + self.getCurrentListPosition(),self.getListItem(self.getCurrentListPosition()).getLabel())
                elif self.getCurrentListPosition() == 10:
                    self.launchinfo(131,self.getListItem(self.getCurrentListPosition()).getLabel())
                else:
                    self.launchinfo(129,self.getListItem(self.getCurrentListPosition()).getLabel())
            elif focusid == 61:
                self.launchinfo(122,self.language(89))
            elif focusid == 62:
                if self.newinbox:
                    self.launchinfo(123,self.language(61))
                else:self.launchinfo(130,self.language(242))
                    
    def updatessl(self,ID,currValue, myvalue=False):
        if myvalue == False:dialog = xbmcgui.Dialog()
        if myvalue == False:value = dialog.numeric(0, self.language(ID),currValue)
        else:
            value=myvalue
            currValue = None
        if value != currValue:
            if ID == 91:
                self.popssl = value
                if value == "0":
                    self.popdefault = False
                    self.getControl(104).setLabel(self.language(90))
                else:
                    self.popdefault = True
                    self.getControl(104).setLabel(self.popssl)
                self.getControl(104).setSelected(self.popdefault)
                self.settings.setSetting("POP SSL",self.popssl)
            else:
                self.smtpssl = value
                if value == "0":
                    self.smtpdefault = False
                    self.getControl(105).setLabel(self.language(90))
                else:
                    self.smtpdefault = True
                    self.getControl(105).setLabel(self.smtpssl)
                self.getControl(105).setSelected(self.smtpdefault)
                self.settings.setSetting("SMTP SSL",self.smtpssl)

    def showKeyboard(self, heading,default="",hidden=0):
        keyboard = xbmc.Keyboard(default,heading)
        if hidden == 1:keyboard.setHiddenInput(True)
        keyboard.doModal()
        if hidden == 1:keyboard.setHiddenInput(False)
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return False


    def launchinfo(self, focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.srcpath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        del dialog







        
