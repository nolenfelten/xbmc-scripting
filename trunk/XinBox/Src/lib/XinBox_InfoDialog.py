

import xbmc, xbmcgui
import sys, os, time

import XinBox_Util
 
class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,thefocid=0,thelabel="No Label",language=0,theheading=False,thetext=False):
        self.control_action = XinBox_Util.setControllerAction()
        self.focusid = thefocid
        self.label = thelabel
        self.lang = language
        self.heading = theheading
        self.thetext = thetext
        
    def onInit(self):
        if not self.heading:
            self.getControl(20).setLabel(self.lang(99) % self.label)
        else:self.getControl(20).setLabel(self.heading)
        if not self.thetext:
            self.getControl(21).setText(self.lang(self.focusid))
        else:self.getControl(21).setText(self.thetext)
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if controlID == 40:
            self.value = True
            self.close()
                    
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.value = False
            self.close()

