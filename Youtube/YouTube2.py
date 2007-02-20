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

import socket
import re
import feedparser
import os

from urllib import FancyURLopener

from xml.sax.saxutils import unescape
from xml.sax.saxutils import escape

# http request timeout in seconds.
timeout = 30
socket.setdefaulttimeout(timeout)

class YouTubeUrlOpener(FancyURLopener):
	"""
	Custom url opener that handles user defined callbacks
	for error reporting and download progress.
	"""

	def __init__(self, errhook=None, errhook_udata=None,
	             rhook=None, rhook_udata=None):
		FancyURLopener.__init__(self)

		self.errhook = errhook
		self.errhook_udata = errhook_udata

		self.rhook = rhook
		self.rhook_udata = rhook_udata

	def http_error_default(self, url, fp, errcode, errmsg, headers):
		"""Call the error hook if exists."""
		if self.errhook is not None:
			self.errhook(errcode, errmsg, self.errhook_udata)

	def report_hook(self, count, blocksize, totalsize):
		"""Call report hook if exists, and check for abort requests."""
		if self.rhook is not None:
			done = min(count * blocksize, totalsize)

			keep_going = self.rhook(done, totalsize, self.rhook_udata)
			if keep_going is not None and not keep_going:
				raise StopIteration

	def fetch(self, url):
		"""Fetch an url to a temp file and return the filename."""

		ret = None
		info = None

		filename = os.path.join(os.getcwd().replace(';',''), 'download.tmp')

		try:
			info = self.retrieve(url, filename=filename,
			                     reporthook=self.report_hook)
		except AttributeError, e:
			# <urlyhack>
			# This happens on http errors, but I don't think 
			# it should, so this is probably my fault.
			# </urlyhack>
			return None
		except StopIteration, e:
			# The users aborted the download.
			return None

		if info is not None:
			ret = info[0]

		return ret


class YouTube2:
	"""YouTube dataminer class."""

	DIR = 0
	VIDEO = 1

	# regexp for the youtube video session id.
	session_pattern = re.compile('&t=([0-9a-zA-Z-_]{32})')

	# various urls.
	stream_url = 'http://youtube.com/get_video?video_id=%s&t=%s'
	video_url = 'http://youtube.com/?v=%s'
	feed_url = 'http://youtube.com/rss/global/%s.rss'
	search_url = 'http://youtube.com/rss/search/%s.rss'

	user_url = 'http://www.youtube.com/rss/user/%s/videos.rss'

	def __init__(self):
		pass

	def get_user_videos(self, user, opener):
		"""Assemble user videos url and return a (desc, id) list."""

		url = YouTube2.user_url % user

		return self.parse_rss(url, opener)

	def get_feed(self, feed, opener):
		"""Assemble feed url and return a (desc, id) list."""

		url = YouTube2.feed_url % feed

		return self.parse_rss(url, opener)

	def search(self, term, opener):
		"""Assemble a search query and return a (desc, id) list."""

		friendly_term = escape(term).replace(' ', '+')
		url = YouTube2.search_url % friendly_term

		return self.parse_rss(url, opener)

	def parse_rss(self, url, opener):
		"""Fetch an url, strip invalid chars and return a (desc, id) list."""

		list = []

		filename = opener.fetch(url)
		d = feedparser.parse(filename)

		for entry in d.entries:
			# Dump exotic characters so we don't have to watch ugly boxes
			str = ''.join([x for x in entry.title if ord(x) < 256])
			if str != entry.title:
				if len(str) != 0:
					str = str + ' '
				str = str + '[invalid characters]'
			list.append((str, entry.link[-11:]))

		return list

	def parse_video(self, id, opener):
		"""Return a proper playback url for some YouTube id."""

		ret = None

		url = YouTube2.video_url % id

		filename = opener.fetch(url)
		if filename is not None:

			fd = open(filename)
			data = fd.read()
			fd.close()

			if data is not None:
				match = YouTube2.session_pattern.search(data)

				if match != None and len(match.groups()) == 1:
					session = match.group(1)
					ret = YouTube2.stream_url % (id, session)

		return ret


# Just for testing.
if __name__ == '__main__':
	yt = YouTube2()

	def progress_handler(done, total, dlg):
		t = int((done*100.0)/(total))
		print t

	def error_handler(code, message, udata):
		print '%d - %s' % (code, message)

	opener = YouTubeUrlOpener(errhook=error_handler, rhook=progress_handler)

	print "--------------------------------------"
	list = yt.get_feed('recently_featured', opener)
	for (desc, id) in list:
		print "%s %s" % (id, desc)

	print "--------------------------------------"
	list = yt.search('bejing', opener)
	for (desc, id) in list:
		print "%s %s" % (id, desc)

	print "--------------------------------------"
	print yt.parse_video('S2n1_h3Bvt0', opener)

	print "--------------------------------------"
	list = yt.get_user_videos('sneseglarn', opener)
	for (desc, id) in list:
		print "%s %s" % (id, desc)
