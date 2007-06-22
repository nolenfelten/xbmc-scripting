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
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,accounts=False):
        self.accounts = accounts

    def onInit(self):
        self.setupcontrols()
        self.setupvars()
        xbmcgui.unlock()

    def setupcontrols(self):
        MenuLabel = self.getControl(80)
        MenuLabel.setLabel(_(30))
        for account in self.accounts:
            self.addItem(account)

    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        pass
                    
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.close()     

class WindowXMLDialogExample(xbmcgui.WindowXMLDialog):
    def __init__(self,strXMLname, strFallbackPath):
        self.heading = ""
        self.line1 = ""
        self.line2 = ""
        self.line3 = ""

    def onInit(self):
        self._setLines()

    def onAction(self, action):
        buttonCode =  action.getButtonCode()
        actionID   =  action.getId()
        if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC or buttonCode == 61467):
            self.close()

    def onClick(self, controlID):
        if (controlID == 10):
            self.close()

    def onFocus(self, controlID):
        pass

    def _setLines(self):
        self.getControl(1).setLabel(self.heading)
        self.getControl(2).setLabel(self.line1)

    def setHeading(self, heading):
        self.heading = heading

    def setLines(self, line1):
        self.line1 = line1
