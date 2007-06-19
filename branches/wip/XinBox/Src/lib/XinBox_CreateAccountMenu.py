"""
    WindowSettings

    A WindowXML setup to handle the basis modifying the settings provided by the settings class

    Author: Sean Donnellan (Donno)  [darkdonno@gmail.com]
    Depends on: xbmcgui, xbmc, os
    Requires: A Setting and Language class passed to it

    How to Use:
        from windowsettings import WindowSettings
        class className(WindowSettings):
            def __init__(self,xmlName,thescriptPath,defaultName,forceFallback):
                WindowSettings.__init__(self, xmlName,thescriptPath,defaultName,forceFallback, scriptSettings, lang, __title__)
                
        # the point is u pass all the main info on as well as the settings and language classes and title
"""


import xbmcgui,traceback
import xbmc
import os



# Maybe make add inbox a dialog over the top of this account :-D


class WindowSettings(xbmcgui.WindowXML):
    def __init__(self, xmlName, thescriptPath,defaultName,forceFallback, scriptSettings,language, title,account):
        self.account = account
     #   self.account = "Chloe"
        
        self.title = title
        self.thescriptPath = thescriptPath
        self.depth = 0
        self.language = language.string
        
        self.settingName = ""
        self.theSettings = scriptSettings
        self.curSettings = self.theSettings

        self.accountSettings = self.getaccountsettings(self.account)
        self.accountinboxes = self.buildinboxdict(self.accountSettings)
        self.inboxSettings = self.getinboxsettings(self.account,"Default")

    def buildinboxdict(self,accountsettings):
        self.inboxes = {} 
        for set in self.accountSettings.getSetting("Inboxes")[1] :
            self.inboxes[set[0]] = set[1]
        return self.inboxes

    def getinboxsettings(self,account,inbox):
        temp = self.theSettings.getSettingInListbyname("Accounts",account)
        return temp.getSettingInListbyname("Inboxes",inbox)

    def getaccountsettings(self,account):
        return self.theSettings.getSettingInListbyname("Accounts",account)

    def onInit(self):
        try:
            xbmcgui.lock()
            self.builsettingsList()
            self.buildinboxlist()
            self.getControl(80).setLabel(self.language(50))
            self.buttonids = [61,62,63,64,65]
            for ID in self.buttonids:
                self.getControl(ID).setLabel(self.language(ID))
            self.getControl(82).setLabel(self.language(20))
            self.getControl(83).setLabel(self.language(21))
            xbmcgui.unlock()
        except: traceback.print_exc()
    
    def builsettingsList(self):
        for set in self.accountSettings.settings:
            if self.accountSettings.getSettingType(set) == "text" or self.accountSettings.getSettingType(set) == "boolean":
                if self.accountSettings.getSetting(set) == "-":
                    self.addItem(self.SettingListItem(set, ""))
                else:
                    self.addItem(self.SettingListItem(set, self.accountSettings.getSetting(set)))

    def buildinboxlist(self):
        for set in self.accountinboxes:
            if set != "Default":
                self.addItem(self.SettingListItem(set, ""))
##        test = self.inboxes[self.getListItem(4).getLabel()]
##      # will be able to do: test = self.inboxes[self.getListItem(self.getCurrentListPosition()).getLabel()]  
##        print "test for inbox = " + str(test)

    def onAction(self, action):
        pass

    def onClick(self, controlID):
        try:
            if ( controlID == 51):
                curPos  = self.getCurrentListPosition()
                curItem = self.getListItem(curPos)
                curName = curItem.getLabel()
                curName2 = curItem.getLabel2()
                if curName2 == "-":
                    curName2 = ""
                type = self.accountSettings.getSettingType(curName)
                if (type == "text"):
                    value = self.showKeyboard(self.language(66) % curName,curName2)
                    curItem.setLabel2(value)
                    self.Addsetting("Accounts",value)
                    self.accountSettings = self.getaccountsettings(value)
                    self.accountSettings.setSetting(curName,value)
            elif ( controlID == 64):
                self.theSettings.saveXMLfromArray()
            elif ( controlID == 65):
                self.close()
        except:traceback.print_exc()

    def addnewItem(self, settingname,value1,value2="",type="text"):
        self.curSettings.addSettingInList(settingname,value1,value2,"settings")
        return

    def onFocus(self, controlID):
        pass

    def showKeyboard(self, heading,default=""):
        # Open the Virutal Keyboard.
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return default
        
    def SettingListItem(self, label1,label2):
        if label2 == "true":
            self.getControl(104).setSelected(True)
            return xbmcgui.ListItem(label1,"","","")
        elif label2 == "false":
            self.getControl(104).setSelected(False)
            return xbmcgui.ListItem(label1,"","","")
        else:
            return xbmcgui.ListItem(label1,label2,"","")

    def showKeyboard(self, heading,default=""):
        # Open the Virutal Keyboard.
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return default
