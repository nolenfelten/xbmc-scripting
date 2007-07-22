      ##########################
      #                        #                      
      #         XinBox         #         
      #     By Stanley87       #         
      #                        #
#######                        #######             
#                                    #
#                                    #
#A pop3 + SMTP email client for XBMC #
#                                    #
######################################
import sys, os, xbmc, time, xbmcgui

sys.path.append( os.path.join( sys.path[0], 'src', 'lib' ) )

import XinBox_MainMenu
from XinBox_Language import Language
import XinBox_Util

scriptpath = os.getcwd().replace(";","")+"\\"

lang = Language(XinBox_Util.__scriptname__)
lang.load(scriptpath + "//src//language")
_ = lang.string

if __name__ == '__main__':
        if xbmc.getCondVisibility('Skin.HasSetting(mmrunning)'):
                dialog = xbmcgui.DialogProgress()
                dialog.create(_(351), _(352))
                xbmc.executebuiltin("Skin.ToggleSetting(mmrunning)")
                while not xbmc.getCondVisibility('Skin.HasSetting(mmfinished)')and not xbmc.getCondVisibility('Skin.HasSetting(timerunning)'):time.sleep(0.1)
                dialog.update(100,_(352))
                dialog.close()
                try:
                        w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath+ "src","DefaultSkin",bforeFallback=False,minimode=sys.argv[1:][0],lang=_)
                except:w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath + "src","DefaultSkin",lang=_)
        else:w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath + "src","DefaultSkin",lang=_)
        w.doModal()
        del w

