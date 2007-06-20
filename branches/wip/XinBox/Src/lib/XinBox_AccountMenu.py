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
        self.account = account
        if self.account == "XinBoxDefault":
            self.newaccount = True
        else:self.newaccount = False
        
        self.title = title
        self.scriptPath = thescriptPath
        self.language = language

        self.theSettings = scriptSettings
        
        if self.newaccount:
            self.accountname = "-"
            self.accountpass = "-"
            self.defaultaccount = False
            self.inboxsettings = False
        else:
            self.accountSettings = self.getaccountsettings(self.account)
            self.accountinboxes = self.buildinboxdict(self.accountSettings)
            self.inboxsettings = self.accountSettings

    def buildinboxdict(self,accountsettings):
        inboxes = {} 
        for set in self.accountSettings.getSetting("Inboxes")[1] :
            inboxes[set[0]] = set[1]
        return inboxes

    def getinboxsettings(self,accountsettings,inbox):
        return accountsettings.getSettingInListbyname("Inboxes",inbox)

    def getaccountsettings(self,account):
        return self.theSettings.getSettingInListbyname("Accounts",account)
    
    def onInit(self):
        xbmcgui.lock()
        self.setupvars()
        self.clearList()
        self.inboxlist.reset()
        self.setupcontrols()
        self.builsettingsList()
        self.buildinboxlist()
        xbmcgui.unlock()

    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        self.inboxlist = self.getControl(88)

    def setupcontrols(self):
        self.getControl(82).setLabel(self.language(20))
        self.getControl(83).setLabel(self.language(21))
        self.buttonids = [61,62,63,64]
        for ID in self.buttonids:
            self.getControl(ID).setLabel(self.language(ID))        
        if self.newaccount:
            self.getControl(64).setEnabled(False)
            self.getControl(63).setEnabled(False)
            self.getControl(62).setEnabled(False)
            self.getControl(80).setLabel(self.language(50))
        else:self.getControl(80).setLabel(self.language(74))
    
    def builsettingsList(self):
        if self.newaccount:
            self.addItem(self.SettingListItem(self.language(51),""))
            self.addItem(self.SettingListItem(self.language(52),self.language(76)))
            self.addItem(self.SettingListItem(self.language(53),""))
        else:
            self.addItem(self.SettingListItem(self.language(51), self.account))
            if self.accountSettings.getSetting("Account Password") == "-":
                self.addItem(self.SettingListItem(self.language(52), self.language(76)))
            else:
                self.addItem(self.SettingListItem(self.language(52), '*' * len(self.accountSettings.getSetting("Account Password"))))
            self.addItem(self.SettingListItem(self.language(53), self.accountSettings.getSetting("Default Account")))
        
    def buildinboxlist(self):
        if self.newaccount:
            self.inboxlist.addItem(self.SettingListItem(self.language(75), ""))
        else:
            for set in self.accountinboxes:
                if set != "XinBoxDefault":
                    self.inboxlist.addItem(self.SettingListItem(set, ""))
            if self.inboxlist.size() == 0:
                self.inboxlist.addItem(self.SettingListItem(self.language(75), ""))
                self.getControl(63).setEnabled(False)
                self.getControl(62).setEnabled(False)

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
                    curItem.setLabel2(value)
                    self.getControl(64).setEnabled(True)
                    if self.newaccount:self.accountname = value
                    else:self.theSettings.setSettingnameInList("Accounts",curName2,value)
            elif curPos == 1:
                value = self.showKeyboard(self.language(66) % curName,"",1)
                if value == "":
                    if self.newaccount:self.accountpass = "-"
                    else:self.accountSettings.setSetting("Account Password","-")
                    curItem.setLabel2(self.language(76))
                else:
                    if self.newaccount:self.accountpass = value
                    else:self.accountSettings.setSetting("Account Password",value)
                    curItem.setLabel2('*' * len(value)) 
            elif curPos == 2:
                self.defaultaccount = not self.defaultaccount
                self.getControl(104).setSelected(self.defaultaccount)
                if not self.newaccount:self.accountSettings.setSetting("Default Account",str(self.defaultaccount))
        elif ( controlID == 61):
            try:
                self.launchinboxmenu("XinBoxNew")
            except:traceback.print_exc()
        elif ( controlID == 64):
            if self.newaccount:self.crnewaccount()
            self.theSettings.saveXMLfromArray()
            self.close()


    def launchinboxmenu(self, inbox):
        w = XinBox_InBoxMenu.GUI("XinBox_InBoxMenu.xml",self.scriptPath,"DefaultSkin",bforeFallback=0,inboxsetts=self.inboxsettings,theinbox=inbox)
        w.doModal()
        del w
        
    def crnewaccount(self):
        self.Addsetting("Accounts",self.accountname)
        self.accountSettings = self.getaccountsettings(self.accountname)
        self.accountSettings.setSetting("Account Password",self.accountpass)
        self.accountSettings.setSetting("Default Account",str(self.defaultaccount))        

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
        keyboard = xbmc.Keyboard(default,heading)
        if hidden == 1:keyboard.setHiddenInput(True)
        keyboard.doModal()
        if hidden == 1:keyboard.setHiddenInput(False)
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return default

    def launchinfo(self, focusid, label):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.scriptPath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language)
        dialog.doModal()
        del dialog


