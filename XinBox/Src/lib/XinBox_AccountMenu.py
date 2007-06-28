


import xbmcgui, xbmc, os, random
import XinBox_Util
import XinBox_InBoxMenu
import XinBox_InfoDialog
from os.path import join, exists
from os import mkdir
DATADIR = "P:\\script_data\\"
SETTINGSDIR = "P:\\script_data\\XinBox\\Accounts\\"

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
        self.originalSettings = self.theSettings

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
        self.savedaccountname = "-"
        self.control_action = XinBox_Util.setControllerAction()
        self.inboxlist = self.getControl(88)
        self.defaultaccount = self.accountSettings.getSetting("Default Account")
        self.hashlist = self.buildhashlist()
        self.origaccounthash = self.accountSettings.getSetting("Account Hash")
        self.newaccounthash = self.origaccounthash

    def buildhashlist(self):
        hashlist = {}
        for set in self.accountSettings.getSetting("Inboxes")[1]:
            hashlist[set[0]] = set[0]
        return hashlist
        
    def setupcontrols(self):
        self.getControl(82).setLabel(self.language(20))
        self.getControl(83).setLabel(self.language(21))
        self.buttonids = [61,62,63,64,65]
        for ID in self.buttonids:
            self.getControl(ID).setLabel(self.language(ID))        
        if self.newaccount:
            self.getControl(64).setEnabled(False)
            self.getControl(80).setLabel(self.language(50))
        else:
            self.getControl(80).setLabel(self.language(74))
            self.getControl(81).setLabel(self.account)
    
    def buildsettingsList(self):
        self.clearList()
        self.addItem(self.SettingListItem(self.language(51), self.account))
        if self.accountSettings.getSetting("Account Password") == "-":
            self.addItem(self.SettingListItem(self.language(52), self.language(76)))
        else:
            self.addItem(self.SettingListItem(self.language(52), '*' * len(self.accountSettings.getSetting("Account Password").decode("hex"))))
        self.addItem(self.SettingListItem(self.language(53), self.defaultaccount))
        
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

    def editallaccounts(self,settingname,value,accountname=""):
        for item in self.theSettings.getSetting("Accounts")[1]:
            if item[0] != accountname:
                account = self.theSettings.getSettingInListbyname("Accounts",item[0])
                account.setSetting(settingname,value)

    def onClick(self, controlID):
        if ( controlID == 51):
            curPos  = self.getCurrentListPosition()
            curItem = self.getListItem(curPos)
            curName = curItem.getLabel()
            curName2 = curItem.getLabel2()
            if curPos == 0:
                value = self.showKeyboard(self.language(66) % curName,curName2)
                if value != False and value != "" and value != curName2:
                    if value in self.accounts:
                        self.launchinfo(95,"",self.language(93))
                    else:
                        curItem.setLabel2(value)
                        self.getControl(64).setEnabled(True)
                        self.theSettings.setSettingnameInList("Accounts",curName2,value)
                        self.newaccounthash  = str(hash(value))
                        self.accountSettings.setSetting("Account Hash",self.newaccounthash)
                        self.account = value
            elif curPos == 1:
                value = self.showKeyboard(self.language(66) % curName,"",1)
                if value != False:
                    if value == "":
                        self.accountSettings.setSetting("Account Password","-")
                        curItem.setLabel2(self.language(76))
                    else:
                        self.accountSettings.setSetting("Account Password",value.encode("hex"))
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
            inboxname = self.inboxlist.getSelectedItem().getLabel()
            if self.deleteing:
                if self.launchinfo(78,"",self.language(77)):
                    self.accountSettings.removeinbox("Inboxes",inboxname)
                    self.accountinboxes.remove(inboxname)
                    self.removehash(inboxname)
                    self.buildinboxlist()
                    self.deleteing = False
            else:self.launchinboxmenu(inboxname)
            self.setFocusId(9000)
        elif ( controlID == 64):
            try:
                if self.defaultaccount:
                        self.accountSettings.setSetting("Default Account",str(self.defaultaccount))
                        self.editallaccounts("Default Account","False",self.account)
                self.theSettings.saveXMLfromArray()
                self.savedaccountname = self.account
                self.getControl(81).setLabel(self.account)
                self.builddirs()
                self.newaccount = False
                self.launchinfo(48,"",self.language(49))
            except:traceback.print_exc()
        elif ( controlID == 65):
            if self.launchinfo(79,"",self.language(77)):
                self.close()

    def builddirs(self):
        accountOrigdir = join(SETTINGSDIR,self.origaccounthash)
        accountNewDir = join(SETTINGSDIR,self.newaccounthash)
        if accountOrigdir != accountNewDir:
            if exists(accountOrigdir):
                os.rename(accountOrigdir,accountNewDir)
            else:
                mkdir(accountNewDir)
        self.origaccounthash = self.newaccounthash
        for set0 in self.hashlist:
            set1 = self.hashlist[set0]
            if set1 == "DELETE":
                if exists(join(accountNewDir,str(hash(set0)))):
                    self.removedir(join(accountNewDir,str(hash(set0))))
            else:
                Origdir = join(accountNewDir,str(hash(set0)))
                NewDir = join(accountNewDir,str(hash(set1)))
                if Origdir != NewDir:
                    if exists(Origdir):
                        os.rename(Origdir,NewDir)
                    else:mkdir(NewDir)
        self.hashlist = self.buildhashlist()

    def removedir(self,mydir):
        for root, dirs, files in os.walk(mydir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir(mydir)

    def gohash(self,inbox,Inboxname):
        for set in self.hashlist:
            set1 = self.hashlist[set]
            if inbox == set1:
                self.hashlist[set] = Inboxname
                return
        self.hashlist[Inboxname] = Inboxname

    def removehash(self,inboxname):
        for set in self.hashlist:
            set1 = self.hashlist[set]
            if inboxname == set1:
                self.hashlist[set] = "DELETE"

    def launchinboxmenu(self, inbox):
        if inbox == "":self.Addinbox("Inboxes",inbox)
        inboxes = self.buildinboxdict(self.accountSettings)
        w = XinBox_InBoxMenu.GUI("XinBox_InBoxMenu.xml",self.scriptPath,"DefaultSkin",accountsetts=self.accountSettings,theinbox=inbox,lang=self.language,inboxlist=inboxes)
        w.doModal()
        ID = w.returnID
        Inboxname = w.inbox
        if ID != 0:
            self.gohash(inbox, Inboxname)
            if inbox == "":
                self.accountinboxes.append(Inboxname)
            else:
                self.accountinboxes.remove(inbox)
                self.accountinboxes.append(Inboxname)
            self.buildinboxlist()
        else:
            if inbox == "":self.accountSettings.removeinbox("Inboxes",Inboxname)
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
            return False
   
    def launchinfo(self, focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.scriptPath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        value = dialog.value
        del dialog
        return value
