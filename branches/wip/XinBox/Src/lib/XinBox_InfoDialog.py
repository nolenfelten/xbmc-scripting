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
import xbmc, sys, os, XinBox_Util
import xbmcgui, time
 
class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,thefocid=0,thelabel="No Label",language=0):
        self.control_action = XinBox_Util.setControllerAction()
        self.focusid = thefocid
        self.label = thelabel
        self.lang = language
        
    def onInit(self):
        self.getControl(20).setLabel(self.lang(99) % self.label)
        self.getControl(21).setText(self.lang(self.focusid))
        
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

