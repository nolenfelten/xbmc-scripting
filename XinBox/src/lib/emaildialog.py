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

import xbmcgui, language, time
lang = language.Language().string
import xbmc, sys,os, threading ,xib_util
import shutil
import default
import traceback
import mailchecker
import email
import poplib, mimetypes

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

class gui( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        self.control_action = xib_util.setControllerAction()

    def setupvars(self, arg1, arg2, arg3, arg4, arg5, arg6):
        self.temp3 = arg1
        self.listsize = arg2
        self.emfolder = arg3
        self.CurrentListPosition = arg4
        self.emails = arg5
        inbox = arg6
        if inbox == 1:
    	    self.box1 = 1
    	    self.box2 = 0
        else:
    	    self.box2 = 1
    	    self.box1 = 0    	    
    
    def onInit(self):
        self.openit()

    def openit(self):
        xbmcgui.lock()
        self.fsoverlay = self.getControl(71)
        self.fsmsgbody = self.getControl(72)
        self.emailinfo = self.getControl(73)
        self.emailrec = self.getControl(74)
        self.attbutn = self.getControl(75)
        self.delbutn = self.getControl(76)
        self.getemailinfo()
        self.getstatus()
        self.readstatus = "READ"
        self.writestatus()
        self.processEmail(self.temp)
        self.emailinfo.reset()
        self.emailrec.reset()
        self.fsmsgbody.reset()
        self.fsmsgbody.setText(self.msgText)
        self.setFocus(self.fsmsgbody)
        self.emailinfo.addLabel(self.temp3)
        self.emailrec.addLabel( lang( 63 ) + str(self.time) + " - " + str(self.date))
        xbmcgui.unlock()        
        
    def onClick(self, controlID):
        if ( controlID == 76):
            self.deletemail()
                
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.exitme()
                
    def exitme(self):
        self.returnvar1 = self.listsize
        self.close()

    def onFocus(self, controlID):
        pass 

    def getemailinfo(self):
        self.temp = self.CurrentListPosition
        fh = open(self.emfolder + CORFOLDER + str(self.temp)+ ".cor")
        self.updateme = fh.read()
        fh.close()
        fh = open(self.emfolder + MAILFOLDER + str(self.updateme) +".sss")
        self.tempStr = fh.read()
        fh.close()
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
        return
    
    def delemail (self, inbox, emailid):
        w = mailchecker.Checkemail(inbox, 0, emailid)
        w.deletemail()
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
    
    def writestatus (self):  
        f = open(self.emfolder + MAILFOLDER + str(self.updateme) +".sss", "w")
        f.write(self.readstatus + "|" + self.time + "|" + self.date + "|" + self.mailid + "|" + self.emailbody)
        f.close()
        return
    
    def parse_email(self, email):
        self.parsemail = email
        return str(self.parsemail)
    
    def deletemail(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.select( lang( 66 ), [ lang( 67 ), lang( 68 ), lang( 69 )])
        if ret == 0:
            os.remove(self.emfolder + MAILFOLDER + str(self.updateme)+".sss")
            self.listsize  = self.listsize - 1
            self.exitme()
        elif ret == 1:
            if self.box1 == 1:
                self.delemail(1, self.mailid)
            else:
                self.delemail(2, self.mailid)
            self.setFocus(self.delbutn)
        elif ret == 2:
            if self.box1 == 1:
                self.delemail(1, self.mailid)
            else:
                self.delemail(2, self.mailid)
            self.getemailinfo()
            os.remove(self.emfolder + MAILFOLDER + str(self.updateme)+".sss")
            self.listsize  = self.listsize - 1
            self.exitme()
        else:self.setFocus(self.delbutn)
