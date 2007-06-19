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
import xbmc, sys, os, default,xib_util
import xbmcgui, language, time, traceback
import XinBox_InfoDialog

import XinBox_LoginMenu, XinBox_Settings
from settings import Settings
from XinBox_Settings import XinBox_Settings 
from language import Language


TITLE = default.__scriptname__
SCRIPTPATH = default.__scriptpath__
SRCPATH = SCRIPTPATH + "src"
VERSION =  default.__version__

lang = Language(TITLE)
lang.load(SRCPATH + "//language")
_ = lang.string

defSettings = {"Accounts": [['Account',[]],"list"]}
setts = Settings("XinBox_Settings.xml",TITLE,defSettings)


class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        pass

    def onInit(self):
        xbmcgui.lock()
        try:
            self.clearList()
            self.setupvars()
            self.setupcontrols()
            xbmcgui.unlock()
        except:traceback.print_exc()

    def setupcontrols(self):
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
        self.control_action = xib_util.setControllerAction()
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if ( controlID == 50):
            if self.getCurrentListPosition() == 0: 
                self.launchmenu("XinBox_LoginMenu")
            elif self.getCurrentListPosition() == 1:
                self.launchcreatemenu()
            elif self.getCurrentListPosition() == 2:
                self.launchmenu("XinBox_LoginMenu")
            elif self.getCurrentListPosition() == 3:
                self.launchmenu("XinBox_LoginMenu")
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

    def launchmenu(self, ID):
        Menus = {"XinBox_LoginMenu":XinBox_LoginMenu}
        w = Menus[ID].GUI(ID + ".xml",SRCPATH,"DefaultSkin")
        w.doModal()
        del w

    def launchinfo(self, focusid, label):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",SRCPATH,"DefaultSkin",thefocid=focusid,thelabel=label,language=_)
        dialog.doModal()
        del dialog

    def launchcreatemenu(self):
        winSettings = XinBox_Settings("XinBox_AccountMenu.xml",SRCPATH,"DefaultSkin",0,scriptSettings=setts,language=_, title=TITLE,account="XinBoxDefault")
        winSettings.doModal()
        del winSettings
