"""

 Creates a window of IMDb information.

 ChangeLog:
 22/10/06 - Created.
 15/11/06 - tweaked
 24/01/07 - tweaked dialogSelect
 21/03/07 - Fixed due to site changes, also enhanced and rearranged.
 07/07/07 - Version that doesnt use latest bbbLib globals setup
 11/12/07 - tweaked layout
 21/01/08 - Uses DIR_IMDB_CACHE from USERDATA
 20/03/08 - Changed to use changed imdbLib gallery
 04/04/08 - Fix to use changed fetchURL() params

"""

import sys,os,os.path, urlparse
import xbmc, xbmcgui

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__title__ = "IMDbWin"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '20-03-2008'
xbmc.output("Imported From: " + __scriptname__ + " title: " + __title__ + " Date: " + __date__)

DIR_USERDATA = sys.modules[ "__main__" ].DIR_USERDATA           # should be in default.py
DIR_IMDB_CACHE = os.path.join(DIR_USERDATA, 'imdb')

try:
	DIR_HOME = sys.modules[ "__main__" ].DIR_HOME     # should be in default.py
	DIR_GFX = sys.modules[ "__main__" ].DIR_GFX                 # should be in default.py
	__language__ = sys.modules[ "__main__" ].__language__
except:
    DIR_RESOURCES = os.path.join(DIR_HOME,'resources')     # should be in default.py
    DIR_GFX = os.path.join(DIR_RESOURCES,'gfx')

from IMDbLib import IMDb, IMDbSearch, IMDbGallery
from bbbLib import *
from bbbGUILib import *

IMDB_LOGO_FILENAME = os.path.join(DIR_GFX ,'imdb_logo.png')
NOIMAGE_FILENAME = os.path.join(DIR_GFX ,'noimage.png')
dialogProgress = xbmcgui.DialogProgress()

# rez GUI defined in
REZ_W = 720
REZ_H = 576
try: Emulating = xbmcgui.Emulating
except: Emulating = False

#################################################################################################################
class IMDbWin(xbmcgui.WindowDialog):
	def __init__(self):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		debug("> IMDbWin()._init_")

		setResolution(self)

		self.backgW = 670
		self.backgH = 580

		# center on screen
		self.xpos = int((REZ_W /2) - (self.backgW /2))
		self.ypos = int((REZ_H /2) - (self.backgH /2)) + 10

		# pic
		self.IMDB_PREFIX = 'imdb_'
		self.photoW = 200
		self.photoH = 170
		self.photoX = self.xpos + 50
		self.photoY = self.ypos + 70
		self.border = 2
		self.picCI = None

		self.EMPTY = 'N/A'
		self.galleryIDX = 0
		self.galleryImgIDX = 0
		self.movie = None

#		makeDir(DIR_USERDATA)
		makeDir(DIR_IMDB_CACHE)

		debug("< IMDbWin()._init_")

	################################################################################
	def onAction(self, action):
		if action in CANCEL_DIALOG:
			removeDir(DIR_IMDB_CACHE, force=True)
			self.close()

	################################################################################
	def onControl(self, control):

		if control == self.photoRightCB:
			self.galleryImgIDX += 1
			# get next img in gallery or move to next gallery first image
			if self.galleryImgIDX >= self.imdbGallery.getGalleryImageCount():
				self.galleryImgIDX = 0
			self.fetchImage()
			self.setFocus(control)
		elif control == self.photoLeftCB:
			self.galleryImgIDX -= 1
			if self.galleryImgIDX < 0:
				self.galleryImgIDX = self.imdbGallery.getGalleryImageCount()-1
			self.fetchImage()
			self.setFocus(control)
		elif control == self.picFrameCB:
			if self.slideshow():
				self.close()

	#################################################################################################
	def findTitle(self, title=''):
		debug("> findTitle()")
		url = None

		dialogProgress.create(__language__(982), title)
		imdbSearch = IMDbSearch(title)
		dialogProgress.close()
		if not imdbSearch.SearchResults:
			if xbmcgui.Dialog().yesno(__language__(980), title, __language__(984)):
				url = ''		# will cause manual entry
		elif len(imdbSearch.SearchResults) > 1:
			# make menu list
			menu = [xbmcgui.ListItem(__language__(500)), xbmcgui.ListItem(__language__(981))]
			for year, title, titleurl in imdbSearch.SearchResults:
				menu.append(xbmcgui.ListItem(title, label2=year))

			# popup dialog to select choice
			selectDialog = DialogSelect()
			selectDialog.setup(__language__(985), width=600, rows=len(menu), banner=IMDB_LOGO_FILENAME)
			selectedPos,action = selectDialog.ask(menu)
			if selectedPos == 1:		# manual entry
				url = ''
			elif selectedPos > 1:		# title selected
				year, title, url = imdbSearch.SearchResults[selectedPos-2]	# allow for exit & Manual
		else:
			year, title, url = imdbSearch.SearchResults[0]

		if url:
			dialogProgress.create(__language__(982),title + ' ' + year)
			self.movie = IMDb(url)
			if not self.movie:
				url = None		# failed to parse movie info
			dialogProgress.close()
		debug("< findTitle()")
		return url

	#################################################################################################
	# fetch & show image
	def fetchImage(self, url=''):
		debug("> fetchImage() " + url)
		exists = False
		imgTitle = ''
		fn = ''
		basename = ''

		if not url:
			debug("using galleryImgIDX=%s" % self.galleryImgIDX)
			imgTitle, url = self.imdbGallery.getThumb(self.galleryImgIDX)

		if url:
			fn, basename = self.makeThumbFilename(url)
			exists = fileExist(fn)
			if not exists:
				dialogProgress.update(0, basename)
#				dialogProgress.create(__language__(986), basename)
				exists = fetchURL(url, fn, encodeURL=False, isBinary=True)
#				dialogProgress.close()

		if exists:
			if not fn:
				fn = NOIMAGE_FILENAME
			debug("image fn=" + fn)
			self.picCI.setImage(fn)
			self.picCI.setVisible(True)
			if not imgTitle:
				imgTitle = __language__(989)
			self.imageTitleCFL.reset()
			self.imageTitleCFL.addLabel(imgTitle)

		debug("< fetchImage() exists=%s" % exists)
		return exists

	#################################################################################################
	def display(self, panel=''):
		debug("> display()")
		xbmcgui.lock()
		imageTitleH = 15
		
		# BACKGROUND PANEL
		try:
			if not panel:
				panel = DIALOG_PANEL
			self.panelCI = xbmcgui.ControlImage(self.xpos, self.ypos, self.backgW, self.backgH, panel)
			self.addControl(self.panelCI)
		except: pass

		# IMDb LOGO
		logoW = 47
		logoH = 23
		x = (self.xpos + self.backgW) - logoW - 10
		y = self.ypos + 15
		try:
			logo = xbmcgui.ControlImage(x, y, logoW, logoH, IMDB_LOGO_FILENAME)
			self.addControl(logo)
		except: pass

		labelData = [
			('IMDb Rating:', self.movie.Rating),
			('Directors:', self.movie.Directors),
			('Creators:', self.movie.Creators),
			('Writers:', self.movie.Writers),
			('Released:', self.movie.ReleaseDate),
			('Certs:', self.movie.Certs),
			('Runtime:', self.movie.Runtime),
			('SoundMix:', self.movie.SoundMix),
			('Aspect:', self.movie.Aspect),
			('Genres:', self.movie.Genres),
			('Countries:', self.movie.Countries),
			('Languages:', self.movie.Languages),
			('Soundtrack:', self.movie.Soundtrack),
			('Awards:', self.movie.Awards),
			('UserComment:', self.movie.UserComment),
			('Trivia:', self.movie.Trivia),
			('Goofs:', self.movie.Goofs)
			]

		IMG_NAV_BTN_W = 15
		COL1_W = 95
		COL1_X = self.photoX + (self.border*4) + self.photoW + (self.border*4) + IMG_NAV_BTN_W
		COL1_X_R = COL1_X + COL1_W 		# for right align

		COL2_X = COL1_X_R + 5
		COL2_W = self.backgW - COL2_X	# remainder to right edge

		detailH = 15
		fontLabel = FONT10
		fontData = FONT10
		colourLabel = '0xFFFFFFFF'
		colourData = '0xFFFFFF99'

		# TITLE
		titleH = 20
		titleW = self.backgW - logoW
		x = self.xpos + 30
		y = self.ypos + 20
		self.titleCL = xbmcgui.ControlFadeLabel(x, y, titleW, titleH, FONT14, '0xFFFFFF00')
		self.addControl(self.titleCL)
		title = self.movie.Title
		if self.movie.AKA:
			title += ' (AKA: ' + self.movie.AKA + ')'
		self.titleCL.addLabel(decodeEntities(title))

		# Tag line
		if self.movie.Tagline:
			y += titleH + 3
			self.tagCL = xbmcgui.ControlFadeLabel(x, y, titleW, titleH, FONT10, '0xFFFFFF99')
			self.addControl(self.tagCL)
			self.tagCL.addLabel(decodeEntities(self.movie.Tagline))

		# PLACE LABEL + DATA
		y = self.photoY
		for label, data in labelData:
#			print label, data
			# LABEL
			self.addControl(xbmcgui.ControlLabel(COL1_X_R, y, COL1_W, detailH, label, \
												 fontLabel, colourLabel, alignment=XBFONT_RIGHT))

			# DATA
			ctrl = xbmcgui.ControlFadeLabel(COL2_X, y, COL2_W, detailH, fontData, colourData)
			self.addControl(ctrl)
			ctrl.addLabel(decodeEntities(data))
			y += detailH
		detailFinalH = y

		# PLOT - TEXT BOX
		y += 5
		h = self.backgH - y
		plotTB = xbmcgui.ControlTextBox(COL1_X, y, COL1_W + COL2_W, h, FONT12, '0xFFFFFF66')
		self.addControl(plotTB)
		plotTB.setText(decodeEntities(self.movie.PlotOutline))

		# CAST LIST
		x = self.xpos+20
		y = self.photoY + self.photoH + imageTitleH + 5
		h = self.backgH - y
		w = COL1_X - x
		castCL = xbmcgui.ControlList(x, y, w, h, font=fontLabel, space=0,itemHeight=20, \
									itemTextXOffset=0, itemTextYOffset=0, alignmentY=XBFONT_CENTER_Y)
		self.addControl(castCL)
#		try:
#			castCL.setPageControlVisible(False)
#		except: pass

		try:
			for actor,role in self.movie.Cast:
				castCL.addItem(xbmcgui.ListItem(decodeEntities(actor), decodeEntities(role)))
		except:
			castCL.addItem(xbmcgui.ListItem('No Cast Details'))

		# THUMBNAIL FRAME - draw last so it overlays/blanks
		# create a control btn as background
		x = self.photoX-self.border
		y = self.photoY-self.border
		w = self.photoW+(self.border*2)
		h = self.photoH+(self.border*2)
		self.picFrameCB = xbmcgui.ControlButton(x, y, w, h, '', \
										FRAME_FOCUS_FILENAME, FRAME_NOFOCUS_FILENAME)
		self.addControl(self.picFrameCB)

		# THUMBNAIL IMAGE
		self.picCI = xbmcgui.ControlImage(self.photoX, self.photoY, self.photoW, self.photoH, \
										  NOIMAGE_FILENAME, aspectRatio=2)
		self.addControl(self.picCI)

		# PHOTO MOVE LEFT
		x -= (self.border*2 + IMG_NAV_BTN_W)
		self.photoLeftCB = xbmcgui.ControlButton(x, self.photoY, IMG_NAV_BTN_W, self.photoH, '<', \
												  alignment=XBFONT_CENTER_X|XBFONT_CENTER_Y)
		self.addControl(self.photoLeftCB)

		# PHOTO MOVE RIGHT
		x = self.photoX + self.photoW + (self.border*2)
		self.photoRightCB = xbmcgui.ControlButton(x, self.photoY, IMG_NAV_BTN_W, self.photoH, '>', \
												  alignment=XBFONT_CENTER_X|XBFONT_CENTER_Y)
		self.addControl(self.photoRightCB)

		# image title
		imageTitleY = self.photoY + self.photoH +1
		self.imageTitleCFL = xbmcgui.ControlFadeLabel(self.photoX, imageTitleY, self.photoW, imageTitleH, \
												 FONT10, '0xFFFFFFCC')
		self.addControl(self.imageTitleCFL)

		# NAV
		self.picFrameCB.controlDown(castCL)
		self.picFrameCB.controlUp(plotTB)
		self.picFrameCB.controlLeft(self.photoLeftCB)
		self.picFrameCB.controlRight(self.photoRightCB)

		self.photoLeftCB.controlLeft(self.photoRightCB)
		self.photoLeftCB.controlRight(self.picFrameCB)
		self.photoLeftCB.controlDown(castCL)
		self.photoLeftCB.controlUp(plotTB)

		self.photoRightCB.controlLeft(self.picFrameCB)
		self.photoRightCB.controlRight(self.photoLeftCB)
		self.photoRightCB.controlDown(castCL)
		self.photoRightCB.controlUp(plotTB)

		plotTB.controlDown(self.picFrameCB)
		plotTB.controlUp(self.picFrameCB)
		plotTB.controlRight(castCL)
		plotTB.controlLeft(castCL)
		
		castCL.controlUp(self.picFrameCB)
		castCL.controlDown(plotTB)
		castCL.controlRight(plotTB)
		castCL.controlLeft(plotTB)

		self.setFocus(plotTB)
		
		xbmcgui.unlock()
		debug("< display()")

	# setup next/prev and image frame states
	def setImageNav(self):
		debug("setImageNav()")
		visible = (self.imdbGallery.getGalleryImageCount() > 0)
		self.photoLeftCB.setVisible(visible)
		self.photoLeftCB.setEnabled(visible)
		self.photoRightCB.setVisible(visible)
		self.photoRightCB.setEnabled(visible)

	def slideshow(self):
		debug("> slideshow()")
		MAX = self.imdbGallery.getGalleryImageCount()
		if MAX:
			dialogProgress.create(__language__(988))
			for idx in range(MAX):
				pct = int(idx*100.0/MAX)

				small_url = self.imdbGallery.getThumbURL(idx)
				small_fn, small_basename = self.makeThumbFilename(small_url)
				large_fn = small_fn.replace(self.IMDB_PREFIX, self.IMDB_PREFIX + 'l_')
				large_url = self.imdbGallery.getLargeThumbURL(idx)
				dialogProgress.update(pct, "%s  (%s/%s)" % (os.path.basename(large_fn), idx, MAX))
				# try to get large image, but save using modified small filename
				if not fileExist(large_fn):
					if not fetchURL(large_url, large_fn, isBinary=True):
						# delete bad large_fn
						deleteFile(large_fn)
						debug("no large, get small image")
						if not fileExist(small_fn):
							dialogProgress.update(pct, "%s  (%s/%s)" % (small_basename, idx, MAX))
							fetchURL(small_url, small_fn, isBinary=True)
			dialogProgress.close()
			xbmc.executebuiltin('XBMC.SlideShow(%s)'% DIR_IMDB_CACHE)
		debug("< slideshow()")
		return MAX
		

	# attempt to make filename more unique by using some of its subfolder names from url
	# return full fn and basename
	def makeThumbFilename(self, url):
		split_info = urlparse.urlsplit(url)
		basename = safeFilename(split_info[2]).replace('/media','').replace('/imdb','').replace('/','').replace('\\','').replace('_','')
		# restrict length
		l = len(basename)
		if l > 30:
			basename = basename[(l-30):]
		return os.path.join(DIR_IMDB_CACHE, self.IMDB_PREFIX + basename), basename

	def ask(self, title='',panel=''):
		debug("> IMDbWin.ask()")
		url = ''
		# loop till we find a title or user quits manual entry
		while not url:
			if title:
				url = self.findTitle(title)

			if url == '':
				title = doKeyboard(title, __language__(981))
				if not title:
					break
			elif url == None:
				break

		if self.movie and url:
			self.display(panel)
			dialogProgress.create(__language__(987))
			self.imdbGallery = IMDbGallery(url)
			self.fetchImage()
			dialogProgress.close()
			self.setImageNav()
			self.setFocus(self.picFrameCB)
			self.doModal()
		debug("< IMDbWin.ask()")

#############################################################################################################
def safeFilename(path):
#	head, tail = os.path.split(path.replace( "\\", "/" ))
	head, tail = os.path.split(path)
	name, ext = os.path.splitext(tail)
	return  os.path.join(head, re.sub(r'[\'\";:?*<>|+\\/,=!\.]', '_', name) + ext)


#win = IMDbWin()
#win.ask('star wars (1977)')
#del win
