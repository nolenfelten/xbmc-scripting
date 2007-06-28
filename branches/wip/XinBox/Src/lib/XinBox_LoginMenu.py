

import xbmc, xbmcgui, time, sys, os

import XinBox_Util
from XinBox_AccountSettings import Account_Settings
from XinBox_Settings import Settings
import XinBox_InfoDialog
import XinBox_MyAccountMenu

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,lang=False,title=False):
        self.scriptPath = strFallbackPath
        self.language = lang
        self.title = title

    def buildaccounts(self):
        accounts = []
        for set in self.settings.getSetting("Accounts")[1]:
            accounts.append(set[0])
        return accounts

    def loadsettings(self):
        self.settings = Settings("XinBox_Settings.xml",self.title,"")

    def getaccountsettings(self,account):
        return self.settings.getSettingInListbyname("Accounts",account)

    def getinboxsettings(self,inbox):
        return self.accountSettings.getSettingInListbyname("Inboxes",inbox)
        
    def onInit(self):
        xbmcgui.lock()
        self.loadsettings()
        self.setupvars()
        self.setupcontrols()
        xbmcgui.unlock()

    def setupcontrols(self):
        self.clearList()
        MenuLabel = self.getControl(80)
        MenuLabel.setLabel(self.language(30))
        self.getControl(82).setLabel(self.language(20))
        self.getControl(83).setLabel(self.language(21))
        for account in self.buildaccounts():
            self.addItem(account)

    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        accountname = self.getListItem(self.getCurrentListPosition()).getLabel()
        self.accountSettings = self.getaccountsettings(accountname)
        accountpass = self.accountSettings.getSetting("Account Password")
        if accountpass == "-":
            self.launchaccountmenu(accountname)
        else:
            value = self.showKeyboard(self.language(31),"",1)
            if value != "":
                if value == accountpass.decode("hex"):
                    self.launchaccountmenu(accountname)
                else:self.launchinfo("","",self.language(93),self.language(32))
                                                                    
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.close()
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title' ):
            self.launchinfo(124,self.getListItem(self.getCurrentListPosition()).getLabel())

    def launchaccountmenu(self, account):
        w = XinBox_MyAccountMenu.GUI("XinBox_AccountMenu.xml",self.scriptPath,"DefaultSkin",lang=self.language,theaccount=account,title=self.title)
        w.doModal()
        del w

    def launchinfo(self, focusid, label,heading=False,text=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.scriptPath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading,thetext=text)
        dialog.doModal()
        value = dialog.value
        del dialog
        return value

    def showKeyboard(self, heading,default="",hidden=0):
        keyboard = xbmc.Keyboard(default,heading)
        if hidden == 1:keyboard.setHiddenInput(True)
        keyboard.doModal()
        if hidden == 1:keyboard.setHiddenInput(False)
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:return default

