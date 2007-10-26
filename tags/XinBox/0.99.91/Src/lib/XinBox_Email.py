

import xbmc, xbmcgui, time, sys, os,email, string,shutil,re,zipfile
import XinBox_Util
import XinBox_InfoDialog
from sgmllib import SGMLParser
from email import Charset
TEMPFOLDER = XinBox_Util.__tempdir__

class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,emailsetts=False,lang=False,myemail=False):
        self.myemail = myemail
        self.srcpath = strFallbackPath
        self.language = lang
        self.emailsettings = emailsetts
   
    def onInit(self):
        self.setupvars()
        self.setupemail()
        self.setupcontrols()

      
    def setupvars(self):
        xbmcgui.lock()
        self.unreadvalue = 0
        self.click = 0
        self.ziplist = []
        self.subject = self.emailsettings[1][0]
        self.emfrom = self.emailsettings[1][1]
        self.to = self.myemail.get('to').replace("\n","")
        self.cc = self.myemail.get('Cc')
        if self.cc == None:
            self.cc = ""
        else:self.cc = self.cc.replace("\n","")
        date = self.myemail.get('date')
        if date == None:
            mytime = time.strptime(xbmc.getInfoLabel("System.Date") + xbmc.getInfoLabel("System.Time"),'%A , %B %d, %Y %I:%M %p')
            self.sent = time.strftime('%a, %d %b %Y %X +0000',mytime).replace("\n","")
        else:self.sent = str(date).replace("\n","")
        self.attachments = []
        self.replyvalue = 0
        self.curpos = 0
        self.showing = False
        self.returnvalue = "-"
        self.control_action = XinBox_Util.setControllerAction()
        self.attachlist = False
        xbmc.executebuiltin("Skin.Reset(attachlistnotempty)")
        xbmc.executebuiltin("Skin.Reset(emaildialog)")

    def setupemail(self):
        self.getControl(73).addLabel(self.subject + "  " + self.language(260) + "   " + self.emfrom)
        self.settextbox()
        self.getControl(74).addLabel(self.emailsettings[4] + " - " + self.emailsettings[5])
        

    def setupcontrols(self):
        self.getControl(50).setEnabled(False)
        self.getControl(80).setImage("XBXinBoXLogo.png")
        self.getControl(81).setEnabled(False)
        self.getControl(89).setLabel(self.language(266))
        if self.emailsettings[2] == 0:
            self.getControl(64).setEnabled(False)
            xbmcgui.unlock()
            self.animating = True
            xbmc.executebuiltin("Skin.ToggleSetting(emaildialog)")
            time.sleep(0.8)
            self.animating = False
        else:
            self.getattachments()
            self.getControl(64).setEnabled(True)
        self.setFocusId(72)
        
    def getattachments(self):
        if self.myemail.is_multipart():
            for part in self.myemail.walk():
                if part.get_content_type() != "text/plain" and part.get_content_type() != "text/html" and part.get_content_type() != "multipart/mixed" and part.get_content_type() != "multipart/alternative":
                    filename = part.get_filename()
                    if filename != None:
                        try:
                            f=open(TEMPFOLDER + filename, "wb")
                            f.write(part.get_payload(decode=1))
                            f.close()
                            self.attachments.append([filename,TEMPFOLDER + filename,os.path.getsize(TEMPFOLDER + filename)])
                        except:pass
                else:
                    filename = part.get_filename()
                    if filename != None:
                        try:
                            if part.get_content_type() == "text/plain":f=open(TEMPFOLDER + filename, "w")
                            else:f=open(TEMPFOLDER + filename, "wb")
                            f.write(part.get_payload(decode=1))
                            f.close()
                            self.attachments.append([filename,TEMPFOLDER + filename,os.path.getsize(TEMPFOLDER + filename)])
                        except:pass
        if len(self.attachments) != 0:
            for attachment in self.attachments:
                self.getControl(81).addItem(attachment[0])
            self.animating = True
            xbmcgui.unlock()
            xbmc.executebuiltin("Skin.ToggleSetting(emaildialog)")
            time.sleep(1.2)
            self.attachlist = not self.attachlist
            self.getControl(81).setEnabled(self.attachlist)
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
            time.sleep(0.8)
            self.animating = False
                   
    def settextbox(self):
        if self.myemail.is_multipart():
            for part in self.myemail.walk():
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    self.body = self.parse_email(part.get_payload())
                    self.getControl(72).setText(self.body)
                    break
        else:
            self.body = self.parse_email(self.myemail.get_payload())
            self.getControl(72).setText(self.body)

    def parse_email(self, email):
        email = email.decode("quopri_codec")
        parser = html2txt()
        parser.reset()
        parser.feed(email)
        parser.close()
        return parser.output()

    def getem(self, myfrom):
        myre = re.search('<([^>]*)>',myfrom).group(1)
        if myre == None:
            return myfrom
        else:return myre

    def goattachlist(self):
        self.animating = True
        self.attachlist = not self.attachlist
        self.click = 0
        self.getControl(81).setEnabled(self.attachlist)
        self.animating = False
        xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
        time.sleep(1)
        self.resetemail()
        
    def onClick(self, controlID):
        if not self.animating:
            if controlID == 64:
                self.goattachlist()
            elif controlID == 65:
                self.unreadvalue = 1
                self.exitme()                
            elif controlID == 61:
                self.replyvalue = [self.emfrom,"","","Re: " + self.subject,self.getreply(self.body),None]
                self.exitme()
            elif controlID == 62:
                if len(self.attachments) == 0:self.attachments = None
                self.replyvalue = ["","","","Fwd: " + self.subject,self.getreply(self.body),self.attachments]
                self.exitme()
            elif controlID == 81:
                self.openattach(self.getControl(81).getSelectedPosition())
            elif controlID == 63:
                dialog = xbmcgui.Dialog()
                if self.emailsettings[6] == "-":
                    ret = dialog.select( self.language(271), [self.language(272)])
                else:ret = dialog.select( self.language(271), [ self.language(272), self.language(273), self.language(274)])
                if ret != -1 :
                    self.returnvalue = ret
                    self.exitme()

    def getreply (self, body):
        newbody = "----- Original Message -----\n"
        newbody = newbody + "From: " + self.emfrom + "\n"
        newbody = newbody + "To: " + self.to + "\n"
        if self.cc != "":newbody = newbody + "Cc: " + self.cc + "\n"
        newbody = newbody + "Sent: " + self.sent + "\n"
        newbody = newbody + "Subject: " + self.subject + "\n\n"
        for line in body.split("\n"):
            newbody = newbody + "> " + line + "\n"
        return newbody
        

    def getsizelabel (self, size):
        if size >= 1024:
            size = size/1024.0
            sizeext = "KB"
            if size >= 1024:
                size = size/1024.0
                sizeext = "MB"
        else:sizeext = "bytes"
        return "%.1f %s" % (size,  sizeext)

    def openattach(self, pos):
        if self.filebel == "Text":
            if not self.showing:
                self.showing = True
                self.showtext(pos)
            else:
                self.resetemail()
                self.curpos = self.getControl(81).getSelectedPosition()
                self.showattach(self.getControl(81).getSelectedPosition())
        elif self.filebel == "Audio":
            xbmc.playSFX(TEMPFOLDER + self.attachments[pos][0])
        elif self.filebel == "Video":
            xbmc.Player().play(TEMPFOLDER + self.attachments[pos][0])
        elif self.filebel == "Image":
            if not self.showing:
                self.showing = True
                self.showimage(pos)
            else:
                self.resetemail()
                self.curpos = self.getControl(81).getSelectedPosition()
                self.showattach(self.getControl(81).getSelectedPosition())
        elif self.filebel == "Archive":
            if not self.showing:
                self.showing = True
                self.showzip(pos)
            else:
                self.resetemail()
                self.curpos = self.getControl(81).getSelectedPosition()
                self.showattach(self.getControl(81).getSelectedPosition())

    def showzip(self,pos):
        self.getControl(73).reset()
        self.getControl(73).addLabel(self.language(320) + " " + self.attachments[pos][0])
        self.getControl(74).reset()
        self.getControl(72).setVisible(False)
        self.getControl(63).setEnabled(False)
        self.getControl(62).setEnabled(False)
        self.getControl(61).setEnabled(False)
        self.zippath = TEMPFOLDER + self.attachments[pos][0]
        self.unzip("",True,False)
        if len(self.ziplist) == 0:self.addItem(self.language(279))
        else:
            self.getControl(50).setEnabled(True)
            self.setFocusId(50)

    def saveattachment(self,pos):
        dialog = xbmcgui.Dialog()
        ret = dialog.browse(3, self.language(268) % self.attachments[pos][0], 'files')
        if ret:
            try:
                shutil.copy(TEMPFOLDER + self.attachments[pos][0], ret)
                di = dialog.ok(self.language(49), self.attachments[pos][0],self.language(269), ret)
            except:di = dialog.ok(self.language(93),self.attachments[pos][0],self.language(270), ret)

    def savezip(self, pos):
        dialog = xbmcgui.Dialog()
        ret = dialog.browse(0, self.language(268) % self.ziplist[pos], 'files')
        if ret:
            try:
                self.unzip(ret,False,self.ziplist[pos])
                di = dialog.ok(self.language(49), self.ziplist[pos],self.language(269), ret)
            except:di = dialog.ok(self.language(93),self.ziplist[pos],self.language(270), ret)
        
    def unzip(self, path, listing, myzipfile):
        zip = zipfile.ZipFile(self.zippath, 'r')
        namelist = zip.namelist()
        for item in namelist:
            if listing:
                self.ziplist.append(str(item))
                self.addItem(str(item))
            else:
                if str(item) == myzipfile:
                    file(path + str(item),'wb').write(zip.read(item))
        zip.close()

    def showimage(self, pos):
        self.getControl(73).reset()
        self.getControl(73).addLabel(self.language(320) + " " + self.attachments[pos][0])
        self.getControl(74).reset()
        self.getControl(91).setImage(TEMPFOLDER + self.attachments[pos][0])
        self.getControl(72).setVisible(False)
        self.getControl(63).setEnabled(False)
        self.getControl(62).setEnabled(False)
        self.getControl(61).setEnabled(False)
        
        
    def showtext(self, pos):
        self.getControl(73).reset()
        self.getControl(73).addLabel(self.language(320) + " " + self.attachments[pos][0])
        self.getControl(74).reset()
        f = open(TEMPFOLDER + self.attachments[pos][0], "r")
        self.getControl(72).setText(f.read().replace("\t",""))
        f.close()
        self.getControl(63).setEnabled(False)
        self.getControl(62).setEnabled(False)
        self.getControl(61).setEnabled(False)
        self.setFocusId(72)


    def showattach(self, pos):
        filetype = string.lower(string.split(self.attachments[pos][0], '.').pop())
        self.filebel = XinBox_Util.getfiletypes(filetype)
        self.getControl(90).setLabel(self.language(267) + self.getsizelabel(self.attachments[pos][2]))
        if self.filebel == "Unknown":self.getControl(80).setImage("XBattachfile.png")
        elif self.filebel == "Text":self.getControl(80).setImage("XBattachtext.png")
        elif self.filebel == "Audio":self.getControl(80).setImage("XBattachaudio.png")
        elif self.filebel == "Video":self.getControl(80).setImage("XBattachvideo.png")
        elif self.filebel == "Image":self.getControl(80).setImage("XBattachimage.png")
        elif self.filebel == "Archive":self.getControl(80).setImage("XBattacharchive.png")
            
    def onAction( self, action ):
        if not self.animating:
            button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
            actionID   =  action.getId()
            try:focusid = self.getFocusId()
            except:focusid = 0
            try:control = self.getFocus()
            except: control = 0
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu' ):
                self.exitme()
            elif focusid == 81:
                if ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Info' ):
                    self.launchinfo(137,self.language(266))
                elif ( button_key == 'Keyboard TAB Button' or button_key == 'White Button' or button_key == 'Remote Display'):
                    self.saveattachment(self.getControl(81).getSelectedPosition())
                else:
                    if self.curpos != self.getControl(81).getSelectedPosition():
                        if self.showing:self.resetemail()
                    self.curpos = self.getControl(81).getSelectedPosition()
                    self.showattach(self.getControl(81).getSelectedPosition())
            elif focusid == 50:
                if ( button_key == 'Keyboard TAB Button' or button_key == 'White Button' or button_key == 'Remote Display'):
                    self.savezip(self.getCurrentListPosition())
            elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Info' ):
                if focusid == 61:
                    self.launchinfo(138,"R")
                elif focusid == 62:
                    self.launchinfo(139,"F")
                elif focusid == 63:
                    self.launchinfo(140,"D")
                elif focusid == 64:
                    self.launchinfo(141,"A")
                elif focusid == 65:
                    self.launchinfo(170,"M")                    
                elif focusid == 72:
                    self.launchinfo(142,self.language(281))
                elif focusid == 50:
                    self.launchinfo(143,self.language(280))

    def launchinfo(self, focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.srcpath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        value = dialog.value
        del dialog
        return value


    def resetemail(self):
        self.ziplist = []
        self.getControl(50).setEnabled(False)
        self.clearList()
        self.getControl(80).setImage("XBXinBoXLogo.png")
        self.getControl(90).setLabel("")
        self.getControl(91).setImage("-")
        self.getControl(72).setVisible(True)
        self.getControl(63).setEnabled(True)
        self.getControl(62).setEnabled(True)
        self.getControl(61).setEnabled(True)
        if self.showing:
            self.getControl(73).reset()
            self.getControl(74).reset()
            self.setupemail()
            self.showing = False
               
    def onFocus(self, controlID):
        pass

    def exitme(self):
        self.animating = True
        if self.attachlist:
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
            time.sleep(0.9)
        xbmc.executebuiltin("Skin.Reset(emaildialog)")
        time.sleep(0.9)
        self.close()

    def removefiles(self,mydir):
        for root, dirs, files in os.walk(mydir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name)) 

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
