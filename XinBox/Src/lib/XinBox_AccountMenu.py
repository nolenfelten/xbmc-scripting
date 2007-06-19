#Thanks to Donno for some of the code below

import xbmcgui,traceback,XinBox_InfoDialog
import xbmc
import os
import xib_util



# Maybe make add inbox a dialog over the top of this account :-D


### Edit Account
##
##


g=mkCrcFun(0x104C11DB7,rev=False)


class AccountSettings(xbmcgui.WindowXML):
    def __init__(self, xmlName, thescriptPath,defaultName,forceFallback, scriptSettings,language, title, account):
        self.account = account
        if self.account == "XinBoxDefault":
            self.newaccount = True
        else:self.newaccount = False
        
        self.title = title
        self.scriptPath = thescriptPath
        self.language = language.string

        self.theSettings = scriptSettings
        
        if self.newaccount:
            self.accountname = "-"
            self.accountpass = "-"
            self.defaultaccount = False
        else:
            self.accountSettings = self.getaccountsettings(self.account)
            self.accountinboxes = self.buildinboxdict(self.accountSettings)

    def buildinboxdict(self,accountsettings):
        self.inboxes = {} 
        for set in self.accountSettings.getSetting("Inboxes")[1] :
            self.inboxes[set[0]] = set[1]
        return self.inboxes

    def getinboxsettings(self,accountsettings,inbox):
        return accountsettings.getSettingInListbyname("Inboxes",inbox)

    def getaccountsettings(self,account):
        return self.theSettings.getSettingInListbyname("Accounts",account)

    
    def onInit(self):
        xbmcgui.lock()
        self.control_action = xib_util.setControllerAction()
        self.list2 = self.getControl(88)
        self.buttonids = [61,62,63,64]
        if self.newaccount:
            self.getControl(64).setEnabled(False)
            self.getControl(63).setEnabled(False)
            self.getControl(62).setEnabled(False)
            self.getControl(80).setLabel(self.language(50))
        else:
            self.getControl(80).setLabel(self.language(74))
            if self.accountSettings.getSetting("Account Name") == "-":
                self.getControl(64).setEnabled(False)
        self.builsettingsList()
        self.buildinboxlist()
        for ID in self.buttonids:
            self.getControl(ID).setLabel(self.language(ID))
        self.getControl(82).setLabel(self.language(20))
        self.getControl(83).setLabel(self.language(21))
        xbmcgui.unlock()
    
    def builsettingsList(self):
        if self.newaccount:
            self.addItem(self.SettingListItem(self.language(51),""))
            self.addItem(self.SettingListItem(self.language(52),self.language(76)))
            self.addItem(self.SettingListItem(self.language(53),""))
        else:
            for set in self.accountSettings.settings:
                if self.accountSettings.getSettingType(set) == "text" or self.accountSettings.getSettingType(set) == "boolean":
                    if set == "Account Password":
                        if self.accountSettings.getSetting(set) == "-":
                            self.addItem(self.SettingListItem(set, self.language(76)))
                        else:
                            self.addItem(self.SettingListItem(set, '*' * len(self.accountSettings.getSetting(set))))
                    else:
                        self.addItem(self.SettingListItem(set, self.accountSettings.getSetting(set)))

        
    def buildinboxlist(self):
        if self.newaccount:
            self.list2.addItem(self.SettingListItem(self.language(75), ""))
        else:
            for set in self.accountinboxes:
                if set != "XinBoxDefault":
                    self.list2.addItem(self.SettingListItem(set, ""))
            if self.list2.size() == 0:
                self.list2.addItem(self.SettingListItem(self.language(75), ""))
                self.getControl(63).setEnabled(False)
                self.getControl(62).setEnabled(False)

##        test = self.inboxes[self.getListItem(4).getLabel()]
##      # will be able to do: test = self.inboxes[self.getListItem(self.getCurrentListPosition()).getLabel()]  
##        print "test for inbox = " + str(test)

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
                self.launchinfo(focusid+47,self.language(focusid))

    def onClick(self, controlID):
        if ( controlID == 51):
            curPos  = self.getCurrentListPosition()
            curItem = self.getListItem(curPos)
            curName = curItem.getLabel()
            curName2 = curItem.getLabel2()
            if self.newaccount:
                if curPos == 0:
                    value = self.showKeyboard(self.language(66) % curName,curName2)
                    if value != "":
                        self.accountname = value
                        curItem.setLabel2(value)
                        self.getControl(64).setEnabled(True)
                elif curPos == 1:
                    value = self.showKeyboard(self.language(66) % curName,"",1)
                    if value == "":
                        self.accountpass = "-"
                        curItem.setLabel2(self.language(76))
                    else:
                        self.accountpass = value
                        curItem.setLabel2('*' * len(value))
                elif curPos == 2:
                    self.defaultaccount = not self.defaultaccount
                    self.getControl(104).setSelected(self.defaultaccount)
            else:
                if curPos == 0:
                    value = self.showKeyboard(self.language(66) % curName,curName2)
                    if value != "":
                        curItem.setLabel2(value)
                        self.accountSettings.setSetting("Account Name",value)
                        self.theSettings.setSettingnameInList("Accounts",curName2,value)
                        self.getControl(64).setEnabled(True)
                elif curPos == 1:
                    value = self.showKeyboard(self.language(66) % curName,"",1)
                    if value == "":
                        self.accountSettings.setSetting("Account Password","-")
                        curItem.setLabel2(self.language(76))
                    else:
                        self.accountSettings.setSetting("Account Password",value)
                        curItem.setLabel2('*' * len(value))                            
                elif curPos == 2:
                    self.defaultaccount = not self.defaultaccount
                    self.getControl(104).setSelected(self.defaultaccount)
                    self.accountSettings.setSetting("Default Account",str(self.defaultaccount))
        elif ( controlID == 64):
            try:
                if self.newaccount:
                    self.Addsetting("Accounts",self.accountname)
                    self.accountSettings = self.getaccountsettings(self.accountname)
                    self.accountSettings.setSetting("Account Name",self.accountname)
                    self.accountSettings.setSetting("Account Password",self.accountpass)
                    self.accountSettings.setSetting("Default Account",str(self.defaultaccount))
                self.theSettings.saveXMLfromArray()
                self.close()
            except:traceback.print_exc()

    def addnewItem(self, settingname,value1,value2="",type="text"):
        self.theSettings.addSettingInList(settingname,value1,value2,"settings")
        return

    def onFocus(self, controlID):
        pass

       
    def SettingListItem(self, label1,label2):
        if label2 == "True":
            self.defaultaccount = True
            self.getControl(104).setSelected(self.defaultaccount)
            return xbmcgui.ListItem(label1,"","","")
        elif label2 == "False":
            self.defaultaccount = False
            self.getControl(104).setSelected(self.defaultaccount)
            return xbmcgui.ListItem(label1,"","","")
        else:
            return xbmcgui.ListItem(label1,label2,"","")

    def showKeyboard(self, heading,default="",hidden=0):
        # Open the Virutal Keyboard.
        keyboard = xbmc.Keyboard(default,heading)
        if hidden == 1:keyboard.setHiddenInput(True)
        keyboard.doModal()
        if hidden == 1:keyboard.setHiddenInput(False)
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return default

    def launchinfo(self, focusid, label):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.scriptPath,"DefaultSkin")
        dialog.setupvars(focusid, label)
        dialog.doModal()
        del dialog
