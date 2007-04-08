 
import xbmcgui, language, time, xib_util
lang = language.Language().string

        
class Settings( xbmcgui.WindowXML ):        
    def onInit(self):
        self.control_action = xib_util.setControllerAction()

    def onClick(self, controlID):
        if ( controlID == 99):
            self.close()
                
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.close()

    def onFocus(self, controlID):
        print 'The control with id="5" just got focus'   
