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
import urllib2
import re
import feedparser

from xml.sax.saxutils import unescape
from xml.sax.saxutils import escape

# http request timeout in seconds
timeout = 30
socket.setdefaulttimeout(timeout)

# TODO: Add support for browsing users, and perhaps even adding stuff to profile.
class YouTube2:
	DIR = 0
	VIDEO = 1

	# regexp for the youtube video session id
	session_pattern = re.compile('&t=([0-9a-zA-Z-_]{32})')

	# various urls
	stream_url = 'http://youtube.com/get_video?video_id=%s&t=%s'
	video_url = 'http://youtube.com/?v=%s'
	feed_url = 'http://youtube.com/rss/global/%s.rss'
	search_url = 'http://youtube.com/rss/search/%s.rss'

	def __init__(self):
		pass

	def get_feed(self, feed):
		url = YouTube2.feed_url % feed
		return self.parse_rss(url)
	
	def search(self, term):
		friendly_term = escape(term).replace(' ', '+')
		url = YouTube2.search_url % friendly_term
		return self.parse_rss(url)

	def parse_rss(self, url):
		list = []

		d = feedparser.parse(url)
		list = [(x.title, x.link[-11:]) for x in d.entries]

		return list
	
	def parse_video(self, id):
		url = YouTube2.video_url % id
		data = YouTube2.fetch_data(url)

		res = YouTube2.session_pattern.search(data)
		if res != None and len(res.groups()) == 1:
			session = res.group(1)
			return YouTube2.stream_url % (id, session)
		else:
			# TODO: Throw exception or something.
			print "ERROR!!!!!!!!"
			print data
			return None

	# TODO: Get rid of most of this crap.
	def fetch_data(url, func=None, udata=None):
		print "Fetching url: " + url
		req = urllib2.Request(unescape(url))

		try:
			s = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			print 'Unable to open url (%s)' % e
			return None

		data = ''
		
		# if content-length is known, pull data progressively
		# to be able to update the progressbar
		hdr = s.info()
		if hdr.has_key('Content-length'):
			len = int(hdr['Content-length'])
			chunk = max(50, int(len / 100.0))
			done = 0
			tmp = ''
			while len > done:
				try:
					tmp = s.read(chunk)
				except IOError, e:
					print 'Incremental download failed (%s)' % e
					data = None
					break

				data += tmp
				done += chunk

				# call the notifier function
				if func != None:
					pos = int((done / len) * 100.0)
					ret = func(pos, udata)
					# cancel transfer
					if ret != None and ret == True:
						data = None
						break

		else:
			try:
				data = s.read()
			except IOError, e:
				print 'One chunk download failed (%s)' % e

		if func != None:
			func(100, udata)

		s.close()

		return data
	fetch_data = staticmethod(fetch_data)

if __name__ == '__main__':
	yt = YouTube2()
	list = yt.parse_feed('top_viewed_week')
	for (desc, id) in list:
		print id, desc

	list = yt.parse_search('karate')
	for (desc, id) in list:
		print id, desc

	print yt.parse_video('S2n1_h3Bvt0')

