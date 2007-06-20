import os
import sys
import xbmcgui, default

from XinBox_Settings import Settings
from XinBox_AccountMenu import AccountSettings

    
class Account_Settings (AccountSettings):
    def __init__(self,xmlName,thescriptPath,defaultName,forceFallback, scriptSettings,language, title="XinBox",account="Default"):
        self.title = title
        AccountSettings.__init__(self, xmlName,thescriptPath,defaultName,forceFallback, scriptSettings,language,title,account)

    def Addsetting(self,settingname,newName):
        defSettingsForAnAccount = {
            "Account Password": ["-","text"],
            "Default Account": ["-","boolean"],
            "Inboxes": [['Inbox',[]],"list"]}
        newSettings = Settings("",self.title,defSettingsForAnAccount,2)
        self.addnewItem(settingname,newName,newSettings,"settings")
