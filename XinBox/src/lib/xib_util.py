      ##########################
      #                        #                      
      #   XinBox (V.0.9)       #         
      #     By Stanley87       #         
      #                        #
#######                        #######             
#                                    #
#                                    #
#   A pop3 email client for XBMC     #
#                                    #
######################################

import xbmcgui, xbmc
import os, sys, default

COMPATIBLE_VERSIONS = [ '1.0', ]
SETTINGDIR = default.__scriptsettings__
SCRIPTSETDIR = SETTINGDIR + default.__scriptname__ + "\\"
SETTINGSFILE = SCRIPTSETDIR + "settings.xib"
MMSETTINGSFILE = SCRIPTSETDIR + "mmsettings.xib"
ROOTDIR = default.__scriptpath__
SRCDIR = ROOTDIR + "src\\"
DATADIR = SCRIPTSETDIR + "data\\"
TEMPDIR = SCRIPTSETDIR + "temp\\"

def setControllerAction(): #Thanks to AMT Team for this :-D
    return {
                61478 : 'Keyboard Up Arrow',
                61480 : 'Keyboard Down Arrow',
                61448 : 'Keyboard Backspace Button',
                61533 : 'Keyboard Menu Button',
                61467 : 'Keyboard ESC Button',
                    216 : 'Remote Back Button',
                    247 : 'Remote Menu Button',
                    229 : 'Remote Title',
                    207 : 'Remote 0',
                    166 : 'Remote Up',
                    167 : 'Remote Down',
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
class createdirs:
    def __init__( self, *args, **kwargs ):
        self.makedirs()

    def makedirs ( self ):
        if not os.path.exists(SETTINGDIR):
            os.mkdir(SETTINGDIR)
        if not os.path.exists(SCRIPTSETDIR):
            os.mkdir(SCRIPTSETDIR)           
        if not os.path.exists(DATADIR):
            os.mkdir(DATADIR)
        if not os.path.exists(TEMPDIR):
            os.mkdir(TEMPDIR)
        print "dirs created OK"
        return



class mmSettings:
    def __init__( self, *args, **kwargs ):
        self.readSettings()
    
    def readSettings( self ):
        try:
            self.usedDefaults = False
            f = open( MMSETTINGSFILE, 'r' )
            s = f.read().split('|')
            f.close()
            self.xib1 = s[0]
            self.xib2 = s[1]
            self.mmen = s[2]
            print 'read mini mode settings OK'
            self.checkmm()
        except:
            print 'ERROR: reading mini mode settings'
            self.setDefaults()

    def checkmm ( self ):
        if self.xib1 == "-" and self.xib2 == "-":
            self.disablemmb = True
            print "Disable mini mode button flag set OK"
        else:
            self.disablemmb = False
        
        
    def setDefaults( self, show_dialog = False ):
        self.xib1 = "-"
        self.xib2 = "-"
        self.mmen = "-"
        print 'used mini mode default settings OK'
        success = self.writeSettings()
        self.usedDefaults = True
        self.checkmm()
        
    def writeSettings( self ):
        try:
            strSettings = '%s|%s|%s' % ( 
                self.xib1,
                self.xib2,
                self.mmen, )
            f = open( MMSETTINGSFILE, 'w' )
            f.write(strSettings)
            f.close()
            print 'mini mode settings write OK'
            return True
        except:
            print 'ERROR: writing mini mode settings'
            return False
        
        
class Settings:#Based on code by TEAM AMT - THANKS TEAM! :-D
    def __init__( self, *args, **kwargs ):
        self.readSettings()

        
    def readSettings( self ):
        try:
            self.usedDefaults = False
            f = open( SETTINGSFILE, 'r' )
            s = f.read().split('|')
            f.close()
            self.mpenable = s[0]
            self.mp = s[1]
            self.server1 = s[2]
            self.user1 = s[3]
            self.pass1 = s[4]
            self.ssl1 = s[5]
            self.server2 = s[6]
            self.user2 = s[7]
            self.pass2 = s[8]
            self.ssl2 = s[9]
            print 'read settings OK'
        except:
            print 'ERROR: reading settings'
            self.setDefaults()
        self.checksf()
        return

    def checksf ( self ):
        if self.user1 == "-" or self.server1 == "-":
            self.disablexb1 = True
            print "Disable XIB 1 flag set OK"
        else:
            self.disablexb1 = False
        if self.user2 == "-" or self.server2 == "-":
            self.disablexb2 = True
            print "Disable XIB 2 flag set OK"
        else:
            self.disablexb2 = False
        return

    def setDefaults( self, show_dialog = False ):
        self.mpenable = "-"
        self.mp = "-"
        self.server1 = "-"
        self.user1 = "-"
        self.pass1 = "-"
        self.ssl1 = "-"
        self.server2 = "-"
        self.user2 = "-"
        self.pass2 = "-"
        self.ssl2 = "-"
        print 'used default settings OK'
        success = self.writeSettings()
        self.usedDefaults = True
        return
        
    def writeSettings( self ):
        try:
            strSettings = '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( 
                self.mpenable,
                self.mp, 
                self.server1,
                self.user1,
                self.pass1,
                self.ssl1,
                self.server2,
                self.user2,
                self.pass2,
                self.ssl2, )
            f = open( SETTINGSFILE, 'w' )
            f.write(strSettings)
            f.close()
            print 'settings write OK'
            return True
        except:
            print 'ERROR: writing settings'
            return False
