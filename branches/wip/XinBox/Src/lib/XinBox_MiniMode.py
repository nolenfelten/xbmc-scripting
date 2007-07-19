import time, sys, xbmc, xbmcgui, traceback
from XinBox_Settings import Settings
import XinBox_Util
from XinBox_EmailEngine import Email
from XinBox_Language import Language
import threading


TITLE = "XinBox"


class Minimode:
    def init(self):
        print "minimode starting"
        self.exit = False
        xbmc.executebuiltin("Skin.Reset(mmfinished)")
        xbmc.executebuiltin("Skin.Reset(mmrunning)")
        time.sleep(1)
        self.account = sys.argv[1:][0]
        self.srcpath = sys.argv[1:][1]
        self.loadsettings()
        self.inboxes = self.buildinboxdict()
        if not len(self.inboxes) == 0:self.startmm()
        print "minimode finished"
        xbmc.executebuiltin("Skin.ToggleSetting(mmfinished)")

    def startmm(self):
        while not xbmc.getCondVisibility('Skin.HasSetting(mmrunning)'):
            print "hmmm"
            for inbox in self.inboxes:
                self.currinbox = inbox
                inboxsettings = self.accountsettings.getSettingInListbyname("Inboxes",inbox)
                self.checkfornew(inboxsettings,inbox)
            time.sleep(int(self.accountsettings.getSetting("MiniMode Time")))
        return
        
    def buildinboxdict(self):
        inboxes = []
        for set in self.accountsettings.getSetting("Inboxes")[1]:
            if set[1].getSetting("Mini Mode Enabled") == "True":
                inboxes.append(set[0])
        return inboxes

    def loadsettings(self):
        self.settings = Settings("XinBox_Settings.xml",TITLE,"")
        self.accountsettings = self.settings.getSettingInListbyname("Accounts",self.account)

    def checkfornew(self, ibsettings, inbox):
        w = Email(ibsettings,inbox,self.account,False, True)
        w.checkemail()
        newlist = w.newlist
        del w
        if len(newlist) != 0:self.popup(newlist)

    def popup(self, newlist):
        mymessage = "Inbox: " + str(self.currinbox) + "\n" + str(len(newlist)) + " # new emails recieved"
        w = Popup("XinBox_Popup.xml",self.srcpath,"DefaultSkin",0,message = mymessage)
        w.doModal()
        del w


class Popup( xbmcgui.WindowXMLDialog ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,message=False):
        self.message = message
        self.control_action = XinBox_Util.setControllerAction()

    def onInit(self):
        xbmc.executebuiltin("Skin.Reset(showpopup)")
        self.getControl(21).setText(self.message)
        self.animating = True
        xbmc.executebuiltin("Skin.ToggleSetting(showpopup)")
        time.sleep(0.5)
        self.animating = False
        self.showing = True
        subThread = threading.Thread(target=self.SubthreadProc, args=())
        subThread.start()

    def SubthreadProc(self):
        time.sleep(8)
        if self.showing:
            self.animating = True
            xbmc.executebuiltin("Skin.Reset(showpopup)")
            time.sleep(0.5)
            self.animating = False
            self.close()

    def onClick(self, controlID):
        pass

    def onAction( self, action ):
        if not self.animating:
            button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
            actionID   =  action.getId()
            try:focusid = self.getFocusId()
            except:focusid = 0
            try:control = self.getFocus()
            except: control = 0
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.animating = True
                xbmc.executebuiltin("Skin.Reset(showpopup)")
                time.sleep(0.5)
                self.animating = False
                self.returnval = 0
                self.showing = False
                self.close()

    def onFocus(self, controlID):
        pass    

Minimode().init()
