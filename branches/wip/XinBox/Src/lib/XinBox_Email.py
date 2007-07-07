

import xbmc, xbmcgui, time, sys, os

import XinBox_Util


class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        self.control_action = XinBox_Util.setControllerAction()

    
    def onInit(self):
        self.attachlist = False
        xbmc.executebuiltin("Skin.SetBool(attachlistnotempty)")
        xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
        xbmc.executebuiltin("Skin.SetBool(emaildialog)")
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
            if self.attachlist:
                xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
                time.sleep(0.8)
            xbmc.executebuiltin("Skin.SetBool(emaildialog)")
            xbmc.executebuiltin("Skin.ToggleSetting(emaildialog)")
            time.sleep(0.8)
            self.close()
        elif ( button_key == 'Keyboard Menu Button' ):
            self.attachlist = not self.attachlist
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
               
    def onFocus(self, controlID):
        pass 


