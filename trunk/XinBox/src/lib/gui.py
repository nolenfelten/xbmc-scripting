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

    
import xbmcgui, language, time, settings
lang = language.Language().string

import xbmc
import sys
import os
import threading
import xib_util
import shutil
import default
import traceback
import mailchecker
import email
import poplib, mimetypes
import emaildialog

SETTINGDIR = default.__scriptsettings__
SCRIPTSETDIR = SETTINGDIR + default.__scriptname__ + "\\"
DATADIR = SCRIPTSETDIR + "data\\"
DELETEFOLDER = "deleted\\"
IDFOLDER = "ids\\"
NEWFOLDER = "new\\"
CORFOLDER = "cor\\"
MAILFOLDER = "mail\\"
SCRIPTFOLDER = default.__scriptpath__
MEDIAFOLDER = SCRIPTFOLDER + "src//skins//media//"

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        xbmcgui.lock()
        xbmc.executebuiltin("Skin.SetBool(xblistnotempty)")
        xbmc.executebuiltin("Skin.ToggleSetting(xblistnotempty)")
        self.createdirs()
        self.getSettings()
        self.getmmSettings()
        self.setupvars()      

    def onInit(self):
        self.setupcontrols()
        self.adjustcontrols()
        xbmcgui.unlock()

    def setupcontrols ( self ):
        self.txtbox = self.getControl(67)
        self.xb1butn = self.getControl(61)
        self.xb2butn = self.getControl(62)
        self.sebutn = self.getControl(63)
        self.mmbutn = self.getControl(64)
        self.title = self.getControl(66)
        self.bkimage = self.getControl(65)
        self.xbempty = self.getControl(70)
        return
        
    def setupvars( self ):
        self.listsize = 0
        self.box1 = 0
        self.box2 = 0
        self.Fullscreen = False
        self.notread = MEDIAFOLDER + "emailnotread.png"
        self.read = MEDIAFOLDER + "emailread.png"
        self.control_action = xib_util.setControllerAction()
        xbmc.log ("setup variables OK")
        return
        
    def adjustcontrols ( self ):
        self.xbempty.setVisible( False )
        self.mmbutn.setLabel( lang(200) )
        self.sebutn.setLabel( lang(201) )
        if self.mmsettings.disablemmb:
            self.mmbutn.setEnabled( False )
        if self.settings.disablexb1:
            self.xb1butn.setEnabled( False )
        if self.settings.disablexb2:
            self.xb2butn.setEnabled( False )
        xbmc.log ("adjusted controls OK")
        return

    def createdirs( self ):
        self.dirs = xib_util.createdirs()
    
    def getmmSettings( self ):
        self.mmsettings = xib_util.mmSettings()
        
    def getSettings( self ):
        self.settings = xib_util.Settings()

    def gettally(self):
        self.readtally()
        if self.tally == "-":
            self.tally = 2
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

    def disablexinbox (self):
        xbmc.executebuiltin("Skin.SetBool(xblistnotempty)")
        xbmc.executebuiltin("Skin.ToggleSetting(xblistnotempty)")
        self.txtbox.reset()
        self.txtbox.setVisible( False )
        self.xbempty.setVisible( True )
        self.xbempty.setLabel( lang(58) )
        if self.box2 ==1:
            self.setFocus(self.xb2butn)
        else:
            self.setFocus(self.xb1butn)
        return
    
    def openinbox( self , inboxy):
        self.inbox = inboxy
        if self.inbox == 1:
    	    self.box1 = 1
    	    self.box2 = 0
    	    self.title.setLabel( lang(0) + " - " + self.settings.user1)
    	    self.xb1butn.setLabel( lang(65))
    	    self.xb2butn.setLabel("XinBox 2")
    	    self.emfolder = DATADIR + self.settings.user1 + "@" + self.settings.server1 + "\\"
        else:
    	    self.box2 = 1
    	    self.box1 = 0
    	    self.title.setLabel( lang(0) + " - " + self.settings.user2)
    	    self.xb2butn.setLabel( lang(65))
    	    self.xb1butn.setLabel("XinBox 1")
    	    self.emfolder = DATADIR + self.settings.user2 + "@" + self.settings.server2 + "\\"
        if not os.path.exists(self.emfolder):
            self.disablexinbox()
        else:
            self.addme()
            if self.listsize == 0:
                self.disablexinbox()
            

    def clearfolder(self, folder):
        for root, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
                   
    def addme( self ):
        xbmcgui.lock()
        xbmc.executebuiltin("Skin.SetBool(xblistnotempty)")
        self.listsize = 0
        self.xbempty.setVisible( False )
        self.txtbox.reset()
        self.txtbox.setVisible( True )
        self.clearfolder(self.emfolder + CORFOLDER)
        self.clearList()
        self.gettally()
        self.count = 0
        self.count2 = 0
        self.count3 = self.tally
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
                            self.myemail = xbmcgui.ListItem(lang(22) +" "+ lang(23) + " "+ self.emails[self.count2].get('from'))
                        else:
                            self.myemail = xbmcgui.ListItem(self.emails[self.count2].get('subject') +" "+ lang(23) + " "+ self.emails[self.count2].get('from'))
                    except:
                        try:
                            self.myemail = xbmcgui.ListItem(lang(22) +" "+ lang(23) + " "+ self.emails[self.count2].get('from'))
                        except:
                            self.myemail = xbmcgui.ListItem("BAD EMAIL")
                    self.addItem(self.myemail)
                    if self.readstatus == "UNREAD":
                        self.myemail.setThumbnailImage(self.notread)
                    else:
                        self.myemail.setThumbnailImage(self.read)
                    self.getListItem(2).setLabel("test")
                    self.listsize  = self.listsize + 1
                    f = open(self.emfolder + CORFOLDER + str(self.listsize-1) +".cor", "w")
                    f.write(str(self.count3))
                    f.close()
                    self.count = self.count+1 
                    self.count2 = self.count2+1
                    self.count3 = self.count3-1
                else:
                    self.count = self.count+1
                    self.count3 = self.count3-1
        xbmcgui.unlock()
        return
       


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
        self.txtbox.setText(self.msgText)
        return
    

    
    def checkemail ( self, inbox, minimode):
        w = mailchecker.Checkemail(inbox, minimode, 0)
        w.setupemail()
        self.newmails = w.returnvar
        del w
        return
    
    def getstatus( self ):
        s = self.tempStr.split('|')
        self.readstatus = s[0]
        self.time = s[1]
        self.date = s[2]
        self.mailid = s[3]
        self.emailbody = s[4]
        return
        
    def goFullscreen(self):
        self.temp = self.getCurrentListPosition()
        self.temp2 = self.getListItem(self.temp)
        self.temp3 = self.temp2.getLabel()
        self.temp2.setIconImage(self.read)
        self.launchemaildialog()

    def launchsettings( self ):
        import settings
        ws = settings.Settings("XinBox_Settings.xml",SCRIPTFOLDER + "src","DefaultSkin")
        ws.doModal()
        del ws

    def launchemaildialog( self ):
        ws = emaildialog.gui("XinBox_EmailDialog.xml",SCRIPTFOLDER + "src","DefaultSkin")
        ws.setupvars(self.temp3, self.listsize, self.emfolder, self.getCurrentListPosition(), self.emails, self.inbox)
        ws.doModal()
        self.listsize = ws.returnvar1
        del ws
        xbmcgui.lock()
        self.doitit()
        
    def doitit(self):
        self.addme()
        if self.listsize == 0:
            self.disablexinbox()
        else:
            self.setFocusId(50)
            self.setCurrentListPosition(self.temp)
            self.printEmail(self.getCurrentListPosition())
        xbmcgui.unlock()
    
        
    def onFocus(self, controlID):
        pass

    def onClick(self, controlID):
        if ( controlID == 61):
            if self.box1 == 1:
                self.checkemail(1,0)
                if self.newmails != 0:
                    self.addme()
            else:
                self.openinbox(1)
        elif ( controlID == 62):
            if self.box2 == 1:
                self.checkemail(2,0)
                if self.newmails != 0:
                    self.addme()
            else:
                self.openinbox(2)
        elif ( controlID == 63):
                self.launchsettings()
                
    def parse_email(self, email):
        self.parsemail = email
        return str(self.parsemail)
    
    def exitscript (self):
        xbmc.executebuiltin("Skin.SetBool(xblistnotempty)")
        self.close()
        
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            if self.Fullscreen == True:
                self.undoFullscreen()
            else:
                self.exitscript()
        elif ( button_key == 'A Button' or button_key == 'Keyboard Menu Button'):
            if (50 <= focusid <= 59):
                self.goFullscreen()
        else:
            if (50 <= focusid <= 59):
                self.printEmail(self.getCurrentListPosition())
                

