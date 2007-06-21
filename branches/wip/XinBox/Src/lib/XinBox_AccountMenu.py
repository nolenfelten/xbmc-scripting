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
        try:
            self.myinit = 1
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
                self.accountSettings = False
                self.accountinboxes = []
            else:
                self.accountSettings = self.getaccountsettings(self.account)
                self.accountinboxes = self.buildinboxdict(self.accountSettings)
                self.inboxsettings = self.getinboxsettings(self.account)
        except: traceback.print_exc()

    def buildinboxdict(self,accountsettings):
        inboxes = []
        for set in self.accountSettings.getSetting("Inboxes")[1] :
            inboxes.append(set[0])
        return inboxes

    def getinboxsettings(self,inbox):
        return self.accountSettings.getSettingInListbyname("Inboxes",inbox)

    def getaccountsettings(self,account):
        return self.theSettings.getSettingInListbyname("Accounts",account)
    
    def onInit(self):
        try:
            xbmcgui.lock()
            if self.myinit == 1:
                self.setupvars()
                self.clearList()
                self.inboxlist.reset()
                self.setupcontrols()
                self.builsettingsList()
                self.buildinboxlist()
                self.myinit = 0
            xbmcgui.unlock()
        except: traceback.print_exc()

    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        self.inboxlist = self.getControl(88)
        self.mysettings = {}
        self.addedinbox = False

    def setupcontrols(self):
        self.getControl(82).setLabel(self.language(20))
        self.getControl(83).setLabel(self.language(21))
        self.buttonids = [61,62,63,64,65]
        for ID in self.buttonids:
            self.getControl(ID).setLabel(self.language(ID))        
        if self.newaccount:
            self.getControl(64).setEnabled(False)
         #   self.getControl(63).setEnabled(False)   uncomment once i add in the save button
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
        self.inboxlist.reset()
        for item in self.accountinboxes:
            self.inboxlist.addItem(self.SettingListItem(item, ""))
        if self.inboxlist.size() == 0:
            self.inboxlist.addItem(self.SettingListItem(self.language(75), ""))
            self.getControl(63).setEnabled(False)
            self.getControl(62).setEnabled(False)
        else:
            self.getControl(62).setEnabled(True)

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
            self.launchinboxmenu("XinBoxNew")
        elif ( controlID == 62):
            self.setFocusId(88)
        elif ( controlID == 88):
            inboxname = self.inboxlist.getSelectedItem(self.inboxlist.getSelectedPosition()).getLabel()
            try:
                self.inboxsettings = self.getinboxsettings(inboxname)
            except:self.inboxsettings = self.mysettings[inboxname]
            self.launchinboxmenu(inboxname)
        elif ( controlID == 64):
            if self.newaccount:
                self.crnewaccount()
            if self.addedinbox:
                self.crnewinbox()
            self.theSettings.saveXMLfromArray()
        elif ( controlID == 65):
            self.close()


    def launchinboxmenu(self, inbox):
        try:
            self.newaccount = True
            w = XinBox_InBoxMenu.GUI("XinBox_InBoxMenu.xml",self.scriptPath,"DefaultSkin",bforeFallback=0,notnewaccount=self.newaccount,inboxsetts=self.inboxsettings,accountsetts=self.accountSettings,theinbox=inbox)
            w.doModal()
            if w.mysettings != False:
                self.mysettings[w.mysettings[0]] = w.mysettings
                self.addedinbox = True
                self.accountinboxes.append(w.mysettings[0])
                self.buildinboxlist()
            else:
                self.accountSettings = w.accountsetts
            self.setFocusId(9000)
            del w
        except: traceback.print_exc()

    def crnewinbox(self):
        for set in self.mysettings:
            self.Addinbox("Inboxes",self.mysettings[set][0])
            self.inboxsettings = self.getinboxsettings(self.mysettings[set][0])
            self.inboxsettings.setSetting("POP Server",self.mysettings[set][1])
            self.inboxsettings.setSetting("SMTP Server",self.mysettings[set][2])
            self.inboxsettings.setSetting("Account Name",self.mysettings[set][3])
            self.inboxsettings.setSetting("Account Password",self.mysettings[set][4])
            self.inboxsettings.setSetting("SERV Inbox Size",self.mysettings[set][5])
            self.inboxsettings.setSetting("XinBox Inbox Size",self.mysettings[set][6])
            self.inboxsettings.setSetting("POP SSL",self.mysettings[set][7])
            self.inboxsettings.setSetting("SMTP SSL",self.mysettings[set][8])
        self.mysettings = {}
        self.addedinbox = False
            
    def crnewaccount(self):
        self.Addaccount("Accounts",self.accountname)
        self.accountSettings = self.getaccountsettings(self.accountname)
        self.accountSettings.setSetting("Account Password",self.accountpass)
        self.accountSettings.setSetting("Default Account",str(self.defaultaccount))
        self.newaccount = False

    def addnewaccount(self, settingname,value1,value2="",type="text"):
        self.theSettings.addSettingInList(settingname,value1,value2,"settings")
        return

    def addinbox(self, settingname,value1,value2="",type="text"):
        self.accountSettings.addSettingInList(settingname,value1,value2,"settings")
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


