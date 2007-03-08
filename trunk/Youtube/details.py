"""
 Copyright (c) 2007 Daniel Svensson, <dsvensson@gmail.com>

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

import os
import sys
import time
import traceback
import urllib2


import xbmc
import xbmcgui

import guibuilder

ACTION_PREVIOUS_MENU  = 10

class Details(xbmcgui.WindowDialog):
	"""Details Window Class."""

	def __init__(self, skin=None):
		try: 
			self.base_path = os.getcwd().replace(';','')

			if not self.load_skin(skin):
				self.close()
		except:
			xbmc.log('Exception (Details:init): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def load_skin(self, name=None):
		"""Loads the GUI skin."""

		if name is None:
			name = 'default'

		skin_path = os.path.join(self.base_path, 'skins', name)
		skin = os.path.join(skin_path, 'details.xml')

		self.img_path = os.path.join(skin_path, 'gfx')

		guibuilder.GUIBuilder(self, skin, self.img_path, 
		                      useDescAsKey=True, fastMethod=True)

		return self.SUCCEEDED

	def get_control(self, desc):
		"""Return the control that matches the widget description."""

		return self.controls[desc]['control']

	def display(self, details):
		"""Set the Details content and display."""

		if details.has_key('description'):
			ctrl = self.get_control('Description')
			ctrl.setText(details['description'])
		if details.has_key('thumbnail_url'):
			req = urllib2.Request(details['thumbnail_url'])
			fp = urllib2.urlopen(req)
			p = os.path.join(self.base_path, 'data', 'thumb.jpg')
			f = open(p, 'wb')
			f.write(fp.read())
			fp.close()
			f.close()
			ctrl = self.get_control('Video Thumbnail')
			ctrl.setImage(p)
		if details.has_key('title'):
			ctrl = self.get_control('Title Label')
			ctrl.setLabel(details['title'])
		if details.has_key('tags'):
			ctrl = self.get_control('Tags Text Label')
			ctrl.reset()
			ctrl.addLabel(details['tags'])
		if details.has_key('author'):
			ctrl = self.get_control('Author Text Label')
			ctrl.setLabel(details['author'])
		if details.has_key('length_seconds'):
			length = int(details['length_seconds'])
			lbl = '%d minutes, %d seconds' % (length / 60, length % 60)
			ctrl = self.get_control('Length Text Label')
			ctrl.setLabel(lbl)
		if details.has_key('rating_avg'):
			ctrl = self.get_control('Rating Text Label')
			ctrl.setLabel(details['rating_avg'])
		if details.has_key('upload_time'):
			unixtime = int(details['upload_time'])
			y, m, d, hour, min, sec, wd, yd, dst = time.gmtime(unixtime)
			lbl = '%d-%02d-%02d %02d:%02d' % (y, m, d, hour, min)
			ctrl = self.get_control('Added Text Label')
			ctrl.setLabel(lbl)

		self.doModal()

	def onControl(self, ctrl):
		"""Handle Details events."""

		try: 
			print ctrl, ctrl.getId()
		except:
			xbmc.log('Exception (Details:onControl): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()

	def onAction(self, action):
		"""Handle Details actions."""

		try: 
			if action == ACTION_PREVIOUS_MENU:
				self.close()
		except:
			xbmc.log('Exception (Details:onAction): ' + str(sys.exc_info()[0]))
			traceback.print_exc()
			self.close()


