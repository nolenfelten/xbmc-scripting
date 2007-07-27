

import xbmc, xbmcgui, time, sys, os, string
import XinBox_Util
from XinBox_Settings import Settings
from os.path import join, exists, basename,getsize

ACCOUNTSDIR = XinBox_Util.__accountsdir__

class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,accountname=False,setts=False,lang=False,thelabel=False):
        self.label = thelabel
        self.language = lang
        self.account = accountname
        self.settings = setts
        self.accountfolder = join(ACCOUNTSDIR,str(hash(self.account))) + "//"
   
    def onInit(self):
        xbmcgui.lock()
        self.setupvars()
        self.builddraftlist()
        self.buildlist()
        xbmcgui.unlock()
        self.animating = True
        xbmc.executebuiltin("Skin.setBool(contactsdialog)")
        time.sleep(0.8)
        self.animating = False

    def setupvars(self):
        self.returnval = 0
        self.getControl(73).addLabel(self.account + " " + self.language(397))
        self.listEnabled = True
        self.control_action = XinBox_Util.setControllerAction()
        self.accountsettings = self.settings.getSettingInListbyname("Accounts",self.account)

    def buildlist(self):
        for set in self.accountsettings.getSetting("Drafts")[1]:
            myto = set[1].getSetting("To Addr")
            mysubject = set[1].getSetting("Subject")
            self.addItem(xbmcgui.ListItem(set[0],self.language(310) + " " + myto + " " + self.language(313) + " " + mysubject,"",""))

    def builddraftlist(self):
        self.drafts  = []
        for set in self.accountsettings.getSetting("Drafts")[1]:
            self.drafts.append(set[0])
        if len(self.drafts) == 0:self.disablelist()

    def disablelist(self):
        self.listEnabled = False
        self.getControl(50).setEnabled(False)
        self.clearList()
        self.addItem(self.language(396))
        
    def enablelist(self):
        self.listEnabled = True
        self.clearList()
        self.getControl(50).setEnabled(True)
               
    def onClick(self, controlID):
        if controlID == 50:
            if self.listEnabled:
                curPos  = self.getCurrentListPosition()
                curItem = self.getListItem(curPos)
                self.builddraft(curItem.getLabel())
                
    def addcontact(self, item):
        if not self.listEnabled:self.enablelist()
        self.addItem(item)

    def onAction( self, action ):
        if not self.animating:
            button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
            actionID   =  action.getId()
            try:focusid = self.getFocusId()
            except:focusid = 0
            try:control = self.getFocus()
            except: control = 0
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.exitme()
            elif ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button'):
                curPos  = self.getCurrentListPosition()
                curItem = self.getListItem(curPos)
                if focusid == 50:
                    dialog = xbmcgui.Dialog()
                    if dialog.yesno(self.language(393) + curItem.getLabel(), self.language(394)):
                        mydraft = self.accountsettings.getSettingInListbyname("Drafts",curItem.getLabel())
                        os.remove(self.accountfolder + str(mydraft.getSetting("Emailbodyhash")) + ".draft")
                        self.accountsettings.removeinbox("Drafts",curItem.getLabel())
                        self.settings.saveXMLfromArray()
                        self.removeItem(curPos)
                        self.builddraftlist()       

    def builddraft(self, name):
        mydraft = self.accountsettings.getSettingInListbyname("Drafts",name)
        toaddr = mydraft.getSetting("To Addr")
        ccaddr = mydraft.getSetting("Cc Addr")
        bccaddr = mydraft.getSetting("Bcc Addr")
        subject = mydraft.getSetting("Subject")
        f = open(self.accountfolder + str(mydraft.getSetting("Emailbodyhash")) + ".draft")
        body = f.read()
        f.close()
        attachments = []
        for attachment in mydraft.getSetting("Attachments"):
            if not exists(attachment):
                dialog = xbmcgui.Dialog()
                dialog.ok(self.language(93), self.language(320) + " " + basename(attachment),self.language(395))
            else:attachments.append([basename(attachment),attachment,getsize(str(attachment))])
        self.returnval = [toaddr,ccaddr,bccaddr,subject,body,attachments]
        self.exitme()

    def exitme(self):
        self.animating = True
        xbmc.executebuiltin("Skin.ToggleSetting(contactsdialog)")
        time.sleep(0.8)
        self.animating = False
        self.close()
                
    def onFocus(self, controlID):
        pass

    def showKeyboard(self, heading,default=""):
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if keyboard.isConfirmed():
            return keyboard.getText()
        else:return False
