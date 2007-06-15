"""
    ircXBMC Settings
    Author: Sean Donnellan (Donno)  [darkdonno@gmail.com]

    Depedeancy: Language,Settings,WindowSettings class

    f=open("q:\\outFile.txt", "w")
    sys.stdout = f

"""

__title__ = 'IRC-XBMC Settings'

import os
import sys
import xbmcgui
scriptPath = os.getcwd().replace( ';' , '' )
sys.path.append( os.path.join( scriptPath ,'libs' ) )

from language import Language
from settings import Settings
from windowsettings import WindowSettings

class ircXBMC_Settings(WindowSettings):
    """
        Add IRC Specifc stuff to this here
    """
    def __init__(self,xmlName,thescriptPath,defaultName,forceFallback, scriptSettings, language, title=__title__):
        WindowSettings.__init__(self, xmlName,thescriptPath,defaultName,forceFallback, scriptSettings, language, title)

    def onListAdd(self, settingName):

        if (settingName == "Servers"):
            serverName = self.showKeyboard(self.language.string(12,"Add %s") % self.language.string(14,"item"),"")
            defSetts = { 'Auto Connect': ["false","boolean"], 'Address': ["irc.SERVER.net","text"],'Channels': [['#xbmc'],'simplelist']}
            # Could show  a CreateServerDialog that gets all the ^ infomation there :) but this way its nice and simple
            newSettings = Settings("",__title__,defSetts,2)
            self.addnewItem(serverName,newSettings,"settings")

def main_Settings():
    print "Starting " + __title__
    lang.load(os.path.join(scriptPath,"Languages"))
    scriptSettings = Settings("ircxbmc.xml",__title__, defSettings)

    winSettings = ircXBMC_Settings("Script_ircXSettings.xml",scriptPath,"DefaultSkin",0,scriptSettings=scriptSettings,language=lang)
    winSettings.doModal()
    del winSettings

    print __title__ + " has been exited"

if __name__ == "__main__":
    lang = Language(__title__)

    defSettingsForAServer = { 'Auto Connect': ["false","boolean"], 'Address': ["irc.freenode.net","text"],'Port': ["6667","text"],'Channels': [['#xbmc'],'simplelist']}
    defServerSettings = Settings("",__title__,defSettingsForAServer,2)

    defSettings = {
        "Username": ["donno","text"],
        "Nickname": ["donno","text"],
        "Secondary Nickname": ["donnoII","text"],
        "Real Name": ["Donno", "text"],
        "Show TimeStamp": ["true","boolean"],
        "Quit Message": ["Quitting","text"],
        "Away Message": ["I'm busy","text"],
        "Auto Connect": ["true","boolean"],
        "Servers": [['server',[["FreeNode",defServerSettings,"settings"]]],"list"]
        }
    main_Settings()
