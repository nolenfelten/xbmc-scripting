
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
__version__ = '0.99.7'
__BaseURL__ = "http://xbmc-scripting.googlecode.com/svn"

IMAGETYPES = ["jpg","jpeg","gif","png","bmp","tbn"]
AUDI0TYPES = ["wav","mp3","mpa","mp2","ac3","dts"]
VIDEOTYPES = ["avi","wmv","mpg"]
TEXTTYPES = ["txt", "rtf", "xml", "bat", "log"]
ARCHIVETYPES = ["zip"]
       
def setControllerAction():
    return {
                61478 : 'Keyboard Up Arrow',
                61480 : 'Keyboard Down Arrow',
                61479 : 'Keyboard Right Arrow',
                61448 : 'Keyboard Backspace Button',
                61533 : 'Keyboard Menu Button',
                61467 : 'Keyboard ESC Button',
                61601 : 'Keyboard Shift Button',
                61603 : 'Keyboard Right Ctrl Button',
                61602 : 'Keyboard Left Ctrl Button',
                61449 : 'Keyboard TAB Button',
                    213 : 'Remote Display',
                    216 : 'Remote Back', 
                    247 : 'Remote Menu',
                    229 : 'Remote Title',
                    195 : 'Remote Info',
                    207 : 'Remote 0',
                    166 : 'Remote Up',
                    167 : 'Remote Down',
                    168 : 'Remote Right',
                    256 : 'A Button',
                    257 : 'B Button',
                    258 : 'X Button',
                    259 : 'Y Button',
                    260 : 'Black Button',
                    261 : 'White Button',
                    274 : 'Start Button',
                    275 : 'Back Button',
                    270 : 'DPad Up',
                    271 : 'DPad Down',
                    272 : 'DPad Left',
                    273 : 'DPad Right'
                }

def getpresetservers():
    return {
            #after @,   pop addy,    smtp addy,  pop ssl,  smtp ssl, server inbox size, Username - none for default, Smtp auth
            "gmail.com" : ["pop.gmail.com","smtp.gmail.com","995","587","0","",True],
            "ihug.co.nz" : ["pop.ihug.co.nz","smtp.ihug.co.nz","0","0","5","",True],
            "xtra.co.nz" : ["pop3.xtra.co.nz","smtp.xtra.co.nz","0","0","100","",True],
            "sky.com" : ["pop.sky.com","smtp.sky.com","0","0","200","",True],
            "aol.com" : ["pop.aol.com","smtp.aol.com","0","587","5000","",True],
            "aim.com" : ["pop.aim.com","smtp.aim.com","0","587","5000","",True],
            "earthlink.net" : ["pop.earthlink.net","smtpauth.earthlink.net","0","587","100","",True],
            "googlemail.com" : ["pop.gmail.com","smtp.gmail.com","995","587","0","",True],
            "yahoo.de" : ["pop.mail.yahoo.de","smtp.mail.yahoo.de","0","0","0","",True],
            "yahoo.com" : ["pop.mail.yahoo.com","smtp.mail.yahoo.com","995","465","0","",True],
            "gmx.net" : ["pop.gmx.net","mail.gmx.net","0","0","1000","Kundennummer",True],
            "gmx.de" : ["pop.gmx.net","mail.gmx.net","0","0","1000","Kundennummer",True],
            "web.de" : ["pop3.web.de","smtp.web.de","0","0","0","",True],
            "freenet.de" : ["pop3.freenet.de","mx.freenet.de","0","0","0","",True]}

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
                f = open(autoexecfile, "w")
                if not "import xbmc\n" in lines:
                    f.write("import xbmc\n")
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
    
    
