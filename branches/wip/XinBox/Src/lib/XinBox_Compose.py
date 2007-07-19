

import xbmc, xbmcgui, time, sys, os, string, traceback
import XinBox_Util
from os.path import join, exists, basename,getsize
TEMPFOLDER = "P:\\script_data\\XinBox\\Temp\\"
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
        xbmc.executebuiltin("Skin.Reset(attachlistnotempty)")
        xbmc.executebuiltin("Skin.Reset(emaildialog)")
        self.attachlist = False
        if self.mydraft[5] == None:self.attachments = []
        else:self.attachments = self.mydraft[5]
        self.body = self.mydraft[4]
        self.addItem("")
        if self.body != "":
            for line in self.body.split("\n"):
                self.addItem(line)
            if self.getListSize() == 0:self.addItem("")
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
        self.getControl(61).setLabel(self.language(314))
        self.getControl(62).setLabel(self.language(61))
        self.getControl(63).setLabel(self.language(333))
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
            xbmcgui.unlock()
            xbmc.executebuiltin("Skin.ToggleSetting(emaildialog)")
            time.sleep(1.2)
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
            time.sleep(0.8)
            self.animating = False
        else:
            self.animating = True
            xbmcgui.unlock()
            xbmc.executebuiltin("Skin.ToggleSetting(emaildialog)")
            time.sleep(0.8)
            self.animating = False            
            self.getControl(81).setEnabled(False)
        self.setFocusId(82)
        
    def onClick(self, controlID):
        if not self.animating:
            if controlID == 50:
                kb = self.showKeyboard(self.language(321) + " " +str(self.getCurrentListPosition()+1),self.getListItem(self.getCurrentListPosition()).getLabel())
                if kb != False:
                    self.getListItem(self.getCurrentListPosition()).setLabel(kb)
                    self.addItem("",self.getCurrentListPosition()+1)
                    self.setCurrentListPosition(self.getCurrentListPosition()+1)
            elif controlID == 82:
                pos = self.getControl(82).getSelectedPosition()
                if pos == 0:
                    kb = self.showKeyboard(self.language(322),self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:
                        self.toaddr = kb
                        self.getControl(82).getSelectedItem().setLabel(kb)
                elif pos == 1:
                    kb = self.showKeyboard(self.language(323),self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:
                        self.ccaddr = kb
                        self.getControl(82).getSelectedItem().setLabel(kb)
                elif pos == 2:
                    kb = self.showKeyboard(self.language(324),self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:
                        self.bccaddr = kb
                        self.getControl(82).getSelectedItem().setLabel(kb)
                elif pos == 3:
                    kb = self.showKeyboard(self.language(325),self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:
                        self.subject = kb
                        self.getControl(82).getSelectedItem().setLabel(kb)           
            elif controlID == 61:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), self.language(332)):
                    self.buildemail()
                    self.returnvalue = [self.toaddr,self.ccaddr,self.bccaddr,self.subject,self.body,self.attachments]
                    self.exitme()
            elif controlID == 62:
                self.addattachment()
            elif controlID == 63:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), self.language(334)):                
                    self.clearList()
                    self.addItem("")
            elif controlID == 81:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), self.language(326)):
                    self.attachments.pop(self.getControl(81).getSelectedPosition())
                    self.getControl(81).reset()
                    if len(self.attachments) == 0:
                        self.animating = True
                        xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
                        time.sleep(0.9)
                        self.animating = False
                        self.getControl(80).setImage("XBXinBoXLogo.png")
                        self.getControl(90).setLabel("")
                        self.attachlist = False
                        self.getControl(81).setEnabled(False)
                        self.setFocusId(62)
                    else:
                        for attach in self.attachments:
                            self.getControl(81).addItem(attach[0])
                        self.showattach(self.getControl(81).getSelectedPosition())
                        
    def addattachment(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.browse(1, self.language(327) , 'files')
        if ret:
            self.attachments.append([basename(ret),ret,getsize(ret)])
            self.getControl(81).addItem(basename(ret))
            if not self.attachlist: 
                xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
                self.getControl(81).setEnabled(True)
            self.attachlist = True


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
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), self.language(328)):
                    self.exitme()
                    #need to change below to propper controls for B button
            elif ( button_key == 'Keyboard Menu Button' or button_key == 'B Button'):
                if focusid == 50:
                    self.addItem("",self.getCurrentListPosition()+1)
                    self.setCurrentListPosition(self.getCurrentListPosition()+1)
            elif ( button_key == 'Keyboard Backspace Button' or button_key == 'Black Button'):
                if focusid == 50:
                    if self.getListSize() == 1:self.getListItem(self.getCurrentListPosition()).setLabel("")  
                    else:
                        self.removeItem(self.getCurrentListPosition())
                        self.setCurrentListPosition(self.getCurrentListPosition()-1)
            elif focusid == 81:
                self.showattach(self.getControl(81).getSelectedPosition())
               
    def onFocus(self, controlID):
        pass

    def buildemail(self):
        dialog = xbmcgui.DialogProgress()
        dialog.create(self.language(210) + self.inbox, self.language(329))
        self.body = ""
        for i in range(0,self.getListSize()):
            self.body = self.body + self.getListItem(i).getLabel() + "\n"
        dialog.close()

    def removefiles(self,mydir):
        for root, dirs, files in os.walk(mydir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

    def exitme(self):
        self.animating = True
        if self.attachlist:
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
            time.sleep(0.9)
        xbmc.executebuiltin("Skin.Reset(emaildialog)")
        time.sleep(0.9)
        if self.returnvalue == 0:
            if len(self.attachments) != 0:self.removefiles(TEMPFOLDER)
        self.close()

    def showKeyboard(self, heading,default=""):
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return False
