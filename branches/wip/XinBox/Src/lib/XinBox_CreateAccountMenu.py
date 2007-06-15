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
import XinBox_InfoDialog

scriptpath = default.__scriptpath__

_ = language.Language().string  

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        print "welcome"

    def onInit(self):
        self.setupcontrols()
        self.setupvars()
        self.default = False
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
        if ( controlID == 51):
            if self.getCurrentListPosition() == 0: 
                pass
            elif self.getCurrentListPosition() == 1:
                pass
            elif self.getCurrentListPosition() == 2:
                self.default = not self.default
                self.getControl(104).setSelected(self.default)
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
            if focusid == 51:
                print "HERE"
                try:
                    self.launchinfo(105 + self.getCurrentListPosition(),self.getListItem(self.getCurrentListPosition()).getLabel())
                except:traceback.print_exc()

    def launchinfo(self, focusid, label):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",scriptpath + "src","DefaultSkin")
        dialog.setupvars(focusid, label)
        dialog.doModal()
        del dialog

