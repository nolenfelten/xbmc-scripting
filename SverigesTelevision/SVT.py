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
		self.base_url = 'http://svt.se/svt/road/Classic/shared/mediacenter/'
		self.default_url = self.base_url+'navigation.jsp?&frameset=true'
	
	def get_start_url(self):
		return self.default_url

	def _get_soup_text(self, node):
		return " ".join([x for x in node.recursiveChildGenerator() if isinstance(x, basestring)]).strip()
	
	def _parse_ram(self, url):
		ram = None

		data = self.retrieve(url)

		if data.endswith('rm'):
			ram = data
		else:
			try:
				ram = data[:data.index('\r')]
			except ValueError, e:
				msg = 'Unable to parse RAM file.'
				raise ParseError(msg)

		return ram 

	def _parse_asx(self, url):
		mms = None

		data = self.retrieve(url)
		soup = BeautifulSoup(data)

		try:
			mms = soup.asx.entry.ref['href'].replace('mms','http')
		except AttributeError, e:
			msg = 'Unable to parse ASX file.'
			raise ParseError(msg)

		return mms

	def parse_directory(self, url):
		list = []

		data = self.retrieve(url)
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
			else:
				url = self.base_url+node.a['href']
			list.append((desc, url, SVTMedia.VIDEO))

		return list
	
	def parse_video(self, url):
		list = []

		data = self.retrieve(url)
		soup = BeautifulSoup(data)

		for node in soup.findAll('li', {'class':'video'}):
			if not node.a.has_key('href'): # hack, should be removed
				continue

			if node.a['href'].startswith('http'):
				url = node.a['href']
			else:
				url = 'http://svt.se'+node.a['href']

			if url.endswith('ram'):
				url = self._parse_ram(url)
			elif url.endswith('asx'):
				url = self._parse_asx(url)

			list.append(url)

		return list

	def set_report_hook(self, func, udata=None):
		self.rhook = func
		self.rudata = udata

	def retrieve(self, url):
		return xbmcutils.net.retrieve(url, rhook=self.rhook, rudata=self.rudata)

if __name__ == '__main__':
	def test(done, size, udata):
		print done, size

	svt = SVTMedia()
	svt.set_report_hook(test)
	#list = svt.parse_directory('http://svt.se/svt/road/Classic/shared/mediacenter/navigation.jsp?d=2156')
	list = svt.parse_directory('http://svt.se/svt/road/Classic/shared/mediacenter/navigation.jsp?d=37689')
	for name, url, type in list:
		if type == SVTMedia.DIR:
			t = 'dir'
		else:
			t = 'video'

		print '%28s - %s (%s)' % (name, url[url.rindex('/'):], t)

	#list = svt.parse_directory('http://svt.se/svt/road/Classic/shared/mediacenter//navigation.jsp?d=37689', test)
	#print list
	#soup = SVTMedia.make_soup('http://svt.se/svt/road/Classic/shared/mediacenter//navigation.jsp?d=40370', test)
	#if soup != None:
	#	list = svt.parse_directory(soup)
	#	print list
