


import os
import sys
import xbmcgui, default

from language import Language
from settings import Settings
from XinBox_AccountMenu import AccountSettings

__title__ = "XinBox"
    
class XinBox_Settings (AccountSettings):
    def __init__(self,xmlName,thescriptPath,defaultName,forceFallback, scriptSettings,language, title=__title__,account="Default"):
        AccountSettings.__init__(self, xmlName,thescriptPath,defaultName,forceFallback, scriptSettings,language,title,account)

    def Addsetting(self,settingname,newName):
        defSettingsForAnAccount = {
            "Account Password": ["-","text"],
            "Default Account": ["-","boolean"],
            "Inboxes": [['Inbox',[]],"list"]}
        newSettings = Settings("",__title__,defSettingsForAnAccount,2)
        self.addnewItem(settingname,newName,newSettings,"settings")
