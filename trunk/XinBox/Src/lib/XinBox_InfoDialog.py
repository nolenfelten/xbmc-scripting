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

class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        self.control_action = xib_util.setControllerAction()

    def setupvars(self, focusid, label):
        self.focusid = focusid
        self.label = label
        
    def onInit(self):
        self.getControl(20).setLabel(_(99) % self.label)
        self.getControl(21).setText(_(self.focusid))
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if controlID == 22:
            self.close()
                    
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.close()

