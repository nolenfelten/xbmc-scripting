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

import youtube
import xbmcgui
import xbmc
import os
import sys
import traceback
import guibuilder
import pickle

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
	STATE_SEARCH = 32
	STATE_USERS = 64

	def __init__(self):
		"""Setup the default skin, state and load 'recently_featured' feed"""

		try: 
			self.base_path = os.getcwd().replace(';','')

			if not self.load_skin('default'):
				self.close()

			self.data = []
			self.yt = youtube.YouTube()
			self.state = YouTubeGUI.STATE_MAIN

			# Get the last search term
			history = self.get_search_history()
			if history is not None and len(history) > 0:
				self.last_search_term = history[0]
			else:
				self.last_search_term = ''

			self.player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)

			self.get_feed('recently_featured')
		except:
			xbmc.log('Exception (init): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def get_search_history(self):
		"""Return a list of old search terms."""

		list = []
		path = os.path.join(self.base_path, 'data', 'history.txt')

		try:
			f = open(path, 'rb')
			list = pickle.load(f)
			f.close()
		except IOError, e:
			print 'There was an error while loading the pickle (%s)' % e

		return list

	def add_search_history(self, term):
		"""Append a term, and trim the search history to max 50 entries."""

		list = self.get_search_history()
		list = filter(lambda x: x != term, list)
		list.insert(0, term)

		if len(list) > 50:
			list = list[:50]

		path = os.path.join(self.base_path, 'data', 'history.txt')
		try:
			f = open(path, 'wb')
			pickle.dump(list, f, protocol=pickle.HIGHEST_PROTOCOL)
			f.close()
		except IOError, e:
			print 'There was an error while saving the pickle (%s)' % e

	def load_skin(self, name=None):
		"""Loads the GUI skin."""

		if not name:
			name = 'default'

		skin_path = os.path.join(self.base_path, 'skins', name)
		skin = os.path.join(skin_path, 'skin.xml')

		self.img_path = os.path.join(skin_path, 'gfx')

		guibuilder.GUIBuilder(self, skin, self.img_path, title='YouTube',
		                      useDescAsKey=True, debug=True)

		return self.SUCCEEDED

	def show_about(self):
		"""Show an 'About' dialog."""

		dlg = xbmcgui.Dialog()
		dlg.ok('About', 'By: Daniel Svensson, 2007',
		       'Paypal: dsvensson@gmail.com',
		       'Bugs: XBMC Forum - Python Script Development')

	def get_control(self, desc):
		"""Return the control that matches the widget description."""

		return self.controls[desc]['control']

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
	
	def error_handler(self, message, udata):
		"""Shows an error dialog with the HTTP error code and a message."""

		dlg = xbmcgui.Dialog()
		dlg.ok('YouTube', 'There was an error.', message)

	def download_data(self, arg, func):
		"""Show a progress dialog while downloading and return the data."""

		dlg = xbmcgui.DialogProgress()
		dlg.create('YouTube', 'Downloading content')

		self.yt.set_error_hook(self.error_handler)
		self.yt.set_report_hook(self.progress_handler, dlg)

		data = func(arg)

		dlg.close()

		return data

	def get_user_videos(self, user=None):
		"""Get rss data and update the list."""

		if user is None:
			user = self.get_input('', 'User')
	
		data = self.download_data(user, self.yt.get_user_videos)
		if self.update_list(data):
			lbl = 'User: %s' % user
			self.get_control('Feed Label').setLabel(lbl)
	
	def get_feed(self, feed):
		"""Get rss data and update the list."""
		data = self.download_data(feed, self.yt.get_feed)
		if self.update_list(data):
			lbl = ' '.join(map(lambda x: x.capitalize(), feed.split('_')))
			self.get_control('Feed Label').setLabel(lbl)
		
	def search(self, term=None):
		"""Get user input and perform a search. On success update the list."""

		if term is None:
			term = self.get_input(self.last_search_term, 'Search')
		
		# Only update the list if the user entered something.
		if term != None:
			self.last_search_term = term
			data = self.download_data(term, self.yt.search)
			if self.update_list(data):
				lbl = 'Search: %s' % term
				self.get_control('Feed Label').setLabel(lbl)
				self.add_search_history(term)
			else:
				dlg = xbmcgui.Dialog()
				dlg.ok('YouTube', 'No videos were found that match your query.')

	def search_history(self):
		"""Get search history and update the list."""

		data = [(x,None) for x in self.get_search_history()]
		if self.update_list(data):
			self.get_control('Feed Label').setLabel('Search History')

	def update_list(self, data):
		"""Updates the list widget with new data."""

		# Either an error dialog has been shown, or the user
		# aborted the download. Anyway, there's no new data
		# to put in the list, so lets just keep the old.
		if data == None or len(data) == 0:
			return False

		self.data = data

		list = self.get_control('Content List')

		xbmcgui.lock()
		list.reset()
		for desc, id in self.data:
			item = xbmcgui.ListItem (label=desc)
			list.addItem(item)
		xbmcgui.unlock()

		return True

	def play_clip(self, id):
		"""Get the url for the id and start playback."""

		file = self.download_data(id, self.yt.get_video_url)
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
			if ctrl is self.get_control('Content List'):
				self.on_control_list(ctrl)
			elif self.state is YouTubeGUI.STATE_MAIN:
				self.on_control_main(ctrl)
			elif self.state is YouTubeGUI.STATE_SEARCH:
				self.on_control_search(ctrl)
			elif self.state is YouTubeGUI.STATE_USERS:
				self.on_control_users(ctrl)
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

	def on_control_list(self, ctrl):
		"""Handle content list events."""
		pos = ctrl.getSelectedPosition()

		try:
			desc, id = self.data[pos]
		except IndexError, e:
			# If this happens something is terribly wrong
			print 'Index out of bounds'
			self.close()
			return

		if id is not None:
			self.play_clip(id)
		else:
			self.search(desc)

	def on_control_main(self, ctrl):
		"""Handle main menu events."""

		if ctrl is self.get_control('Feeds Button'):
			self.set_button_state(YouTubeGUI.STATE_FEEDS)
		elif ctrl is self.get_control('Users Button'):
			self.set_button_state(YouTubeGUI.STATE_USERS)
		elif ctrl is self.get_control('Search Button'):
			self.set_button_state(YouTubeGUI.STATE_SEARCH)
		elif ctrl is self.get_control('About Button'):
			self.show_about()

	def on_control_search(self, ctrl):
		"""Handle search menu events."""
		if ctrl is self.get_control('Search Entry Button'):
			self.search()
		elif ctrl is self.get_control('Search History Button'):
			self.search_history()

	def on_control_users(self, ctrl):
		if ctrl is self.get_control('User Favorites Button'):
			self.not_implemented()
		elif ctrl is self.get_control('User Videos Button'):
			self.get_user_videos()
		elif ctrl is self.get_control('User Friends Button'):
			self.not_implemented()

	def on_control_feeds(self, ctrl):
		"""Handle feeds menu events."""

		if ctrl is self.get_control('Recently Added Button'):
			self.get_feed('recently_added')
		elif ctrl is self.get_control('Recently Featured Button'):
			self.get_feed('recently_featured')
		elif ctrl is self.get_control('Top Favorites Button'):
			self.get_feed('top_favorites')
		elif ctrl is self.get_control('Top Rated Button'):
			self.get_feed('top_rated')
		elif ctrl is self.get_control('Most Viewed Button'):
			self.set_button_state(YouTubeGUI.STATE_MOST_VIEWED)
		elif ctrl is self.get_control('Most Discussed Button'):
			self.set_button_state(YouTubeGUI.STATE_MOST_DISCUSSED)

	def on_control_most_viewed(self, ctrl):
		"""Handle most viewed time frame events."""

		if ctrl is self.get_control('Today Button'):
			self.get_feed('top_viewed_today')
		elif ctrl is self.get_control('This Week Button'):
			self.get_feed('top_viewed_week')
		elif ctrl is self.get_control('This Month Button'):
			self.get_feed('top_viewed_month')
		elif ctrl is self.get_control('All Time Button'):
			self.get_feed('top_viewed')

	def on_control_most_discussed(self, ctrl):
		"""Handle most discussed time frame events."""

		if ctrl is self.get_control('Today Button'):
			self.get_feed('most_discussed_today')
		elif ctrl is self.get_control('This Week Button'):
			self.get_feed('most_discussed_week')
		elif ctrl is self.get_control('This Month Button'):
			self.get_feed('most_discussed_month')

	def set_button_state(self, state):
		"""Update button visibility, current state and focused widget."""

		xbmcgui.lock()

		# Are we in the main menu?
		visible = bool(state & YouTubeGUI.STATE_MAIN)

		self.get_control('Feeds Button').setVisible(visible)
		self.get_control('Users Button').setVisible(visible)
		self.get_control('Search Button').setVisible(visible)
		self.get_control('About Button').setVisible(visible)

		if visible:
			dominant = self.get_control('Feeds Button')

		# Are we in the feeds menu?
		visible = bool(state & YouTubeGUI.STATE_FEEDS)

		self.get_control('Recently Added Button').setVisible(visible)
		self.get_control('Recently Featured Button').setVisible(visible)
		self.get_control('Top Favorites Button').setVisible(visible)
		self.get_control('Top Rated Button').setVisible(visible)
		self.get_control('Most Viewed Button').setVisible(visible)
		self.get_control('Most Discussed Button').setVisible(visible)

		if visible:
			dominant = self.get_control('Recently Added Button')

		# Are we in the most discussed menu?
		visible = bool(state & ~YouTubeGUI.STATE_FEEDS &
		               YouTubeGUI.STATE_MOST_DISCUSSED)

		self.get_control('Today Button').setVisible(visible)
		self.get_control('This Week Button').setVisible(visible)
		self.get_control('This Month Button').setVisible(visible)
		self.get_control('All Time Button').setVisible(visible)

		if visible:
			dominant = self.get_control('Today Button')

		# Are we in the most viewed menu?
		visible = bool(state & ~YouTubeGUI.STATE_MOST_DISCUSSED &
		               YouTubeGUI.STATE_MOST_VIEWED)

		self.get_control('All Time Button').setEnabled(visible)

		# Are we in the users menu?
		visible = bool(state & YouTubeGUI.STATE_USERS)

		self.get_control('User Favorites Button').setVisible(visible)
		self.get_control('User Videos Button').setVisible(visible)
		self.get_control('User Friends Button').setVisible(visible)

		if visible:
			dominant = self.get_control('User Favorites Button')

		# Are we in the search menu?
		visible = bool(state & YouTubeGUI.STATE_SEARCH)

		self.get_control('Search Entry Button').setVisible(visible)
		self.get_control('Search History Button').setVisible(visible)

		if visible:
			dominant = self.get_control('Search Entry Button')



		# Set focus to the top-most relevant button, and move
		# to that when leaving the list.
		self.setFocus(dominant)
		self.get_control('Content List').controlLeft(dominant)
		
		self.state = state

		xbmcgui.unlock()

yt = YouTubeGUI()
yt.doModal()
del yt 
