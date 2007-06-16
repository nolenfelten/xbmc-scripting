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
import XinBox_InfoDialog, traceback
from settings import Settings

scriptpath = default.__scriptpath__

_ = language.Language().string  
defSettings = {_(51): ["Add Acount Name Here","text"],
                _(52): ["Add Account Password Here","text"],
                _(53): ["false","boolean"],}

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        print "welcome"

    def onInit(self):
        try:
            self.scriptSettings = Settings("XinBox_Account_Settings.xml","XinBox Account Settings", defSettings)
        except:
            traceback.print_exc()
        self.setupcontrols()
        self.setupvars()
        self.buildlist()
        self.default = False


    def setupcontrols(self):
        xbmcgui.lock()
        self.getControl(80).setLabel(_(50))
        self.buttonids = [61,62,63,64,65]
        for ID in self.buttonids:
            self.getControl(ID).setLabel(_(ID))
        self.getControl(82).setLabel(_(20))
        self.getControl(83).setLabel(_(21))
        xbmcgui.unlock()

    def buildlist(self):
        xbmcgui.lock()
        for set in self.scriptSettings.settings:
            self.addItem(self.SettingListItem(set, self.scriptSettings.getSetting(set)))
        xbmcgui.unlock()

    def SettingListItem(self, label1,label2):
        if label2 == "true":
            self.getControl(104).setSelected(True)
            return xbmcgui.ListItem(label1,"","","")
        elif label2 == "false":
            self.getControl(104).setSelected(False)
            return xbmcgui.ListItem(label1,"","","")
        else:
            return xbmcgui.ListItem(label1,label2,"","")
    
    def setupvars(self):
        self.control_action = xib_util.setControllerAction()
        self.testsetting = ""

      
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if ( controlID == 51):
            curPos  = self.getCurrentListPosition()
            curItem = self.getListItem(curPos)
            curName = curItem.getLabel()
            type = self.scriptSettings.getSettingType(curName)
            if (type == "text"):
                value = self.showKeyboard(_(66) % curName,curItem.getLabel2())
                curItem.setLabel2(value)
                self.scriptSettings.setSetting(curName,value)
            elif (type == "boolean"):
                if self.scriptSettings.getSetting(curName,"true") == "false":
                    self.scriptSettings.setSetting(curName,"true")
                    self.getControl(104).setSelected(True)
                else:
                    self.scriptSettings.setSetting(curName,"false")
                    self.getControl(104).setSelected(False)
        elif ( controlID == 64 ):
            self.scriptSettings.saveXMLfromArray()
        elif ( controlID == 65 ):
            self.close()
            
    def showKeyboard(self, heading,default=""):
        # Open the Virutal Keyboard.
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return default

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
