      ##########################
      #                        #                      
      #   XinBox (V.0.9)       #         
      #     By Stanley87       #         
      #                        #
#######                        #######             
#                                    #
#                                    #
#   A pop3 email client for XBMC     #
#                                    #
######################################
import xbmc, sys, os, XinBox_Util, default
import xbmcgui, time,traceback,XinBox_InfoDialog

TITLE = default.__scriptname__
SCRIPTPATH = default.__scriptpath__
SRCPATH = SCRIPTPATH + "src"
VERSION =  default.__version__


class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,accountsetts=False,theinbox=False,lang=False,inboxlist=False):
        self.language = lang
        self.inbox = theinbox
        self.inboxlist = inboxlist
        self.accountSettings = accountsetts
        if self.inbox == "":
            self.newinbox = True
        else:self.newinbox = False
        self.settings = self.getinboxsettings(self.inbox)

    def getinboxsettings(self,inbox):
        return self.accountSettings.getSettingInListbyname("Inboxes",inbox)
    
    def onInit(self):
        try:
            xbmcgui.lock()
            self.setupvars()
            self.setupcontrols()
            self.builsettingsList()
            xbmcgui.unlock()
        except:traceback.print_exc()

    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        self.settnames = {}
        self.settnames[1] = "Email Address"
        self.settnames[2] = "POP Server"
        self.settnames[3] = "SMTP Server"
        self.settnames[4] = "Account Name"
        self.settnames[5] = "Account Password"
        self.settnames[6] = "SERV Inbox Size"
        self.settnames[7] = "XinBox Inbox Size"
        self.keepemails = self.settings.getSetting("Keep Copy Emails")
        self.popssl = self.settings.getSetting("POP SSL")
        self.smtpssl = self.settings.getSetting("SMTP SSL")
        if self.popssl == "0":
            self.popdefault = False
            self.getControl(104).setSelected(self.popdefault)
            self.getControl(104).setLabel(self.language(90))
        else:
            self.popdefault = True
            self.getControl(104).setLabel(self.popssl)
        self.getControl(104).setSelected(self.popdefault)
        if self.smtpssl == "0":
            self.smtpdefault = False
            self.getControl(105).setLabel(self.language(90))
        else:
            self.smtpdefault = True
            self.getControl(105).setLabel(self.smtpssl)
        self.getControl(105).setSelected(self.smtpdefault)
        if self.keepemails == "True":
            self.keepemails = True
        else:self.keepemails = False
        self.getControl(106).setSelected(self.keepemails)

    def setupcontrols(self):
        self.getControl(82).setLabel(self.language(20))
        self.getControl(83).setLabel(self.language(21))
        self.getControl(61).setLabel(self.language(89))
        self.getControl(62).setLabel(self.language(61))
        if self.newinbox:
            self.getControl(62).setEnabled(False)
            self.getControl(80).setLabel(self.language(80))
            self.getControl(104).setLabel(self.language(90))
            self.getControl(105).setLabel(self.language(90))
        else:
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
        else:self.addItem(self.SettingListItem(self.language(86), '*' * len(self.settings.getSetting("Account Password"))))
        self.addItem(self.SettingListItem(self.language(87), self.settings.getSetting("SERV Inbox Size")))
        self.addItem(self.SettingListItem(self.language(88), self.settings.getSetting("XinBox Inbox Size")))
        self.addItem(self.SettingListItem(self.language(97),""))
        
    def SettingListItem(self, label1,label2):
        if label2 == "-":
            return xbmcgui.ListItem(label1,"","","")
        return xbmcgui.ListItem(label1,label2,"","")

        
    def onFocus(self, controlID):
        pass
    
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
                    self.settings.setSetting(self.settnames[curPos],value)
            elif curPos == 6 or curPos == 7:
                dialog = xbmcgui.Dialog()
                value = dialog.numeric(0, self.language(66) % curName, curName2)
                if value == "0":
                    curItem.setLabel2("")
                    self.settings.setSetting(self.settnames[curPos],"-")
                elif value != curName2:
                    curItem.setLabel2(value)
                    self.settings.setSetting(self.settnames[curPos],value)
            elif curPos == 8:
                self.keepemails = not self.keepemails
                self.getControl(106).setSelected(self.keepemails)
                self.settings.setSetting("Keep Copy Emails",str(self.keepemails))                
            else:
                value = self.showKeyboard(self.language(66) % curName,curName2)
                if value != False:
                    if value != "":
                        if curPos == 0:
                            if value in self.inboxlist:
                                self.launchinfo(94,"",self.language(93))
                            else:
                                self.accountSettings.setSettingnameInList("Inboxes",curName2,value)
                                self.inbox = value
                                self.getControl(81).setLabel(self.inbox)
                                self.getControl(62).setEnabled(True)
                                curItem.setLabel2(value)
                        else:
                            self.settings.setSetting(self.settnames[curPos],value)
                            curItem.setLabel2(value)
        elif ( controlID == 62):
            self.closeme(1)


    def closeme(self,ID):
        if ID == 0:
            self.returnID = 0
            self.close()
        else:
            self.returnID = 1
            self.close()
        
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.closeme(0)
        elif ( button_key == 'Keyboard Right Arrow' or button_key == 'DPad Right' or button_key == 'Remote Right' ):
            if focusid == 51:
                if self.getCurrentListPosition() == 2:
                    self.updatessl(91,self.popssl)
                elif self.getCurrentListPosition() == 3:
                    self.updatessl(92,self.smtpssl)
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title' ):
            if focusid == 51:
                self.launchinfo(113 + self.getCurrentListPosition(),self.getListItem(self.getCurrentListPosition()).getLabel())
            elif focusid == 61:
                self.launchinfo(122,self.language(89))
            elif focusid == 62:
                self.launchinfo(123,self.language(65))
                    
    def updatessl(self,ID,currValue):
        dialog = xbmcgui.Dialog()
        value = dialog.numeric(0, self.language(ID),currValue)
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
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",SRCPATH,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        del dialog







        
