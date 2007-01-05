###################################################################
#
#   CNN v1.5
#       Orginal by asteron. Lastest update by DC.
#
#   Watch hundreds of video reports from CNN.com, select from 
#   different categories.
#
#------------------------------------------------------------------
# Version History:
#     10/15/05 - AST - Initial creation
#     10/16/05 - AST - logo, description, NITN support
#     10/17/05 - AST - NITN format is different on somedays.  Added
#                      regular expression to fix lockup.
#     12/10/05 - AST - More stability, remember category on left side
# 1.2 08/09/06 - DC - Updated for changes CNN did to website
#                     and video formats. 
#                     Works with 03-07-2006 version of XBMC.
# 1.3 08/10/06 - DC - Now in the news link being a pain.
#                     Changed to use podcasting video link.
# 1.4 08/19/06 - DC - RSS link changed. Encoding changed as well.
#                     Now using feedparser to get rss feed.
# 1.5 09/19/06 - DC - CNN Now in the news link changed again. Fixed.
#                     Increased HTTP timeout.
#                     Corrected problem moving between categories.
# 1.6 09/20/06 - DC - CNN decided to add HTML to their descriptions
#                     Needed to strip.
# 1.7 01/05/06 - AST - CNN changed their rss again
#                      Switched from MMS to http to avoid playlist
###################################################################


from string import *
import codecs, datetime, os, re, sys, threading, urllib, urllib2
import xbmc, xbmcgui

#----- XBMC constants ---------------------------------------------

ACTION_MOVE_LEFT        = 1 
ACTION_MOVE_RIGHT       = 2
ACTION_MOVE_UP          = 3
ACTION_MOVE_DOWN        = 4
ACTION_PAGE_UP          = 5
ACTION_PAGE_DOWN        = 6
ACTION_SELECT_ITEM      = 7
ACTION_HIGHLIGHT_ITEM   = 8
ACTION_PARENT_DIR       = 9
ACTION_PREVIOUS_MENU    = 10
ACTION_SHOW_INFO        = 11
ACTION_PAUSE            = 12
ACTION_STOP             = 13
ACTION_NEXT_ITEM        = 14
ACTION_PREV_ITEM        = 15
ACTION_SCROLL_UP        = 111
ACTION_SCROLL_DOWN      = 112

XBFONT_LEFT       = 0x00000000
XBFONT_RIGHT      = 0x00000001
XBFONT_CENTER_X   = 0x00000002
XBFONT_CENTER_Y   = 0x00000004
XBFONT_TRUNCATED  = 0x00000008

COORD_1080I      = 0 
COORD_720P       = 1 
COORD_480P_4X3   = 2 
COORD_480P_16X9  = 3 
COORD_NTSC_4X3   = 4 
COORD_NTSC_16X9  = 5 
COORD_PAL_4X3    = 6 
COORD_PAL_16X9   = 7 
COORD_PAL60_4X3  = 8 
COORD_PAL60_16X9 = 9 

#------------------------------------------------------------------

ROOT_DIR = os.getcwd()[:-1]+'\\'    

import feedparser
Dependencies = ["time"]

HTTP_TIMEOUT = 30.0     # Max. seconds to wait for a response when fetching webpages


CNN_RSS_FEED = 'http://feeds.feedburner.com/cnn/video?format=usm'

# Need to parse this to get the current NITN URL
# DC - Using podcasting page to get filename for Now in the News.
CNN_NOW_IN_THE_NEWS_PAGE = 'http://rss.cnn.com/services/podcasting/nitn/rss'


class Item:
	def __init__(self, title, url, desc, category, date):
		self.title = title
		self.url = url
		self.description = desc
		self.category = category
		self.date = date

#possible categories are below
#[u'world', u'us', u'offbeat', u'sports', u'politics', u'showbiz', u'bestoftv', u'health', u'business', u'law', u'tech', u'education', u'specials', u'moos']
CATEGORIES = ['All','World','US','Politics','Showbiz','Sports','Tech','Business','Law','BestofTV','Offbeat','Other']


# Global progress dialog
dialogProgress = xbmcgui.DialogProgress()


#----- DC - Set DO_LOGGING = 1 to enable logging to Q:\scripts\CNN\log.txt.
DO_LOGGING = 1
try:
	LOG_FILE.close()
except Exception:
	pass
if DO_LOGGING:
	LOG_FILE = open(ROOT_DIR + '\\log.txt','w')
def LOG(message):
	if DO_LOGGING:
		LOG_FILE.write(str(message)+"\n")
		LOG_FILE.flush()    
def LOGCLOSE():
	if DO_LOGGING:
		LOG_FILE.close()


txdata = None
txheaders = {   
	'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.6) Gecko/20060728 Firefox/1.5.0.6',
	'Accept-Language': 'en-US',
	'Accept-Encoding': 'gzip, deflate, compress;q=0.9',
	'Keep-Alive': '300',
	'Connection': 'keep-alive',
	'Cache-Control': 'max-age=0',
}

items = []

FeedDate = datetime.date.today()

def FetchURL(url):
	LOG('FetchURL url=' + url)
	def SubthreadProc(url, result):
		try:
			req = urllib2.Request(url, txdata, txheaders)
			data = urllib2.urlopen(req).read()
		except Exception:
			# Could be a socket error or an HTTP error--either way, we
			# don't care--it's a failure to us.
			result.append(-1)
		else:
			result.append(data)
	result = []
	subThread = threading.Thread(target=SubthreadProc, args=(url, result))
	subThread.setDaemon(True)
	LOG(' starting url retrieval')
	subThread.start()
	subThread.join(HTTP_TIMEOUT)
	LOG(' finished url retrieval')
	if dialogProgress.iscanceled():
		dialogProgress.close()
		xbmcgui.Dialog().ok('ERROR','Cancelled.')
		return ''
	elif result == []:
		# Subthread hasn't give a result yet.  Consider it timed out.
		dialogProgress.close()
		xbmcgui.Dialog().ok('TIMEOUT','Video listing download timed out.')
		return ''
	elif result[0] == -1:
		dialogProgress.close()
		xbmcgui.Dialog().ok('ERROR','Failed to retrieve video listing')
		return ''
	else:
		return result[0]


HTMLRe = re.compile('<(.|\n)+?>',re.MULTILINE + re.DOTALL + re.IGNORECASE)
	
def StripHtml(arHtml):
	stripped = replace(arHtml, '<br>', ' ')
	stripped = HTMLRe.sub('',stripped)
	return stripped;


class CNNBrowser(xbmcgui.Window):
	def __init__(self):
		self.setCoordinateResolution(COORD_NTSC_4X3)
		self.addControl(xbmcgui.ControlImage(0,0, 720,480, 'background.png'))
		self.lstVideos = xbmcgui.ControlList(211,100,460,355,imageWidth=30,imageHeight=30)
		self.addControl(self.lstVideos)
		self.setFocus(self.lstVideos)
		self.makeButtons()
		self.addControl(xbmcgui.ControlImage(60, 20, 142, 73,ROOT_DIR + 'default.tbn'))
		self.lblDescription = xbmcgui.ControlTextBox(211,25,455,5000,'font12','FFFFFF00')
		self.addControl(self.lblDescription)
		self.currentCategory = 0
		
	def makeButtons(self):
		self.btnCategories = []
		for i in range(len(CATEGORIES)):
			btn = xbmcgui.ControlButton(60, 100+27*i, 140, 27, CATEGORIES[i],textXOffset=17)
			self.addControl(btn)
			self.btnCategories.append(btn)
		
		for i in range(len(CATEGORIES)):
			self.btnCategories[i].controlUp(self.btnCategories[i-1])
			self.btnCategories[i].controlDown(self.btnCategories[(i+1) % len(CATEGORIES)])
			self.btnCategories[i].controlRight(self.lstVideos)
			
			
	
	def onAction(self, action):
		if action == ACTION_PREVIOUS_MENU:
			self.close()
			
		elif (action == ACTION_MOVE_LEFT or action == ACTION_MOVE_RIGHT 
			or action == ACTION_MOVE_UP or action == ACTION_MOVE_DOWN
			or action == ACTION_PAGE_UP or action == ACTION_PAGE_DOWN
			or action == ACTION_SCROLL_UP or action == ACTION_SCROLL_DOWN):
			
			def SubthreadUpdate(self):
				self.lblDescription.reset()
				try:
					self.lblDescription.setText(self.listedItems[self.lstVideos.getSelectedPosition()].description)
				except:
					pass

			subThread = threading.Thread(target=SubthreadUpdate, args=[self])
			subThread.setDaemon(True)
			xbmcgui.lock()
			subThread.start()
			subThread.join(0.05)    
			xbmcgui.unlock()
		
		if action == ACTION_MOVE_LEFT:
			self.setFocus(self.btnCategories[self.currentCategory])
		
	def onControl(self, control):
		
		if control == self.lstVideos:
			item = self.listedItems[self.lstVideos.getSelectedPosition()]
			LOG("perform action")
			url = item.url
			LOG("original url is: " +url)			
			if item == items[0]: #now in the news needs to do some additional parsing
				url = self.findNowInTheNewsURL(item.url)
			if url == "":
				return
			try:
				LOG("Opening file " + url)
				"""			
				# DC - play(url) does not seem to work consistently with MMS: stream. Use playlist instead.
				#               xbmc.Player().play(url)
				pls = xbmc.PlayList(2)
				pls.clear()
				pls.add(url)
				xbmc.Player().play(pls)
				
				pls.clear()
				"""
				# Ast - This works fine... just use http instead of mms
				xbmc.Player().play(url)
				LOG("Found address " + url)
				
			except:
				xbmcgui.Dialog().ok('ERROR','Failed to connect to video server')
				return 
		
		for i in range(len(CATEGORIES)):
			if control == self.btnCategories[i]:
				self.filterList(i)
				self.lstVideos.selectItem(0)
				
			
	def filterList(self, idx):
		LOG("selecting " + str(idx))
		self.btnCategories[self.currentCategory].setLabel(CATEGORIES[self.currentCategory], "font13", "FFFFFFFF")
		self.btnCategories[idx].setLabel(CATEGORIES[idx], "font13", "FFFFFF00")
		self.currentCategory = idx
		self.filterListOn(CATEGORIES[idx].lower())
		
	def filterListOn(self, cat):
		if cat == 'all':
			self.listedItems = items[:]
		elif cat == 'other':
			cats = [cat.lower() for cat in CATEGORIES][:-1]
			self.listedItems = filter(lambda item: item.category.lower() not in cats,items)
		else:
			self.listedItems = filter(lambda item: item.category == cat,items)
		self.populateList()
	
	def reformURL(self,url):
		try:
			start = url.index("?url=/video/") + len ("?url=/video/")
			end = url.index("&date")
			return ("http://wmscnn.stream.aol.com.edgestreams.net/cnn/"+url[start:end]+".ws.wmv").encode("utf8")#?MSWMExt=.asf"
		except:
			return ""

	def findNowInTheNewsURL(self, inUrl):
		LOG("findNowInTheNewsURL inUrl=" + inUrl)
		try:
			url = CNN_NOW_IN_THE_NEWS_PAGE
			data = urllib.urlopen(url).read()
			
			current = re.search ( '(<enclosure url=")(.*?)(.m4v?)',data).group(2)
			LOG(" found string: " + current)
			theUrl = current+".m4v"
			LOG(" theUrl=" + theUrl)
			return theUrl
		except:
			pass

		xbmcgui.Dialog().ok("'Now in the News' Podcast Not Available.","Will try the 1st edition of 'Now in the News'.")
			
		# Sometimes podcasting page is blank. Try another way to get link.
		# 
		# There appear to be 12 editions of Now in the News created each day.
		# Unfortunately I do not know the logic behind generating the 12 editions.
		# Default to using the first one for now. Hopefully there. DC.
		try:
			theDay = FeedDate.strftime("%d")
			theMonth = FeedDate.strftime("%m")
			theYear = FeedDate.strftime("%Y")
			current = theYear + '/' + theMonth + '/' + theDay

			LOG(" current: " + current)
			theUrl = 'http://wmscnn.stream.aol.com.edgestreams.net/cnn/nitn/' + current + '/nitn.edition.01.cnn.ws.wmv'
			LOG(" theUrl=" + theUrl)
			return theUrl
		except:
			xbmcgui.Dialog().ok('ERROR',"Failed to retrieve 'Now in the News'.")
			return ""
	
	def downloadFeed(self):
		dialogProgress.create("Downloading...", "Fetching video listing.")
		LOG('downloadFeed')
		self.getVideoListing()
		dialogProgress.close()
		self.filterList(0)
		
	def populateList(self):
		xbmcgui.lock()
		self.lstVideos.reset()
		for item in self.listedItems:
			self.lstVideos.addItem(xbmcgui.ListItem(label=item.title,label2=item.date,thumbnailImage='defaultVideo.png'))
		self.lblDescription.reset()
		self.lblDescription.setText(self.listedItems[0].description)
		xbmcgui.unlock()

	def getVideoListing(self):
		LOG('getVideoListing')

		try:
			data = feedparser.parse(CNN_RSS_FEED)
		except:
			LOG(' Problem parsing RSS feed.')
			return
			
		if data == '':
			return

		if data.has_key("channel"):
			mytitle = data["channel"].get("title", "No title")
			LOG(' RSS Title=' + mytitle)
			
			FeedDate = data["channel"].get("date", datetime.date.today())

			try:
				rssItems = data.get('items', None)
			except:
				LOG(' Problem parsing items from RSS feed.')
				return
			
			if rssItems:			
				for rssItem in rssItems:
					try:
						title = rssItem.get('title','')
						url = rssItem.get('feedburner_origlink','')
						date = rssItem.get('date','')
						desc = StripHtml(rssItem.get('description',''))
						category = rssItem.get('category','')
					except:
						LOG(' Problem reading item fields from RSS feed.')
						return

					try:
						items.append(Item(title, url, desc, category,date))
					except:
						LOG(' Problem adding item info to items.')
						return
				# some post processing
				lookup = 'JanFebMarAprMayJunJulAugSepOctNovDec'
				for item in items:
					if item != items[0]:
						item.url = self.reformURL(item.url)
					try:
						date = item.date.split()
						item.date = date[0] + ' ' + str(lookup.index(date[2])/3+1) + '/' + date[1] + ' ' + ':'.join(date[4].split(':')[0:2])
					except:
						pass
			else:
				LOG(' RSS Feed has no items.')
		else:
			LOG(' RSS Feed has no channel')


w = CNNBrowser()
w.downloadFeed()
w.doModal()

LOGCLOSE()

if dialogProgress:
	dialogProgress.close()
