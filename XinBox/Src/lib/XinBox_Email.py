

import xbmc, xbmcgui, time, sys, os,email, traceback

import XinBox_Util
from sgmllib import SGMLParser  
TEMPFOLDER = "P:\\script_data\\XinBox\\"

class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,emailsetts=False,lang=False):
        self.language = lang
        self.emailsettings = emailsetts
        print "emsettings = " + str(self.emailsettings)
   
    def onInit(self):
        self.setupvars()
        self.setupcontrols()

        
    def setupvars(self):
        self.control_action = XinBox_Util.setControllerAction()
        self.attachlist = False
        xbmc.executebuiltin("Skin.SetBool(attachlistnotempty)")
        xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
        xbmc.executebuiltin("Skin.SetBool(emaildialog)")

    def setupcontrols(self):
        self.getControl(81).setEnabled(False)
        if self.emailsettings[2] == 0:
            self.getControl(64).setEnabled(False)
        else:self.getControl(64).setEnabled(True)
        self.getControl(73).addLabel(self.emailsettings[1].get('subject').replace("\n","") + "  " + self.language(260) + "   " + self.emailsettings[1].get('from').replace("\n",""))
        self.settextbox()
        self.getControl(74).addLabel(self.language(261) + self.emailsettings[4] + "-" + self.emailsettings[5])
        
    def getattachments(self):
        try:
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
                                self.attachments.append(filename)
                            except:pass
                    else:
                        filename = part.get_filename()
                        if filename != None:
                            try:
                                f=open(TEMPFOLDER + filename, "wb")
                                f.write(part.get_payload(decode=1))
                                f.close()
                                self.attachments.append(filename)
                            except:pass
            for attachment in self.attachments:
                self.getControl(81).addItem(attachment)        
        except:traceback.print_exc()
        
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
        if controlID == 64:
            self.attachlist = not self.attachlist
            xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")     
            
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            if self.attachlist:
                xbmc.executebuiltin("Skin.ToggleSetting(attachlistnotempty)")
                time.sleep(0.8)
            xbmc.executebuiltin("Skin.SetBool(emaildialog)")
            xbmc.executebuiltin("Skin.ToggleSetting(emaildialog)")
            time.sleep(0.8)
            self.close()
               
    def onFocus(self, controlID):
        pass 

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
