###XBMC Changelog script################################################
#Coded by SveinT (sveint@gmail.com)
# Updated by Killarny (killarny@gmail.com)
#
#Thanks to Modplug for the idea :)
#Thanks a lot to ChokeManiac for help and of course for his great skins!
#
#Last updated: 2006 August 13
########################################################################

import xbmcgui, xbmc
dialog = xbmcgui.DialogProgress()
dialog.create('XBMC Changelog')
dialog.update(5, 'Importing modules & initializing...')
import urllib
dialog.update(10)
import datetime
dialog.update(15)
import sys
dialog.update(20)
from os import path
dialog.update(25)

# url for the raw changelog
CHANGELOG = 'http://appliedcuriosity.cc/xbox/changelog.txt'
# how many lines of changes to show

sys.path.append(sys.path[0] +  '\\extras\\lib')
SkinPath			= sys.path[0] +  '\\extras\\skins\\'

def get_changes():
	# get the actual changelog.txt from sourceforge
	data = urllib.urlopen( CHANGELOG )
	data = data.read()

	# ignore the top 7 lines, as they contain nothing useful
	changes = data.split('\n')[8:]

	# search each line to determine if it has a hyphen as the second
	# character, meaning that it is a new change, and not a multiline
	# change
	changelog = []
	for each in changes:
		# ignore empty lines
		if not len( each ):
			continue
		changelog += [ each ]
	changes = '\n'.join( changelog )
	return changes

class windowOverlay( xbmcgui.Window ):
	def __init__( self ):
		dialog.update(50, 'Setting up GUI')
		import  guibuilder
		skin = xbmc.getSkinDir()
		if (not path.exists(SkinPath + skin + '\\skin.xml')): skin = 'Project Mayhem III'
		guibuilder.GUIBuilder(self, skinXML=SkinPath + skin + '\\skin.xml', fastMethod=True)
		if (not self.SUCCEEDED): 
			dialog.close()
			self.close()
		else: 
			dialog.update(75, 'Downloading changelog', 'Please wait...' )
			try:
				change_text = get_changes()
			finally:
				dialog.update(100)
				dialog.close()
			self.controls[200].setText( change_text )

	def onAction( self, action ):
		if action == 10: self.close()


MyDisplay = windowOverlay()
if (MyDisplay.SUCCEEDED): MyDisplay.doModal()
del MyDisplay