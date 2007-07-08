

import xbmc, xbmcgui, time, sys, os,email, string,shutil

import XinBox_Util
from sgmllib import SGMLParser  
TEMPFOLDER = "P:\\script_data\\XinBox\\Temp\\"
IMAGEFILETYPES = ["jpg","jpeg","gif","png","bmp"]
AUDIOFILETYPES = ["wav","mp3","mpa","mp2","ac3","dts"]
VIDEOFILETYPES = ["avi","wmv"]
TEXTFILETYPES = ["txt", "doc", "rtf", "xml"]

class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,emailsetts=False,lang=False):
        self.language = lang
        self.emailsettings = emailsetts
   
    def onInit(self):
        self.setupvars()
        self.setupcontrols()
        self.setupemail()

        
    def setupvars(self):
        self.click = 0
        self.curpos = 0
        self.showing = False
        self.exiting = False
        self.deleserv = False
        self.returnvalue = "-"
        self.control_action = XinBox_Util.setControllerAction()
        self.attachlist = False
        xbmc.executebuiltin("Skin.SetBool(attachlistnotempty)")
        xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
        xbmc.executebuiltin("Skin.SetBool(emaildialog)")

    def setupemail(self):
        self.getControl(73).addLabel(self.emailsettings[1].get('subject').replace("\n","") + "  " + self.language(260) + "   " + self.emailsettings[1].get('from').replace("\n",""))
        self.settextbox()
        self.getControl(74).addLabel(self.language(261) + self.emailsettings[4] + "-" + self.emailsettings[5])
        self.getControl(80).setImage("XBXinBoXLogo.png")
        self.getControl(90).setLabel("")
        

    def setupcontrols(self):
        self.getControl(80).setImage("XBXinBoXLogo.png")
        self.getControl(81).setEnabled(False)
        self.getControl(89).setLabel(self.language(266))
        if self.emailsettings[2] == 0:
            self.getControl(64).setEnabled(False)
        else:
            self.getattachments()
            self.getControl(64).setEnabled(True)
        
    def getattachments(self):
        self.attachments = []
        if self.emailsettings[1].is_multipart():
            for part in self.emailsettings[1].walk():
                if part.get_content_type() != "text/plain" and part.get_content_type() != "text/html" and part.get_content_type() != "multipart/mixed" and part.get_content_type() != "multipart/alternative":
                    filename = part.get_filename()
                    if filename:
                        try:
                            f=open(TEMPFOLDER + filename, "wb")
                            f.write(part.get_payload(decode=1))
                            f.close()
                            self.attachments.append([filename,os.path.getsize(TEMPFOLDER + filename)])
                        except:pass
                else:
                    filename = part.get_filename()
                    if filename != None:
                        try:
                            f=open(TEMPFOLDER + filename, "wb")
                            f.write(part.get_payload(decode=1))
                            f.close()
                            self.attachments.append([filename,os.path.getsize(TEMPFOLDER + filename)])
                        except:pass
        for attachment in self.attachments:
            self.getControl(81).addItem(attachment[0])

                   
    def settextbox(self):
        if self.emailsettings[1].is_multipart():
            for part in self.emailsettings[1].walk():
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    self.getControl(72).setText(self.parse_email(part.get_payload()))
                    break
        else:self.getControl(72).setText(self.parse_email(self.emailsettings[1].get_payload()))

    def parse_email(self, email):
        parser = html2txt()
        parser.reset()
        parser.feed(email)
        parser.close()
        return parser.output()
        
    def onClick(self, controlID):
        if not self.exiting:
            if controlID == 64:
                self.exiting = True
                self.attachlist = not self.attachlist
                xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
                time.sleep(0.8)
                self.click = 0
                self.resetemail()
                self.getControl(81).setEnabled(self.attachlist)
                self.exiting = False
            elif controlID == 81:
                self.openattach(self.getControl(81).getSelectedPosition())
            elif controlID == 63:
                dialog = xbmcgui.Dialog()
                if self.emailsettings[6] == "-" or self.deleserv:
                    ret = dialog.select( self.language(271), [self.language(272)])
                else:ret = dialog.select( self.language(271), [ self.language(272), self.language(273), self.language(274)])
                if ret == 0:
                    if self.deleserv:
                        self.returnvalue = 2
                    else:self.returnvalue = 0
                    self.exitme()
                elif ret == 1:
                    self.deleserv = True
                    self.returnvalue = 1
                elif ret == 2:
                    self.returnvalue = 2
                    self.exitme()

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
        if self.filebel == "Unknown":
            self.saveattachment(pos)
        elif self.filebel == "Text":
            self.showing = True
            if self.click == 0:
                self.click = 1
                self.showtext(pos)
            else:self.saveattachment(pos)
        elif self.filebel == "Audio":
            if self.click == 0:
                xbmc.playSFX(TEMPFOLDER + self.attachments[pos][0])
                self.click = 1
            else:self.saveattachment(pos)
        elif self.filebel == "Video":
            if self.click == 0:
                self.click = 1
                xbmc.Player().play(TEMPFOLDER + self.attachments[pos][0])
            else:self.saveattachment(pos)
        elif self.filebel == "Image":
            self.showing = True
            if self.click == 0:
                self.click = 1
                self.showimage(pos)
            else:self.saveattachment(pos)

    def saveattachment(self,pos):
        dialog = xbmcgui.Dialog()
        ret = dialog.browse(0, self.language(268) % self.attachments[pos][0] , 'files')
        if ret:
            try:
                shutil.copy(TEMPFOLDER + self.attachments[pos][0], ret)
                di = dialog.ok(self.language(49), self.language(269) % (self.attachments[pos][0], ret))
            except:
                di = dialog.ok(self.language(93), self.language(270) % (self.attachments[pos][0], ret))

    def showimage(self, pos):
        self.getControl(73).reset()
        self.getControl(73).addLabel("Attachment: " + self.attachments[pos][0])
        self.getControl(74).reset()
        self.getControl(91).setImage(TEMPFOLDER + self.attachments[pos][0])
        self.getControl(72).setVisible(False)
        self.getControl(63).setEnabled(False)
        self.getControl(62).setEnabled(False)
        self.getControl(61).setEnabled(False)
        
        

    def showtext(self, pos):
        self.getControl(73).reset()
        self.getControl(73).addLabel("Attachment: " + self.attachments[pos][0])
        self.getControl(74).reset()
        f = open(TEMPFOLDER + self.attachments[pos][0], "r")
        self.getControl(72).setText(f.read())
        f.close()
        self.getControl(63).setEnabled(False)
        self.getControl(62).setEnabled(False)
        self.getControl(61).setEnabled(False)


    def showattach(self, pos):
        filetype = string.lower(string.split(self.attachments[pos][0], '.').pop())
        self.filebel = self.getbel(filetype)
        self.getControl(90).setLabel(self.language(267) + self.getsizelabel(self.attachments[pos][1]))
        if self.filebel == "Unknown":
            self.getControl(80).setImage("XBattachfile.png")
        elif self.filebel == "Text":
            self.getControl(80).setImage("XBattachtext.png")
        elif self.filebel == "Audio":
            self.getControl(80).setImage("XBattachaudio.png")
        elif self.filebel == "Video":
            self.getControl(80).setImage("XBattachvideo.png")
        elif self.filebel == "Image":
            self.getControl(80).setImage("XBattachimage.png")
            
            
    def getbel(self,filetype):
        if filetype in IMAGEFILETYPES:return "Image"
        elif filetype in AUDIOFILETYPES:return "Audio"
        elif filetype in VIDEOFILETYPES:return "Video"
        elif filetype in TEXTFILETYPES:return "Text"
        else:return "Unknown"
        
            
    def onAction( self, action ):
        if not self.exiting:
            button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
            actionID   =  action.getId()
            try:focusid = self.getFocusId()
            except:focusid = 0
            try:control = self.getFocus()
            except: control = 0
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.exitme()
            elif focusid == 81:
                if self.curpos != self.getControl(81).getSelectedPosition():
                    self.click = 0
                    if self.showing:
                        self.resetemail()
                self.curpos = self.getControl(81).getSelectedPosition()
                self.showattach(self.getControl(81).getSelectedPosition())

    def resetemail(self):
        self.showing = False
        self.getControl(91).setImage("-")
        self.getControl(72).setVisible(True)
        self.getControl(63).setEnabled(True)
        self.getControl(62).setEnabled(True)
        self.getControl(61).setEnabled(True)
        self.getControl(73).reset()
        self.getControl(74).reset()
        self.setupemail()
               
    def onFocus(self, controlID):
        pass

    def exitme(self):
        self.exiting = True
        if self.attachlist:
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
            time.sleep(0.8)
        xbmc.executebuiltin("Skin.SetBool(emaildialog)")
        xbmc.executebuiltin("Skin.ToggleSetting(emaildialog)")
        time.sleep(0.8)
        self.removefiles(TEMPFOLDER)
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
