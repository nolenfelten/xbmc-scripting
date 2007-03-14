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

import xbmcgui
import xbmc
import os
import sys
import traceback

from xbmcutils.net import DownloadAbort, DownloadError

from SVT import SVTMedia, ParseError

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

class SVTGui(xbmcgui.Window):
	def __init__(self):
		self.stack = []
		self.data = []

		self.img_path = os.path.join(os.getcwd()[:-1], 'gfx')
		self.svt = SVTMedia()

		self.player = xbmc.Player(xbmc.PLAYER_CORE_MPLAYER)

		xbmcgui.lock()

		# Background image
		img = os.path.join(self.img_path, 'background.png')
		widget = xbmcgui.ControlImage(0,0,720,576, img)
		self.addControl(widget)

		# Sveriges Television logo
		img = os.path.join(self.img_path, 'svt-fargstor.png')
		widget = xbmcgui.ControlImage(50,15,177,125, img)
		self.addControl(widget)

		# About button
		widget = xbmcgui.ControlButton(40, 113, 150, 30, 'Om')
		self.addControl(widget)
		self.about = widget

		# Content list
		widget = xbmcgui.ControlList(217, 113, 450, 435)
		widget.setImageDimensions(32, 32)
		self.addControl(widget)
		self.setFocus(widget)
		self.list = widget

		# Movement
		self.about.controlRight(self.list)
		self.list.controlLeft(self.about)

		xbmcgui.unlock()

		self.list_contents(self.svt.get_start_url())

	def show_about(self):
		dlg = xbmcgui.Dialog()
		dlg.ok('Om', 'Av: Daniel Svensson, 2007',
		       'Paypal: dsvensson@gmail.com',
		       'Felrapporter: XBMC Forum - Python Script Development')

	def list_contents(self, url):
		self.data = self.download_data(url, self.svt.parse_directory)
		if self.data != None:
			pass

		self.stack.append(url)

		xbmcgui.lock()
		self.list.reset()
		for desc, url, type in self.data:
			item = xbmcgui.ListItem (label=desc)
			if type is SVTMedia.DIR:
				img = os.path.join(self.img_path, 'folder.png')
				item.setThumbnailImage(img)
			elif type is SVTMedia.VIDEO:
				img = os.path.join(self.img_path, 'video-x-generic.png')
				item.setThumbnailImage(img)
			self.list.addItem(item)
		xbmcgui.unlock()

	def play_clip(self, url):
		file = self.download_data(url, self.svt.parse_video)
		if file == None:
			pass

		self.player.play(str(file[0]))

	def onControl(self, control):
		try: 
			if control == self.list:
				pos = self.list.getSelectedPosition()
				desc, url, type = self.data[pos]
				if type is SVTMedia.DIR:
					self.list_contents(url)
				elif type is SVTMedia.VIDEO:
					self.play_clip(url)
			elif control == self.about:
				self.show_about()
		except:
			xbmc.log('Exception (onControl): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()
	
	def onAction(self, action):
		try: 
			if action == ACTION_PREVIOUS_MENU:
				self.close()
			elif action == ACTION_PARENT_DIR and len(self.stack) > 1:
				url = self.stack.pop() # current
				url = self.stack.pop() # prev
				self.list_contents(url)
		except:
			xbmc.log('Exception (onAction): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def update_progress(self, done, size, dlg):
		msg = 'Hamtar data (%dkB)' % int(done / 1024)
		percent = min(int((done * 100.0) / size), size)
		dlg.update(percent, msg)

		return not dlg.iscanceled()
	
	def download_data(self, url, func):
		data = None

		dlg = xbmcgui.DialogProgress()
		dlg.create('Sveriges Television', 'Hamtar data')

		self.svt.set_report_hook(self.update_progress, dlg)

		try:
			data = func(url)
		except ParseError, e:
			err_dlg = xbmcgui.Dialog()
			err_dlg.ok('Sveriges Television', 'Kunde inte tolka data.')
		except DownloadError, e:
			err_dlg = xbmcgui.Dialog()
			err_dlg.ok('Sveriges Television', 'Kunde inte hamta data.')
		except DownloadAbort, e:
			pass

		dlg.close()

		return data

svt = SVTGui()
svt.doModal()
del svt


