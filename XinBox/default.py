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
from os.path import join, exists
sys.path.append( os.path.join( sys.path[0], 'src', 'lib' ) )

import XinBox_MainMenu
from XinBox_Language import Language
import XinBox_Util
import threading

scriptpath = os.getcwd().replace(";","")+"\\"

lang = Language(XinBox_Util.__scriptname__)
lang.load(scriptpath + "\\src\\language")
_ = lang.string


if __name__ == '__main__':
        if exists("Q://mmrunning.xib"):
                dialog = xbmcgui.DialogProgress()
                dialog.create(_(351), _(352))
                if exists("Q://mmcomu.xib"):
                        os.remove("Q:\\mmcomu.xib")
                while exists("Q://mmrunning.xib"):time.sleep(0.1)
                dialog.update(100,_(352))
                dialog.close()
                try:
                        w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath+ "src","DefaultSkin",bforeFallback=False,minimode=sys.argv[1:][0],lang=_)
                except:w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath + "src","DefaultSkin",lang=_)
        else:w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath + "src","DefaultSkin",lang=_)
        w.doModal()
        del w

