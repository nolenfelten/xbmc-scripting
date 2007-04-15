 
import xbmcgui, language, time, xib_util
lang = language.Language().string

        
class Settings( xbmcgui.WindowXML ):        
    def onInit(self):
        self.control_action = xib_util.setControllerAction()
        self.getmycontrols()
        self.getSettings()
        self.sortsettings()
        for item in self.listitems:
            self.addItem(xbmcgui.ListItem(item))
        xbmcgui.unlock()

    def getmycontrols(self):
        self.labelist = self.getControl(60)
        for i in range (0,9):
            self.labelist.addItem(lang(88+i))
        
    def sortsettings(self):
        self.listitems = []
        self.server1 = self.settings.server1
        self.user1 = self.settings.user1
        self.pass1 = self.settings.pass1
        self.ssl1 = self.settings.ssl1
        self.server2 = self.settings.server2
        self.user2 = self.settings.user2
        self.pass2 = self.settings.pass2
        self.ssl2 = self.settings.ssl2
        self.mpenable = self.settings.mpenable
        self.mp = self.settings.mp
        if self.server1 == "-":
            self.listitems.append(lang(81))
        else:
            self.listitems.append(str(self.server1))
        if self.user1 == "-":
            self.listitems.append(lang(82))
        else:
            self.listitems.append(str(self.user1))
        if self.pass1 == "-":
            self.listitems.append(lang(83))
        else:
            self.listitems.append(str(self.pass1))
        if self.ssl1 == "-":
            self.listitems.append(lang(84))
        else:
            self.listitems.append(str(self.ssl1))
        if self.server2 == "-":
            self.listitems.append(lang(85))
        else:
            self.listitems.append(str(self.server2))
        if self.user2 == "-":
            self.listitems.append(lang(86))
        else:
            self.listitems.append(str(self.user2))
        if self.pass2 == "-":
            self.listitems.append(lang(87))
        else:
            self.listitems.append(str(self.pass2))
        if self.ssl2 == "-":
            self.listitems.append(lang(88))
        else:
            self.listitems.append(str(self.ssl2))        
            
    def onClick(self, controlID):
        if ( controlID == 99):
            self.close()
                
    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.close()

    def onFocus(self, controlID):
        print 'The control with id="5" just got focus'   

    def getSettings( self ):
        self.settings = xib_util.Settings()
