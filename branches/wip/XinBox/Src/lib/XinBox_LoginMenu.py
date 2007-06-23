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
import xbmcgui, time,traceback
from XinBox_AccountSettings import Account_Settings
from XinBox_Settings import Settings
import XinBox_InfoDialog


TITLE = default.__scriptname__
SCRIPTPATH = default.__scriptpath__
SRCPATH = SCRIPTPATH + "src"
VERSION =  default.__version__


class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,lang=False):
        self.language = lang

    def buildaccounts(self):
        accounts = []
        for set in self.settings.getSetting("Accounts")[1]:
            accounts.append(set[0])
        if accounts == []:
            self.noaccounts = True
        else:self.noaccounts = False
        return accounts

    def loadsettings(self):
        self.settings = Settings("XinBox_Settings.xml",TITLE,"")
        
    def onInit(self):
        xbmcgui.lock()
        self.loadsettings()
        self.buildaccounts()
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
        inboxname = self.getListItem(self.getCurrentListPosition()).getLabel()
        self.launchaccountmenu(inboxname)
                    
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

    def launchaccountmenu(self,theaccount):
        winSettings = Account_Settings("XinBox_AccountMenu.xml",SRCPATH,"DefaultSkin",0,scriptSettings=self.settings,language=self.language, title=TITLE,account=theaccount)
        winSettings.doModal()
        del winSettings

    def launchinfo(self,focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",SRCPATH,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        del dialog
