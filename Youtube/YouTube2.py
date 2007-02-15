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

# Custom url opener that handles user defined callbacks
# for error reporting and download progress.
class YouTubeUrlOpener(FancyURLopener):
	def __init__(self, errhook=None, errhook_udata=None,
	             rhook=None, rhook_udata=None):
		FancyURLopener.__init__(self)

		self.errhook = errhook
		self.errhook_udata = errhook_udata

		self.rhook = rhook
		self.rhook_udata = rhook_udata

	# Called on error.
	def http_error_default(self, url, fp, errcode, errmsg, headers):
		if self.errhook is not None:
			self.errhook(errcode, errmsg, self.errhook_udata)

	# Periodically called while downloading.
	def report_hook(self, count, blocksize, totalsize):
		if self.rhook is not None:
			done = min(count * blocksize, totalsize)
			keep_going = self.rhook(done, totalsize, self.rhook_udata)
			if keep_going is not None and not keep_going:
				raise StopIteration

	# Fetch an url and return the data.
	def fetch(self, url):
		ret = None
		info = None

		filename = os.path.join(os.getcwd().replace(';',''), 'download.tmp')

		try:
			info = self.retrieve(url, filename=filename, reporthook=self.report_hook)
		except AttributeError, e:
			# TODO: Investigate why this happens.
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


# TODO: Add support for browsing users, and perhaps even adding stuff to profile.
class YouTube2:
	DIR = 0
	VIDEO = 1

	# regexp for the youtube video session id.
	session_pattern = re.compile('&t=([0-9a-zA-Z-_]{32})')

	# various urls.
	stream_url = 'http://youtube.com/get_video?video_id=%s&t=%s'
	video_url = 'http://youtube.com/?v=%s'
	feed_url = 'http://youtube.com/rss/global/%s.rss'
	search_url = 'http://youtube.com/rss/search/%s.rss'

	def __init__(self):
		pass

	def get_feed(self, feed, opener):
		url = YouTube2.feed_url % feed
		return self.parse_rss(url, opener)
	
	def search(self, term, opener):
		friendly_term = escape(term).replace(' ', '+')
		url = YouTube2.search_url % friendly_term
		return self.parse_rss(url, opener)

	def parse_rss(self, url, opener):
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

