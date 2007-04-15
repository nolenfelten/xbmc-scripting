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
import xbmc, sys, os, default, xib_util, gui
import xbmcgui, language, time

_ = language.Language().string


class main:
    def __init__( self ):
        xbmc.log("startup .py running")
        self.cwd = default.__scriptpath__
        self.createdirs()
        self.getSettings()
        self.password()

    def password ( self ):
        xbmc.log("password menu started")
        if self.settings.mpenable == "yes":
            xbmc.log ("Master password is enabled")
            if self.settings.mp != "-":
                xbmc.log ("Master password is legit")
                self.mpcheck()
            else:
                xbmc.log ("Master password is not legit, starting UI")
                self.launchgui()
        elif self.settings.mpenable == "no":
            xbmc.log ("Master password is disabled, starting UI")
            self.launchgui()
        else:
            xbmc.log ("Master password has not been setup")
            self.mpsetup()

    def mpcheck( self ):
        xbmc.log ("Getting user input password")
        dialog = xbmcgui.Dialog()
        passw = ""
        keyboard = xbmc.Keyboard(passw, _( 40 ))
        keyboard.setHiddenInput(True)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            if (keyboard.isConfirmed()):
                passw = keyboard.getText()
            else:
                keyboard.setHiddenInput(False)
                return
            if passw != self.settings.mp:
                dialog.ok( _( 41 ), _( 42 ))
                xbmc.log ("Wrong password entered")
                self.mpcheck()
            else:
                xbmc.log ("Password OK")
                keyboard.setHiddenInput(False)
                self.launchgui()            
                
    def mpsetup( self ):
        dialog = xbmcgui.Dialog()
        if dialog.yesno( _( 43 ), _( 44 )):
            xbmc.log ("Master Password Enabled by user")
            self.settings.mpenable = "yes"
            self.writeSettings()
            self.getmp()
        else:
            xbmc.log ("Master Password Disabled by user")
            self.settings.mpenable = "no"
            self.writeSettings()
            self.launchgui()          
    
    def getmp( self ):
        dialog = xbmcgui.Dialog()
        mastpassw = ""
        keyboard = xbmc.Keyboard(mastpassw, _( 40 )) 
        keyboard.setHiddenInput(True)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            mastpassw = keyboard.getText()
        else:
            keyboard.setHiddenInput(False)
            return
        if mastpassw == "":
            xbmc.log ("No password entered")
            dialog.ok( _( 41 ), _( 45 ))
            self.getmp()
        else:
            self.mp = mastpassw
            xbmc.log ("1st Password entered")
            keyboard.setHiddenInput(False)
            self.confmp()

    def confmp( self ):
        dialog = xbmcgui.Dialog()
        mastpassw2 = ""
        keyboard = xbmc.Keyboard(mastpassw2, _( 46 ))
        keyboard.setHiddenInput(True)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            mastpassw2 = keyboard.getText()
        else:
            keyboard.setHiddenInput(False)
            return
        if self.mp == mastpassw2:
            self.settings.mp = mastpassw2
            self.writeSettings()
            xbmc.log ("Password confirmeds and saved")
            keyboard.setHiddenInput(False)
            dialog.ok( _( 49 ), _( 47 ))
            self.launchgui()
        else:
            xbmc.log ("Password didn't match, return to getmp")
            keyboard.setHiddenInput(False)
            dialog.ok( _( 41 ), _( 48 ))
            self.getmp()  
            
    def createdirs( self ):
        self.dirs = xib_util.createdirs()

    def getSettings( self ):
        self.settings = xib_util.Settings()        

    def writeSettings( self ):
        test = self.settings.writeSettings()
        if test:
           xbmc.log ("Settings write OK")
        else:
            xbmc.log ("ERROR: writing settings")

    def launchgui( self ):
        xbmcgui.lock()
        w = gui.GUI("XinBox_Main.xml",self.cwd + "src","DefaultSkin")
        w.doModal()
        del w
