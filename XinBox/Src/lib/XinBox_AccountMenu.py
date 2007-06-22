import xbmcgui,traceback,XinBox_InfoDialog
import xbmc
import os
import XinBox_Util
import XinBox_InBoxMenu


# Maybe make add inbox a dialog over the top of this account :-D


### Edit Account
##
##

class AccountSettings(xbmcgui.WindowXML):
    def __init__(self, xmlName, thescriptPath,defaultName,forceFallback, scriptSettings,language, title, account):
        self.myinit = 1
        self.account = account
        self.title = title
        self.scriptPath = thescriptPath
        self.language = language
        self.theSettings = scriptSettings
        
        if self.account == "":
            self.newaccount = True
            self.crnewaccount(self.account)
        else:self.newaccount = False

        self.accounts = self.buildaccounts()
        self.accountSettings = self.getaccountsettings(self.account)
        self.accountinboxes = self.buildinboxdict(self.accountSettings)

    def buildinboxdict(self,accountsettings):
        inboxes = []
        for set in self.accountSettings.getSetting("Inboxes")[1]:
            inboxes.append(set[0])
        return inboxes

    def buildaccounts(self):
        accounts = []
        for set in self.theSettings.getSetting("Accounts")[1]:
            accounts.append(set[0])
        return accounts

    def getaccountsettings(self,account):
        return self.theSettings.getSettingInListbyname("Accounts",account)
    
    def onInit(self):
        xbmcgui.lock()
        if self.myinit == 1:
            self.setupvars()
            self.setupcontrols()
            self.buildsettingsList()
            self.buildinboxlist()
            self.myinit = 0
        xbmcgui.unlock()

    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        self.inboxlist = self.getControl(88)
        self.defaultaccount = self.accountSettings.getSetting("Default Account")

    def setupcontrols(self):
        self.getControl(82).setLabel(self.language(20))
        self.getControl(83).setLabel(self.language(21))
        self.buttonids = [61,62,63,64,65]
        for ID in self.buttonids:
            self.getControl(ID).setLabel(self.language(ID))        
        if self.newaccount:
            self.getControl(64).setEnabled(False)
            self.getControl(63).setEnabled(False)
            self.getControl(62).setEnabled(False)
            self.getControl(80).setLabel(self.language(50))
        else:self.getControl(80).setLabel(self.language(74))
    
    def buildsettingsList(self):
        self.clearList()
        self.addItem(self.SettingListItem(self.language(51), self.account))
        if self.accountSettings.getSetting("Account Password") == "-":
            self.addItem(self.SettingListItem(self.language(52), self.language(76)))
        else:
            self.addItem(self.SettingListItem(self.language(52), '*' * len(self.accountSettings.getSetting("Account Password"))))
        self.addItem(self.SettingListItem(self.language(53), self.defaultaccount))
        
    def buildinboxlist(self):
        self.inboxlist.reset()
        for item in self.accountinboxes:
            self.inboxlist.addItem(self.SettingListItem(item, ""))
        if self.inboxlist.size() == 0:
            self.inboxlist.addItem(self.SettingListItem(self.language(75), ""))
            self.getControl(63).setEnabled(False)
            self.getControl(62).setEnabled(False)
            self.setFocusId(51)
        else:
            self.getControl(62).setEnabled(True)
            self.getControl(63).setEnabled(True)

    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            if focusid == 88:
                self.setFocusId(9000)
            else:self.close()
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title' ):
            if focusid == 51:
                self.launchinfo(105 + self.getCurrentListPosition(),self.getListItem(self.getCurrentListPosition()).getLabel())
            else:self.launchinfo(focusid+47,self.language(focusid))

    def onClick(self, controlID):
        if ( controlID == 51):
            curPos  = self.getCurrentListPosition()
            curItem = self.getListItem(curPos)
            curName = curItem.getLabel()
            curName2 = curItem.getLabel2()
            if curPos == 0:
                value = self.showKeyboard(self.language(66) % curName,curName2)
                if value != "":
                    if value in self.accounts:
                        self.launchinfo(95,"",self.language(93))
                    else:
                        curItem.setLabel2(value)
                        self.getControl(64).setEnabled(True)
                        self.theSettings.setSettingnameInList("Accounts",curName2,value)
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
        elif ( controlID == 61):
            self.launchinboxmenu("")
        elif ( controlID == 62):
            self.deleteing = False
            self.setFocusId(88)
        elif ( controlID == 63):
            self.deleteing = True
            self.setFocusId(88)
        elif ( controlID == 88):
            inboxname = self.inboxlist.getSelectedItem(self.inboxlist.getSelectedPosition()).getLabel()
            if self.deleteing:
                self.accountSettings.removeinbox("Inboxes",inboxname)
                self.accountinboxes.remove(inboxname)
                self.buildinboxlist()
                self.deleteing = False
            else:self.launchinboxmenu(inboxname)
            self.setFocusId(9000)
        elif ( controlID == 64):
            self.theSettings.saveXMLfromArray()
            self.newaccount = False
        elif ( controlID == 65):
            self.close()


    def launchinboxmenu(self, inbox):
        if inbox == "":self.Addinbox("Inboxes",inbox)
        inboxes = self.buildinboxdict(self.accountSettings)
        w = XinBox_InBoxMenu.GUI("XinBox_InBoxMenu.xml",self.scriptPath,"DefaultSkin",accountsetts=self.accountSettings,theinbox=inbox,lang=self.language,inboxlist=inboxes)
        w.doModal()
        ID = w.returnID
        if ID != 0:
            Inboxname = w.inbox
            if inbox == "":
                self.accountinboxes.append(Inboxname)
            else:
                self.accountinboxes.remove(inbox)
                self.accountinboxes.append(Inboxname)
            self.buildinboxlist()
        del w

            
    def crnewaccount(self,accountname):
        self.Addaccount("Accounts",accountname)

    def addnewaccount(self, settingname,value1,value2="",type="text"):
        self.theSettings.addSettingInList(settingname,value1,value2,"settings")
        return

    def addinbox(self, settingname,value1,value2="",type="text"):
        self.accountSettings.addSettingInList(settingname,value1,value2,"settings")
        return    

    def onFocus(self, controlID):
        pass

       
    def SettingListItem(self, label1,label2):
        if label2 == "-":
            return xbmcgui.ListItem(label1,"","","")
        elif label2 == "True":
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
        keyboard = xbmc.Keyboard(default,heading)
        if hidden == 1:keyboard.setHiddenInput(True)
        keyboard.doModal()
        if hidden == 1:keyboard.setHiddenInput(False)
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return default
   
    def launchinfo(self, focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.scriptPath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        del dialog


