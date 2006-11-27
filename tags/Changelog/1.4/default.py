###XBMC Changelog script################################################
#Coded by SveinT (sveint@gmail.com)
# Updated by Killarny (killarny@gmail.com)
#
#Thanks to Modplug for the idea :)
#Thanks a lot to ChokeManiac for help and of course for his great skins!
#
#Last updated: 2006 August 13
########################################################################

import urllib, os, datetime
import xbmc, xbmcgui

# url for the raw changelog
CHANGELOG = 'http://xbmc.svn.sourceforge.net/viewvc/*checkout*/xbmc/trunk/XBMC/Changelog.txt'
# how many lines of changes to show
LISTRANGE = 100

def get_changes():
	# get the actual changelog.txt from sourceforge
	data = urllib.urlopen( CHANGELOG )
	data = data.read()

	# ignore the top 7 lines, as they contain nothing useful
	changes = data.split('\n')[7:]

	# search each line to determine if it has a hyphen as the second
	# character, meaning that it is a new change, and not a multiline
	# change
	changelog = []
	for each in changes:
		# ignore empty lines
		if not len( each ):
			continue
		if each[1] == '-':
			# add an extra hyphen at the beginning so that we can reliably
			# split the changes apart later
			each = '-' + each
		changelog += [ each ]
	changes = '\n'.join( changelog )

	# split by '- - ', ignoring the first item, as it will be the extra
	# junk at the top of the file
	changes = changes.split('- - ')[1:]
	changelog = []
	for each in changes:
		# wrap the date of the change in brackets to help highlight it
		each = '[%s] %s' % ( each.split(' ')[0], ' '.join( each.split(' ')[1:] ) )
		# add a hyphen to differentiate each change
		each = '- ' + each
		# convert tabs to 4 spaces
		each = each.replace( '\t', ' ' * 4 )
		# split each change by linefeed
		changelog += each.split('\n')[:-1]

	# join up to LISTRANGE items with a linefeed character
	changelog = '\n'.join( changelog[:LISTRANGE] )

	return changelog

class GUI( xbmcgui.Window ):
	def __init__( self ):

		self.dialogProgress = xbmcgui.DialogProgress()
		self.scaleX = float(self.getWidth())  / float(720)
		self.scaleY = float(self.getHeight()) / float(480)

		self.addControl(
			xbmcgui.ControlImage(
				0, 0, int( 720 * self.scaleX ), int( 480 * self.scaleY ), 
				os.path.join( os.getcwd()[:-1], 'changelog.png' ) 
			)
		)
		self.label = xbmcgui.ControlLabel(
			int( 420 * self.scaleX ), int( 70 * self.scaleY ), 
			250, 6, '', 'font12', '0xFFFFFFFF'
		)
		self.addControl( self.label )

		# If you want to use the normal PMIII bg uncomment the line below and 
		# comment out the line below that one for correct offset.

		# self.TextBox = xbmcgui.ControlTextBox(
		# 	int( 208 * self.scaleX ), int( 100 * self.scaleY ),
		#	int( 450 * self.scaleX ), int( 330 * self.scaleY )
		# )
		self.TextBox = xbmcgui.ControlTextBox(
			int( 60 * self.scaleX ), int( 100 * self.scaleY ),
			int( 595 * self.scaleX ), int( 340 * self.scaleY )
		)

		self.addControl( self.TextBox )

		self.dialogProgress.create( 'Downloading changelog', 'Please wait...' )
		try:
			change_text = get_changes()
		finally:
			self.dialogProgress.close()

		self.label.setLabel( datetime.datetime.now().strftime( '%Y %B %d, %H:%M' ) )

		self.TextBox.setText( change_text )
		self.setFocus( self.TextBox )

	def onAction( self, action ):
		if action == 10:
			self.close()


gui = GUI()
gui.doModal()
del gui