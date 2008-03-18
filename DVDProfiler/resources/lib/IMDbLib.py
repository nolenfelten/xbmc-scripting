""" IMDbLib Movie Information Library:
Movie Information parsing from http://www.imdb.com

Originally Written By:
---------------------

No1CaNTeL
AllTheKillx

MODIFIED by BigBellyBilly AT gmail DOT com
-------------------------
Fixed and modified in several areas. NO NOT REPLACE THIS LIBRARY FILE
Changelog:
02/11/06 Change: IMDBSearch lookupstr to ensure it always replaces space with +
28/04/07 Fix: IMDb site changes and added extra tags.
05/06/07 Fix: Gallery regex
09/07/07 Fix: Seach for title. caused by site change
11/12/07 Fix: Scraping regex (see date comments)
18/01/08 Fix: regex for Cast
"""

import os,sys,re,urllib,string
from string import find

DEBUG = True
def log(s):
    if DEBUG:
        print s

fixReg = re.compile(r"&#[0-9]{1,3};")

reFlags = re.MULTILINE+re.IGNORECASE+re.DOTALL
# full page RE
titleReg        = '<title>(.*?)<'
taglineReg      = '>Tagline:<.*?>([^<]*)'									# 11/12/07
plotOutlineReg  = '>Plot (?:Outline|Summary):<.*?>([^<]*)'					# 11/12/07
yearReg         = 'Sections/Years/.*?>(.*?)<'
ratingReg       = '<b>User Rating:</b>[^<]*<b>(.*?)<.*?">(.*?)<'			# 11/12/07
runtimeReg      = '>Runtime:<.*?>([^<]*)'									# 11/12/07
countriesReg    = '>Country:<.*?>([^<]*)</a'								# 11/12/07
languagesReg    = '>Language:<.*?>([^<]*)</a'								# 11/12/07
awardsReg       = '>Awards:<.*?>([^<]*)'									# 11/12/07
releaseDateReg  = '>Release Date:<.*?>(.*?)<'
userCommentReg  = '>User Comments:<.*?>(.*?)<'
akaReg          = '>Also Known As:<.*?>(.*?)<'
aspectReg       = '>Aspect Ratio:<.*?>(.*?)<'
triviaReg       = '>Trivia:<.*?>(.*?)</div'									# 11/12/07
goofsReg        = '>Goofs:<.*?>(.*?)</div'									# 11/12/07
soundtrackReg   = '>Soundtrack:<.*?>(.*?)</div'								# 11/12/07
soundMixReg     = '>Sound Mix:<.*?>(.*?)</div'								# 11/12/07
posterURLReg    = '"photo">.*?src="(.*?)" height="(\d+)" width="(\d+)"'
companyReg		= '"/company/[^/]*/">([^<]*)</a>'							# 11/12/07
genresReg       = re.compile(r'/Genres/.*?>(.*?)<', reFlags)
certsReg        = re.compile(r'certificates=.*?>(.*?)<', reFlags)

# per line RE
directorsReg   = re.compile(r'.*?Director:.*')
writersReg     = re.compile(r'.*?Writer.*')
castReg        = re.compile(r'.*?class="cast".*')
creatorsReg   = re.compile(r'.*?Creator.*')

in_directorsReg = re.compile(r'href="/name/.*?>(.*?)</')
in_writersReg   = re.compile(r'href="/name/.*?>(.*?)</')
in_castReg   = re.compile(r'href="/name/[nm0-9]*/">(.*?)<.*?(?:/character/|"char").*?>(.*?)(?:</a|</t)')	# 25/01/08
in_creatorsReg = re.compile(r'href="/name/.*?>(.*?)</')

# gallery RE
galleriesRE = re.compile('href="photogallery(-.*?)"',reFlags)
galleryRE = re.compile('<a href="/gallery.*? src="(.*?)".*?(?:width|height)="(\d+)".*?(?:width|height)="(\d+)".*?</a>',reFlags)

class IMDb:
	def __init__(self,url):
		log("IMDb() " + url)

		NA = 'N/A'
		self.Title           = NA
		self.Tagline         = NA
		self.PlotOutline     = NA
		self.Year            = NA
		self.Rating          = NA
		self.Runtime         = NA
		self.Countries       = NA
		self.Languages       = NA
		self.Awards          = NA
		self.ReleaseDate     = NA
		self.UserComment     = NA
		self.AKA             = ''
		self.Aspect          = NA
		self.Trivia          = NA
		self.Goofs           = NA
		self.Soundtrack      = NA
		self.SoundMix        = NA
		self.PosterURL      = None
		self.Cast            = []
		self.Certs            = NA
		self.Creators         = NA
		self.Writers         = NA
		self.Directors		= NA
		self.Genres          = NA


		page = readPage(url)
		if not page:
			return None

		# FUL PAGE REGEX
		log("do full page regex searches ...")
		matches = re.search(titleReg, page, reFlags)
		if matches:
			self.Title = clean(matches.group(1))

		# TAGLINE
		matches = re.search(taglineReg, page, reFlags)
		if matches:
			self.Tagline = clean(matches.group(1))

		# YEARS
		matches = re.search(yearReg, page, reFlags)
		if matches:
			self.Year = clean(matches.group(1))

		# PLOT SUMMARY
		matches = re.search(plotOutlineReg, page, reFlags)
		if matches:
			self.PlotOutline = clean(matches.group(1))

		# RATING
		matches = re.search(ratingReg, page, reFlags)
		if matches:
			self.Rating = "%s %s" % (matches.group(1).strip(), matches.group(2).strip())

		# RUNTIME
		matches = re.search(runtimeReg, page, reFlags)
		if matches:
			self.Runtime = clean(matches.group(1))

		# COUNTRY
		matches = re.search(countriesReg, page, reFlags)
		if matches:
			self.Countries = clean(matches.group(1))

		# LANG
		matches = re.search(languagesReg, page, reFlags)
		if matches:
			self.Languages = clean(matches.group(1))

		# AWARDS
		matches = re.search(awardsReg, page, reFlags)
		if matches:
			self.Awards = clean(matches.group(1))

		# RELEASE DATE
		matches = re.search(releaseDateReg, page, reFlags)
		if matches:
			self.ReleaseDate = clean(matches.group(1))

		# USER COMMENT
		matches = re.search(userCommentReg, page, reFlags)
		if matches:
			self.UserComment = clean(matches.group(1))

		# AKA
		matches = re.search(akaReg, page, reFlags)
		if matches:
			self.AKA = clean(matches.group(1))

		# ASPECT
		matches = re.search(aspectReg, page, reFlags)
		if matches:
			self.Aspect = clean(matches.group(1))

		# TRIVIA
		matches = re.search(triviaReg, page, reFlags)
		if matches:
			self.Trivia = clean(matches.group(1))

		# GOOFS
		matches = re.search(goofsReg, page, reFlags)
		if matches:
			self.Goofs = clean(matches.group(1))

		# SOUNDTRACK
		matches = re.search(soundtrackReg, page, reFlags)
		if matches:
			self.Soundtrack = clean(matches.group(1))

		# SOUNDMIX
		matches = re.search(soundMixReg, page, reFlags)
		if matches:
			self.SoundMix = clean(matches.group(1))

		# POSTER PHOTO
		matches = re.search(posterURLReg, page, reFlags)
		if matches:
			self.PosterURL = clean(matches.group(1))

		# GENRES
		matches = genresReg.findall(page)
		if matches:
			self.Genres = ','.join(matches)

		# CERTS
		matches = certsReg.findall(page)
		if matches:
			self.Certs = ','.join(matches)

		log("do pre line regex searches ...")
		pageLines = page.split('\n')
		i = 0
		while i < len(pageLines):
			if directorsReg.match(pageLines[i]):
				i += 1
				matches = in_directorsReg.findall(pageLines[i])
				if matches:
					self.Directors = clean(','.join(matches))

			elif writersReg.match(pageLines[i]):
				i += 1
				matches = in_writersReg.findall(pageLines[i])
				if matches:
					self.Writers = clean(','.join(matches))

			elif castReg.match(pageLines[i]):
				matches = in_castReg.findall(pageLines[i])
				for actor,role in matches:
					self.Cast.append([clean(actor), clean(role)])

			if creatorsReg.match(pageLines[i]):
				i += 1
				matches = in_creatorsReg.findall(pageLines[i])
				if matches:
					self.Creators = clean(','.join(matches))

			i+=1

		if DEBUG:	# switch on for debug results
			print "Title            =", self.Title
			print "Tagline          =", self.Tagline   
			print "PlotOutline      =", self.PlotOutline
			print "Year             =", self.Year
			print "Rating           =", self.Rating
			print "Runtime          =", self.Runtime
			print "Countries        =", self.Countries
			print "Languages        =", self.Languages
			print "Awards           =", self.Awards
			print "ReleaseDate      =", self.ReleaseDate
			print "UserComment      =", self.UserComment
			print "AKA              =", self.AKA
			print "Aspect           =", self.Aspect
			print "Trivia           =", self.Trivia
			print "Goofs            =", self.Goofs
			print "Soundtrack       =", self.Soundtrack
			print "SoundMix         =", self.SoundMix
			print "PosterURL        =", self.PosterURL
			print "Certs            =", self.Certs
			print "Creators         =", self.Creators
			print "Writers          =", self.Writers
			print "Directors        =", self.Directors
			print "Genres           =", self.Genres
			print "Cast             =", self.Cast


###########################################################################################################
class IMDbSearch:
	def __init__(self, findStr):
		log("IMDbSearch() " + findStr)
		self.YEAR = 0
		self.TITLE = 1
		self.URL = 2
		try:
			lookupStr = findStr.strip().translate(string.maketrans('',''),'~!@#$%^&*()_+`-={}|[]\:";\'<>?,./').replace(' ','+')
		except:
			lookupStr = findStr.replace(' ','+')

		self.SearchResults = []
		url = 'http://www.imdb.com/find?s=tt&q=' + lookupStr
		page = readPage(url)
		if not page:
			print "page not found: ", url
			return

		if string.find(page, 'No Matches') != -1:
			log( "IMDbSearch no matches" )
		elif string.find(page, '>Popular') != -1:
			log( "search 'Popular'" )
			# title code, title, year
			search = re.compile('href="/title/([t0-9]*)/">(.*?)</a> *\(([0-9]*)')		# updated 11/12/2007
			matches = search.findall(page)
			if matches:
				for a in matches:
					url = "http://www.imdb.com/title/%s/" % (a[0])
					title = urlTextToASCII(a[1])
					year = a[2]
					self.SearchResults.append((year, title, url))

				# sort resul tuple into year reverse order
				self.SearchResults.sort()
				self.SearchResults.reverse()
			else:
				log( "no matches on page" )
		else:
			log( "search 'Years'" )
			search = re.compile('/Years/([0-9]*)\".*?/title/([t0-9]*)/', re.DOTALL + re.MULTILINE + re.IGNORECASE)
			matches = search.findall(page)
			if matches:
				year = matches[0][0]
				url = "http://www.imdb.com/title/%s/" % (matches[0][1])
				self.SearchResults.append((year, findStr, url))
			else:
				log( "no matches on page" )

	def getSearchResults(self):
		return self.SearchResults
	def getSearchResult(self, idx):
		try:
			return self.SearchResults[idx]
		except:
			return None
	def getTitle(self, idx):
		self.SearchResults[idx][self.TITLE]
	def getURL(self, idx):
		self.SearchResults[idx][self.URL]
	def getYear(self, idx):
		self.SearchResults[idx][self.YEAR]


###########################################################################################################
class IMDbGallery:
	def __init__(self, url):
		log("IMDbGallery() " + url)

		if url[-1] != '/': url += '/'
		self.baseURL = url + 'photogallery'

		self.posterURL = None
		self.galleries = []
		self.galleyThumbs = {}
		self.THUMB_ATTR_IMG = 0
		self.THUMB_ATTR_X = 1
		self.THUMB_ATTR_Y = 2

		# FETCH PHOTOGALLERY
		self.page = readPage(self.baseURL)
		if self.page:
			# GET POSTER URL
			matches = re.search(posterURLReg, self.page, reFlags)
			if matches:
				self.posterURL = matches.group(1)

			# GET GALLERY URLS
			self.galleries = self.getGalleries()

			# fetch thumb url for each image in gallery
			for gURL in self.galleries:
				self.galleyThumbs[gURL]= self.getGalleryThumbs(gURL)

		if DEBUG:
			print "baseURL=", self.baseURL
			print "posterURL=", self.posterURL
			print "galleries=", len(self.galleries)
			print "galleyThumbs=", len(self.galleyThumbs)

			for key, value in self.galleyThumbs.items():
				print key, " count=", len(self.galleyThumbs[key])

	def getThumbAttr(self, thumbInfo, attr):
		return thumbInfo[attr]

	def getThumbURL(self, galleryIDX, galleyImgIdx):
		try:
			gURL = self.galleries[galleryIDX]
			thumbInfo = self.galleyThumbs[gURL][galleyImgIdx]
			return self.getThumbAttr(thumbInfo, self.THUMB_ATTR_IMG)
		except:
			return None

	# alter URL to point to large image
	def getLargeURL(self, galleryIDX, galleyImgIdx):
		url = self.getThumbURL(galleryIDX, galleyImgIdx)
		if url:
			url = url.replace('th-','/')
		return url

	def getGalleryImageCount(self, galleryIDX):
		try:
			gURL = self.galleries[galleryIDX]
			return len(self.galleyThumbs[gURL])
		except:
			return 0

	def getGalleries(self):
		galleries = []
		matches = galleriesRE.findall(self.page)
		for match in matches:
			try:
				url = self.baseURL + match
				galleries.index(url)
			except:
				galleries.append(url)
		return galleries

	# GET GALLERY THUMB IMAGES
	def getGalleryThumbs(self, url):
		page = readPage(url)
		if page:
			return galleryRE.findall(page)
		return None


###########################################################################################################
def readPage(url, readLines=False):
	log("readPage() readLines=" + str(readLines) + " " +url)
	page = None
	try:
		sock = urllib.urlopen(url)
		if not readLines:
			page = sock.read()
		else:
			page = sock.readlines()
		sock.close()
	except:
		log("urlopen() exception")

	return page

###########################################################################################################
def clean(text):
	return urlTextToASCII(cleanHTML(text)).strip()


###########################################################################################################
def cleanHTML(data):
	try:
		reobj = re.compile('<.+?>', re.IGNORECASE+re.DOTALL+re.MULTILINE)
		return (re.sub(reobj, '', data)).strip()
	except:
		return data

###########################################################################################################
def urlTextToASCII(text):
	try:
		compile_obj = re.compile('(&#x(.*?);)',  re.IGNORECASE + re.MULTILINE + re.DOTALL)
		match_obj = compile_obj.findall(text)
		for match in match_obj:
			ch = chr(int('0x'+match[1], 16))
			text = text.replace(match[0], ch)

		compile_obj = re.compile('(&#(\d+);)',  re.IGNORECASE + re.MULTILINE + re.DOTALL)
		match_obj = compile_obj.findall(text)
		for match in match_obj:
			ch = chr(int(match[1]))
			text = text.replace(match[0], ch)

		text = text.replace('&amp;','&').replace('\n',' ').replace('\r',' ').replace('\t',' ')

		compile_obj = re.compile('(&(.*?);)', re.IGNORECASE+re.DOTALL+re.MULTILINE)
		text = (re.sub(compile_obj, '', text))

	except: pass
	return text

