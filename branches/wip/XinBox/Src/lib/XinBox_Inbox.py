

import xbmc,xbmcgui, time, sys, os,traceback
import XinBox_Util
from XinBox_Settings import Settings
from XinBox_EmailEngine import Checkemail

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,lang=False,theinbox=False,account=False,title=False):
        self.language = lang
        self.inbox = theinbox
        self.account = account
        self.title = title

    def loadsettings(self):
        self.settings = Settings("XinBox_Settings.xml",self.title,"")
        self.accountsettings = self.settings.getSettingInListbyname("Accounts",self.account)
        self.ibsettings = self.accountsettings.getSettingInListbyname("Inboxes",self.inbox)
 
    def onInit(self):
        try:
            xbmcgui.lock()
            self.loadsettings()
            self.setupvars()
            self.setupcontrols()
            xbmcgui.unlock()
        except:traceback.print_exc()
        
    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if controlID == 64:
            self.close()
        elif controlID == 61:
            try:
                self.checkfornew(self.inbox,self.ibsettings)
            except:traceback.print_exc()
  
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.close()
    
    def setupcontrols(self):
        self.getControl(80).setLabel(self.inbox)
        self.getControl(61).setLabel(self.language(250))
        self.getControl(62).setLabel(self.language(251))
        self.getControl(63).setLabel(self.language(252))
        self.getControl(64).setLabel(self.language(65))

    def checkfornew(self, inbox, ibsettings):
        w = Checkemail(ibsettings,inbox,self.account,self.language,False)
        w.checkemail()
        del w
