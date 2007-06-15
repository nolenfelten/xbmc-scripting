#!/usr/bin/env python
# ircXBMC2 - Instant Relay Chat for Xbox Media Center.
# Author: Donno
# Email: Donno (darkdonno@gmail.com)
# Copyright:    ircXBMC by Copyright (C) 2005 Donno
#               The IRCLIB Copyright (C) 1999--2002  Joel Rosdahl

"""
  Copyright (C) 1989, 1991 Free Software Foundation, Inc.
  51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

  Everyone is permitted to copy and distribute verbatim copies
  of this license document, but changing it is not allowed.
  Full License at http://www.gnu.org/copyleft/gpl.html
"""

# // Version History  \\
"""
  24th March 2007 - Added Language Class
  20th March 2007 - Started this script
"""

__title__ = 'IRC-XBMC'
__author__ = 'Donno'
__credits__ = 'Coded by: Donno \nIRC Libary: Joel Rosdahl'
__version__ = '0.1'

import xbmcgui
import os
import sys

scriptPath = os.getcwd().replace( ';' , '' ) #scriptPath = sys.path[0]
scriptMedia = os.path.join( scriptPath ,'media' )
sys.path.append( os.path.join( scriptPath ,'libs' ) )

from language import Language
from settings import Settings
#import irclib

try: Emulating = xbmcgui.Emulating
except: Emulating = False

DEBUG = 1
#irclib.DEBUG = 0

ALPHA = 0
BETA = 1
RC = 2
FINAL = 3

STATUS = ALPHA


# Keys
KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

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

setts = Settings("ircxbmc.xml",__title__,defSettings)

_ = lang.string

from ircXBMC_Settings import ircXBMC_Settings
#f=open("q:\\outFile.txt", "w")
#sys.stdout = f

class Splash(xbmcgui.WindowDialog):
    """
        The opening splash screen
    """
    def __init__(self):
        dPrnt("onInit(): Splash Initalized")
        self.addControl(xbmcgui.ControlImage(180,168,360,240, os.path.join(scriptMedia ,"ircXBMC2.png")))
        if (STATUS == ALPHA):
            self.addControl(xbmcgui.ControlImage(180,168,360,240, os.path.join(scriptMedia , "alpha.png" )))
        elif (STATUS == BETA):
            self.addControl(xbmcgui.ControlImage(180,168,360,240, os.path.join(scriptMedia , "beta.png" )))

    def onAction(self, action):
        self.close()
        dPrnt("onAction(): Splash Closing")


def MenuListItem(label1,label2,thumb,icon):
    basePath = os.path.join(scriptPath,'media')
    li = xbmcgui.ListItem(label1,label2,os.path.join(basePath,thumb),os.path.join(basePath,icon))
    return  li

class IRCSetup(xbmcgui.WindowXML):
    def __init__(self, xmlName, thescriptPath,defaultName,forceFallback):
        self.setup = False

    def onInit(self):
        """
        """
        dPrnt("onInit(): Window Initalized")

        if (self.setup == False):
            self.getControl(13).setLabel(_(8,"Main Menu"))
            self.addItem(MenuListItem(_(0,"Launch IRC Client"),_(4,"Run the client"), "chat.png", "chat.png"))
            self.addItem(MenuListItem(_(1,"Settings"),_(5,"Configure %s") % __title__, "package_settings.png", "package_settings.png"))
            self.addItem(MenuListItem(_(2,"About"),_(6,"About the Script"), "khelpcenter.png", "khelpcenter.png"))
            self.addItem(MenuListItem(_(3,"Leave %s") % __title__,_(7,"Close the script"), "exit.png", "exit.png"))
            self.setup = True

    def onAction(self, action):
        """"
            onAction in WindowXML works same as on a Window or WindowDialog its for keypress/controller buttons etc
            This function has been implemented and works
        """
        buttonCode =  action.getButtonCode()
        actionID   =  action.getId()
        dPrnt("onAction(): actionID=%i buttonCode=%i" % (actionID,buttonCode))
        if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC or buttonCode == 61467):
            self.close()

    def onClick(self, controlID):
        """
            onClick(self, controlID) is the replacement for onControl. It gives an interger.
            This function has been implemented and works
        """
        dPrnt("onclick(): control %i" % controlID)
        if (50 <= controlID <= 52):
            if (self.getCurrentListPosition() == 3):
                self.close()
                return
            elif (self.getCurrentListPosition() == 1):
                dPrnt("onClick(): Loading Settings Window")
                winSettings = ircXBMC_Settings("Script_ircXSettings.xml",scriptPath,"DefaultSkin",0,scriptSettings=setts,language=lang, title=__title__)
                winSettings.doModal()
                del winSettings

            elif (self.getCurrentListPosition() == 2):
                xbmcgui.Dialog().ok(__title__ + ": About","Version: " + __version__, __credits__,)


    def onFocus(self, controlID):
        """"
            onFocus(self, int controlID)
            This function has been implemented and works
        """
        dPrnt("onFocus(): control %i" % controlID)
        if (controlID == 5):
            print 'The control with id="5" just got focus'

def dPrnt(text,minlvl=1):
    if DEBUG: print "DEBUG: " + text

def main():
    print "Starting " + __title__
    lang.load(os.path.join(scriptPath,"Languages"))
    t = Splash()
    t.doModal()
    del t
    win = IRCSetup("Script_ircXMainMenu.xml",scriptPath,"DefaultSkin",0)

    win.doModal()
    del win
    print __title__ + " has been exited"

if __name__ == "__main__":
    main()



