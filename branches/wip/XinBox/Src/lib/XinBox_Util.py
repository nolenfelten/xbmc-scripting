
import os, sys
from os.path import join, exists

__datadir__ = "P:\\script_data\\"
__settingdir__ = "P:\\script_data\\XinBox\\"
__accountsdir__ = "P:\\script_data\\XinBox\\Accounts\\"
__tempdir__ = "P:\\script_data\\XinBox\\Temp\\"
__autoexecdir__ = "Q:\\scripts\\"


__scriptname__ = 'XinBox'
__author__ = 'Stanley87'
__url__ = 'http://xbmc-scripting.googlecode.com/svn/tags/XinBox/'
__version__ = 'V.1.1'



IMAGETYPES = ["jpg","jpeg","gif","png","bmp","tbn"]
AUDI0TYPES = ["wav","mp3","mpa","mp2","ac3","dts"]
VIDEOTYPES = ["avi","wmv","mpg"]
TEXTTYPES = ["txt", "doc", "rtf", "xml", "bat", "log"]
ARCHIVETYPES = ["zip"]

def setControllerAction():
    return {
                61478 : 'Keyboard Up Arrow',
                61480 : 'Keyboard Down Arrow',
                61479 : 'Keyboard Right Arrow',
                61448 : 'Keyboard Backspace Button', #B button
                61533 : 'Keyboard Menu Button', #Y button
                61467 : 'Keyboard ESC Button', #back button
                61601 : 'Keyboard Shift Button',
                61603 : 'Keyboard Right Ctrl Button',
                61602 : 'Keyboard Left Ctrl Button',
                61449 : 'Keyboard TAB Button', #White button
                    213 : 'Remote Display' #white button
                    216 : 'Remote Back', #back button
                    247 : 'Remote Menu', 
                    229 : 'Remote Title',#B button
                    195 : 'Remote Info'#Y button
                    207 : 'Remote 0',
                    166 : 'Remote Up',
                    167 : 'Remote Down',
                    168 : 'Remote Right',
                    256 : 'A Button',
                    257 : 'B Button',#used for quick delete emails,remove compose line and delete contact
                    258 : 'X Button',
                    259 : 'Y Button',#used for help
                    260 : 'Black Button',
                    261 : 'White Button',#used for Extra Features (add contact, launch compose from contacts, launch contact list from compos)
                    274 : 'Start Button',
                    275 : 'Back Button', #back
                    270 : 'DPad Up',
                    271 : 'DPad Down',
                    272 : 'DPad Left',
                    273 : 'DPad Right'
                }

def getpresetservers():
    return {
            "gmail.com" : ["pop.gmail.com","smtp.gmail.com","995","587","0",""],
            "ihug.co.nz" : ["pop.ihug.co.nz","smtp.ihug.co.nz","0","0","5",""],
            "xtra.co.nz" : ["pop3.xtra.co.nz","smtp.xtra.co.nz","0","0","100",""],
            "sky.com" : ["pop.sky.com","smtp.sky.com","0","0","200",""],
            "aol.com" : ["pop.aol.com","smtp.aol.com","0","587","5000",""],
            "aim.com" : ["pop.aim.com","smtp.aim.com","0","587","5000",""],
            "earthlink.net" : ["pop.earthlink.net","smtpauth.earthlink.net","0","587","100",""],
            "googlemail.com" : ["pop.gmail.com","smtp.gmail.com","995","587","0",""],
            "yahoo.de" : ["pop.mail.yahoo.de","smtp.mail.yahoo.de","995","465","0",""],
            "yahoo.com" : ["pop.mail.yahoo.com","smtp.mail.yahoo.com","995","465","0",""],
            "gmx.net" : ["pop.gmx.net","mail.gmx.net","0","0","1000","Kundennummer"],
            "web.de" : ["pop3.web.de","smtp.web.de","0","0","0",""],
            "freenet.de" : ["pop3.freenet.de","mx.freenet.de","0","0","0",""]}

def getfiletypes(filetype):
    if filetype in IMAGETYPES: return "Image"
    elif filetype in AUDI0TYPES: return "Audio"
    elif filetype in VIDEOTYPES: return "Video"
    elif filetype in TEXTTYPES: return "Text"
    elif filetype in ARCHIVETYPES: return "Archive"
    else: return "Unknown"
    

def addauto(scriptpath, accountname, srcpath):
        changing = False
        Script = 'xbmc.executebuiltin("XBMC.RunScript(' + scriptpath.replace("\\","\\\\") + "\\\\lib\\\\XinBox_MiniMode.py" + "," + accountname + "," + srcpath.replace("\\","\\\\") + ')")'
        script2 = 'xbmc.executebuiltin("XBMC.RunScript(' + scriptpath.replace("\\","\\\\") + "\\\\lib\\\\XinBox_MiniMode.py"
        autoexecfile = __autoexecdir__ + "autoexec.py"                      
        if os.path.exists(autoexecfile):
                fh = open(autoexecfile)
                lines = []
                for line in fh.readlines():
                     theLine = line.strip()
                     if script2 in theLine:
                         changing = True
                         lines.append(Script+"\n")
                     else:lines.append(line)
                if not changing:lines.append(Script+"\n")
                fh.close()
                if not "import xbmc\n" in lines:lines.append("import xbmc\n")
                f = open(autoexecfile, "w")
                f.writelines(lines)
                f.close()
                return
        else:
                f = open(autoexecfile, "w")
                f.write("import xbmc\n")
                f.write(Script)
                f.close()
                return


def removeauto(scriptpath, accountname, srcpath):
        Script = 'xbmc.executebuiltin("XBMC.RunScript(' + scriptpath.replace("\\","\\\\") + "\\\\lib\\\\XinBox_MiniMode.py" + "," + accountname + "," + srcpath.replace("\\","\\\\") + ')")'
        autoexecfile = __autoexecdir__ + "autoexec.py"    
        if os.path.exists(autoexecfile):
                fh = open(autoexecfile)
                lines = [ line for line in fh if not line.strip().startswith(Script) ]
                fh.close()
                f = open(autoexecfile, "w")
                f.writelines(lines)
                f.close()
                return
        return
