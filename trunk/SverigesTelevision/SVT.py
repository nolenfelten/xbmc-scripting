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

from BeautifulSoup import BeautifulSoup
from xml.sax.saxutils import unescape

# http request timeout in seconds
timeout = 10
socket.setdefaulttimeout(timeout)

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
	
	def _parse_ram(self, data):
		url = None

		if data.endswith('rm'):
			url = data
		else:
			try:
				url = data[:data.index('\r')]
			except ValueError, e:
				print 'Unable to parse RAM file (%s)' % e
				url = 'http://'

		return url

	def _parse_asx(self, soup):
		url = None

		try:
			url = soup.asx.entry.ref['href'].replace('mms','http')
		except AttributeError, e:
			print 'Unable to parse ASX file (%s)' % e
			url = 'http://'

		return url

	def parse_directory(self, soup):
		list = []
		try:
			for node in soup.findAll('div', {'class':'enddep'}):
				if not node.a.has_key('href'): # hack, should be removed
					continue

				desc = unescape(self._get_soup_text(node.a))

				if node.a['href'].startswith('http'):
					url = node.a['href']
				else:
					url = self.base_url+node.a['href']
				list.append((desc, url, SVTMedia.DIR))

			for node in soup.findAll('div', {'class':'video'}):
				if not node.a.has_key('href'): # hack, should be removed
					continue

				desc = unescape(self._get_soup_text(node.a))

				if node.a['href'].startswith('http'):
					url = node.a['href']
				else:
					url = self.base_url+node.a['href']
				list.append((desc, url, SVTMedia.VIDEO))

		except AttributeError, e:
			print 'Unable to parse directory listing (%s)' % e
			list = None

		return list
	
	def parse_video(self, soup):
		list = []
		try:
			for node in soup.findAll('li', {'class':'video'}):
				if not node.a.has_key('href'): # hack, should be removed
					continue

				if node.a['href'].startswith('http'):
					url = node.a['href']
				else:
					url = 'http://svt.se'+node.a['href']

				if url.endswith('ram'):
					url = self._parse_ram(SVTMedia.fetch_data(url))
				elif url.endswith('asx'):
					url = self._parse_asx(SVTMedia.make_soup(url))

				list.append(url)
		except AttributeError, e:
			print 'Unable to parse video listing (%s)' % e
			list = None

		return list

	def fetch_data(url, func=None, udata=None):
		print "Fetching url: " + url
		req = urllib2.Request(unescape(url))

		try:
			s = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			print 'Unable to open url (%s)' % e
			return None
		except urllib2.URLError, e:
			print 'Unable to open url (%s, %s)' % (url, e)
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

	def make_soup(url, func=None, udata=None):
		data = SVTMedia.fetch_data(url, func, udata)
		if data != None:
			return BeautifulSoup(data)
		else:
			return None
	make_soup = staticmethod(make_soup)


if __name__ == '__main__':
	def test(pos, udata):
		print pos

	svt = SVTMedia()
	#list = svt.parse_directory(svt.get_start_url(), test)

	soup = SVTMedia.make_soup('http://svt.se/svt/road/Classic/shared/mediacenter/navigation.jsp?d=2156')
	list = svt.parse_directory(soup)
	for name, url, type in list:
		print '%28s - %s' % (name, url[url.rindex('/'):])

	#list = svt.parse_directory('http://svt.se/svt/road/Classic/shared/mediacenter//navigation.jsp?d=37689', test)
	#print list
	#soup = SVTMedia.make_soup('http://svt.se/svt/road/Classic/shared/mediacenter//navigation.jsp?d=40370', test)

	
	#if soup != None:
	#	list = svt.parse_directory(soup)
	#	print list
