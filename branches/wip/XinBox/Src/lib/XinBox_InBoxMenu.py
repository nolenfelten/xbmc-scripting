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
import xbmc, sys, os, XinBox_Util, default
import xbmcgui, time
from XinBox_Language import Language

TITLE = default.__scriptname__
SCRIPTPATH = default.__scriptpath__
SRCPATH = SCRIPTPATH + "src"
VERSION =  default.__version__

lang = Language(TITLE)
lang.load(SRCPATH + "//language")
_ = lang.string

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,inboxsetts=False,theinbox="XinBoxNew"):
        print "inbox = " + str(theinbox)
        print "inboxsetts = " + str(inboxsetts)
        self.language = _
        self.inbox = theinbox
        self.settings = inboxsetts
        if self.inbox == "XinBoxNew":
            self.newinbox = True
        else:self.newinbox = False
        if not self.settings:
            self.newaccount = True
        else:self.newaccount = False

    def onInit(self):
        try:
            xbmcgui.lock()
            self.setupvars()
            self.setupcontrols()
            self.builsettingsList()
            xbmcgui.unlock()
        except:traceback.print_exc()

    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        if self.newinbox:
            self.popssl = "0"
            self.smtpssl = "0"
            self.popdefault = False
            self.smtpdefault = False
        else:
            self.popdefault = self.settings#.getsetting blah blah
            self.smtpdefault = self.settings #.getsetting blah blah

    def setupcontrols(self):
        self.getControl(61).setLabel(self.language(89))
        self.getControl(62).setLabel(self.language(64))
        if self.newinbox:
            self.getControl(80).setLabel(self.language(80))
            self.getControl(104).setLabel(self.language(90))
            self.getControl(105).setLabel(self.language(90))
        else:
            self.getControl(80).setLabel(self.language(81))
            self.getControl(81).setLabel(self.inbox)

    def builsettingsList(self):
        if self.newinbox:
            for x in range(82,89):
                self.addItem(self.SettingListItem(self.language(x),""))
##        else:
##            self.addItem(self.SettingListItem(self.language(51), self.account))
##            if self.accountSettings.getSetting("Account Password") == "-":
##                self.addItem(self.SettingListItem(self.language(52), self.language(76)))
##            else:
##                self.addItem(self.SettingListItem(self.language(52), '*' * len(self.accountSettings.getSetting("Account Password"))))
##            self.addItem(self.SettingListItem(self.language(53), self.accountSettings.getSetting("Default Account")))
##
    def SettingListItem(self, label1,label2):
        if label2 == "POPTrue":
            self.popdefault = True
            self.getControl(104).setSelected(self.popdefault)
            return xbmcgui.ListItem(label1,"","","")
        elif label2 == "POPFalse":
            self.popdefault = False
            self.getControl(104).setSelected(self.popdefault)
            return xbmcgui.ListItem(label1,"","","")
        elif label2 == "SMTPTrue":
            self.smtpdefault = True
            self.getControl(104).setSelected(self.smtpdefault)
            return xbmcgui.ListItem(label1,"","","")
        elif label2 == "SMTPFalse":
            self.smtpdefault = False
            self.getControl(104).setSelected(self.smtpdefault)
            return xbmcgui.ListItem(label1,"","","")        
        else:
            return xbmcgui.ListItem(label1,label2,"","")

        
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
        elif ( button_key == 'Keyboard Right Arrow' or button_key == 'DPad Right' or button_key == 'Remote Right' ):
            if focusid == 51:
                if self.getCurrentListPosition() == 1:
                    self.updatessl(91,self.popssl)
                elif self.getCurrentListPosition() == 2:
                    self.updatessl(92,self.smtpssl)
                    
    def updatessl(self,ID,currValue):
        dialog = xbmcgui.Dialog()
        value = dialog.numeric(0, self.language(ID),currValue)
        if value != currValue:
            if ID == 91:
                self.popssl = value
                if value == "0":
                    self.popdefault = False
                    self.getControl(104).setLabel(self.language(90))
                else:
                    self.popdefault = not self.popdefault
                    self.getControl(104).setLabel(self.popssl)
                self.getControl(104).setSelected(self.popdefault)
            else:
                self.smtpssl = value
                if value == "0":
                    self.smtpdefault = False
                    self.getControl(105).setLabel(self.language(90))
                else:
                    self.smtpdefault = not self.smtpdefault
                    self.getControl(105).setLabel(self.smtpssl)
                self.getControl(105).setSelected(self.smtpdefault)

    def showKeyboard(self, heading,default="",hidden=0):
        keyboard = xbmc.Keyboard(default,heading)
        if hidden == 1:keyboard.setHiddenInput(True)
        keyboard.doModal()
        if hidden == 1:keyboard.setHiddenInput(False)
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return default













        
