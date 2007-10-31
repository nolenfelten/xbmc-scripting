import xbmc, xbmcgui, traceback
import sys, os, time, email
from sgmllib import SGMLParser

import XinBox_Util
 
class GUI( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,emailist=None,lang=None):
        self.emailist = emailist
        self.lang = lang
        self.control_action = XinBox_Util.setControllerAction()
        
    def onInit(self):
        xbmc.executebuiltin("Skin.Reset(mmemailpanel)")
        xbmc.executebuiltin("Skin.Reset(mmemail)")
        self.returnval = 0
        self.getControl(61).setLabel(self.lang(225))
        self.getControl(62).setLabel(self.lang(73))
        self.printEmail(self.emailist[0])
        for i, email in enumerate(self.emailist):
            self.addItem(self.lang(359) % str(i+1))
        self.animating = True
        xbmc.executebuiltin("Skin.ToggleSetting(mmemailpanel)")
        time.sleep(0.6)
        xbmc.executebuiltin("Skin.ToggleSetting(mmemail)")
        time.sleep(0.9)
        self.animating = False
        
    def onFocus(self, controlID):
        pass
    
    def onClick(self, controlID):
        if not self.animating:
            if controlID == 62:
                self.returnval = 1
                self.exitme()

    def exitme(self):
        self.animating = True
        xbmc.executebuiltin("Skin.ToggleSetting(mmemail)")
        time.sleep(0.9)
        xbmc.executebuiltin("Skin.ToggleSetting(mmemailpanel)")
        time.sleep(0.6)
        self.animating = False
        self.close()        
    
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
            elif focusid == 50:
                curpos = self.getCurrentListPosition()
                self.printEmail(self.emailist[curpos])

    def printEmail(self, selected):
        f = open(selected, "r")                
        myemail = email.message_from_string(f.read())
        f.close()
        self.getControl(73).reset()
        subject = self.parsesubject(myemail.get('subject'))
        myfrom = myemail.get('From').replace("\n","")
        self.getControl(73).addLabel(subject + "  " + self.lang(260) + "   " + myfrom)
        if myemail.is_multipart():
            for part in myemail.walk():
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    self.getControl(72).setText(self.parse_email(part.get_payload()))
                    break
        else:self.getControl(72).setText(self.parse_email(myemail.get_payload()))

    def parse_email(self, email):
        email = email.decode("quopri_codec")
        parser = html2txt()
        parser.reset()
        parser.feed(email)
        parser.close()
        return parser.output()

    def parsesubject(self, subject):
        subject = subject.replace("\n","")
        if subject == "":
            return self.language(255)
        else:return subject

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
