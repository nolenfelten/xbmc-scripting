


import os
import sys
import xbmcgui, default

from language import Language
from settings import Settings
from XinBox_CreateAccountMenu import WindowSettings
__title__ = "XinBox"
scriptpath = default.__scriptpath__

    
class ircXBMC_Settings(WindowSettings):
    def __init__(self,xmlName,thescriptPath,defaultName,forceFallback, scriptSettings,language, title=__title__,account="Default"):
        self.lang = language.string
        WindowSettings.__init__(self, xmlName,thescriptPath,defaultName,forceFallback, scriptSettings,language,title,account)

    def Addsetting(self,settingname,newName):
        defSettingsForAInBox =  {
            self.lang(67): ["-","text"],
            self.lang(68): ["-","text"],
            self.lang(69): ["-","text"],
            self.lang(70): ["-","text"],
            self.lang(71): ["-","text"],
            self.lang(72): ["-","text"]}
        defInboxSettings = Settings("",__title__,defSettingsForAInBox,2)
        defSettingsForAnAccount = {
            self.lang(51): ["-","text"],
            self.lang(52): ["-","text"],
             self.lang(53): ["-","boolean"],
            "Inboxes": [['Inbox',[["Default",defInboxSettings,"settings"]]],"list"]}
        newSettings = Settings("",__title__,defSettingsForAnAccount,2)
        self.addnewItem(settingname,newName,newSettings,"settings")

##def main_Settings():
##    lang.load(os.path.join(scriptPath,"language"))
##    scriptSettings = Settings("XinBox_Settings.xml",__title__, defSettings)
##
##    winSettings = ircXBMC_Settings("XinBox_CreateAccountMenu.xml",scriptPath,"DefaultSkin",0,scriptSettings=scriptSettings,language=lang,)
##    winSettings.doModal()
##    del winSettings
##
##if __name__ == "__main__":
##    lang = Language(__title__)
##
##    defSettingsForAInBox =  {
##        _(67): ["-","text"],
##        _(68): ["-","text"],
##        _(69): ["-","text"],
##        _(70): ["-","text"],
##        _(71): ["-","text"],
##        _(72): ["-","text"]}
##    defInboxSettings = Settings("",__title__,defSettingsForAInBox,2)
##    defSettingsForAnAccount = {
##        _(51): ["-","text"],
##        _(52): ["-","text"],
##         _(53): ["-","boolean"],
##        "Inboxes": [['Inbox',[["Default",defInboxSettings,"settings"]]],"list"]}
##
##    defAccountSettings = Settings("",__title__,defSettingsForAnAccount,2)
##    defSettings = {
##        "Accounts": [['Account',[["Default",defAccountSettings,"settings"]]],"list"]}
##
##
##
##    main_Settings()
