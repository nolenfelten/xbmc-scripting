

import xbmc, xbmcgui, time, sys, os

import default
import XinBox_InfoDialog
import XinBox_Util
import XinBox_LoginMenu
from XinBox_Settings import Settings
from XinBox_AccountSettings import Account_Settings
from XinBox_Language import Language
import XinBox_MyAccountMenu

TITLE = default.__scriptname__
SCRIPTPATH = default.__scriptpath__
SRCPATH = SCRIPTPATH + "src"
VERSION =  default.__version__

lang = Language(TITLE)
lang.load(SRCPATH + "//language")
_ = lang.string

defSettings = {"Accounts": [['Account',[]],"list"]}

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        self.init = 0
        print "Welcome to XinBox"

    def loadsettings(self):
        self.settings = Settings("XinBox_Settings.xml",TITLE,defSettings)     

    def onInit(self):
        xbmcgui.lock()
        self.loadsettings()
        self.accounts = self.buildaccounts()
        if self.init == 0:
            self.init = 1
            self.checkdefault()
        self.setupvars()
        self.setupcontrols()
        xbmcgui.unlock()

    def checkdefault(self):
        for account in self.accounts:
            self.accountsettings = self.getaccountsettings(account)
            if self.accountsettings.getSetting("Default Account") == "True":
                print "the account with default = " + str(account)
                xbmcgui.unlock()
                self.defaultlogin(account)
                break

    def defaultlogin(self, account):
        w = XinBox_MyAccountMenu.GUI("XinBox_AccountMenu.xml",SRCPATH,"DefaultSkin",lang=_,theaccount=account,title=TITLE)
        w.doModal()
        del w
        
    def buildaccounts(self):
        accounts = []
        for set in self.settings.getSetting("Accounts")[1]:
            accounts.append(set[0])
        if len(accounts) == 0:
            self.noaccounts = True
        else:self.noaccounts = False
        return accounts

    def getaccountsettings(self,account):
        return self.settings.getSettingInListbyname("Accounts",account)
    
    def getinboxsettings(self,inbox,settings):
        return settings.getSettingInListbyname("Inboxes",inbox)
    
    def setupcontrols(self):
        self.clearList()
        self.getControl(80).setLabel(_(10))
        self.getControl(81).setLabel(VERSION)
        self.getControl(82).setLabel(_(20))
        self.getControl(83).setLabel(_(21))
        MenuItems = [xbmcgui.ListItem(_(11),_(16),"XBlogin.png","XBlogin.png"),
                     xbmcgui.ListItem(_(12),_(17),"XBcreatenew.png","XBcreatenew.png"),
                     xbmcgui.ListItem(_(13),_(18),"XBchangesettings.png","XBchangesettings.png"),
                     xbmcgui.ListItem(_(14),_(19),"XBabouticon.png","XBabouticon.png"),
                     xbmcgui.ListItem(_(15),_(19),"XBquiticon.png","XBquiticon.png")]
        for item in MenuItems:
            self.addItem(item)

    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if ( controlID == 50):
            if self.getCurrentListPosition() == 0:
                if self.noaccounts:
                    self.launchinfo(22,"",_(93))
                else:self.launchloginmenu()
            elif self.getCurrentListPosition() == 1:
                self.launchcreatemenu()
            elif self.getCurrentListPosition() == 2:
                pass
            elif self.getCurrentListPosition() == 3:
                pass
            elif self.getCurrentListPosition() == 4:
                self.close()
                    
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.close()
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title' ):
            self.launchinfo(100 + self.getCurrentListPosition(),self.getListItem(self.getCurrentListPosition()).getLabel())

##    def launchmenu(self, ID):
##        Menus = {"XinBox_LoginMenu":XinBox_LoginMenu}
##        w = Menus[ID].GUI(ID + ".xml",SRCPATH,"DefaultSkin")
##        w.doModal()
##        del w

    def launchinfo(self,focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",SRCPATH,"DefaultSkin",thefocid=focusid,thelabel=label,language=_,theheading=heading)
        dialog.doModal()
        del dialog

    def launchcreatemenu(self):
        winSettings = Account_Settings("XinBox_EditAccountMenu.xml",SRCPATH,"DefaultSkin",0,scriptSettings=self.settings,language=_, title=TITLE,account="")
        winSettings.doModal()
        self.loadsettings()
        del winSettings

    def launchloginmenu(self):
        self.accounts = self.buildaccounts()
        w = XinBox_LoginMenu.GUI("XinBox_LoginMenu.xml",SRCPATH,"DefaultSkin",lang=_,title=TITLE)
        w.doModal()
        del w
