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

def createProgressDialog( __line3__ ):
    global dialog, pct
    pct = 0
    dialog = xbmcgui.DialogProgress()
    dialog.create( _( 0 ) )
    updateProgressDialog( __line3__ )

def updateProgressDialog( __line3__ ):
    global dialog, pct
    pct += 5
    dialog.update( pct, __line1__, __line2__, __line3__ )

def closeProgessDialog():
    global dialog
    dialog.close()
    
import xbmcgui, language, time
_ = language.Language().string

__line1__ = _(60)
__line2__ = _(61)

createProgressDialog( '%s xbmc' % ( _( 62 ), ))
import xbmc
updateProgressDialog( '%s sys' % ( _( 62 ), ))
import sys
updateProgressDialog( '%s os' % ( _( 62 ), ))
import os
updateProgressDialog( '%s threading' % ( _( 62 ), ))
import threading
updateProgressDialog( '%s guibuilder' % ( _( 62 ), ))
import guibuilder
updateProgressDialog( '%s xib_util' % ( _( 62 ), ))
import xib_util
updateProgressDialog( '%s shutil' % ( _( 62 ), ))
import shutil
updateProgressDialog( '%s default' % ( _( 62 ), ))
import default
updateProgressDialog( '%s traceback' % ( _( 62 ), ))
import traceback
updateProgressDialog( '%s mailchecker' % ( _( 62 ), ))
import mailchecker
updateProgressDialog( '%s email' % ( _( 62 ), ))
import email
updateProgressDialog( '%s poplib' % ( _( 62 ), ))
import poplib, mimetypes
closeProgessDialog()

SETTINGDIR = default.__scriptsettings__
SCRIPTSETDIR = SETTINGDIR + default.__scriptname__ + "\\"
DATADIR = SCRIPTSETDIR + "data\\"
DELETEFOLDER = "deleted\\"
IDFOLDER = "ids\\"
NEWFOLDER = "new\\"
CORFOLDER = "cor\\"
MAILFOLDER = "mail\\" 
class GUI( xbmcgui.Window ):
    def __init__( self ):
        xbmc.log("Xinbox GUI Start")
        self.box1 = 0
        self.box2 = 0
        self.cwd = default.__scriptpath__
        self.createdirs()
        self.getSettings()
        self.getmmSettings()
        self.gui_loaded = self.setupGUI()
        if ( not self.gui_loaded ):
            xbmc.log("ERROR: setup gui failed")
            self.close()
        else:
            xbmc.log("setup GUI OK")
            self.adjustcontrols()
            self.setupvars()
    
    def getSettings( self ):
        self.settings = xib_util.Settings()
        
    def setupvars( self ):
        self.Fullscreen = False
        self.notread = self.image_path + "\\" + "emailnotread.png"
        self.read = self.image_path + "\\" + "emailread.png"
        if xbmc.Player().isPlayingAudio():
            self.enablemusicinfo()
            image = xbmc.getInfoImage("MusicPlayer.Cover")
            self.controls['music logo']['control'].setImage(image)
        self.skin = self.settings.skin
        self.dummy()
        self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_AUTO, function = self.myPlayerChanged )
        self.control_action = xib_util.setControllerAction()
        
    def dummy( self ):
        self.Timer = threading.Timer( 60*60*60, self.dummy,() )
        self.Timer.start()
    
    def myPlayerChanged( self, event ):
        time.sleep(0.1)
        if event == 2:
            self.enablemusicinfo()
            image = xbmc.getInfoImage("MusicPlayer.Cover")
            self.controls['music logo']['control'].setImage(image)
        else:
            self.disablemusicinfo()
    
    def disablemusicinfo ( self ):
        try:
            self.removeControl(self.controls['music logo']['control'])
            self.removeControl(self.controls['music rectangle']['control'])
            self.removeControl(self.controls['play time label']['control'])
            self.removeControl(self.controls['album/artist/genre etc info label']['control'])
        except:pass
    
    def checkemail ( self, inbox, minimode):
        w = mailchecker.Checkemail(inbox, minimode)
        w.setupemail()
        self.newmails = w.returnvar
        del w
        return
        
    def enablemusicinfo ( self ):
        try:
            self.addControl(self.controls['music logo']['control'])
            self.addControl(self.controls['music rectangle']['control'])
            self.addControl(self.controls['play time label']['control'])
            self.addControl(self.controls['album/artist/genre etc info label']['control'])
        except:pass
            
    def adjustcontrols ( self ):
        self.controls['listControl']['control'].setEnabled( False )
        self.controls['cmButton']['control'].setLabel("XinBox 1", "font14")
        self.controls['csButton']['control'].setLabel("XinBox 2", "font14")
        if self.mmsettings.disablemmb:
            self.controls['mmButton']['control'].setEnabled( False )
        if self.settings.disablexb1:
            self.controls['cmButton']['control'].setEnabled( False )
        if self.settings.disablexb2:
            self.controls['csButton']['control'].setEnabled( False )
        self.controls['fsButton']['control'].setEnabled( False )
        self.controls['vaButton']['control'].setEnabled( False )
        xbmc.log ("adjusted controls OK")
    

    def setupGUI( self ):
        skin_path = os.path.join( self.cwd, 'src', 'skins')
        if ( self.settings.skin == 'Default' ): current_skin = xbmc.getSkinDir()
        else: current_skin = self.settings.skin
        if ( not os.path.exists( os.path.join( skin_path, current_skin ))): current_skin = 'default'
        self.image_path = os.path.join( skin_path, current_skin, "gfx" )
        gb = guibuilder.GUIBuilder()
        ok =  gb.create_gui( self, skin=current_skin, skinXML="skin", skinPath = skin_path, imageFolder = "gfx", useDescAsKey = True, 
            title = sys.modules[ "__main__" ].__scriptname__, line1 = __line1__, dlg = dialog, pct = pct, fastMethod = False, language = _, debug = True )
        return ok    

    def openinbox( self , inbox):
        self.controls['listControl']['control'].reset()
        self.controls['msgbody']['control'].reset()
        self.controls['fsButton']['control'].setEnabled( False )
        if inbox == 1:
    	    self.box1 = 1
    	    self.box2 = 0
    	    self.controls['title']['control'].setLabel("XinBox - " + self.settings.user1)
    	    self.controls['cmButton']['control'].setLabel("Check For New", "font14")
    	    self.controls['csButton']['control'].setLabel("XinBox 2", "font14")
    	    self.emfolder = DATADIR + self.settings.user1 + "@" + self.settings.server1 + "\\"
        else:
    	    self.box2 = 1
    	    self.box1 = 0
    	    self.controls['title']['control'].setLabel("XinBox - " + self.settings.user2)
    	    self.controls['csButton']['control'].setLabel("Check For New", "font14")
    	    self.controls['cmButton']['control'].setLabel("XinBox 1", "font14")
    	    self.emfolder = DATADIR + self.settings.user2 + "@" + self.settings.server2 + "\\"
        if not os.path.exists(self.emfolder):
            self.controls['listControl']['control'].addItem( _(0) + " "+ _(58))
            self.controls['listControl']['control'].setEnabled( False )
        else:
            self.addme()

    def clearfolder(self, folder):
        for root, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))        

    def addme( self ):
        self.clearfolder(self.emfolder + CORFOLDER)
        self.controls['listControl']['control'].setEnabled( True )
        self.controls['listControl']['control'].reset()
        self.gettally()
        self.myemails = []
        self.count = 0
        self.count2 = 0
        self.count3 = self.tally
        self.count4 = 0
        self.emails = []
        for self.count in range(self.tally):
                self.temp2 = self.emfolder + MAILFOLDER + str(self.count3) +".sss"
                if os.path.exists(self.temp2):
                    fh = open(self.temp2)
                    self.tempStr = fh.read()
                    fh.close()
                    self.getstatus()
                    self.emails.append(email.message_from_string(self.emailbody))
                    try:
                        temp = self.emails[self.count2].get('subject')
                        if temp == "":
                            self.myemails.append(xbmcgui.ListItem(_(22) +" "+ _(23) + " "+ self.emails[self.count2].get('from')))
                        else:
                            self.myemails.append(xbmcgui.ListItem(self.emails[self.count2].get('subject') +" "+ _(23) + " "+ self.emails[self.count2].get('from')))
                    except:
                        self.myemails.append(xbmcgui.ListItem(_(22) +" "+ _(23) + " "+ self.emails[self.count2].get('from')))
                    if self.readstatus == "UNREAD":
                        self.myemails[self.count4].setThumbnailImage(self.notread)
                    else:
                        self.myemails[self.count4].setThumbnailImage(self.read)
                    self.controls['listControl']['control'].addItem(self.myemails[self.count4])
                    f = open(self.emfolder + CORFOLDER + str(self.controls['listControl']['control'].size()-1) +".cor", "w")
                    f.write(str(self.count3))
                    f.close()
                    self.count = self.count+1 
                    self.count2 = self.count2+1
                    self.count3 = self.count3-1
                    self.count4 = self.count4+1
                else:
                    self.count = self.count+1
                    self.count3 = self.count3-1
        if self.controls['listControl']['control'].size() == 0:
            self.controls['listControl']['control'].addItem( _(0) + " "+ _(58))
            self.controls['listControl']['control'].setEnabled( False )
        return

      

    def getstatus( self ):
        s = self.tempStr.split('|')
        self.readstatus = s[0]
        self.emailbody = s[1]
        return
        
    
    def processEmail(self, selected):
        self.controls['msgbody']['control'].setVisible(True)
        self.attachments = []
        if self.emails[selected].is_multipart():
            for part in self.emails[selected].walk():
                if part.get_content_type() != "text/plain" and part.get_content_type() != "text/html" and part.get_content_type() != "multipart/mixed" and part.get_content_type() != "multipart/alternative":
                    filename = part.get_filename()
                    if not filename:
                        ext = mimetypes.guess_extension(part.get_type())
                        if not ext:
                            # Use a generic extension
                            ext = '.bin'
                        filename = 'temp' + ext
                    try:
                        f=open(TEMPFOLDER + filename, "wb")
                        f.write(part.get_payload(decode=1))
                        f.close()
                    except:
                        print "problem saving attachment " + filename
                    self.attachments.append(filename)       
        if len(self.attachments)==0:
            # disable the attachments button
            self.controls['vaButton']['control'].setEnabled( False )
        else:
            # enable the attachments button
            self.controls['vaButton']['control'].setEnabled( True ) 
        self.printEmail(selected)        

    def parse_email(self, email):
        self.parsemail = email
        return str(self.parsemail)


    def printEmail(self, selected):
        self.msgText = ""
        if self.emails[selected].is_multipart():
            for part in self.emails[selected].walk():
                if part.get_content_type() == "text/plain":
                    print part.get_payload()
                    email = self.parse_email(part.get_payload())
                    self.msgText = email
                    break
        else:
            if self.emails[selected].get_content_type() == "text/html":
                # email in html only, so strip html tags
                email2 = self.parse_email(self.emails[selected].get_payload())
                self.msgText = email2
            else:
                email3 = self.parse_email(self.emails[selected].get_payload())
                self.msgText = email3
                print self.msgText
        self.controls['msgbody']['control'].setText(self.msgText)
        self.setFocus(self.controls['msgbody']['control'])

    def goFullscreen(self):
        self.controls['msgbody']['control'].setVisible( False )
        self.controls['attachlist']['control'].setVisible( False )
        self.controls['fsoverlay']['control'].setVisible(True)
        self.controls['fsmsgbody']['control'].setVisible(True)
        self.controls['fsmsgbody']['control'].setText(self.msgText)
        self.setFocus(self.controls['fsmsgbody']['control'])
        self.Fullscreen = True

    def undoFullscreen(self):
        self.controls['msgbody']['control'].setVisible( True )
        self.controls['fsoverlay']['control'].setVisible(False)
        self.controls['fsmsgbody']['control'].setVisible(False)
        self.setFocus(self.controls['msgbody']['control'])
        self.Fullscreen = False
        return

    def createdirs( self ):
        self.dirs = xib_util.createdirs()
    
    def getmmSettings( self ):
        self.mmsettings = xib_util.mmSettings()
    
    def exitscript( self ):
        if ( self.Timer ): self.Timer.cancel()
        self.close()

    def updateicon(self):
        temp = self.controls['listControl']['control'].getSelectedItem()
        temp.setThumbnailImage(self.read)
        temp = self.controls['listControl']['control'].getSelectedPosition()
        fh = open(self.emfolder + CORFOLDER + str(temp)+ ".cor")
        updateme = fh.read()
        fh.close()
        fh = open(self.emfolder + MAILFOLDER + str(updateme) +".sss")
        self.tempStr = fh.read()
        fh.close()
        self.getstatus()
        self.readstatus = "READ"
        f = open(self.emfolder + MAILFOLDER + str(updateme) +".sss", "w")
        f.write(self.readstatus + "|" + self.emailbody)
        f.close()
        return
        

    def onControl( self, control ):
        try:
            if ( control is self.controls['cmButton']['control'] ):
                if self.box1 == 1:
                    self.checkemail(1,0)
                    if self.newmails != 0:
                        self.addme()
                else:
                    self.openinbox(1)
            elif ( control is self.controls['csButton']['control'] ):
                if self.box2 == 1:
                    self.checkemail(2,0)
                    if self.newmails != 0:
                        self.addme()
                else:
                    self.openinbox(2)
            elif ( control == self.controls['fsButton']['control'] ):
                    self.goFullscreen()                   
            elif ( control == self.controls['listControl']['control'] ):
                self.controls['fsButton']['control'].setEnabled( True )
                self.processEmail(self.controls['listControl']['control'].getSelectedPosition())
                self.updateicon()
            else:pass
        except: traceback.print_exc()
        
    def onAction( self, action ):
        try:
            button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
            control = self.getFocus()
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                if self.Fullscreen == True:
                    self.undoFullscreen()
                else:
                    self.exitscript()
            elif ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
                self.exitscript()
            else:pass
        except: traceback.print_exc()

    
    def gettally(self):
        self.readtally()
        if self.tally == "-":
            self.tally = 1
        self.tally = int(self.tally)
        self.writetally()
        return
    
    def readtally(self):
        try:
            fh = open(self.emfolder + "tally.sss")
            for line in fh.readlines():
                theLine = line.strip()
                if theLine.count("<tally>") > 0:
                    self.tally = theLine[7:-8]    
                    fh.close()
            return
        except IOError:
            self.createtally()
            self.readtally()
            return
    
    def writetally(self):
            f = open(self.emfolder + "tally.sss", "wb")
            f.write("\t<tally>"+ str(self.tally) +"</tally>\n")
            f.close()
            return
    
    def createtally(self):
            f = open(self.emfolder + "tally.sss", "wb")
            f.write("\t<tally>-</tally>\n")
            f.close()
            return


## Thanks Thor918 for this class ##
class MyPlayer( xbmc.Player ):
    def  __init__( self, *args, **kwargs ):
        if ( kwargs.has_key( 'function' )): 
            self.function = kwargs['function']
            xbmc.Player.__init__( self )
    
    def onPlayBackStopped( self ):
        self.function( 0 )
    
    def onPlayBackEnded( self ):
        self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )



