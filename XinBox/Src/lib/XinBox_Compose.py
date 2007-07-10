

import xbmc, xbmcgui, time, sys, os, string, traceback
import XinBox_Util
from os.path import join, exists, basename,getsize

IMAGEFILETYPES = ["jpg","jpeg","gif","png","bmp"]
AUDIOFILETYPES = ["wav","mp3","mpa","mp2","ac3","dts"]
VIDEOFILETYPES = ["avi","wmv","mpg"]
TEXTFILETYPES = ["txt", "doc", "rtf", "xml"]


class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,inboxsetts=False,lang=False,emailfromfile=False,inboxname=False,mydraft=False,ibfolder=False):
        self.mydraft = mydraft
        self.ibfolder = ibfolder
        self.inbox = inboxname
        self.language = lang
        self.ibsettings = inboxsetts
   
    def onInit(self):
        self.setupvars()
        self.setupcontrols()

    def setupvars(self):
        xbmcgui.lock()
        xbmc.executebuiltin("Skin.SetBool(attachlistnotempty)")
        xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
        xbmcgui.unlock()
        self.animating = True
        xbmc.executebuiltin("Skin.SetBool(emaildialog)")
        time.sleep(0.9)
        self.animating = False
        self.setFocusId(82)
        self.attachlist = False
        if self.mydraft[5] == None:self.attachments = []
        else:self.attachments = self.mydraft[5]
        print "attachments = " + str(self.attachments)
        self.body = self.mydraft[4]
        self.returnvalue = 0
        self.toaddr = self.mydraft[0]
        self.ccaddr = self.mydraft[1]
        self.bccaddr = self.mydraft[2]
        self.subject = self.mydraft[3]
        self.control_action = XinBox_Util.setControllerAction()
        self.attachlist = False
        
    def setupcontrols(self):
        self.getControl(80).setImage("XBXinBoXLogo.png")
        self.getControl(89).setLabel(self.language(266))
        self.getControl(84).setLabel(self.language(310))
        self.getControl(85).setLabel(self.language(311))
        self.getControl(86).setLabel(self.language(312))
        self.getControl(87).setLabel(self.language(313))
        self.getControl(60).setLabel(self.language(64))
        self.getControl(61).setLabel(self.language(314))
        self.getControl(62).setLabel(self.language(61))
        self.getControl(82).addItem(self.toaddr)
        self.getControl(82).addItem(self.ccaddr)
        self.getControl(82).addItem(self.bccaddr)
        self.getControl(82).addItem(self.subject)
        self.getControl(73).addLabel(self.language(315) + " " + self.inbox + " <" + self.ibsettings.getSetting("Email Address") + ">")
        if len(self.attachments) != 0:
            self.attachlist = True
            for attach in self.attachments:
                self.getControl(81).addItem(attach[0])
            self.getControl(81).setEnabled(True)
            self.animating = True
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
            time.sleep(0.8)
            self.animating = False
        else:self.getControl(81).setEnabled(False)
        
    def onClick(self, controlID):
        if not self.animating:
            if controlID == 82:
                pos = self.getControl(82).getSelectedPosition()
                if pos == 0:
                    kb = self.showKeyboard("Enter To: Address(s):",self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:
                        self.toaddr = kb
                        self.getControl(82).getSelectedItem().setLabel(kb)
                elif pos == 1:
                    kb = self.showKeyboard("Enter Cc: Address(s):",self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:
                        self.ccaddr = kb
                        self.getControl(82).getSelectedItem().setLabel(kb)
                elif pos == 2:
                    kb = self.showKeyboard("Enter Bcc: Address(s):",self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:
                        self.bccaddr = kb
                        self.getControl(82).getSelectedItem().setLabel(kb)
                elif pos == 3:
                    kb = self.showKeyboard("Enter Subject):",self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:
                        self.subject = kb
                        self.getControl(82).getSelectedItem().setLabel(kb)
            elif controlID == 60:pass
                #self.savedraft()             
            elif controlID == 61:
                self.returnvalue = [self.toaddr,self.ccaddr,self.bccaddr,self.subject,"XinBox Test",self.attachments]
                self.exitme()
            elif controlID == 62:
                self.addattachment()
            elif controlID == 81:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), "Remove this attchment?"):
                    self.attachments.pop(self.getControl(81).getSelectedPosition())
                    self.getControl(81).reset()
                    if len(self.attachments) == 0:
                        self.animating = True
                        xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
                        time.sleep(0.8)
                        self.animating = False
                        self.getControl(80).setImage("XBXinBoXLogo.png")
                        self.getControl(90).setLabel("")
                        self.attachlist = False
                        self.getControl(81).setEnabled(False)
                        self.setFocusId(62)
                    else:
                        for attach in self.attachments:
                            self.getControl(81).addItem(attach[0])
                
    def savedraft(self):
        myattach = ""
        for attach in self.attachments:
            myattach = attach[1] + "," + myattach
        if exists(self.ibfolder + "\\drafts.xib"):
            f = open(self.ibfolder + "\\drafts.xib","r")
            draft = f.read()
            f.close()
            draft = draft + self.toaddr + "|" + self.ccaddr + "|" + self.bccaddr + "|" + self.subject + "|" + self.body + "|" + myattach + "<>"
            f = open(self.ibfolder + "\\drafts.xib","w")
            f.write(draft)
            f.close()
        else:
            f = open(self.ibfolder + "\\drafts.xib","w")
            f.write(self.toaddr + "|" + self.ccaddr + "|" + self.bccaddr + "|" + self.subject + "|" + self.body + "|" + myattach + "<>")
            f.close()

    def addattachment(self):
        try:
            dialog = xbmcgui.Dialog()
            ret = dialog.browse(1, "Browse for attchment" , 'files')
            if ret:
                self.attachments.append([basename(ret),ret])
                self.getControl(81).addItem(basename(ret))
                if not self.attachlist: 
                    xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
                    self.getControl(81).setEnabled(True)
                self.attachlist = True
        except:traceback.print_exc()

    def getbel(self,filetype):
        if filetype in IMAGEFILETYPES:return "Image"
        elif filetype in AUDIOFILETYPES:return "Audio"
        elif filetype in VIDEOFILETYPES:return "Video"
        elif filetype in TEXTFILETYPES:return "Text"
        else:return "Unknown"

    def getsizelabel (self, size):
        if size >= 1024:
            size = size/1024.0
            sizeext = "KB"
            if size >= 1024:
                size = size/1024.0
                sizeext = "MB"
        else:sizeext = "bytes"
        return "%.1f %s" % (size,  sizeext)

    def showattach(self, pos):
        filetype = string.lower(string.split(self.attachments[pos][0], '.').pop())
        self.filebel = self.getbel(filetype)
        self.getControl(90).setLabel(self.language(267) + self.getsizelabel(getsize(self.attachments[pos][1])))
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
        
    def onAction( self, action ):
        if not self.animating:
            button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
            actionID   =  action.getId()
            try:focusid = self.getFocusId()
            except:focusid = 0
            try:control = self.getFocus()
            except: control = 0
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), "Confirm to close Compose Dialog"):
                    self.exitme()
            elif focusid == 81:
                try:
                    self.showattach(self.getControl(81).getSelectedPosition())
                except:traceback.print_exc()
               
    def onFocus(self, controlID):
        pass

    def exitme(self):
        self.animating = True
        if self.attachlist:
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
            time.sleep(0.8)
        xbmc.executebuiltin("Skin.SetBool(emaildialog)")
        xbmc.executebuiltin("Skin.ToggleSetting(emaildialog)")
        time.sleep(0.8)
        self.close()

    def showKeyboard(self, heading,default=""):
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return False
