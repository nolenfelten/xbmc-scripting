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
        if exists("X:\\mmcomu.xib"):
                os.remove("X:\\mmcomu.xib")
                try:
                        w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath+ "src","DefaultSkin",bforeFallback=False,minimode=sys.argv[1:][0],lang=_)
                except:w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath + "src","DefaultSkin",lang=_)
        else:w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath + "src","DefaultSkin",lang=_)
        w.doModal()
        del w

