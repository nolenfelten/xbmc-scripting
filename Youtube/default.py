# Copyright (c) 2007 Daniel Svensson
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from YouTube2 import YouTube2
import xbmcgui
import xbmc
import os
import sys
import traceback
import guibuilder

# Gamepad constans
ACTION_MOVE_LEFT      = 1  
ACTION_MOVE_RIGHT     = 2
ACTION_MOVE_UP        = 3
ACTION_MOVE_DOWN      = 4
ACTION_PAGE_UP        = 5 
ACTION_PAGE_DOWN      = 6
ACTION_SELECT_ITEM    = 7
ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR     = 9
ACTION_PREVIOUS_MENU  = 10
ACTION_SHOW_INFO      = 11
ACTION_PAUSE          = 12
ACTION_STOP           = 13
ACTION_NEXT_ITEM      = 14
ACTION_PREV_ITEM      = 15

class Logger:
	def write(data):
		xbmc.log(data)
	write = staticmethod(write)
sys.stdout = Logger
sys.stderr = Logger

class YouTubeGUI(xbmcgui.Window):

	# GUI States.
	STATE_MAIN = 1
	STATE_FEEDS = 2
	STATE_USERS = 4
	STATE_MOST_VIEWED = STATE_FEEDS | 8 
	STATE_MOST_DISCUSSED = STATE_FEEDS | 16

	def __init__(self):
		try: 
			if not self.load_skin('default'):
				self.close()

			self.data = []
			self.yt = YouTube2()
			self.state = YouTubeGUI.STATE_MAIN

			# TODO: Save this to file.
			self.last_search_term = ''

			self.player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)

			self.list_contents('recently_featured')
		except:
			xbmc.log('Exception (init): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	# Lodads the GUI skin.
	# TODO: Take resolution into account when choosing skin.
	def load_skin(self, name=None):
		if not name:
			name = 'default'

		skin_path = os.path.join(os.getcwd()[:-1], 'skins', name)
		skin = os.path.join(skin_path, 'skin.xml')

		self.img_path = os.path.join(skin_path, 'gfx')

		guibuilder.GUIBuilder(self, skin, self.img_path,
		                      useDescAsKey=True, debug=True)

		return self.SUCCEEDED

	# About dialog.
	# TODO: Make this not a dialog but a window with possibility
	#       to add contribution authors.
	def show_about(self):
		dlg = xbmcgui.Dialog()
		dlg.ok('About', 'By: Daniel Svensson, 2007',
		       'Paypal: dsvensson@gmail.com',
		       'Bugs: XBMC Forum - Python Script Development')
	
	# Just shows a 'not implemented' dialog.
	# TODO: Get rid of this one.
	def not_implemented(self):
		dlg = xbmcgui.Dialog()
		dlg.ok('YouTube', 'Not Implemented, check back later')

	# Fire up the virtual keyboard and gather some text to search for.
	# TODO: Add search history in some strange way
	#       perhaps add a STATE_SEARCH with a history
	#       button that fills the content list with
	#       old search terms.
	def search(self):
		term = self.get_input(self.last_search_term, 'Search')
		if term != None:
			self.list_contents(term, True)
			self.last_search_term = term

	# Collect text input from the virtual keyboard.
	def get_input(self, default, title):
		ret = None

		keyboard = xbmc.Keyboard(default, title)
		keyboard.doModal()

		if keyboard.isConfirmed():
			ret = keyboard.getText()

		return ret

	# Plays a clip based on some id ('Jb76RTQBWQc' for example).
	def play_clip(self):
		print "Trying to play clip"
		list = self.controls['Content List']['control']

		pos = list.getSelectedPosition()

		try:
			desc, id = self.data[pos]
		except IndexError, e:
			print 'Index out of bounds'
			# TODO: Show some error dialog.
			return

		file = self.yt.parse_video(id)
		if file == None:
			print 'Nothing to play'
			# TODO: Show some error dialog.
			return

		self.player.play(str(file))

	# Lists contents of some browsing result.
	# TODO: Do something prettier to search.
	#       Add progressbar for downloads.
	def list_contents(self, url, search=False):
		if search:
			self.data = self.yt.search(url)
		else:
			self.data = self.yt.get_feed(url)

		if self.data == None:
			# TODO: Show some error dialog.
			return

		list = self.controls['Content List']['control']

		xbmcgui.lock()
		list.reset()
		for desc, id in self.data:
			item = xbmcgui.ListItem (label=desc)
			list.addItem(item)
		xbmcgui.unlock()

	# Handle user input events.
	def onAction(self, action):
		try: 
			if action == ACTION_PREVIOUS_MENU:
				if self.state is YouTubeGUI.STATE_MAIN:
					self.close()
				else:
					self.set_button_state(YouTubeGUI.STATE_MAIN)
		except:
			xbmc.log('Exception (onAction): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	# Handle widget events.
	def onControl(self, ctrl):
		try: 
			if ctrl is self.controls['Content List']['control']:
				self.play_clip()
			elif self.state & YouTubeGUI.STATE_MAIN:
				self.on_control_main(ctrl)
			elif self.state & YouTubeGUI.STATE_FEEDS:
				self.on_control_feeds(ctrl)
		except:
			xbmc.log('Exception (onControl): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	# Main menu events.
	# TODO: Add support for Users view.
	def on_control_main(self, ctrl):
		if ctrl is self.controls['Feeds Button']['control']:
			self.set_button_state(YouTubeGUI.STATE_FEEDS)
		elif ctrl is self.controls['Search Button']['control']:
			self.search()
		elif ctrl is self.controls['About Button']['control']:
			self.show_about()
		else:
			self.not_implemented()

	# Feeds menu events.
	# TODO: Add support for Most Viewed, Most Discussed.
	def on_control_feeds(self, ctrl):
		if ctrl is self.controls['Recently Added Button']['control']:
			self.list_contents('recently_added')
		elif ctrl is self.controls['Recently Featured Button']['control']:
			self.list_contents('recently_featured')
		elif ctrl is self.controls['Top Favorites Button']['control']:
			self.list_contents('top_favorites')
		elif ctrl is self.controls['Top Rated Button']['control']:
			self.list_contents('top_rated')
		else:
			self.not_implemented()

	# Update what buttons are to be shown.
	# TODO: Add support for Most Viewed, Most Discussed.
	def set_button_state(self, state):
		xbmcgui.lock()

		# Are we in the main menu?
		visible = bool(state & YouTubeGUI.STATE_MAIN)

		self.controls['Feeds Button']['control'].setVisible(visible)
		self.controls['Users Button']['control'].setVisible(visible)
		self.controls['Search Button']['control'].setVisible(visible)
		self.controls['About Button']['control'].setVisible(visible)

		if visible:
			dominant = self.controls['Feeds Button']['control']

		# Are we in the feeds menu?
		visible = bool(state & YouTubeGUI.STATE_FEEDS)

		self.controls['Recently Added Button']['control'].setVisible(visible)
		self.controls['Recently Featured Button']['control'].setVisible(visible)
		self.controls['Top Favorites Button']['control'].setVisible(visible)
		self.controls['Top Rated Button']['control'].setVisible(visible)
		self.controls['Most Viewed Button']['control'].setVisible(visible)
		self.controls['Most Discussed Button']['control'].setVisible(visible)

		if visible:
			dominant = self.controls['Recently Added Button']['control']

		# Set focus to the top-most visible button, and move
		# to that when leaving the list.
		self.setFocus(dominant)
		self.controls['Content List']['control'].controlLeft(dominant)
		
		self.state = state

		xbmcgui.unlock()

yt = YouTubeGUI()
yt.doModal()
del yt 
