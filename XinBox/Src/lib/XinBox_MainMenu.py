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
import xbmcgui, language, time, traceback
import XinBox_InfoDialog

import XinBox_LoginMenu, XinBox_CreateAccountMenu,XinBox_Settings
from settings import Settings

from language import Language


__title__ = "XinBox"
lang = Language()
_ = lang.string

defSettingsForAInBox =  {
    _(67): ["-","text"],
    _(68): ["-","text"],
    _(69): ["-","text"],
    _(70): ["-","text"],
    _(71): ["-","text"],
    _(72): ["-","text"]}
defInboxSettings = Settings("",__title__,defSettingsForAInBox,2)
defSettingsForAnAccount = {
    _(51): ["-","text"],
    _(52): ["-","text"],
     _(53): ["-","boolean"],
    "Inboxes": [['Inbox',[["Default",defInboxSettings,"settings"]]],"list"]}

defAccountSettings = Settings("",__title__,defSettingsForAnAccount,2)
defSettings = {
    "Accounts": [['Account',[["Default",defAccountSettings,"settings"]]],"list"]}

setts = Settings("XinBox_Settings.xml",__title__,defSettings)

scriptpath = default.__scriptpath__

from XinBox_Settings import ircXBMC_Settings



VERSION = "V.1.0"
class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        print "welcome"

    def onInit(self):
        self.clearList()
        self.setupcontrols()
        self.setupvars()
        xbmcgui.unlock()

    def setupcontrols(self):
        MenuItems = [xbmcgui.ListItem(_(11),_(16),"XBlogin.png","XBlogin.png"),
                     xbmcgui.ListItem(_(12),_(17),"XBcreatenew.png","XBcreatenew.png"),
                     xbmcgui.ListItem(_(13),_(18),"XBchangesettings.png","XBchangesettings.png"),
                     xbmcgui.ListItem(_(14),_(19),"XBabouticon.png","XBabouticon.png"),
                     xbmcgui.ListItem(_(15),_(19),"XBquiticon.png","XBquiticon.png")]
        for item in MenuItems:
            self.addItem(item)
        self.getControl(80).setLabel(_(10))
        self.getControl(81).setLabel(VERSION)
        self.getControl(82).setLabel(_(20))
        self.getControl(83).setLabel(_(21))

    def setupvars(self):
        self.control_action = xib_util.setControllerAction()
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if ( controlID == 50):
            if self.getCurrentListPosition() == 0: 
                self.launchmenu("XinBox_LoginMenu")
            elif self.getCurrentListPosition() == 1:
                try:
                    self.gosettings()
                except:traceback.print_exc()
            elif self.getCurrentListPosition() == 2:
                self.launchmenu("XinBox_LoginMenu")
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
            self.launchinfo(100 + self.getCurrentListPosition(),self.getListItem(self.getCurrentListPosition()).getLabel())

    def launchmenu(self, ID):
        Menus = {"XinBox_LoginMenu":XinBox_LoginMenu,"XinBox_CreateAccountMenu":XinBox_CreateAccountMenu}
        w = Menus[ID].GUI(ID + ".xml",scriptpath + "src","DefaultSkin")
        w.doModal()
        del w

    def launchinfo(self, focusid, label):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",scriptpath + "src","DefaultSkin")
        dialog.setupvars(focusid, label)
        dialog.doModal()
        del dialog

    def gosettings(self):
        winSettings = ircXBMC_Settings("XinBox_CreateAccountMenu.xml",scriptpath + "src","DefaultSkin",0,scriptSettings=setts,language=lang, title=__title__,account="Default")
        winSettings.doModal()
        del winSettings
