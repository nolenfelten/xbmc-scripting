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
import xbmcgui, language, time
lang = language.Language().string
import xbmc, sys,os, threading ,xib_util, re
import shutil
import default
import traceback
import mailchecker
import email
import poplib, mimetypes
import string

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
TEMPFOLDER = SCRIPTSETDIR + "temp\\"
IMAGEFILETYPES = ["jpg","jpeg","gif","png","bmp"]
AUDIOFILETYPES = ["wav","mp3","mpa","mp2","ac3","dts"]
VIDEOFILETYPES = ["avi"]
TEXTFILETYPES = ["txt", "doc", "rtf"]

class gui( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0):
        self.control_action = xib_util.setControllerAction()

    def setupvars(self, arg1, arg3, arg4, arg5, arg6):
        self.temp3 = arg1
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
        xbmcgui.unlock()
        
    def openit(self):
        xbmc.executebuiltin("Skin.SetBool(attachlistnotempty)")
        xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
        self.attachlabel = self.getControl(79)
        self.filesizeinfo = self.getControl(81)
        self.attlist = self.getControl(77)
        self.fsoverlay = self.getControl(71)
        self.fsmsgbody = self.getControl(72)
        self.emailinfo = self.getControl(73)
        self.emailrec = self.getControl(74)
        self.attbutn = self.getControl(75)
        self.delbutn = self.getControl(76)
        self.imgagebox = self.getControl(80)
        self.attachsize = self.getControl(82)
        self.attachlabel.setLabel( lang(202) )
        self.attopen = False
        self.showingimage = False
        self.showingtext = False
        self.getemailinfo()
        self.getstatus()
        self.readstatus = "READ"
        self.writestatus()
        self.processEmail(self.temp)
        self.setuplabels()
        self.setFocus(self.fsmsgbody)

    def setuplabels (self):
        self.filesizeinfo.reset()
        self.emailinfo.reset()
        self.emailrec.reset()
        self.fsmsgbody.reset()
        self.fsmsgbody.setText(self.msgText)
        self.filesizeinfo.addLabel( lang( 74 ) + self.emailsiselabel)
        self.emailinfo.addLabel(self.temp3)
        self.emailrec.addLabel( lang( 63 ) + str(self.time) + " - " + str(self.date))
        
    def onClick(self, controlID):
        if ( controlID == 76):
            self.deletemail()
        elif ( controlID == 75):
            if not self.attopen:
                self.click = 0
                self.click2 = 0
                self.click3 = 0
                self.click4 = 0
                self.attopen = True
                xbmc.executebuiltin("Skin.SetBool(attachlistnotempty)")
            else:
                self.attopen = False
                xbmc.executebuiltin("Skin.SetBool(attachlistnotempty)")
                xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
                self.RemoveImage()
                self.RemoveText()
                self.attachsize.reset()
            
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.deleteme = 0
                self.exitme()
        elif ( button_key == 'A Button' or button_key == 'Keyboard Menu Button'):
            if (focusid == 77):
                self.openattach(self.attlist.getSelectedPosition())

    def openattach(self, arg1):
        filetype = string.split(self.attachments[arg1], '.').pop()
        lcfiletype = string.lower(filetype)
        if lcfiletype in IMAGEFILETYPES:
            if self.showingtext:
                self.RemoveText()
            self.click2 = 0
            self.click3 = 0
            self.click4 = 0
            if not self.showingimage:
                self.click = self.click + 1
                self.ShowImage(self.attachments[arg1])
            else:
                if self.currentimage != self.attachments[arg1]:
                    self.click = 1
                    self.RemoveImage()
                    self.attachsize.reset()
                    self.ShowImage(self.attachments[arg1])
                else:
                    self.click = self.click + 1
                    if self.click == 2:
                        self.saveattachment(self.attachments[arg1])
                        self.click = 2
                    elif self.click == 3:
                        self.RemoveImage()
                        self.attachsize.reset()
                        self.click = 0
        elif lcfiletype in (AUDIOFILETYPES + VIDEOFILETYPES):
            if lcfiletype in AUDIOFILETYPES:
                self.media = 1
            elif lcfiletype in VIDEOFILETYPES:
                self.media = 0
            self.RemoveImage()
            if self.showingtext:
                self.RemoveText()
            self.click = 0
            self.click3 = 0
            self.click4 = 0
            if self.click2 == 0:
                self.PlayMedia(self.attachments[arg1])
                self.click2 = 1
            elif self.click2 == 1:
                self.saveattachment(self.attachments[arg1])
                self.click2 = 0
        elif lcfiletype in TEXTFILETYPES:
            self.RemoveImage()
            self.click = 0
            self.click2 = 0
            self.click4 = 0
            if not self.showingtext:
                self.click3 = self.click3 + 1
                self.ShowText(self.attachments[arg1])
            else:
                if self.currenttext != self.attachments[arg1]:
                    self.click3 = 1
                    self.RemoveText()
                    self.attachsize.reset()
                    self.ShowText(self.attachments[arg1])
                else:
                    self.click3 = self.click3 + 1
                    if self.click3 == 2:
                        self.saveattachment(self.attachments[arg1])
                        self.click3 = 2
                    elif self.click3 == 3:
                        self.RemoveText()
                        self.attachsize.reset()
                        self.click3 = 0          
        else:
            if self.showingtext:
                self.RemoveText()
            self.click = 0
            self.click2 = 0
            self.click3 = 0
            if not self.showingimage:
                self.currentimage = self.attachments[arg1]
                self.click4 = self.click4 + 1
                self.imgagebox.setImage(MEDIAFOLDER + "XBbadfile.png")
                self.attachsize.reset()
                self.attsize = os.path.getsize(TEMPFOLDER + self.attachments[arg1])
                self.attachsize.addLabel(lang( 75 ) + self.getsizelabel(self.attsize))
                self.showingimage = True
            else:
                self.click4 = self.click4 + 1
                if self.currentimage != self.attachments[arg1]:
                    self.currentimage = self.attachments[arg1]
                    self.click4 =1
                    self.imgagebox.setImage(MEDIAFOLDER + "XBbadfile.png")
                    self.attachsize.reset()
                    self.attsize = os.path.getsize(TEMPFOLDER + self.attachments[arg1])
                    self.attachsize.addLabel(lang( 75 ) + self.getsizelabel(self.attsize))
                    self.showingimage = True                    
                if self.click4 == 2:
                    self.saveattachment(self.attachments[arg1])
                    self.click4 = 2
                elif self.click4 == 3:
                    self.RemoveImage()
                    self.attachsize.reset()
                    self.click4 = 0
                    
    def saveattachment(self, filename):
        dialog = xbmcgui.Dialog()
        fn = dialog.browse(0, lang(77) % filename , 'files')
        if fn:
            try:
                path = fn
                shutil.copy(TEMPFOLDER + filename, path)
                fn = dialog.ok(lang(0), lang(78) % (filename, path))
            except:
                fn = dialog.ok(lang(0), lang(79) % (filename, path))
            
    def PlayMedia(self, filename):
        self.attachsize.reset()
        self.attsize = os.path.getsize(TEMPFOLDER + filename)
        self.attachsize.addLabel(lang( 75 ) + self.getsizelabel(self.attsize))
        if self.media == 1:
            xbmc.playSFX(TEMPFOLDER + filename)
        else:
            xbmc.Player().play(TEMPFOLDER + filename)
        
        
    def RemoveImage(self):
        self.imgagebox.setImage(MEDIAFOLDER + "XB.png")
        self.showingimage = False   

    def getsizelabel (self, size):
        if size >= 1024:
            size = size/1024.0
            sizeext = "KB"
            if size >= 1024:
                size = size/1024.0
                sizeext = "MB"
        else:sizeext = "bytes"
        return "%.1f %s" % (size,  sizeext)
        
    def ShowImage(self, filename):
        self.attachsize.reset()
        self.attsize = os.path.getsize(TEMPFOLDER + filename)
        self.attachsize.addLabel(lang( 75 ) + self.getsizelabel(self.attsize))
        self.currentimage = filename
        self.imgagebox.setImage(TEMPFOLDER + filename)
        self.showingimage = True
        
    def RemoveText (self):
        self.setuplabels()
        self.delbutn.setEnabled( True )
        self.showingtext = False
        
    def ShowText(self, filename):
        self.filesizeinfo.reset()
        self.attachsize.reset()
        self.attsize = os.path.getsize(TEMPFOLDER + filename)
        self.attachsize.addLabel(lang( 75 ) + self.getsizelabel(self.attsize))        
        self.delbutn.setEnabled( False )
        self.currenttext = filename
        fh = open(TEMPFOLDER + filename)
        text = fh.read()
        self.fsmsgbody.reset()
        self.emailinfo.reset()
        self.emailrec.reset()
        self.emailinfo.addLabel( lang(202)+ " - " + filename)
        self.fsmsgbody.setText(text)
        self.showingtext = True

        
    def exitme(self):
        self.returnvar2 = self.deleteme
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
        self.emailsize = os.path.getsize(self.emfolder + MAILFOLDER + str(self.updateme) +".sss")
        self.emailsiselabel = self.getsizelabel(self.emailsize)

    def processEmail(self, selected):
        self.attachments = []
        if self.emails[selected].is_multipart():
            for part in self.emails[selected].walk():
                if part.get_content_type() != "text/plain" and part.get_content_type() != "text/html" and part.get_content_type() != "multipart/mixed" and part.get_content_type() != "multipart/alternative":
                    filename = part.get_filename()
                    if not filename:
                        print "Bad attachment - no Filename, Attachment not saved."
                    else:
                        self.attachments.append(filename)
                        print "problem saving attachment " + filename
                else:
                    filename = part.get_filename()
                    if filename != None:
                        try:
                            f=open(TEMPFOLDER + filename, "wb")
                            f.write(part.get_payload(decode=1))
                            f.close()
                            self.attachments.append(filename)
                        except:
                            print "problem saving attachment " + filename
                    else:
                        print "no attachment bitch"
        for attachment in self.attachments:
            self.attlist.addItem(attachment)        
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
        parser = html2txt()
        parser.reset()
        parser.feed(email)
        parser.close()
        self.parsemail = parser.output()
       # self.parsemail = self.parse_email2(self.parsemail)
        return self.parsemail

        
    def parse_email2(self, email):
        self.parsemail = re.sub('<STYLE.*?>', '<!--', email)
        self.parsemail = re.sub('&copy', '�', self.parsemail)
        self.parsemail = re.sub('&#174;', '�', self.parsemail)
        self.parsemail = re.sub('<SCRIPT.*?>', '<!--', self.parsemail)
        self.parsemail = re.sub('<style.*?>', '<!--', self.parsemail)
        self.parsemail = re.sub('<script.*?>', '<!--', self.parsemail)
        self.parsemail = re.sub('</STYLE>', '-->', self.parsemail)
        self.parsemail = re.sub('</SCRIPT>', '-->', self.parsemail)
        self.parsemail = re.sub('</style>', '-->', self.parsemail)
        self.parsemail = re.sub('</script>', '-->', self.parsemail)
        self.parsemail = re.sub('(?s)<!--.*?-->', '', self.parsemail)
        self.parsemail = re.sub('(?s)<.*?>', ' ', self.parsemail)
        self.parsemail = re.sub('&nbsp;', ' ', self.parsemail)
        self.parsemail = re.sub('=0D=0A', ' ', self.parsemail)
        return str(self.parsemail)
    
    def deletemail(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.select( lang( 66 ), [ lang( 67 ), lang( 68 ), lang( 69 )])
        if ret == 0:
            os.remove(self.emfolder + MAILFOLDER + str(self.updateme)+".sss")
            self.deleteme = 1
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
            self.deleteme = 1
            os.remove(self.emfolder + MAILFOLDER + str(self.updateme)+".sss")
            self.exitme()
        else:self.setFocus(self.delbutn)

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

