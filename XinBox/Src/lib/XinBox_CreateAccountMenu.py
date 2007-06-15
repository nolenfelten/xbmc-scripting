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
        self.set_controls_values()
        self.default = False


    def setupcontrols(self):
        xbmcgui.lock()
        for x in range( 1, 4 ):
            self.addItem(xbmcgui.ListItem())
        self.getControl(80).setLabel(_(50))
        self.buttonids = [61,62,63,64,65]
        for ID in self.buttonids:
            self.getControl(ID).setLabel(_(ID))
        self.getControl(82).setLabel(_(20))
        self.getControl(83).setLabel(_(21))
        xbmcgui.unlock()

    def set_controls_values(self): #thanks to Nuka for this!
        xbmcgui.lock()
        try:
            self.getListItem(0).setLabel(_(51))
            self.getListItem(0).setLabel2(self.testsetting)
            self.getListItem(1).setLabel(_(52))
            self.getListItem(1).setLabel2("")
            self.getListItem(2).setLabel(_(53))
        except: traceback.print_exc()
        xbmcgui.unlock()

    def setupvars(self):
        self.control_action = xib_util.setControllerAction()
        self.testsetting = ""

      
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if ( controlID == 51):
            if self.getCurrentListPosition() == 0: 
                self.testsetting = "Stanley87"
                self.set_controls_values()
            elif self.getCurrentListPosition() == 1:
                pass
            elif self.getCurrentListPosition() == 2:
                self.default = not self.default
                self.getControl(104).setSelected(self.default)
        elif ( controlID == 65 ):
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
                self.launchinfo(105 + self.getCurrentListPosition(),self.getListItem(self.getCurrentListPosition()).getLabel())
            else:
                self.launchinfo(focusid+47,_(focusid))
                

    def launchinfo(self, focusid, label):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",scriptpath + "src","DefaultSkin")
        dialog.setupvars(focusid, label)
        dialog.doModal()
        del dialog

