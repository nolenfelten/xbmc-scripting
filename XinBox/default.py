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
import sys, os, xbmc

scriptpath = sys.path[0]
sys.path.append( os.path.join( sys.path[0], 'src', 'lib' ) )

import XinBox_MainMenu

__scriptsettings__ = "P:\\script_data\\"
__scriptpath__ = os.getcwd().replace(";","")+"\\"
__scriptname__ = 'XinBox'
__author__ = 'Stanley87'
__url__ = 'http://xbmc-scripting.googlecode.com/svn/branches/wip/XinBox/'
__credits__ = 'XBMC TEAM, freenode/#xbmc-scripting'
__version__ = 'V.1.0'

__credits_l1__ = 'Head Developer & Coder'
__credits_r1__ = 'Stanley87'
__credits_l2__ = 'Coder & Skinning'
__credits_r2__ = 'YOUR NAME HERE?'
__credits_l3__ = 'Code Template'
__credits_r3__ = 'The AMT Team'

__acredits_l1__ = 'Xbox Media Center'
__acredits_r1__ = 'Team XBMC'
__acredits_l3__ = 'Language Routine'
__acredits_r3__ = 'Rockstar & Donno'

if __name__ == '__main__':
        w = XinBox_MainMenu.GUI("XinBox_MainMenu.xml",__scriptpath__ + "src","DefaultSkin")
        w.doModal()
        del w   
