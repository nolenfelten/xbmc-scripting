import sys, os, xbmc

scriptpath = sys.path[0]
sys.path.append( os.path.join( sys.path[0], 'src', 'lib' ) )

import startup

__scriptsettings__ = "P:\\script_data\\"
__scriptpath__ = os.getcwd().replace(";","")+"\\"
__scriptname__ = 'XinBox'
__author__ = 'Stanley87'
__url__ = 'http://code.google.com/p/xbmc-scripting/'
__credits__ = 'XBMC TEAM, freenode/#xbmc-scripting'
__version__ = '1.0'

__credits_l1__ = 'Head Developer & Coder'
__credits_r1__ = 'Stanley87'
__credits_l2__ = 'Coder & Skinning'
__credits_r2__ = '?????'
__credits_l3__ = 'Graphics & Skinning'
__credits_r3__ = '???????'

__acredits_l1__ = 'Xbox Media Center'
__acredits_r1__ = 'Team XBMC'
__acredits_l3__ = 'Language Routine'
__acredits_r3__ = 'Rockstar & Donno'

class Logger:
	def write(data):
		xbmc.log(data)
	write = staticmethod(write)
sys.stdout = Logger
sys.stderr = Logger


if __name__ == '__main__':
   # try:
        s = startup
        s.main()
        del stu      
    #except:
    #    xbmc.log ("Startup failed")
