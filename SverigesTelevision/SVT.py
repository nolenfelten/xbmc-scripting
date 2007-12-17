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

from BeautifulSoup import BeautifulSoup
from xml.sax.saxutils import unescape
import re

import xbmcutils.net

class ParseError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SVTMedia:
	DIR = 0
	VIDEO = 1

	def __init__(self):
		play_url = 'http://svt.se/svt/road/Classic/shared'

		self.base_url = play_url + '/mediacenter/'
		self.search_url = play_url + '/search/video/MediaplayerSearch.jsp'

		self.default_url = self.base_url+'navigation.jsp?&frameset=true'

		self.flash_pattern = re.compile('http://[^"]+')

	def get_start_url(self):
		return self.default_url

	def _get_soup_text(self, node):
		return " ".join([x for x in node.recursiveChildGenerator() if isinstance(x, basestring)]).strip()

	def _parse_ram(self, url):
		ram = None

		data = self.retrieve(url)

		return data.split('\r')

	def _parse_asx(self, url):
		mms = None

		data = self.retrieve(url)
		soup = BeautifulSoup(data)

		try:
			mms = soup.asx.entry.ref['href']
		except AttributeError, e:
			try:
				mms = self._get_soup_text(soup)
			except Exception, e:
				msg = 'Unable to parse ASX file.'
				raise ParseError(msg)

		mms = mms.replace('mms', 'http')

		return [mms]

	def list_directory(self, url):
		data = self.retrieve(url)
		return self.parse_directory(data)

	def parse_directory(self, data):
		list = []

		soup = BeautifulSoup(data)

		for node in soup.findAll('div', {'class':'enddep'}):
			if not node.a.has_key('href'):
				continue

			desc = unescape(self._get_soup_text(node.a))

			if node.a['href'].startswith('http'):
				url = node.a['href']
			else:
				url = self.base_url+node.a['href']
			list.append((desc, url, SVTMedia.DIR))

		for node in soup.findAll('div', {'class':'video'}):
			if not node.a.has_key('href'):
				continue

			desc = unescape(self._get_soup_text(node.a))

			if node.a['href'].startswith('http'):
				url = node.a['href']
			elif node.a['href'].startswith('player'):
				url = self.base_url + node.a['href']
			else:
				url = 'http://svt.se' + node.a['href']
			list.append((desc, url, SVTMedia.VIDEO))

		return list

	def parse_video(self, url):
		list = []

		data = self.retrieve(url)
		soup = BeautifulSoup(data)

		for node in soup.findAll('li', {'class':'video'}):
			if not node.a.has_key('href'): # hack, should be removed
				continue

			# fixup the url
			if node.a['href'].startswith('http'):
				url = node.a['href']
			else:
				url = 'http://svt.se' + node.a['href']

			entries = []

			# get the real video clip urls
			if url.endswith('ram'):
				entries = self._parse_ram(url)
			elif url.endswith('asx') or '.asx?' in url:
				entries = self._parse_asx(url)

			list = list + entries

		if not list:
			for node in soup.findAll('div', {'id':'playerWrapper'}):
				if node.script:
					text = self._get_soup_text(node.script)
					match = self.flash_pattern.search(text)
					if match is not None:
						list = list + [match.group(0)]

		return list

	def set_report_hook(self, func, udata=None):
		self.report_hook = func
		self.report_udata = udata

	def retrieve(self, url, data=None, headers={}):
		return xbmcutils.net.retrieve(url, data, headers,
		                              self.report_hook,
		                              self.report_udata)

	def search(self, term):
		post = {'queryString':term}
		data = self.retrieve(self.search_url, post)

		return self.parse_directory(data)


if __name__ == '__main__':
	def test(done, size, udata):
		print done, size

	svt = SVTMedia()
	svt.set_report_hook(test)
	"""
	print 'downloading'
	#list = svt.list_directory(svt.base_url + '/navigation.jsp?d=2156')
	#list = svt.list_directory(svt.base_url + '/navigation.jsp?d=37689')
	#list = svt.list_directory(svt.base_url + '/navigation.jsp?d=63330')
	list = svt.list_directory(svt.base_url + '/navigation.jsp?d=37689')
	print 'download complete'
	for name, url, type in list:
		if type == SVTMedia.DIR:
			t = 'dir'
		else:
			t = 'video'

		print '%28s - %s (%s)' % (name, url, t)

	#list = svt.list_directory(svt.base_url + '/navigation.jsp?d=37689', test)
	#print list
	#soup = SVTMedia.make_soup(svt.base_url + '/navigation.jsp?d=40370', test)
	#if soup != None:
	#	list = svt.list_directory(soup)
	#	print list

	list = svt.search('percy')
	for name, url, type in list:
		if type == SVTMedia.DIR:
			t = 'dir'
		else:
			t = 'video'

		print '%28s - %s (%s)' % (name.encode('UTF-8'), url[url.rindex('/'):].encode('UTF-8'), t)
		u = url

	print svt.parse_video(u)

	"""
	print svt.base_url
	#print svt.parse_video(svt.base_url + '/player.jsp?d=63330&a=743767')
	#print svt.parse_video(svt.base_url + '/player.jsp?d=63330&a=743771')
	#print svt.parse_video(svt.base_url + '/player.jsp?&d=60388&a=927600&lid=is_mediaplayer_search&lpos=0')
	#print svt.parse_video(svt.base_url + 'player.jsp?a=995955&d=37689')
	print svt.parse_video(svt.base_url + 'player.jsp?a=1003341&d=37591')

