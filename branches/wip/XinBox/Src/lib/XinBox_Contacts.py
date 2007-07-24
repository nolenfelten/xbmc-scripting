

import xbmc, xbmcgui, time, sys, os, string
import XinBox_Util


class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,accountname=False,setts=False,lang=False,thelabel=False):
        self.label = thelabel
        self.language = lang
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
        self.getControl(73).addLabel(self.account + " " + self.language(370))
        self.getControl(61).setLabel(self.language(61))
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
        self.addItem(self.language(371))
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
                value = self.showKeyboard(self.language(372),curName)
                if value != False and value != "":
                    if (value != curName) and (value in self.contacts):
                        dialog = xbmcgui.Dialog()
                        dialog.ok(self.language(93), self.language(373))
                    else:
                        contname = value
                        self.accountsettings.setSettingnameInList("Contacts",curName,contname)
                        curItem.setLabel(contname)
                        self.buildcontactlist()
                        value = self.showKeyboard(self.language(374),curName2)
                        if value != False and value != "":
                            self.accountsettings.setSettingInList("Contacts",contname,value)
                            curItem.setLabel2(value)
                        self.settings.saveXMLfromArray()
            elif ( controlID == 61):
                value = self.showKeyboard(self.language(372),"")
                if value != False and value != "":
                    if value in self.contacts:
                        dialog = xbmcgui.Dialog()
                        dialog.ok(self.language(93), self.language(373))
                    else:
                        contname = value
                        self.accountsettings.addSettingInList("Contacts",contname,"","text")
                        self.buildcontactlist()
                        value = self.showKeyboard(self.language(374),"")
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
                curPos  = self.getCurrentListPosition()
                curItem = self.getListItem(curPos)
                if focusid == 50:
                    dialog = xbmcgui.Dialog()
                    if dialog.yesno(self.language(376)+ curItem.getLabel(), self.language(375)):
                        self.accountsettings.removeinbox("Contacts",curItem.getLabel())
                        self.settings.saveXMLfromArray()
                        self.removeItem(curPos)
                        self.buildcontactlist()
            elif ( button_key == 'Keyboard Ctrl Button' or button_key == 'White Button'):
                curPos  = self.getCurrentListPosition()
                curItem = self.getListItem(curPos)
                contact = '"' + curItem.getLabel() + '" <' + curItem.getLabel2() + '>'
                if self.label == False:
                    dialog = xbmcgui.Dialog()
                    if not dialog.yesno(self.language(376)+ curItem.getLabel(), self.language(377)):return
                else:
                    if contact in self.label:
                        dialog = xbmcgui.Dialog()
                        dialog.ok(self.language(376)+ curItem.getLabel(), self.language(379))
                        return
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
