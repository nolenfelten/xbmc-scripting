

import xbmc, xbmcgui, time, sys, os, string, traceback
import XinBox_Util


class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,accountname=False,setts=False):
        self.account = accountname
        self.settings = setts
   
    def onInit(self):
        xbmcgui.lock()
        self.setupvars()
        self.buildcontactlist()
        self.buildlist()
        xbmcgui.unlock()
        self.animating = True
        xbmc.executebuiltin("Skin.setBool(contactsdialog)")
        time.sleep(0.8)
        self.animating = False

    def setupvars(self):
        self.returnval = 0
        self.getControl(73).addLabel(self.account + "'s Contacts:")
        self.listEnabled = True
        self.control_action = XinBox_Util.setControllerAction()
        self.accountsettings = self.settings.getSettingInListbyname("Accounts",self.account)

    def buildlist(self):
        for set in self.accountsettings.getSetting("Contacts")[1]:
            self.addItem(xbmcgui.ListItem(set[0],set[1],"",""))

    def buildcontactlist(self):
        self.contacts  = []
        for set in self.accountsettings.getSetting("Contacts")[1]:
            self.contacts.append(set[0])
        if len(self.contacts) == 0:self.disablelist()

    def disablelist(self):
        self.listEnabled = False
        self.getControl(50).setEnabled(False)
        self.clearList()
        self.addItem("No Contacts")
        self.setFocusId(61)

    def enablelist(self):
        self.listEnabled = True
        self.clearList()
        self.getControl(50).setEnabled(True)
               
    def onClick(self, controlID):
        if not self.animating:
            if ( controlID == 50):
                curPos  = self.getCurrentListPosition()
                curItem = self.getListItem(curPos)
                curName = curItem.getLabel()
                curName2 = curItem.getLabel2()
                value = self.showKeyboard("Edit Contact Name:",curName)
                if value != False and value != "":
                    if value != curName:
                        if value in self.contacts:
                            dialog = xbmcgui.Dialog()
                            dialog.ok("Error", "You can not have two contacts with same name")
                    else:
                        contname = value
                        self.accountsettings.setSettingnameInList("Contacts",curName,contname)
                        curItem.setLabel(contname)
                        self.buildcontactlist()
                        value = self.showKeyboard("Edit Contact Email:",curName2)
                        if value != False and value != "":
                            self.accountsettings.setSettingInList("Contacts",contname,value)
                            curItem.setLabel2(value)
                        self.settings.saveXMLfromArray()
            elif ( controlID == 61):
                value = self.showKeyboard("Add Contact Name:","")
                if value != False and value != "":
                    if value in self.contacts:
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Error", "You can not have two contacts with same name")
                    else:
                        contname = value
                        self.accountsettings.addSettingInList("Contacts",contname,"","text")
                        self.buildcontactlist()
                        value = self.showKeyboard("Add Contact Email:","")
                        if value != False and value != "":
                            self.accountsettings.setSettingInList("Contacts",contname,value)
                            self.addcontact(xbmcgui.ListItem(contname,value,"",""))
                        else:self.addcontact(contname)
                        self.settings.saveXMLfromArray()
                
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
                if focusid == 50:
                    dialog = xbmcgui.Dialog()
                    if dialog.yesno("Warning", "Delete this Contact?"):
                        self.accountsettings.removeinbox("Contacts",self.getListItem(self.getCurrentListPosition()).getLabel())
                        self.settings.saveXMLfromArray()
                        self.removeItem(self.getCurrentListPosition())
                        self.buildcontactlist()
            elif ( button_key == 'Keyboard Ctrl Button' or button_key == 'White Button'):
                curPos  = self.getCurrentListPosition()
                curItem = self.getListItem(curPos)
                contact = '"' + curItem.getLabel() + '" <' + curItem.getLabel2() + '>'
                self.returnval = contact
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
