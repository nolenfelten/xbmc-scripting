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

from sgmllib import SGMLParser    
import xbmcgui, language, time, settings, re
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
MAILFOLDER = "mail\\"
SCRIPTFOLDER = default.__scriptpath__
MEDIAFOLDER = SCRIPTFOLDER + "src//skins//media//"
TEMPFOLDER = SCRIPTSETDIR + "temp\\"

class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        self.initon = 0
        xbmc.executebuiltin("Skin.SetBool(xblistnotempty)")
        xbmc.executebuiltin("Skin.ToggleSetting(xblistnotempty)")
        self.createdirs()
        self.getSettings()
        self.getmmSettings()
        self.setupvars()      

    def onInit(self):
        if self.initon == 0:
            self.setupcontrols()
            self.adjustcontrols()
            self.initon = 1
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
        self.xbsize = self.getControl(71)
        self.servsize = self.getControl(72)
        return
        
    def setupvars( self ):
        self.listsize = 0
        self.box1 = 0
        self.box2 = 0
        self.Fullscreen = False
        self.notreadattach = MEDIAFOLDER + "XBemailnotreadattach.png"
        self.notread = MEDIAFOLDER + "XBemailnotread.png"
        self.read = MEDIAFOLDER + "XBemailread.png"
        self.readattach = MEDIAFOLDER + "XBemailreadattach.png"
        self.control_action = xib_util.setControllerAction()
        xbmc.log ("setup variables OK")
        return
        
    def adjustcontrols ( self ):
        self.title.setVisible( False )
        self.xbempty.setVisible( False )
        self.xbempty.setLabel( lang(58) )
        self.xbsize.setVisible( False )
        self.mmbutn.setLabel( lang(200) )
        self.sebutn.setLabel( lang(201) )
        if self.mmsettings.disablemmb:
            self.mmbutn.setEnabled( False )
        if self.settings.disablexb1:
            self.xb1butn.setEnabled( False )
        if self.settings.disablexb2:
            self.xb2butn.setEnabled( False )
        self.servsize.setVisible( False )  
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
        self.xbsize.setVisible( False )
        self.txtbox.setVisible( False )
        self.xbempty.setVisible( True )
        if self.box2 ==1:
            self.setFocus(self.xb2butn)
        else:
            self.setFocus(self.xb1butn)
        return
    
    def openinbox( self , inboxy):
        self.title.setVisible( True )
        self.servsize.setVisible( False )
        self.resetlists()
        self.xbsize.setVisible( False )
        self.inbox = inboxy
        if self.inbox == 1:
    	    self.box1 = 1
    	    self.box2 = 0
    	    self.title.setLabel(self.settings.user1)
    	    self.xb1butn.setLabel( lang(65))
    	    self.xb2butn.setLabel("XinBox 2")
    	    self.emfolder = DATADIR + self.settings.user1 + "@" + self.settings.server1 + "\\"
    	    self.serversize = self.settings.serversize1
        else:
    	    self.box2 = 1
    	    self.box1 = 0
    	    self.title.setLabel(self.settings.user2)
    	    self.xb2butn.setLabel( lang(65))
    	    self.xb1butn.setLabel("XinBox 1")
    	    self.emfolder = DATADIR + self.settings.user2 + "@" + self.settings.server2 + "\\"
    	    self.serversize = self.settings.serversize2
        if not os.path.exists(self.emfolder):
            self.disablexinbox()
        else:
            self.addme()
            if self.listsize == 0:
                self.disablexinbox()
            else:
                 self.setsizelabel()
            self.getmailboxsize()
            self.dialog.close()
            xbmcgui.unlock()
                     
    def getservsize(self):
        self.servsize.setEnabled(True)
        if self.inbox == 1:
            server = self.settings.serversize1
        else:server = self.settings.serversize2
        if server != "-":
            if self.xbsizeb != 0:
                temp1 = int(server)*1024.0
                temp2 = (self.xbsizeb/temp1)*100.0
                self.mypercent = "%.0f" % (temp2) + "%"
                self.servsize.setVisible( True )
                if temp2 >= 90:
                    self.servsize.setLabel(lang(98)%(self.label,self.mypercent,server))
                    self.servsize.setEnabled(False)
                else:
                    self.servsize.setLabel(lang(98)%(self.label,self.mypercent,server))
            else:
                self.mypercent = "0%"
                self.servsize.setLabel(lang(98)%(self.label,self.mypercent,server))

    def getmailboxsize(self):
        if self.serversize != "-":
            if self.inbox == 1:
                self.user = self.settings.user1
                self.server = self.settings.server1
                self.passw = self.settings.pass1
                self.ssl = self.settings.ssl1
            else:
                self.user = self.settings.user2
                self.server = self.settings.server2
                self.passw = self.settings.pass2
                self.ssl = self.settings.ssl2
            try:
                if self.ssl == "-":
                    mail = poplib.POP3(self.server)
                else:
                    mail = poplib.POP3_SSL(self.server, self.ssl)
                mail.user(self.user)
                mail.pass_(self.passw)
                self.label = self.getsizelabel(mail.stat()[1])
                self.getservsize()
                mail.quit()
            except:traceback.print_exc()
        
    def resetlists(self):
        self.clearList()
        self.mainarray = []
        self.mylistitems = []
        self.emails = []
        self.listsize = 0
        
                
    def setsizelabel(self):
        size = self.getxinboxsize()
        mylabel = self.getsizelabel(size)
        self.xbsize.setLabel( lang(80) + mylabel)
        self.xbsize.setVisible( True )
        
    def getxinboxsize(self):
        size = 0
        for files in os.listdir(self.emfolder + MAILFOLDER):
            temp = os.path.getsize(self.emfolder + MAILFOLDER + str(files))
            size = size + temp
        return size
            
    def getsizelabel (self, size):
        if size >= 1024:
            size = size/1024.0
            sizeext = "KB"
            self.xbsizeb = size
            if size >= 1024:
                size = size/1024.0
                sizeext = "MB"
        else:
            self.xbsizeb = 0
            sizeext = "bytes"
        return "%.1f %s" % (size,  sizeext)            
            
    def clearfolder(self, folder):
        for root, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

        
    def addme( self ):
        xbmcgui.lock()
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create( lang(0), lang(76))        
        xbmc.executebuiltin("Skin.SetBool(xblistnotempty)")
        self.xbempty.setVisible( False )
        self.txtbox.reset()
        self.txtbox.setVisible( True )
        self.gettally()
        self.count = 0
        self.count3 = self.tally
        for self.count in range(self.tally):
                self.dialog.update((self.count*100)/self.tally)
                self.temp2 = self.emfolder + MAILFOLDER + str(self.count3) +".sss"
                if os.path.exists(self.temp2):
                    fh = open(self.temp2)
                    self.tempStr = fh.read()
                    fh.close()
                    self.getstatus()
                    temp = email.message_from_string(self.emailbody)
                    self.emails.append(temp)
                    attachmenty = self.checkattachment(temp)
                    try:
                        subject = temp.get('subject')
                        subject = subject.replace("\n","")
                        ffrom = temp.get('from')
                        ffrom = ffrom.replace("\n","")
                        if subject == "":
                            self.myemail = xbmcgui.ListItem(lang(22) +" "+ lang(23) + " "+ ffrom)
                        else:
                            self.myemail = xbmcgui.ListItem(subject +" "+ lang(23) + " "+ ffrom)
                    except:
                        try:
                            ffrom = temp.get('from')
                            ffrom = ffrom.replace("\n","")
                            self.myemail = xbmcgui.ListItem(lang(22) +" "+ lang(23) + " "+ ffrom)
                        except:
                            self.myemail = xbmcgui.ListItem(lang(96))
                    self.addItem(self.myemail)
                    self.mylistitems.append(self.myemail)
                    if self.readstatus == "UNREAD":
                        if attachmenty:
                            self.myemail.setThumbnailImage(self.notreadattach)
                        else:
                            self.myemail.setThumbnailImage(self.notread)
                    else:
                        if attachmenty:
                            self.myemail.setThumbnailImage(self.readattach)
                        else:
                            self.myemail.setThumbnailImage(self.read)
                    self.listsize  = self.listsize + 1
                    self.mainarray.append(self.count3)
                    self.count = self.count+1 
                    self.count3 = self.count3-1
                else:
                    self.count = self.count+1
                    self.count3 = self.count3-1

    def printEmail(self, selected):
        self.msgText = ""
        if self.emails[selected].is_multipart():
            for part in self.emails[selected].walk():
                if part.get_content_type() == "text/plain":
                    email = self.parse_email(part.get_payload())
                    self.msgText = email
                    break
        else:
            if self.emails[selected].get_content_type() == "text/html":
                email2 = self.parse_email(self.emails[selected].get_payload())
                self.msgText = email2
            else:
                email3 = self.parse_email(self.emails[selected].get_payload())
                self.msgText = email3
        self.txtbox.setText(self.msgText)
        return
    
    def checkattachment(self, myemail):
        if myemail.is_multipart():
            for part in myemail.walk():
                if part.get_content_type() != "text/plain" and part.get_content_type() != "text/html" and part.get_content_type() != "multipart/mixed" and part.get_content_type() != "multipart/alternative":
                    filename = part.get_filename()
                    if not filename:pass
                    else:return True
                else:
                    filename = part.get_filename()
                    if filename != None:return True
                    else:pass
        else:return False
        return False
    
    def checkemail ( self, inbox, minimode):
        w = mailchecker.Checkemail(inbox, minimode, 0)
        w.setupemail()
        self.newmails = w.returnvar
        self.newids = w.returnvar2
        del w
        if self.newids != []:
            self.addmylistitem()
            try:
                self.getmailboxsize()
                dialog.close()
                xbmcgui.unlock()
            except:
                traceback.print_exc()
                self.dialog.close()
                xbmcgui.unlock()

    def addmylistitem(self):
        xbmcgui.lock()
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create( lang(0), lang(97))  
        xbmc.executebuiltin("Skin.SetBool(xblistnotempty)")
        self.xbempty.setVisible( False )
        self.myemail = xbmcgui.ListItem("test")
        self.txtbox.reset()
        self.txtbox.setVisible( True )
        for ids in self.newids:
            self.listsize = self.listsize + 1
            temp = self.emfolder + MAILFOLDER + str(ids) +".sss"
            fh = open(temp)
            self.tempStr = fh.read()
            fh.close()
            self.getstatus()
            temp = email.message_from_string(self.emailbody)
            attachmenty = self.checkattachment(temp)
            try:
                subject = temp.get('subject')
                subject = subject.replace("\n","")
                ffrom = temp.get('from')
                ffrom = ffrom.replace("\n","")
                if subject == "":
                    self.myemail = xbmcgui.ListItem(lang(22) +" "+ lang(23) + " "+ ffrom)
                else:
                    self.myemail = xbmcgui.ListItem(subject +" "+ lang(23) + " "+ ffrom)
            except:
                try:
                    ffrom = temp.get('from')
                    ffrom = ffrom.replace("\n","")
                    self.myemail = xbmcgui.ListItem(lang(22) +" "+ lang(23) + " "+ ffrom)
                except:
                    self.myemail = xbmcgui.ListItem(lang(96))
            self.addItem(self.myemail,0)
            if self.readstatus == "UNREAD":
                if attachmenty:
                    self.myemail.setThumbnailImage(self.notreadattach)
                else:
                    self.myemail.setThumbnailImage(self.notread)
            else:
                if attachmenty:
                    self.myemail.setThumbnailImage(self.readattach)
                else:
                    self.myemail.setThumbnailImage(self.read)
            self.mainarray.insert( 0, ids)
            self.mylistitems.insert( 0, self.myemail)
            self.emails.insert( 0, temp)
        self.setsizelabel()
    
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
        self.temp4 = self.mylistitems[self.temp]
        self.temp3 = self.temp4.getLabel()
        attach = self.checkattachment(self.emails[self.temp])
        if attach:
            self.temp4.setThumbnailImage(self.readattach)
        else:
            self.temp4.setThumbnailImage(self.read)
        self.launchemaildialog()

    def launchsettings( self ):
        import settings
        xbmcgui.lock()
        ws = settings.Settings("XinBox_Settings.xml",SCRIPTFOLDER + "src","DefaultSkin")
        ws.doModal()
        del ws

    def launchemaildialog( self ):
        xbmcgui.lock()
        ws = emaildialog.gui("XinBox_EmailDialog.xml",SCRIPTFOLDER + "src","DefaultSkin")
        ws.setupvars(self.temp3, self.emfolder, self.getCurrentListPosition(), self.emails, self.inbox,self.mainarray)
        ws.doModal()
        self.deleteme = ws.returnvar2
        self.servchanged = ws.returnvar1
        del ws
        xbmcgui.lock()
        self.doitit()
        
    def doitit(self):
        try:
            if self.servchanged  == 1:
                self.getmailboxsize()
            if self.deleteme != 0:
                self.removeItem(self.temp)
                temp = self.mainarray[self.temp]
                self.mainarray.remove(temp)
                self.mylistitems.remove(self.temp4)
                temp = self.emails[self.temp]
                self.emails.remove(temp)
                self.listsize = self.listsize - 1
                self.setsizelabel()
            if self.listsize == 0:
                self.disablexinbox()
            else:self.printEmail(self.getCurrentListPosition())
            xbmcgui.unlock()
        except:traceback.print_exc()
    
            
    def onFocus(self, controlID):
        pass

    def onClick(self, controlID):
        if ( controlID == 61):
            if self.box1 == 1:
                self.checkemail(1,0)
            else:
                self.openinbox(1)
        elif ( controlID == 62):
            if self.box2 == 1:
                self.checkemail(2,0)
            else:
                self.openinbox(2)
        elif ( controlID == 63):
                self.launchsettings()
                
    def parse_email(self, email):
        parser = html2txt()
        parser.reset()
        parser.feed(email)
        parser.close()
        return parser.output()
    
    def exitscript (self):
        xbmc.executebuiltin("Skin.SetBool(xblistnotempty)")
        self.clearfolder(TEMPFOLDER)
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

            
        
                
class html2txt(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.pieces = []

    def handle_data(self, text):
        self.pieces.append(text)

    def handle_entityref(self, ref):
        if ref=='amp':
            self.pieces.append("&")

    def output(self):
        return " ".join(self.pieces)
