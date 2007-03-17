"""
 Copyright (c) 2007 Daniel Svensson

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

import xbmcgui
import xbmc
import os
import sys
import traceback

from xbmcutils.net import DownloadAbort, DownloadError

import xbmcutils.gui
import xbmcutils.guibuilder

from SVT import SVTMedia, ParseError

class Logger:
	def write(data):
		xbmc.log(data)
	write = staticmethod(write)
sys.stdout = Logger
sys.stderr = Logger

class SVTGui(xbmcgui.Window):
	def __init__(self):
		try:
			self.stack = []
			self.data = []

			self.base_path = os.getcwd().replace(';','')

			if not self.load_skin('default'):
				self.close()

			self.img_path = os.path.join(os.getcwd()[:-1], 'gfx')
			self.svt = SVTMedia()

			self.player = xbmc.Player(xbmc.PLAYER_CORE_MPLAYER)

			self.list_contents(self.svt.get_start_url())
		except:
			xbmc.log('Exception (init): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def get_control(self, desc):
		"""Return the control that matches the widget description."""

		return self.controls[desc]['control']

	def load_skin(self, name=None):
		"""Loads the GUI skin."""

		if not name:
			name = 'default'

		skin_path = os.path.join(self.base_path, 'skins', name)
		skin = os.path.join(skin_path, 'skin.xml')

		self.img_path = os.path.join(skin_path, 'gfx')

		xbmcutils.guibuilder.GUIBuilder(self, skin, self.img_path,
		                                useDescAsKey=True, fastMethod=True)

		return self.SUCCEEDED

	def show_about(self):
		dlg = xbmcgui.Dialog()
		dlg.ok('Om', 'Av: Daniel Svensson, 2007',
		       'Paypal: dsvensson@gmail.com',
		       'Felrapporter: XBMC Forum - Python Script Development')

	def list_contents(self, url):
		data = self.download_data(url, self.svt.parse_directory)
		if data is None:
			# Nothing to update.
			return False

		self.data = data

		self.stack.append(url)

		list = self.get_control('Content List')

		xbmcgui.lock()
		list.reset()
		for desc, url, type in self.data:
			item = xbmcgui.ListItem (label=desc)
			if type is SVTMedia.DIR:
				img = os.path.join(self.img_path, 'folder.png')
				item.setThumbnailImage(img)
			elif type is SVTMedia.VIDEO:
				img = os.path.join(self.img_path, 'video-x-generic.png')
				item.setThumbnailImage(img)
			list.addItem(item)
		xbmcgui.unlock()

		return True

	def play_clip(self, url):
		file = self.download_data(url, self.svt.parse_video)
		if file is not None:
			self.player.play(str(file[0]))

	def onControl(self, control):
		try: 
			if control is self.get_control('Content List'):
				list = self.get_control('Content List')
				pos = list.getSelectedPosition()
				desc, url, type = self.data[pos]
				if type is SVTMedia.DIR:
					self.list_contents(url)
				elif type is SVTMedia.VIDEO:
					self.play_clip(url)
			elif control is self.get_control('About Button'):
				self.show_about()
		except:
			xbmc.log('Exception (onControl): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()
	
	def onAction(self, action):
		try: 
			if action == xbmcutils.gui.ACTION_PREVIOUS_MENU:
				self.close()
			elif action == xbmcutils.gui.ACTION_PARENT_DIR and len(self.stack) > 1:
				cur = self.stack.pop()
				prev = self.stack.pop()
				if not self.list_contents(prev):
					# Still at the same ol' position.
					self.stack.append(prev)
					self.stack.append(cur)

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


