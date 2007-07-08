

import xbmc,xbmcgui, time, sys, os
import XinBox_Util
import XinBox_InfoDialog
from XinBox_Settings import Settings
from XinBox_AccountSettings import Account_Settings
from os.path import join, exists
from os import mkdir
ACCOUNTSDIR = "P:\\script_data\\XinBox\\Accounts\\"
import XinBox_Inbox

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,lang=False,theaccount = False, title = False):
        self.init = 0
        self.srcpath = strFallbackPath
        self.language = lang
        self.account = theaccount
        self.title = title

    def loadsettings(self):
        self.settings = Settings("XinBox_Settings.xml",self.title,"")
        
    def onInit(self):
        xbmcgui.lock()
        if self.init == 0:
            self.loadsettings()
            self.setupvars()
            self.setupcontrols()
            self.init = 1
        xbmcgui.unlock()

    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        self.accountsettings = self.settings.getSettingInListbyname("Accounts",self.account)
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if ( controlID == 51):
            inboxname = self.getListItem(self.getCurrentListPosition()).getLabel()
            self.launchinbox(inboxname)
        elif ( controlID == 61):
            self.launchaccountmenu(self.account)
        elif ( controlID == 62):
            if self.launchinfo(201,"",self.language(77)):
                self.deleteaccount()
        elif ( controlID == 63):
            self.close()

    def deleteaccount(self):
        self.settings.removeinbox("Accounts",self.account)
        self.settings.saveXMLfromArray()
        self.removedir(ACCOUNTSDIR + str(hash(self.account)))
        self.close()
        

    def removedir(self,mydir):
        for root, dirs, files in os.walk(mydir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(mydir)
     
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
            if focusid == 51:
                self.launchinfo(125,self.getListItem(self.getCurrentListPosition()).getLabel())
            elif focusid == 61:
                self.launchinfo(126,self.language(62))
            elif focusid == 62:
                self.launchinfo(127,self.language(63))
            elif focusid == 63:
                self.launchinfo(128,self.language(65))


    def setupcontrols(self):
        self.clearList()
        self.getControl(80).setLabel(self.language(200))
        self.getControl(81).setLabel(self.account)
        self.getControl(82).setLabel(self.language(20))
        self.getControl(83).setLabel(self.language(21))
        self.getControl(61).setLabel(self.language(62))
        self.getControl(62).setLabel(self.language(63))
        self.getControl(63).setLabel(self.language(65))
        self.buildinboxes()

    def buildinboxes(self):
        self.getControl(51).setEnabled(True)
        for set in self.accountsettings.getSetting("Inboxes")[1]:
            self.addItem(set[0])
        if self.getListSize() == 0:
            self.addItem(self.language(75))
            self.setFocusId(61)
            self.getControl(51).setEnabled(False)
            
    def launchaccountmenu(self,theaccount):
        winSettings = Account_Settings("XinBox_EditAccountMenu.xml",self.srcpath,"DefaultSkin",0,scriptSettings=self.settings,language=self.language, title=self.title,account=theaccount)
        winSettings.doModal()
        account = winSettings.savedaccountname
        if account != "-":
            self.account = account
        del winSettings
        self.loadsettings()
        self.setupvars()
        self.setupcontrols()

    def launchinbox(self, inbox):
        winSettings = XinBox_Inbox.GUI("XinBox_Inbox.xml",self.srcpath,"DefaultSkin",lang=self.language,theinbox=inbox,account=self.account,title=self.title)
        winSettings.doModal()
        del winSettings      

    def launchinfo(self, focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.srcpath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        value = dialog.value
        del dialog
        return value

    
