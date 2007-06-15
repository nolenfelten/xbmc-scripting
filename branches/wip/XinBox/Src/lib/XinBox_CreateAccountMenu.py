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
import xbmcgui, language, time

_ = language.Language().string  

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        print "welcome"

    def onInit(self):
        self.setupcontrols()
        self.setupvars()
        xbmcgui.unlock()

    def setupcontrols(self):
        ListItems = [xbmcgui.ListItem(_(51)),
                     xbmcgui.ListItem(_(52)),
                     xbmcgui.ListItem(_(53)),]
        for item in ListItems:
            self.addItem(item)
        self.getControl(80).setLabel(_(50))

    def setupvars(self):
        self.control_action = xib_util.setControllerAction()
        
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
