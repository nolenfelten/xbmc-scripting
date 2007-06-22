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
import xbmcgui, time
from XinBox_Language import Language

TITLE = default.__scriptname__
SCRIPTPATH = default.__scriptpath__
SRCPATH = SCRIPTPATH + "src"
VERSION =  default.__version__

lang = Language(TITLE)
lang.load(SRCPATH + "//language")
_ = lang.string

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,notnewaccount=True,inboxsetts=False,accountsetts=False,theinbox="XinBoxNew"):
        try:
            self.language = _
            self.inbox = theinbox
            self.settings = inboxsetts
            self.accountsetts = accountsetts
            if self.inbox == "XinBoxNew":
                self.newinbox = True
                self.settings = ["-","-","-","-","-","-","-","0","0"]
                self.mysettings = self.settings
            else:self.newinbox = False
            if notnewaccount:
                self.newaccount = False
            else:self.newaccount = True
        except:traceback.print_exc()

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
        if not self.newaccount:
            self.mysettings = {}
            for x in range (0,9):
                self.mysettings[x] = self.settings[x]
            self.popssl = self.settings[7]
            self.smtpssl = self.settings[8]
        else:
            self.settnames = {}
            self.settnames[1] = "POP Server"
            self.settnames[2] = "SMTP Server"
            self.settnames[3] = "Account Name"
            self.settnames[4] = "Account Password"
            self.settnames[5] = "SERV Inbox Size"
            self.settnames[6] = "XinBox Inbox Size"
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

    def setupcontrols(self):
        self.getControl(61).setLabel(self.language(89))
        self.getControl(62).setLabel(self.language(65))
        if self.newinbox:
            self.getControl(80).setLabel(self.language(80))
            self.getControl(104).setLabel(self.language(90))
            self.getControl(105).setLabel(self.language(90))
        else:
            self.getControl(80).setLabel(self.language(81))
            self.getControl(81).setLabel(self.inbox)

    def builsettingsList(self):
        if not self.newaccount:
                self.addItem(self.SettingListItem(self.language(82), self.settings[0]))
                self.addItem(self.SettingListItem(self.language(83), self.settings[1]))
                self.addItem(self.SettingListItem(self.language(84), self.settings[2]))
                self.addItem(self.SettingListItem(self.language(85), self.settings[3]))
                if self.settings[4] == "-":
                    self.addItem(self.SettingListItem(self.language(86), ""))
                else:self.addItem(self.SettingListItem(self.language(86), '*' * len(self.settings[4])))
                self.addItem(self.SettingListItem(self.language(87), self.settings[5]))
                self.addItem(self.SettingListItem(self.language(88), self.settings[6]))               
        else:
            self.addItem(self.SettingListItem(self.language(82), self.inbox))
            self.addItem(self.SettingListItem(self.language(83), self.settings.getSetting("POP Server")))
            self.addItem(self.SettingListItem(self.language(84), self.settings.getSetting("SMTP Server")))
            self.addItem(self.SettingListItem(self.language(85), self.settings.getSetting("Account Name")))
            if self.settings.getSetting("Account Password") == "-":
                self.addItem(self.SettingListItem(self.language(86), ""))
            else:self.addItem(self.SettingListItem(self.language(86), '*' * len(self.settings.getSetting("Account Password"))))
            self.addItem(self.SettingListItem(self.language(87), self.settings.getSetting("SERV Inbox Size")))
            self.addItem(self.SettingListItem(self.language(88), self.settings.getSetting("XinBox Inbox Size")))

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
            if curPos == 4:
                value = self.showKeyboard(self.language(66) % curName,"",1)
                if value == "":
                    curItem.setLabel2("")
                    if not self.newaccount:self.mysettings[curPos] = "-"
                    else:
                        self.settings.setSetting(self.settnames[curPos],"-")
                else:
                    curItem.setLabel2('*' * len(value))
                    if not self.newaccount:self.mysettings[curPos] = value
                    else:
                        self.settings.setSetting(self.settnames[curPos],value)
            elif curPos == 5 or curPos == 6:
                dialog = xbmcgui.Dialog()
                value = dialog.numeric(0, self.language(66) % curName, curName2)
                if value == "0":
                    curItem.setLabel2("")
                    if not self.newaccount:self.mysettings[curPos] = "-"
                    else:
                        self.settings.setSetting(self.settnames[curPos],"-")
                elif value != curName2:
                    curItem.setLabel2(value)
                    if not self.newaccount:self.mysettings[curPos] = value
                    else:
                        self.settings.setSetting(self.settnames[curPos],value)    
            else:
                value = self.showKeyboard(self.language(66) % curName,curName2)
                if value != "":
                    curItem.setLabel2(value)
                 #   self.inbox = value 
                    if self.newinbox:
                        self.mysettings[curPos] = value
                    else:
                        if curPos == 0:
                            if self.newaccount:
                                self.accountsetts.setSettingnameInList("Inboxes",curName2,value)                            
                        else:self.settings.setSetting(self.settnames[curPos],value)
        elif ( controlID == 62):
            self.closeme()

    def closeme(self):
        if self.newinbox:
            self.returnvalue = 1
            self.returnsettings = self.mysettings
        elif not self.newinbox and self.newaccount:
            self.returnvalue = 2
            self.returnsettings = self.mysettings
        elif not self.newinbox and not self.newaccount:
            self.returnvalue = 3
            self.returnsettings = self.accountsetts
        self.close()
            
                    
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.mysettings = False
            self.closeme()
        elif ( button_key == 'Keyboard Right Arrow' or button_key == 'DPad Right' or button_key == 'Remote Right' ):
            if focusid == 51:
                if self.getCurrentListPosition() == 1:
                    self.updatessl(91,self.popssl)
                elif self.getCurrentListPosition() == 2:
                    self.updatessl(92,self.smtpssl)
                    
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
                if not self.newaccount:
                    self.mysettings[7] = self.popssl
                else:
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
                if not self.newaccount:
                    self.mysettings[8] = self.smtpssl
                else:
                    self.settings.setSetting("SMTP SSL",self.smtpssl)

    def showKeyboard(self, heading,default="",hidden=0):
        keyboard = xbmc.Keyboard(default,heading)
        if hidden == 1:keyboard.setHiddenInput(True)
        keyboard.doModal()
        if hidden == 1:keyboard.setHiddenInput(False)
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return default













        
