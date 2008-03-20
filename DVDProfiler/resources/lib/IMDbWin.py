"""

 Creates a window of IMDb information.

 ChangeLog:
 22/10/06 - Created.
 15/11/06 - tweaked
 24/01/07 - tweaked dialogSelect
 21/03/07 - Fixed due to site changes, also enhanced and rearranged.
 07/07/07 - Version that doesnt use latest bbbLib globals setup
 11/12/07 - tweaked layout
 21/01/08 - Uses DIR_CACHE from USERDATA
 20/03/08 - Changed to use changed imdbLib gallery

"""

import sys,os,os.path
import xbmc, xbmcgui

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__title__ = "IMDbWin"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '20-03-2008'
xbmc.output("Imported From: " + __scriptname__ + " title: " + __title__ + " Date: " + __date__)

DIR_USERDATA = sys.modules[ "__main__" ].DIR_USERDATA           # should be in default.py
DIR_CACHE = sys.modules[ "__main__" ].DIR_CACHE                 # should be in default.py

try:
	DIR_HOME = sys.modules[ "__main__" ].DIR_HOME     # should be in default.py
	DIR_RESOURCES = sys.modules[ "__main__" ].DIR_RESOURCES     # should be in default.py
	__language__ = sys.modules[ "__main__" ].__language__
	DIR_GFX = sys.modules[ "__main__" ].DIR_GFX                 # should be in default.py
except:
    DIR_RESOURCES = os.path.join(DIR_HOME,'resources')     # should be in default.py
    DIR_GFX = os.path.join(DIR_RESOURCES,'gfx')

from IMDbLib import IMDb, IMDbSearch, IMDbGallery
from bbbLib import *
from bbbGUILib import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

IMDB_LOGO_FILENAME = os.path.join(DIR_GFX ,'imdb_logo.png')
NOIMAGE_FILENAME = os.path.join(DIR_GFX ,'noimage.png')
dialogProgress = xbmcgui.DialogProgress()

# rez GUI defined in
REZ_W = 720
REZ_H = 576

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

		makeDir(DIR_USERDATA)
		makeDir(DIR_CACHE)

		debug("< IMDbWin()._init_")

	################################################################################
	def onAction(self, action):
		if action == ACTION_BACK or action == ACTION_B:
			self.deleteCacheImages()
			self.close()

	################################################################################
	def onControl(self, control):

		if control == self.photoRightCB:
			self.galleryImgIDX += 1
			# get next img in gallery or move to next gallery first image
			if self.galleryImgIDX >= self.imdbGallery.getGalleryImageCount():
				self.galleryImgIDX = 0

			self.fetchImage()
		elif control == self.photoLeftCB:
			self.galleryImgIDX -= 1
			if self.galleryImgIDX < 0:
				self.galleryImgIDX = self.imdbGallery.getGalleryImageCount()-1

			self.fetchImage()
		self.setFocus(control)

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

		if not url:
			debug("using galleryImgIDX=%s" % self.galleryImgIDX)
			imgTitle, url = self.imdbGallery.getThumb(self.galleryImgIDX)

		if url:
			basenameTitle = os.path.basename(url)
			fn = safeFilename(os.path.join(DIR_CACHE, self.IMDB_PREFIX + basenameTitle))
			exists = fileExist(fn)
			if not exists:
				dialogProgress.create(__language__(986), basenameTitle)
				exists = fetchURL(url, fn, isImage=True)
				dialogProgress.close()

		if exists:
			if not fn:
				fn = NOIMAGE_FILENAME
			self.picCI.setImage(fn)
			if not imgTitle:
				imgTitle = basenameTitle
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
		imageTitleX = x
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
		imageTitleW = (IMG_NAV_BTN_W *2) + self.photoW
		self.imageTitleCFL = xbmcgui.ControlFadeLabel(imageTitleX, imageTitleY, imageTitleW, imageTitleH, \
												 FONT10, '0xFFFFFFCC')
		self.addControl(self.imageTitleCFL)

		# NAV
		self.picFrameCB.controlDown(castCL)
		self.picFrameCB.controlUp(plotTB)
		self.picFrameCB.controlLeft(self.photoLeftCB)
		self.picFrameCB.controlRight(self.photoRightCB)

		self.photoLeftCB.controlLeft(self.photoRightCB)
		self.photoLeftCB.controlRight(self.picFrameCB)

		self.photoRightCB.controlLeft(self.picFrameCB)
		self.photoRightCB.controlRight(self.photoLeftCB)

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

	def deleteCacheImages(self):
		debug("> deleteCacheImages()")

		files = os.listdir(DIR_CACHE)
		for file in files:
			fn, ext = os.path.splitext(file)
			if ext == '.jpg' and fn.startswith(self.IMDB_PREFIX):
				deleteFile(os.path.join(DIR_CACHE, file))
		debug("< deleteCacheImages()")

	# setup next/prev and image frame states
	def setImageNav(self):
		debug("setImageNav()")
		visible = (self.imdbGallery.getGalleryImageCount() > 0)
		self.photoLeftCB.setVisible(visible)
		self.photoLeftCB.setEnabled(visible)
		self.photoRightCB.setVisible(visible)
		self.photoRightCB.setEnabled(visible)


	def ask(self, title=''):
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
			self.display()
#			dialogProgress.create(__language__(987))
			self.imdbGallery = IMDbGallery(url)
#			dialogProgress.close()
			self.fetchImage()
			self.setImageNav()
			self.setFocus(self.picFrameCB)
			self.doModal()
		debug("< IMDbWin.ask()")

#############################################################################################################
def safeFilename(path):
	head, tail = os.path.split(path.replace( "\\", "/" ))
	return  os.path.join(head, re.sub(r'[\'\";:?*<>|+\\/,=!]', '_', tail))


#win = IMDbWin()
#win.ask('star wars (1977)')
#del win
