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
    dialog.create( lang( 0 ) )
    updateProgressDialog( __line3__ )

def updateProgressDialog( __line3__ ):
    global dialog, pct
    pct += 5
    dialog.update( pct, __line1__, __line2__, __line3__ )

def closeProgessDialog():
    global dialog
    dialog.close()
    
import xbmcgui, language, time
lang = language.Language().string

__line1__ = lang(60)
__line2__ = lang(61)

createProgressDialog( '%s xbmc' % ( lang( 62 ), ))
import xbmc
updateProgressDialog( '%s sys' % ( lang( 62 ), ))
import sys
updateProgressDialog( '%s os' % ( lang( 62 ), ))
import os
updateProgressDialog( '%s threading' % ( lang( 62 ), ))
import threading
updateProgressDialog( '%s guibuilder' % ( lang( 62 ), ))
import guibuilder
updateProgressDialog( '%s xib_util' % ( lang( 62 ), ))
import xib_util
updateProgressDialog( '%s shutil' % ( lang( 62 ), ))
import shutil
updateProgressDialog( '%s default' % ( lang( 62 ), ))
import default
updateProgressDialog( '%s traceback' % ( lang( 62 ), ))
import traceback
updateProgressDialog( '%s mailchecker' % ( lang( 62 ), ))
import mailchecker
updateProgressDialog( '%s email' % ( lang( 62 ), ))
import email
updateProgressDialog( '%s poplib' % ( lang( 62 ), ))
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
SCRITPFOLDER = default.__scriptpath__
MEDIAFOLDER = SCRITPFOLDER + "src//media//"

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        self.url = "http://xboxmediacenter.com"

    def onInit(self):
        self.setupcontrols()
        self.createdirs()
        self.getSettings()
        self.getmmSettings()
        self.adjustcontrols()
        self.setupvars()
        xbmcgui.unlock()

    def setupcontrols ( self ):
        self.list = self.getControl(68)
        self.txtbox = self.getControl(67)
        self.xb1butn = self.getControl(61)
        self.xb2butn = self.getControl(62)
        self.sebutn = self.getControl(63)
        self.mmbutn = self.getControl(64)
        self.title = self.getControl(66)
        self.bkimage = self.getControl(65)
        self.xbempty = self.getControl(70)
        self.fsoverlay = self.getControl(71)
        self.fsmsgbody = self.getControl(72)
        self.emailinfo = self.getControl(73)
        self.emailrec = self.getControl(74)
        self.attbutn = self.getControl(75)
        self.delbutn = self.getControl(76)
        return
        
    def setupvars( self ):
        self.box1 = 0
        self.box2 = 0
        self.Fullscreen = False
        self.notread = MEDIAFOLDER + "emailnotread.png"
        self.read = MEDIAFOLDER + "emailread.png"
        self.control_action = xib_util.setControllerAction()
        xbmc.log ("setup variables OK")
        return
        
    def adjustcontrols ( self ):
        self.delbutn.setVisible( False )
        self.attbutn.setVisible( False )
        self.fsmsgbody.setVisible( False )
        self.emailinfo.setVisible( False )
        self.emailrec.setVisible( False )        
        self.fsoverlay.setVisible( False )
        self.xbempty.setVisible( False )
        self.list.setVisible( False )
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

    def disablexinbox (self):
        self.txtbox.reset()
        self.txtbox.setVisible( False )
        self.list.setVisible( False )
        self.xbempty.setVisible( True )
        self.xbempty.setLabel( lang(58) )
        if self.box2 ==1:
            self.setFocus(self.xb2butn)
        else:
            self.setFocus(self.xb1butn)
        return
    
    def openinbox( self , inbox):
        if inbox == 1:
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
            if self.list.size() == 0:
                self.disablexinbox()

    def clearfolder(self, folder):
        for root, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
                   
    def addme( self ):
        self.xbempty.setVisible( False )
        self.txtbox.reset()
        self.txtbox.setVisible( True )
        self.clearfolder(self.emfolder + CORFOLDER)
        self.list.setVisible( True )
        self.list.reset()
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
                    if self.readstatus == "UNREAD":
                        self.myemail.setThumbnailImage(self.notread)
                    else:
                        self.myemail.setThumbnailImage(self.read)
                    self.list.addItem(self.myemail)
                    f = open(self.emfolder + CORFOLDER + str(self.list.size()-1) +".cor", "w")
                    f.write(str(self.count3))
                    f.close()
                    self.count = self.count+1 
                    self.count2 = self.count2+1
                    self.count3 = self.count3-1
                else:
                    self.count = self.count+1
                    self.count3 = self.count3-1
        return

    def processEmail(self, selected):
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
            self.attbutn.setEnabled( False )
        else:
            self.attbutn.setEnabled( True )
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
        self.txtbox.setText(self.msgText)
        return

    def getemailinfo(self):
        self.temp = self.list.getSelectedPosition()
        self.temp2 = self.list.getSelectedItem()
        self.temp3 = self.temp2.getLabel()
        fh = open(self.emfolder + CORFOLDER + str(self.temp)+ ".cor")
        self.updateme = fh.read()
        fh.close()
        fh = open(self.emfolder + MAILFOLDER + str(self.updateme) +".sss")
        self.tempStr = fh.read()
        fh.close()
        return

    def delemail (self, inbox, emailid):
        w = mailchecker.Checkemail(inbox, 0, emailid)
        w.deletemail()
        del w
        return
    
    def deletemail(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.select( lang( 66 ), [ lang( 67 ), lang( 68 ), lang( 69 )])
        if ret == 0:
            os.remove(self.emfolder + MAILFOLDER + str(self.updateme)+".sss") 
            self.addme()
            self.undoFullscreen()
            if self.list.size() == 0:
                self.disablexinbox()
            else:
                self.setFocus(self.list)
                try:
                    self.list.selectItem(self.temp)
                except:pass
                self.printEmail(self.list.getSelectedPosition())    
        elif ret == 1:
            if self.box1 == 1:
                self.delemail(1, self.mailid)
            else:
                self.delemail(2, self.mailid)
            self.setFocus(self.delbutn)
            return
        elif ret == 2:
            if self.box1 == 1:
                self.delemail(1, self.mailid)
            else:
                self.delemail(2, self.mailid)
            self.getemailinfo()
            os.remove(self.emfolder + MAILFOLDER + str(self.updateme)+".sss")
            self.addme()
            self.undoFullscreen()
            if self.list.size() == 0:
                self.disablexinbox()
            else:
                self.setFocus(self.list)
                try:
                    self.list.selectItem(self.temp)
                except:pass
                self.printEmail(self.list.getSelectedPosition())
        else:self.setFocus(self.delbutn)
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
        self.emailinfo.reset()
        self.emailrec.reset()
        self.fsmsgbody.reset()
        self.getemailinfo()
        self.getstatus()
        self.temp2.setThumbnailImage(self.read)
        self.readstatus = "READ"
        self.writestatus()
        self.processEmail(self.temp)
        self.attbutn.setVisible( True )
        self.delbutn.setVisible( True )
        self.fsoverlay.setVisible(True)
        self.fsmsgbody.setVisible(True)
        self.fsmsgbody.setText(self.msgText)
        self.setFocus(self.fsmsgbody)
        self.emailinfo.addLabel(self.temp3)
        self.emailrec.addLabel( lang( 63 ) + str(self.time) + " - " + str(self.date))
        self.emailinfo.setVisible(True)
        self.emailrec.setVisible(True)
        self.Fullscreen = True

    def writestatus (self):  
        f = open(self.emfolder + MAILFOLDER + str(self.updateme) +".sss", "w")
        f.write(self.readstatus + "|" + self.time + "|" + self.date + "|" + self.mailid + "|" + self.emailbody)
        f.close()
        return
    
    def undoFullscreen(self):
        self.attbutn.setVisible( False )
        self.delbutn.setVisible( False )
        self.fsoverlay.setVisible(False)
        self.emailinfo.setVisible(False)
        self.emailrec.setVisible(False)
        self.fsmsgbody.setVisible(False)
        self.Fullscreen = False
        self.setFocus(self.list)
        return
        
    def onFocus(self, controlID):
        print 'The control with id="5" just got focus'

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
        elif ( controlID == 76):
                self.deletemail()
                
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try: control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            if self.Fullscreen == True:
                self.undoFullscreen()
            else:
                self.close()
        elif ( button_key == 'A Button' or button_key == 'Keyboard Menu Button'):
            if control == self.list:
                self.goFullscreen()                
        else:
            if control == self.list:
                self.printEmail(self.list.getSelectedPosition())
                
            
        



