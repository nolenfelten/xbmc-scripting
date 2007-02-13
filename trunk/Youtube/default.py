"""
	YouTube.Com Script for XBMC
	Using RSS Feed for the Data
	Remade by Daniel Svensson [dsvensson@gmail.com]

	Version: ##

	Permission is hereby granted, free of charge, to any person
	obtaining a copy of this software and associated documentation
	files (the "Software"), to deal in the Software without
	restriction, including without limitation the rights to use,
	copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the
	Software is furnished to do so, subject to the following
	conditions:
	
	The above copyright notice and this permission notice shall be
	included in all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
	EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
	OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
	NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
	HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
	WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
	FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
	OTHER DEALINGS IN THE SOFTWARE.
"""

from YouTube2 import YouTube2
import xbmcgui
import xbmc
import os
import sys
import traceback

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

# GUI States
STATE_MAIN = 0
STATE_FEEDS = 1
STATE_USERS = 2

class Logger:
	def write(data):
		xbmc.log(data)
	write = staticmethod(write)
sys.stdout = Logger
sys.stderr = Logger

class YouTubeMain(xbmcgui.Window):
	def __init__(self):
		self.data = []
		self.state = STATE_MAIN
		self.button_list = []

		self.img_path = os.path.join(os.getcwd()[:-1], 'gfx')
		self.yt = YouTube2()

		self.player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)

		xbmcgui.lock()

		# Background image
		img = os.path.join(self.img_path, 'background.png')
		widget = xbmcgui.ControlImage(0, 0, 720, 576, img)
		self.addControl(widget)

		# YouTube logo
		img = os.path.join(self.img_path, 'youtube.png')
		widget = xbmcgui.ControlImage(40, 25, 200, 80, img)
		self.addControl(widget)

		# Content list
		self.list = xbmcgui.ControlList(217, 113, 450, 435)
		self.list.setImageDimensions(32, 32)
		self.addControl(self.list)
		self.setFocus(self.list)

		# Populate buttons
		self.create_buttons()

		# Show main buttons
		self.show_main_buttons()

		# List movement
		self.list.controlLeft(self.feeds)

		xbmcgui.unlock()

		self.list_contents('recently_featured')

	def show_main_buttons(self):
		xbmcgui.lock()

		map(lambda x: x.setVisible(False), self.button_list)

		self.feeds.setVisible(True)
		self.users.setVisible(True)
		self.search.setVisible(True)
		self.about.setVisible(True)

		self.setFocus(self.feeds)
		self.list.controlLeft(self.feeds)

		self.state = STATE_MAIN

		xbmcgui.unlock()

	def show_feed_buttons(self):
		xbmcgui.lock()

		map(lambda x: x.setVisible(False), self.button_list)

		self.recently_added.setVisible(True)
		self.recently_featured.setVisible(True)
		self.top_favorites.setVisible(True)
		self.top_rated.setVisible(True)
		self.most_viewed.setVisible(True)
		self.most_discussed.setVisible(True)

		self.setFocus(self.recently_added)
		self.list.controlLeft(self.recently_added)

		self.state = STATE_FEEDS

		xbmcgui.unlock()

	def create_button(self, x, y, w, h, title):
		btn = xbmcgui.ControlButton(x, y, w, h, title)
		btn.setVisible(False)
		self.addControl(btn)
		self.button_list.append(btn)
		return btn

	def create_buttons(self):
		# Main buttons
		self.feeds  = self.create_button(40, 115, 150, 30, 'Feeds')
		self.users  = self.create_button(40, 145, 150, 30, 'Users')
		self.search = self.create_button(40, 175, 150, 30, 'Search')
		self.about  = self.create_button(40, 205, 150, 30, 'About')

		# Main movements
		self.feeds.controlRight(self.list)
		self.feeds.controlUp(self.about)
		self.feeds.controlDown(self.users)

		self.users.controlRight(self.list)
		self.users.controlUp(self.feeds)
		self.users.controlDown(self.search)

		self.search.controlRight(self.list)
		self.search.controlUp(self.users)
		self.search.controlDown(self.about)

		self.about.controlRight(self.list)
		self.about.controlUp(self.search)
		self.about.controlDown(self.feeds)

		# Feed buttons
		self.recently_added    = self.create_button(40, 115, 150, 30, 'Recently Added')
		self.recently_featured = self.create_button(40, 145, 150, 30, 'Recently Featured')
		self.top_favorites     = self.create_button(40, 175, 150, 30, 'Top Favorites')
		self.top_rated         = self.create_button(40, 205, 150, 30, 'Top Rated')
		self.most_viewed       = self.create_button(40, 235, 150, 30, 'Most Viewed')
		self.most_discussed    = self.create_button(40, 265, 150, 30, 'Most Discussed')
 
		# Feed movements
		self.recently_added.controlRight(self.list)
		self.recently_added.controlUp(self.most_discussed)
		self.recently_added.controlDown(self.recently_featured)

		self.recently_featured.controlRight(self.list)
		self.recently_featured.controlUp(self.recently_added)
		self.recently_featured.controlDown(self.top_favorites)

		self.top_favorites.controlRight(self.list)
		self.top_favorites.controlUp(self.recently_featured)
		self.top_favorites.controlDown(self.top_rated)

		self.top_rated.controlRight(self.list)
		self.top_rated.controlUp(self.top_favorites)
		self.top_rated.controlDown(self.most_viewed)

		self.most_viewed.controlRight(self.list)
		self.most_viewed.controlUp(self.top_rated)
		self.most_viewed.controlDown(self.most_discussed)

		self.most_discussed.controlRight(self.list)
		self.most_discussed.controlUp(self.most_viewed)
		self.most_discussed.controlDown(self.recently_added)

		# Current selected button
		self.current = self.feeds

	def show_about(self):
		dlg = xbmcgui.Dialog()
		dlg.ok('About', 'By: Daniel Svensson, 2007',
		       'Paypal: dsvensson@gmail.com',
		       'Bugs: XBMC Forum - Python Script Development')
	
	# TODO: merge with search_term
	def list_contents(self, url):
		self.data = self.download_data(url, self.yt.parse_feed)
		if self.data == None:
			return

		xbmcgui.lock()
		self.list.reset()
		for desc, id in self.data:
			item = xbmcgui.ListItem (label=desc)
			img = os.path.join(self.img_path, 'video-x-generic.png')
			item.setIconImage(img)
			self.list.addItem(item)
		xbmcgui.unlock()

	# TODO: merge with list_contents
	def search_term(self, url):
		self.data = self.download_data(url, self.yt.parse_search)
		if self.data == None:
			return

		xbmcgui.lock()
		self.list.reset()
		for desc, id in self.data:
			item = xbmcgui.ListItem (label=desc)
			img = os.path.join(self.img_path, 'video-x-generic.png')
			item.setIconImage(img)
			self.list.addItem(item)
		xbmcgui.unlock()

	def play_clip(self, url):
		file = self.download_data(url, self.yt.parse_video)
		if file == None:
			pass

		self.player.play(str(file))

	def on_control_main(self, control):
		if control == self.feeds:
			self.show_feed_buttons()
		elif control == self.search:
			term = self.get_input('Search')
			if term != None:
				self.search_term(term)
		elif control == self.about:
			self.show_about()
		else:
			self.not_implemented()

	def on_control_feeds(self, control):
		if control == self.recently_added:
			self.list_contents('recently_added')
		elif control == self.recently_featured:
			self.list_contents('recently_featured')
		elif control == self.top_favorites:
			self.list_contents('top_favorites')
		elif control == self.top_rated:
			self.list_contents('top_rated')
		else:
			self.not_implemented()

	def onControl(self, control):
		try: 
			if control == self.list:
				pos = self.list.getSelectedPosition()
				desc, id = self.data[pos]
				self.play_clip(id)
			elif self.state == STATE_MAIN:
				self.on_control_main(control)
			elif self.state == STATE_FEEDS:
				self.on_control_feeds(control)
		except:
			xbmc.log('Exception (onControl): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()
	
	def onAction(self, action):
		try: 
			if action == ACTION_PREVIOUS_MENU:
				if self.state == STATE_MAIN:
					self.close()
				else:
					self.show_main_buttons()
		except:
			xbmc.log('Exception (onAction): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def get_input(self, title):
		keyboard = xbmc.Keyboard('', title)
		keyboard.doModal()
		if keyboard.isConfirmed():
			return keyboard.getText()
		else:
			return None

	def update_progress(val, dlg):
		dlg.update(val)
		return dlg.iscanceled()
	update_progress = staticmethod(update_progress)
	
	def download_data(self, url, func):
		data = func(url)
		if data == None:
			dlg = xbmcgui.Dialog()
			dlg.ok('Sveriges Television', 'Kunde inte tolka data')
			self.close()
			return None

		return data
	
	def not_implemented(self):
		dlg = xbmcgui.Dialog()
		dlg.ok('YouTube', 'Not Implemented, check back later')

try:
	yt = YouTubeMain()
	yt.doModal()
	del yt 
except:
	xbmc.log('Exception (onAction): ' + str(sys.exc_info()[0]))
	traceback.print_exc()
