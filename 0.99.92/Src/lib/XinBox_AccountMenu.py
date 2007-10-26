


import xbmcgui, xbmc, os, random, traceback
import XinBox_Util
import XinBox_InBoxMenu
import XinBox_InfoDialog
from os.path import join, exists
from os import mkdir
from XinBox_Settings import Settings

DATADIR = XinBox_Util.__datadir__
SETTINGSDIR = XinBox_Util.__accountsdir__

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
        for set in accountsettings.getSetting("Inboxes")[1]:
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
            self.unsaveddef = self.defaultaccount
            self.unsavemm = self.mmaccount
        xbmcgui.unlock()

    def setupvars(self):
        self.saved = True
        self.savedaccountname = "-"
        self.control_action = XinBox_Util.setControllerAction()
        self.inboxlist = self.getControl(88)
        if self.theSettings.getSetting("Default Account") == self.account:
            self.defaultaccount = True
        else:self.defaultaccount = False
        if self.theSettings.getSetting("Mini Mode Account") == self.account:
            self.mmaccount = True
        else:self.mmaccount = False
        if self.accountSettings.getSetting("Mini Mode SFX") == "True":
            self.mmenablesfx = True
        else:self.mmenablesfx = False
        if self.accountSettings.getSetting("XinBox Promote") == "True":
            self.promote = True
        else:self.promote  = False
        if self.accountSettings.getSetting("Auto Check") == "True":
            self.autocheck = True
        else:self.autocheck  = False
        if self.accountSettings.getSetting("Email Dialogs") == "True":
            self.emaildia = True
        else:self.emaildia  = False        
        self.setupcompsetts()
        self.hashlist = self.buildhashlist()
        self.origaccounthash = str(self.accountSettings.getSetting("Account Hash"))
        self.newaccounthash = self.origaccounthash

    def setupcompsetts(self):
        self.checksettings = str(self.accountSettings.settings)

    def checkforchanges(self):
        if self.account != "":
            if str(self.accountSettings.settings) != self.checksettings:
                self.getControl(64).setEnabled(True)
                self.saved = False
            else:
                if self.defaultaccount != self.unsaveddef:
                    self.getControl(64).setEnabled(True)
                    self.saved = False
                elif self.mmaccount != self.unsavemm:
                    self.getControl(64).setEnabled(True)
                    self.saved = False                   
                else:
                    self.getControl(64).setEnabled(False)
                    self.saved = True
        else:
            self.getControl(64).setEnabled(False)
            self.saved = True

    def buildhashlist(self):
        hashlist = {}
        for set in self.accountSettings.getSetting("Inboxes")[1]:
            hashlist[set[0]] = set[0]
        return hashlist
        
    def setupcontrols(self):
        for ID in [61,62,63,64,65]:
            self.getControl(ID).setLabel(self.language(ID))
        self.getControl(64).setEnabled(False)
        self.getControl(105).setSelected(self.mmaccount)
        self.getControl(104).setSelected(self.defaultaccount)
        self.getControl(106).setSelected(self.mmenablesfx)
        self.getControl(107).setSelected(self.promote)
        self.getControl(108).setSelected(self.autocheck)
        self.getControl(109).setSelected(self.emaildia)
        if self.newaccount:
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
        self.addItem(self.language(53))
        self.addItem(self.SettingListItem(self.language(354), self.accountSettings.getSetting("MiniMode Time")))
        self.addItem(self.language(357))
        self.addItem(self.language(353))
        self.addItem(self.language(336))
        self.addItem(self.language(203))
        self.addItem(self.language(205))
        
    def buildinboxlist(self):
        self.inboxlist.reset()
        inbox = self.accountSettings.getSetting("Default Inbox")
        for item in self.accountinboxes:
            if item == inbox:
                self.inboxlist.addItem(self.SettingListItem(item, self.language(204)))
            else:self.inboxlist.addItem(self.SettingListItem(item, ""))
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
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu' ):
            if focusid == 88:
                self.setFocusId(9000)
            else:
                if not self.saved:
                    dialog = xbmcgui.Dialog()
                    if dialog.yesno(self.language(77), self.language(65) + "?",self.language(79)):
                        self.close()
                else:
                    self.close()
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Info' ):
            if focusid == 51:
                if self.getCurrentListPosition() == 5:
                    self.launchinfo(144,self.getListItem(self.getCurrentListPosition()).getLabel())
                elif self.getCurrentListPosition() == 4:
                    self.launchinfo(162,self.getListItem(self.getCurrentListPosition()).getLabel())
                elif self.getCurrentListPosition() == 3:
                    self.launchinfo(145,self.getListItem(self.getCurrentListPosition()).getLabel())
                elif self.getCurrentListPosition() == 6:
                    self.launchinfo(163,self.getListItem(self.getCurrentListPosition()).getLabel())
                elif self.getCurrentListPosition() == 7:
                    self.launchinfo(171,self.getListItem(self.getCurrentListPosition()).getLabel())
                elif self.getCurrentListPosition() == 8:
                    self.launchinfo(173,self.getListItem(self.getCurrentListPosition()).getLabel())                    
                else:self.launchinfo(105 + self.getCurrentListPosition(),self.getListItem(self.getCurrentListPosition()).getLabel())
            else:self.launchinfo(focusid+47,self.language(focusid))

##    def editallaccounts(self,settingname,value,accountname=""):
##        for item in self.theSettings.getSetting("Accounts")[1]:
##            if item[0] != accountname:
##                account = self.theSettings.getSettingInListbyname("Accounts",item[0])
##                account.setSetting(settingname,value)

    def onClick(self, controlID):
        if ( controlID == 51):
            curPos  = self.getCurrentListPosition()
            curItem = self.getListItem(curPos)
            curName = curItem.getLabel()
            curName2 = curItem.getLabel2()
            if curPos == 0:
                value = self.showKeyboard(self.language(66) % self.language(51),curName2)
                if value != False and value != "" and value != curName2:
                    if value in self.accounts:
                        self.launchinfo(95,"",self.language(93))
                    else:
                        curItem.setLabel2(value)
                        self.theSettings.setSettingnameInList("Accounts",curName2,value)
                        self.newaccounthash  = str(hash(value))
                        self.accountSettings.setSetting("Account Hash",self.newaccounthash)
                        self.accounts = self.buildaccounts()
                        self.account = value
                        self.checkforchanges()
            elif curPos == 1:
                value = self.showKeyboard(self.language(66) % self.language(52),"",1)
                if value != False:
                    if value == "":
                        self.accountSettings.setSetting("Account Password","-")
                        curItem.setLabel2(self.language(76))
                    else:
                        self.accountSettings.setSetting("Account Password",value.encode("hex"))
                        curItem.setLabel2('*' * len(value))
                    self.checkforchanges()
            elif curPos == 2:
                self.defaultaccount = not self.defaultaccount
                self.getControl(104).setSelected(self.defaultaccount)
                self.checkforchanges()
            elif curPos == 3:
                dialog = xbmcgui.Dialog()
                value = dialog.numeric(0,self.language(354), curName2)
                curItem.setLabel2(value)
                self.accountSettings.setSetting("MiniMode Time",value)
                self.checkforchanges()
            elif curPos == 4:
                self.mmenablesfx = not self.mmenablesfx
                self.getControl(106).setSelected(self.mmenablesfx)
                self.accountSettings.setSetting("Mini Mode SFX", str(self.mmenablesfx))
                self.checkforchanges()
            elif curPos == 5:
                self.mmaccount = not self.mmaccount
                self.getControl(105).setSelected(self.mmaccount)
                self.checkforchanges()
            elif curPos == 6:
                self.promote = not self.promote
                self.getControl(107).setSelected(self.promote)
                self.accountSettings.setSetting("XinBox Promote", str(self.promote))
                self.checkforchanges()
            elif curPos == 7:
                self.autocheck = not self.autocheck
                self.getControl(108).setSelected(self.autocheck)
                self.accountSettings.setSetting("Auto Check", str(self.autocheck))
                self.checkforchanges()
            elif curPos == 8:
                self.emaildia = not self.emaildia
                self.getControl(109).setSelected(self.emaildia)
                self.accountSettings.setSetting("Email Dialogs", str(self.emaildia))
                self.checkforchanges()                
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
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), self.language(78)):
                    if self.accountSettings.getSetting("Default Inbox") == inboxname:
                       self.accountSettings.setSetting("Default Inbox", "-")
                    self.accountSettings.removeinbox("Inboxes",inboxname)
                    self.accountinboxes.remove(inboxname)
                    self.removehash(inboxname)
                    self.buildinboxlist()
                    self.deleteing = False
                    self.checkforchanges()
            else:self.launchinboxmenu(inboxname)
            self.setFocusId(9000)
        elif ( controlID == 64):
            if self.defaultaccount:
                self.theSettings.setSetting("Default Account", self.account)
            else:
                if self.theSettings.getSetting("Default Account") == self.account:
                    self.theSettings.setSetting("Default Account", "-")
            if self.mmaccount:
                self.theSettings.setSetting("Mini Mode Account", self.account)
                XinBox_Util.addauto(self.scriptPath, self.account, self.scriptPath)
            else:
                if self.theSettings.getSetting("Mini Mode Account") == self.account:
                    self.theSettings.setSetting("Mini Mode Account", "-")
                    XinBox_Util.removeauto(self.scriptPath, self.account, self.scriptPath)
            self.theSettings.saveXMLfromArray()
            self.getControl(64).setEnabled(False)
            self.setupcompsetts()
            self.saved = True
            self.unsavemm = self.mmaccount
            self.unsaveddef = self.defaultaccount
            self.accounts = self.buildaccounts()
            self.savedaccountname = self.account
            self.getControl(81).setLabel(self.account)
            self.builddirs()
            self.newaccount = False
            self.launchinfo(48,"",self.language(49))
            self.setFocusId(65)
        elif ( controlID == 65):
            if not self.saved:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), self.language(65) + "?",self.language(79)):
                    self.close()
            else:self.close()

    def builddirs(self):
        accountOrigdir = join(SETTINGSDIR,self.origaccounthash)
        accountNewDir = join(SETTINGSDIR,self.newaccounthash)
        if exists(accountOrigdir):
            if accountOrigdir != accountNewDir:
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
                if exists(Origdir):
                    if Origdir != NewDir:
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
        w = XinBox_InBoxMenu.GUI("XinBox_InBoxMenu.xml",self.scriptPath,"DefaultSkin",accountsetts=self.accountSettings,theinbox=inbox,lang=self.language)
        w.doModal()
        ID = w.returnID
        Inboxname = w.inbox
        change = w.settchanged
        if change == "True" and self.account != "":
            self.getControl(64).setEnabled(True)
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
