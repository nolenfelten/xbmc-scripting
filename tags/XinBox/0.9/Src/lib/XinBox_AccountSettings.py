import os
import sys
import xbmcgui

from XinBox_Settings import Settings
from XinBox_AccountMenu import AccountSettings

    
class Account_Settings (AccountSettings):
    def __init__(self,xmlName,thescriptPath,defaultName,forceFallback, scriptSettings,language, title="XinBox",account="Default"):
        self.title = title
        self.srcpath = thescriptPath
        AccountSettings.__init__(self, xmlName,thescriptPath,defaultName,forceFallback, scriptSettings,language,title,account)

    def Addaccount(self,settingname,newName):
        defSettingsForAnAccount = {
            "Account Password": ["-","text"],
            "Default Inbox": ["-","text"],
            "Account Hash": ["-","text"],
            "Inboxes": [['Inbox',[]],"list"],
            "MiniMode Time": ["60","text"],
            "Contacts": [['Contact',[]],"list"]}
        newSettings = Settings("",self.title,defSettingsForAnAccount,2)
        self.addnewaccount(settingname,newName,newSettings,"settings")

    def Addinbox(self,settingname,newName):
        defSettingsForAnAccount = {
            "Email Address": ["-","text"],
            "POP Server": ["-","text"],
            "SMTP Server": ["-","text"],
            "Account Name": ["-","text"],
            "Account Password": ["-","text"],
            "SERV Inbox Size": ["0","text"],
            "XinBox Inbox Size": ["0","text"],
            "Keep Copy Emails": ["True","boolean"],
            "POP SSL": ["0","text"],
            "SMTP SSL": ["0","text"],
            "Inbox Hash": ["-","text"],
            "Email Notification": [self.srcpath+"\\SFX\\Email Notification\\You Have Mail.wav","text"],
            "Mini Mode Enabled": ["True","boolean"],}
        newSettings = Settings("",self.title,defSettingsForAnAccount,2)
        self.addinbox(settingname,newName,newSettings,"settings")
