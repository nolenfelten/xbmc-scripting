

import xbmc, xbmcgui, time, sys, os, traceback
import XinBox_Util

class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,inboxsetts=False,lang=False,fwdemail=False,inboxname=False):
        self.inbox = inboxname
        self.fwdemail = fwdemail
        self.language = lang
        self.ibsettings = inboxsetts
   
    def onInit(self):
        self.setupvars()
        self.setupcontrols()

    def setupvars(self):
        self.returnvalue = 0
        self.toaddr = ""
        self.ccaddr = ""
        self.bccaddr = ""
        self.subject = ""
        self.exiting = False
        self.control_action = XinBox_Util.setControllerAction()
        self.attachlist = False
        xbmc.executebuiltin("Skin.SetBool(attachlistnotempty)")
        xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
        xbmc.executebuiltin("Skin.SetBool(emaildialog)")

    def setupcontrols(self):
        try:
            self.getControl(80).setImage("XBXinBoXLogo.png")
            self.getControl(81).setEnabled(False)
            self.getControl(89).setLabel(self.language(266))
            self.getControl(84).setLabel(self.language(310))
            self.getControl(85).setLabel(self.language(311))
            self.getControl(86).setLabel(self.language(312))
            self.getControl(87).setLabel(self.language(313))
            self.getControl(61).setLabel(self.language(314))
            self.addItem(self.toaddr)
            self.addItem(self.ccaddr)
            self.addItem(self.bccaddr)
            self.addItem(self.subject)
            self.getControl(73).addLabel(self.language(315) + " " + self.inbox + " <" + self.ibsettings.getSetting("Email Address") + ">")
        except:traceback.print_exc()
        
    def onClick(self, controlID):
        if controlID == 50:
            pos = self.getCurrentListPosition()
            if pos == 0:
                kb = self.showKeyboard("Enter To: Address(s):",self.getListItem(pos).getLabel())
                if kb != False:
                    self.toaddr = kb
                    self.getListItem(pos).setLabel(kb)
            elif pos == 1:
                kb = self.showKeyboard("Enter Cc: Address(s):",self.getListItem(pos).getLabel())
                if kb != False:
                    self.ccaddr = kb
                    self.getListItem(pos).setLabel(kb)
            elif pos == 2:
                kb = self.showKeyboard("Enter Bcc: Address(s):",self.getListItem(pos).getLabel())
                if kb != False:
                    self.bccaddr = kb
                    self.getListItem(pos).setLabel(kb)
            elif pos == 3:
                kb = self.showKeyboard("Enter Subject):",self.getListItem(pos).getLabel())
                if kb != False:
                    self.subject = kb
                    self.getListItem(pos).setLabel(kb)
        elif controlID == 61:
            self.returnvalue = [self.toaddr,self.ccaddr,self.bccaddr,self.subject,"XinBox Test",[]]
            self.exitme()
            
        
    def onAction( self, action ):
        if not self.exiting:
            button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
            actionID   =  action.getId()
            try:focusid = self.getFocusId()
            except:focusid = 0
            try:control = self.getFocus()
            except: control = 0
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.exitme()
               
    def onFocus(self, controlID):
        pass

    def exitme(self):
        self.exiting = True
        xbmc.executebuiltin("Skin.SetBool(emaildialog)")
        xbmc.executebuiltin("Skin.ToggleSetting(emaildialog)")
        time.sleep(0.8)
        self.close()

    def showKeyboard(self, heading,default=""):
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return False
