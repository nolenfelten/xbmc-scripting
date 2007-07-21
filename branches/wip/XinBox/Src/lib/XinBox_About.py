

import xbmc, xbmcgui, time, sys, os
import XinBox_Util



class GUI( xbmcgui.WindowXML ):
    def __init__(self,strXMLname, strFallbackPath,strDefaultName, lang=False):
        f = open(strFallbackPath + "//credits//about.txt")
        self.aboutcr = f.read()
        f.close()
        f = open(strFallbackPath + "//credits//language.txt")
        self.languagecr = f.read()
        f.close()
        f = open(strFallbackPath + "//credits//skinning.txt")
        self.skinningcr = f.read()
        f.close()
        self.lang = lang

    def onInit( self ):
        self.control_action = XinBox_Util.setControllerAction()
        self.setupcontrols()

    def setupcontrols( self ):
        self.getControl(61).setLabel(self.lang(360))
        self.getControl(62).setLabel(self.lang(361))
        self.getControl(63).setLabel(self.lang(362))
        self.getControl(64).addLabel(XinBox_Util.__url__)
        self.getControl(80).setLabel(self.lang(14))
        self.getControl(81).setLabel(XinBox_Util.__version__)
        self.getControl(72).setText(self.aboutcr)
        
    def onClick( self, controlId ):
        if controlId == 61:
            self.getControl(72).setText(self.aboutcr)
        elif controlId == 62:
            self.getControl(72).setText(self.languagecr)
        elif controlId == 63:
            self.getControl(72).setText(self.skinningcr)

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.close()
