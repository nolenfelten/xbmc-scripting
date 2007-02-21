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

import urllib2
import elementtree.ElementTree
import re

from xml.sax.saxutils import unescape
from xml.sax.saxutils import escape

class YouTube:
	"""YouTube dataminer class."""

	categories = {1:'Arts & Animation',
	              2:'Autos & Vehicles',
	              23:'Comedy',
	              24:'Entertainment',
	              10:'Music',
	              25:'News & Blogs',
	              22:'People',
	              15:'Pets & Animals',
	              26:'Science & Technology',
	              17:'Sports',
	              19:'Travel & Places',
	              20:'Video Games'}

	def __init__(self):
		# regexp for the youtube video session id.
		self.session_pattern = re.compile('&t=([0-9a-zA-Z-_]{32})')

		# various urls
		self.api_url = 'http://www.youtube.com/api2_rest?method=%s&dev_id=k1jPjdICyu0&%s'
		self.feed_url = 'http://youtube.com/rss/global/%s.rss'
		self.stream_url = 'http://youtube.com/get_video?video_id=%s&t=%s'
		self.video_url = 'http://youtube.com/?v=%s'
		self.search_url = 'http://youtube.com/rss/search/%s.rss'
		self.user_url = 'http://www.youtube.com/rss/user/%s/videos.rss'

		# should exotic characters be stripped?
		self.strip_chars = True

	def strip_exotic_chars(self, str):
		# Dump exotic characters so we don't have to watch ugly boxes
		stripped = ''.join([c for c in str if ord(c) < 256])
		if stripped != str:
			if len(stripped) != 0:
				stripped = stripped + ' '
			str = stripped + '[invalid characters]'
		return str

	def get_rss(self, url):
		data = self.retrieve(url)
		tree = elementtree.ElementTree.XML(data)

		list = []
		for node in tree.findall('channel/item'):
			title = node.find('title').text
			if self.strip_chars:
				title = self.strip_exotic_chars(title)
			id = node.find('link').text[-11:]
			list.append((title, id))

		return list

	def get_user_videos(self, user):
		"""Assemble user videos url and return a (desc, id) list."""

		url = self.user_url % user
		return self.get_rss(url)

	def get_feed(self, feed):
		"""Assemble feed url and return a (desc, id) list."""

		url = self.feed_url % feed
		return self.get_rss(url)

	def search(self, term):
		"""Assemble a search query and return a (desc, id) list."""

		friendly_term = escape(term).replace(' ', '+')
		url = self.search_url % friendly_term
		return self.get_rss(url)


	def call_method(self, method, param):
		"""Call a REST method and return the result as an ElementTree."""
		url = self.api_url % (method, param)

		data = self.retrieve(url)
		return elementtree.ElementTree.XML(data)
	

	def get_video_list(self, method, param):
		"""Return a list of (desc, id) pairs from the REST result."""

		tree = self.call_method(method, param)
		list = []
		for node in tree.findall('video_list/video'):
			title = node.find('title').text
			if self.strip_chars:
				title = self.strip_exotic_chars(title)
			id = node.find('id').text
			list.append((title, id))

		return list

	def get_user_profile(self, name):
		"""Collect user profile data from the REST call."""

		param = 'user=%s' % name
		method = 'youtube.users.get_profile'
		tree = self.call_method(method, param)
		profile = {}
		for node in tree.findall('user_profile/*'):
			profile[node.tag] = node.text

		return profile

	def get_user_favorites(self, name):
		"""Return a list of (desc, id) pairs."""

		param = 'user=%s' % name
		method = 'youtube.users.list_favorite_videos'
		return self.get_video_list(method, param)
	
	def get_user_friends(self, name, page=None, per_page=None):
		"""Return a list of friends."""

		param = 'user=%s' % name
		method = 'youtube.users.list_friends'

		tree = self.call_method(method, param)

		friends = []
		for node in tree.findall('friend_list/friend/user'):
			friends.append(node.text)

		return friends

	def get_video_details(self, id):
		"""Collect video details data from the REST call."""

		param = 'video_id=%s' % id
		method = 'youtube.videos.get_details'

		tree = self.call_method(method, param)

		details = {}
		for node in tree.findall('video_details/*'):
			details[node.tag] = node.text

		return details

	def get_videos_by_tag(self, tag,
	                      page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'tag=%s' % tag
		method = 'youtube.videos.list_by_tag'

		return self.get_video_list(method, param)

	def get_videos_by_user(self, user,
	                       page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'user=%s' % user
		method = 'youtube.videos.list_by_user'

		return self.get_video_list(method, param)

	def get_videos_by_related(self, tag,
	                          page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'tag=%s' % tag
		method = 'youtube.videos.list_by_related'

		return self.get_video_list(method, param)

	def get_videos_by_playlist(self, id,
	                           page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'id=%s' % id
		method = 'youtube.videos.list_by_playlist'

		return self.get_video_list(method, param)

	def get_videos_by_tag_and_category(self, category, tag,
	                                   page=None, per_page=None):
		"""Return a list of (desc, id) pairs."""

		param = 'category_id=%d&tag=%s' % (category, tag)
		method = 'youtube.videos.list_by_category_and_tag'

		return self.get_video_list(method, param)

	def get_video_url(self, id):
		"""Return a proper playback url for some YouTube id."""

		ret = None

		url = self.video_url % id

		data = self.retrieve(url)
		if data is not None:
			match = self.session_pattern.search(data)

			if match != None and len(match.groups()) == 1:
				session = match.group(1)
				ret = self.stream_url % (id, session)

		return ret

	def set_error_hook(self, func, udata=None):
		"""Set the error handler."""
		self.error_hook = func
		self.error_udata = udata

	def set_report_hook(self, func, udata=None):
		"""Set the download progress report handler."""
		self.report_hook = func
		self.report_udata = udata

	def retrieve(self, url):
		"""Downloads an url."""

		data = ''

		if self.report_hook is not None:
			self.report_hook(0, -1, self.report_udata)

		try:
			req = urllib2.Request(unescape(url))
			fp = urllib2.urlopen(req)
		except Exception, e:
			if self.error_hook is not None:
				self.error_hook(str(e), self.error_udata)
			else:
				print e
			return None

		hdr = fp.info()
		if hdr.has_key('Content-length'):
			size = int(hdr['Content-length'])
		else:
			size = -1

		bs = max(int(size / 100.0), 1024)

		read = 0
		while True:
			block = fp.read(bs)
			if block == "":
				break
			read += len(block)
			data += block

			if self.report_hook is not None:
				keep_going = self.report_hook(read, size, self.report_udata)
				if keep_going is not None and not keep_going:
					read = size
					data = None
					break

		fp.close()

		if size > 0 and read < size and self.error_hook is not None:
			msg = 'Download incomplete. Got only %d out of %d.' % (read, size)
			self.error_hook(msg, self.error_udata)

		return data

if __name__ == '__main__':
	yt = YouTube()

	def report(done, size, udata):
		print done, size
	
	def error(msg, udata):
		print msg

	yt.set_error_hook(error)
	yt.set_report_hook(report)

	print "User Profile (sneseglarn):"
	print yt.get_user_profile('sneseglarn')
	print "------------------------------------------"
	print "User Favorite Videos (sneseglarn):"
	print yt.get_user_favorites('sneseglarn')
	print "------------------------------------------"
	print "User Friends (bungloid):"
	print yt.get_user_friends('bungloid')
	print "------------------------------------------"
	print "Video Details (NGrrPReQaOE):"
	print yt.get_video_details('NGrrPReQaOE')
	print "------------------------------------------"
	print "Videos by Tag ('blender')"
	print yt.get_videos_by_tag('blender')
	print "------------------------------------------"
	print "Videos by Tag and Category (1, 'blender')"
	print yt.get_videos_by_tag_and_category(1, 'blender')
	print "------------------------------------------"
	print "Videos from Feed ('recently_featured')"
	print yt.get_feed('recently_featured')
	print "------------------------------------------"
	print "Videos Url from Id ('whG99kjeXOM')"
	print yt.get_video_url('whG99kjeXOM')
	print "------------------------------------------"
	print "Videos from Search ('snowboard')"
	print yt.search('snowboard')
	print "------------------------------------------"
	print "Videos from User ('sneseglarn')"
	print yt.get_user_videos('sneseglarn')

