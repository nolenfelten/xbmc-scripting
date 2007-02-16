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

from YouTube2 import YouTube2, YouTubeUrlOpener
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
	"""YouTube browser GUI."""

	# GUI States.
	STATE_MAIN = 1
	STATE_FEEDS = 2
	STATE_USERS = 4
	STATE_MOST_DISCUSSED = STATE_FEEDS | 8
	STATE_MOST_VIEWED = STATE_MOST_DISCUSSED | 16

	def __init__(self):
		"""Setup the default skin, state and load 'recently_featured' feed"""

		try: 
			if not self.load_skin('default'):
				self.close()

			self.data = []
			self.yt = YouTube2()
			self.state = YouTubeGUI.STATE_MAIN

			self.last_search_term = ''

			self.player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)

			self.get_feed('recently_featured')
		except:
			xbmc.log('Exception (init): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def load_skin(self, name=None):
		"""Loads the GUI skin."""

		if not name:
			name = 'default'

		skin_path = os.path.join(os.getcwd().replace(';',''), 'skins', name)
		skin = os.path.join(skin_path, 'skin.xml')

		self.img_path = os.path.join(skin_path, 'gfx')

		guibuilder.GUIBuilder(self, skin, self.img_path,
		                      useDescAsKey=True, debug=True)

		return self.SUCCEEDED

	def show_about(self):
		"""Show an 'About' dialog."""

		dlg = xbmcgui.Dialog()
		dlg.ok('About', 'By: Daniel Svensson, 2007',
		       'Paypal: dsvensson@gmail.com',
		       'Bugs: XBMC Forum - Python Script Development')

	def get_input(self, default, title):
		"""Show a virtual keyboard and return the entered text."""

		ret = None

		keyboard = xbmc.Keyboard(default, title)
		keyboard.doModal()

		if keyboard.isConfirmed():
			ret = keyboard.getText()

		return ret
	
	def not_implemented(self):
		"""Show a 'not implemented' dialog."""
		dlg = xbmcgui.Dialog()
		dlg.ok('YouTube', 'Not Implemented, check back later')

	def progress_handler(self, done, total, dlg):
		"""Update progress dialog percent and return abort status."""

		percent = int((done * 100.0) / total)

		dlg.update(percent)
		return not dlg.iscanceled()
	
	def error_handler(self, code, message, udata):
		"""Shows an error dialog with the HTTP error code and a message."""

		msg = '%d - %s' % (code, message)

		dlg = xbmcgui.Dialog()
		dlg.ok('YouTube', 'There was an error.', msg)

	def download_data(self, arg, func):
		"""Show a progress dialog while downloading and return the data."""

		dlg = xbmcgui.DialogProgress()
		dlg.create('YouTube', 'Downloading content')

		opener = YouTubeUrlOpener(self.error_handler, None,
		                          self.progress_handler, dlg)
		data = func(arg, opener)

		dlg.close()

		return data

	def get_feed(self, feed):
		"""Get rss data and update the list."""
		data = self.download_data(feed, self.yt.get_feed)
		self.update_list(data)
		
	def search(self):
		"""Get user input and perform a search. On success update the list."""

		term = self.get_input(self.last_search_term, 'Search')
		
		# Only update the list if the user entered something.
		if term != None:
			data = self.download_data(term, self.yt.search)
			self.update_list(data)
			self.last_search_term = term

	def update_list(self, data):
		"""Updates the list widget with new data."""

		# Either an error dialog has been shown, or the user
		# aborted the download. Anyway, there's no new data
		# to put in the list, so lets just keep the old.
		if data == None or len(data) == 0:
			return False

		self.data = data

		list = self.controls['Content List']['control']

		xbmcgui.lock()
		list.reset()
		for desc, id in self.data:
			item = xbmcgui.ListItem (label=desc)
			list.addItem(item)
		xbmcgui.unlock()

		return True

	def play_clip(self):
		"""Get the url to the selected list item and start playback."""

		list = self.controls['Content List']['control']

		pos = list.getSelectedPosition()

		try:
			desc, id = self.data[pos]
		except IndexError, e:
			# If this happens something is terribly wrong
			print 'Index out of bounds'
			self.close()
			return

		file = self.download_data(id, self.yt.parse_video)
		if file is not None:
			self.player.play(str(file))

	def onAction(self, action):
		"""Handle user input events."""

		try: 
			if action == ACTION_PREVIOUS_MENU:
				if self.state is YouTubeGUI.STATE_MAIN:
					self.close()
				elif self.state & ~YouTubeGUI.STATE_FEEDS & YouTubeGUI.STATE_MOST_DISCUSSED:
					self.set_button_state(YouTubeGUI.STATE_FEEDS)
				else:
					self.set_button_state(YouTubeGUI.STATE_MAIN)
		except:
			xbmc.log('Exception (onAction): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def onControl(self, ctrl):
		"""Handle widget events."""

		try: 
			if ctrl is self.controls['Content List']['control']:
				self.play_clip()
			elif self.state is YouTubeGUI.STATE_MAIN:
				self.on_control_main(ctrl)
			elif self.state is YouTubeGUI.STATE_FEEDS:
				self.on_control_feeds(ctrl)
			elif self.state is YouTubeGUI.STATE_MOST_VIEWED:
				self.on_control_most_viewed(ctrl)
			elif self.state is YouTubeGUI.STATE_MOST_DISCUSSED:
				self.on_control_most_discussed(ctrl)
		except:
			xbmc.log('Exception (onControl): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def on_control_main(self, ctrl):
		"""Handle main menu events."""

		if ctrl is self.controls['Feeds Button']['control']:
			self.set_button_state(YouTubeGUI.STATE_FEEDS)
		elif ctrl is self.controls['Search Button']['control']:
			self.search()
		elif ctrl is self.controls['About Button']['control']:
			self.show_about()
		else:
			self.not_implemented()

	def on_control_feeds(self, ctrl):
		"""Handle feeds menu events."""

		if ctrl is self.controls['Recently Added Button']['control']:
			self.get_feed('recently_added')
		elif ctrl is self.controls['Recently Featured Button']['control']:
			self.get_feed('recently_featured')
		elif ctrl is self.controls['Top Favorites Button']['control']:
			self.get_feed('top_favorites')
		elif ctrl is self.controls['Top Rated Button']['control']:
			self.get_feed('top_rated')
		elif ctrl is self.controls['Most Viewed Button']['control']:
			self.set_button_state(YouTubeGUI.STATE_MOST_VIEWED)
		elif ctrl is self.controls['Most Discussed Button']['control']:
			self.set_button_state(YouTubeGUI.STATE_MOST_DISCUSSED)

	def on_control_most_viewed(self, ctrl):
		"""Handle most viewed time frame events."""

		if ctrl is self.controls['Today Button']['control']:
			self.get_feed('top_viewed_today')
		elif ctrl is self.controls['This Week Button']['control']:
			self.get_feed('top_viewed_week')
		elif ctrl is self.controls['This Month Button']['control']:
			self.get_feed('top_viewed_month')
		elif ctrl is self.controls['All Time Button']['control']:
			self.get_feed('top_viewed')

	def on_control_most_discussed(self, ctrl):
		"""Handle most discussed time frame events."""

		if ctrl is self.controls['Today Button']['control']:
			self.get_feed('most_discussed_today')
		elif ctrl is self.controls['This Week Button']['control']:
			self.get_feed('most_discussed_week')
		elif ctrl is self.controls['This Month Button']['control']:
			self.get_feed('most_discussed_month')

	def set_button_state(self, state):
		"""Update button visibility, current state and focused widget."""

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

		# Are we in the most discussed menu?
		visible = bool(state & ~YouTubeGUI.STATE_FEEDS &
		               YouTubeGUI.STATE_MOST_DISCUSSED)

		self.controls['Today Button']['control'].setVisible(visible)
		self.controls['This Week Button']['control'].setVisible(visible)
		self.controls['This Month Button']['control'].setVisible(visible)

		if visible:
			dominant = self.controls['Today Button']['control']

		# Are we in the most viewed menu?
		visible = bool(state & ~YouTubeGUI.STATE_MOST_DISCUSSED &
		               YouTubeGUI.STATE_MOST_VIEWED)

		self.controls['All Time Button']['control'].setVisible(visible)


		# Set focus to the top-most relevant button, and move
		# to that when leaving the list.
		self.setFocus(dominant)
		self.controls['Content List']['control'].controlLeft(dominant)
		
		self.state = state

		xbmcgui.unlock()

yt = YouTubeGUI()
yt.doModal()
del yt 
