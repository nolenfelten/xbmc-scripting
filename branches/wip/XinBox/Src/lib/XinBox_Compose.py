

import xbmc, xbmcgui, time, sys, os, string, traceback
import XinBox_Util
import XinBox_Contacts
from os.path import join, exists, basename,getsize
import XinBox_InfoDialog
from XinBox_Settings import Settings

TEMPFOLDER = XinBox_Util.__tempdir__
ACCOUNTSDIR = XinBox_Util.__accountsdir__

class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,inboxsetts=False,lang=False,emailfromfile=False,inboxname=False,mydraft=False,ibfolder=False,account=False,setts=False):
        self.srcpath = strFallbackPath
        self.mydraft = mydraft
        self.ibfolder = ibfolder
        self.account = account
        self.inbox = inboxname
        self.language = lang
        self.settings = setts
        self.ibsettings = inboxsetts
        self.accountsettings = self.settings.getSettingInListbyname("Accounts",self.account)
        self.accountfolder = join(ACCOUNTSDIR,str(hash(self.account))) + "//"
   
    def onInit(self):
        self.setupvars()
        self.builddraftlist()
        self.setupcontrols()

    def builddraftlist(self):
        self.drafts  = []
        for set in self.accountsettings.getSetting("Drafts")[1]:
            self.drafts.append(set[0])


    def setupvars(self):
        xbmcgui.lock()
        xbmc.executebuiltin("Skin.Reset(attachlistnotempty)")
        xbmc.executebuiltin("Skin.Reset(emaildialog)")
        self.attachlist = False
        if self.mydraft[5] == None:self.attachments = []
        else:self.attachments = self.mydraft[5]
        self.body = self.mydraft[4]
        if self.body != "":
            for line in self.body.split("\n"):
                self.addItem(line)
        if self.getListSize() == 0:self.addItem("")
        else:
            if self.getListItem(0).getLabel() != "":self.addItem("",0)
        self.returnvalue = 0
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
        self.getControl(64).setLabel(self.language(64))
        self.getControl(82).addItem(self.mydraft[0])
        self.getControl(82).addItem(self.mydraft[1])
        self.getControl(82).addItem(self.mydraft[2])
        self.getControl(82).addItem(self.mydraft[3])
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
                    if kb != False:self.getControl(82).getSelectedItem().setLabel(kb)
                elif pos == 1:
                    kb = self.showKeyboard(self.language(323),self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:self.getControl(82).getSelectedItem().setLabel(kb)
                elif pos == 2:
                    kb = self.showKeyboard(self.language(324),self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:self.getControl(82).getSelectedItem().setLabel(kb)
                elif pos == 3:
                    kb = self.showKeyboard(self.language(325),self.getControl(82).getSelectedItem().getLabel())
                    if kb != False:self.getControl(82).getSelectedItem().setLabel(kb)           
            elif controlID == 61:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), self.language(332)):
                    self.buildemail()
            elif controlID == 62:
                self.addattachment()
            elif controlID == 63:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(self.language(77), self.language(334)):                
                    self.clearList()
                    self.addItem("")
            elif controlID == 64:
                value = self.showKeyboard(self.language(390),"")
                if value != False and value != "":
                    if (value in self.drafts):
                        dialog = xbmcgui.Dialog()
                        dialog.ok(self.language(93),self.language(391))
                    else:self.buildemail(True, value)
                        
    def savedraft(self, settings, value):
        draftfile = self.accountfolder + str(hash(value)) + ".draft"
        f = open(draftfile, "w")
        f.write(settings[4])
        f.close()
        attachments = []
        for setting in settings[5]:
            attachments.append(setting[1])
        DraftSettings = {
                            "To Addr": [settings[0],"text"],
                            "Cc Addr": [settings[1],"text"],
                            "Bcc Addr": [settings[2],"text"],
                            "Subject": [settings[3],"text"],
                            "Attachments": [attachments ,'simplelist'],
                            "Emailbodyhash": [str(hash(value)),"text"],}
        self.accountsettings.addSettingInList("Drafts",value,Settings("","XinBox",DraftSettings,2),"settings")
        self.settings.saveXMLfromArray()
        self.builddraftlist()
        dialog = xbmcgui.Dialog()
        dialog.ok(self.language(49),self.language(392))
        
                        
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

    def launchcontacts(self, label):
        w = XinBox_Contacts.GUI("XinBox_Contacts.xml",self.srcpath,"DefaultSkin",0,accountname=self.account,setts=self.settings,lang=self.language,thelabel=label)
        w.doModal()
        returnval = w.returnval
        del w
        if returnval != 0:
            if label != "":
                self.getControl(82).getSelectedItem().setLabel(label + "; " + returnval)
            else:self.getControl(82).getSelectedItem().setLabel(returnval)

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
            elif ( button_key == 'Keyboard TAB Button' or button_key == 'White Button'):
                if focusid == 82 and self.getControl(82).getSelectedPosition() != 3:
                    value = self.launchcontacts(self.getControl(82).getSelectedItem().getLabel())
                elif focusid == 50:
                    self.addItem("",self.getCurrentListPosition()+1)
                    self.setCurrentListPosition(self.getCurrentListPosition()+1)
            elif ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button'):
                if focusid == 50:
                    if self.getListSize() == 1:self.getListItem(self.getCurrentListPosition()).setLabel("")  
                    else:
                        self.removeItem(self.getCurrentListPosition())
                        self.setCurrentListPosition(self.getCurrentListPosition()-1)
                elif focusid == 82:
                    self.getControl(82).getSelectedItem().setLabel("")
                elif focusid == 81:
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
            elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title' ):
                if focusid == 82:
                    if self.getControl(82).getSelectedPosition() == 0:
                        self.launchinfo(147,self.language(310))
                    elif self.getControl(82).getSelectedPosition() == 1:
                        self.launchinfo(148,self.language(311))
                    elif self.getControl(82).getSelectedPosition() == 2:
                        self.launchinfo(149,self.language(312))
                    elif self.getControl(82).getSelectedPosition() == 3:
                        self.launchinfo(150,self.language(313))
                elif focusid == 50:
                    self.launchinfo(151,self.language(335))
                elif focusid == 61:
                    self.launchinfo(152,self.language(314))
                elif focusid == 62:
                    self.launchinfo(154,self.language(61))
                elif focusid == 63:
                    self.launchinfo(153,self.language(333))
                elif focusid == 81:
                    self.launchinfo(155,self.language(266))
            elif focusid == 81:
                self.showattach(self.getControl(81).getSelectedPosition())
               
    def onFocus(self, controlID):
        pass

    def buildemail(self, draft=False, name=False):
        dialog = xbmcgui.DialogProgress()
        dialog.create(self.language(210) + self.inbox, self.language(329))
        toadd = self.getControl(82).getListItem(0).getLabel()
        ccadd = self.getControl(82).getListItem(1).getLabel()
        bccadd = self.getControl(82).getListItem(2).getLabel()
        subject = self.getControl(82).getListItem(3).getLabel()
        body = ""
        for i in range(0,self.getListSize()):
            body = body + self.getListItem(i).getLabel() + "\n"
        dialog.close()
        if not draft:
            self.returnvalue = [toadd,ccadd,bccadd,subject,body,self.attachments]
            self.exitme()
        else:self.savedraft([toadd,ccadd,bccadd,subject,body,self.attachments], name)

    def exitme(self):
        self.animating = True
        if self.attachlist:
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
            time.sleep(0.9)
        xbmc.executebuiltin("Skin.Reset(emaildialog)")
        time.sleep(0.9)
        self.close()

    def showKeyboard(self, heading,default=""):
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return False

    def launchinfo(self, focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.srcpath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        del dialog
