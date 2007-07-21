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

scriptpath = os.getcwd().replace(";","")+"\\"

if __name__ == '__main__':
        print "XinBox: Started"
        if xbmc.getCondVisibility('Skin.HasSetting(mmrunning)'):
                dialog = xbmcgui.DialogProgress()
                dialog.create("Please Wait", "Shutting down Mini-Mode")
                xbmc.executebuiltin("Skin.ToggleSetting(mmrunning)")
                while not xbmc.getCondVisibility('Skin.HasSetting(mmfinished)')and not xbmc.getCondVisibility('Skin.HasSetting(timerunning)'):time.sleep(0.1)
                dialog.update(100,"Shutting down Mini-Mode")
                dialog.close()
                w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath+ "src","DefaultSkin",bforeFallback=False,minimode=sys.argv[1:][0])
        else:w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",scriptpath + "src","DefaultSkin")
        w.doModal()
        del w
        print "XinBox: Closed"

