"""
    Python XBMC script to view comics from RSS Feeds and/or HTML pages.

	Written By BigBellyBilly
	bigbellybilly AT gmail DOT com	- bugs, comments, ideas, help ...

	THANKS:
	To everyone who's ever helped in anyway, or if I've used code from your own scripts, MUCH APPRECIATED!

	CHANGELOG: see ..\resources\changelog.txt or view throu Settings Menu
	README: see ..\resources\language\<language>\readme.txt or view throu Settings Menu

    Additional support may be found on xboxmediacenter forum.	
"""

import xbmc, xbmcgui
import sys, os.path
import Image, re, os, time
from os import path
from string import find, strip, replace, rjust
from urlparse import urljoin
from shutil import rmtree

# Script doc constants
__scriptname__ = "Comics"
__version__ = '1.5'
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '28-02-2008'
xbmc.output(__scriptname__ + " Version: " + __version__ + " Date: " + __date__)

# Shared resources
DIR_HOME = os.getcwd().replace( ";", "" )
DIR_RESOURCES = os.path.join( DIR_HOME , "resources" )
DIR_RESOURCES_LIB = os.path.join( DIR_RESOURCES , "lib" )
#DIR_USERDATA = os.path.join( "T:\\script_data", __scriptname__ )
DIR_GFX = os.path.join(DIR_RESOURCES,'gfx')
DIR_CACHE = os.path.join(DIR_HOME, "cache")
sys.path.insert(0, DIR_RESOURCES_LIB)

# Custom libs
import language
mylanguage = language.Language()
__language__ = mylanguage.localized

import update                                       # script update module
from bbbLib import *
from bbbSkinGUILib import TextBoxDialogXML

ELEMENT_TITLE = 'title'
ELEMENT_LINK = 'link'
ELEMENT_DESC = 'description'
ELEMENT_RE_ITEM = 'reItem'
ELEMENT_RE_IMAGE = 'reImage'

# dialog object for the whole app
dialogProgress = xbmcgui.DialogProgress()

#################################################################################################################
# MAIN
#################################################################################################################
class GUI(xbmcgui.WindowXML):
	# control id's
	CLBL_VERSION = 21
	CLBL_SOURCE = 22
	CLBL_TITLE = 23
	CLBL_DESC = 24
	CI_BACKGROUND = 100
	CI_COMIC = 110
	CI_FS_GUIDE = 120
	CGROUP_LIST_FEEDS = 2100
	CLST_FEEDS = 2110
	CGROUP_LIST_ITEMS = 2200
	CLST_ITEMS = 2210
	CGROUP_LIST_ITEM_IMAGES = 2300
	CLST_ITEM_IMAGES = 2310
	CGROUP_BTNS = 2400
	CLBL_Y_BTN = 2411
	CLBL_X_BTN = 2421
	CLBL_A_BTN = 2431
	CLBL_B_BTN = 2441
	CI_HEADER = 1001
	CI_FOOTER = 2001
	CGROUP_HEADER = 1000
	CGROUP_FOOTER = 2000

	#################################################################################################################
	def __init__(self, *args, **kwargs):
		debug("> __init__")

		# check for script update on SVN
		self.scriptUpdated = update_script(False, False)
		if not self.scriptUpdated:
			self.reset()

		debug("< __init__")

	#################################################################################################################
	def onInit( self ):
		debug("> onInit() ")
		xbmcgui.lock()
		self.getControl(self.CI_COMIC).setVisible(False)
		self.getControl( self.CLBL_VERSION ).setLabel( "v" + __version__ )
		self.clearAll()
		xbmcgui.unlock()

		if not self.scriptUpdated:
			# get comic image display area
			image_control = self.getControl( self.CI_COMIC )
			x, y = image_control.getPosition()
			w = image_control.getWidth()
			h = image_control.getHeight()
			self.imageNormalScreenDims = (x, y, w, h)

			# get w h of area being rendered into that windowXML thinks its using, not actual screen rez
			self.displayW = self.getControl(self.CI_BACKGROUND).getWidth()
			self.displayH = self.getControl(self.CI_BACKGROUND).getHeight()
			while not self.ready:
				if not self.selectSource():
					debug("close()")
					self.close()
					break
				else:
					self.ready = self.switchSource()
		else:
			print "script updating, close script"
			self.close()

		debug("< onInit() self.ready="+str(self.ready))

	#################################################################################################################
	def onAction(self, action):
		debug( "onAction() self.ready=%s" % self.ready )
		if not action or not self.ready:
			return
		buttonCode =  action.getButtonCode()
		actionID   =  action.getId()
		debug( "onAction(): actionID=%i  buttonCode=%i" % (actionID, buttonCode) )
		if not buttonCode or buttonCode in [1991528071, 11109936]:
			return
		if not actionID and buttonCode:
			actionID = buttonCode

		self.ready = False
		if actionID in CONTEXT_MENU:
			self.mainMenu()
		elif actionID == ACTION_X or buttonCode == KEYBOARD_X:
			if self.comicImage:
				self.toggleFullscreen()
		elif actionID in CANCEL_DIALOG and self.IS_FULLSCREEN:
			self.toggleFullscreen()
		elif actionID in [ACTION_Y, BUTTON_Y, ACTION_REMOTE_PAUSE] or buttonCode == KEYBOARD_Y:
			if self.selectSource():
				self.switchSource()
		elif actionID in EXIT_SCRIPT and not self.IS_FULLSCREEN:
			self.close()
		elif actionID in MOVEMENT_LEFT_STICK + MOVEMENT_RIGHT_STICK and self.IS_FULLSCREEN:
			self.moveImage(actionID)

		self.ready = True

	#################################################################################################################
	def onClick(self, controlID):
		if not controlID or not self.ready:
			return
		debug( "onclick(): control %i" % controlID )
		self.ready = False

		if (controlID == self.CLST_FEEDS):
			debug("CLST_FEEDS")
			self.feedSelected()

		elif (controlID == self.CLST_ITEMS):
			debug("CLST_ITEM")
			if self.itemSelected():
				self.itemImageSelected(0)

		elif (controlID == self.CLST_ITEM_IMAGES):
			debug("CLST_ITEM_IMAGES")
			self.itemImageSelected()

		self.ready = True

	###################################################################################################################
	def onFocus(self, controlID):
		debug("onFocus(): controlID %i" % controlID)
		self.controlID = controlID

	###################################################################################################
	def reset(self):
		debug("> reset()")

		# SELF vars
		self.controlID = 0
		self.COMIC_SOURCE_IDX = -1			# unselected source for startup
		self.filename = None				# filename used to save downloaded image to
		self.IS_FULLSCREEN = False			# current status of display
		self.lastSourcePos = -1				# saves last item list pos
		self.lastFeedsPos = -1				# saves last item list pos
		self.lastItemsPos = -1				# saves last item list pos
		self.lastItemImagesPos = -1			# saves last item list pos
		self.loadedImageSize = []
#		self.zoom = 0
		self.comicImage = None					# control to hold image
		self.ready = False

		self.sources = []
		self.sources.append(Tapestry())
#		self.sources.append(Funnies())		# no longer available 18/02/08
		self.sources.append(Comics())
		self.sources.append(MyComics())

		debug("< reset()")

	###################################################################################################
	def isReady(self):
		return self.ready

	##############################################################################################################
	def clearAll(self, clearSourceLbl=True):
		debug("> clearAll() clearSourceLbl="+str(clearSourceLbl))
		xbmcgui.lock()

		self.IS_FULLSCREEN = False
		self.setAllFooterListsVisible()
		self.clearComicImage()
		self.setHeader()
		if clearSourceLbl:
			self.getControl( self.CLBL_SOURCE ).setLabel("")

		xbmcgui.unlock()
		debug("< clearAll()")

	####################################################################################################################
	def clearComicImage(self):
		debug("clearComicImage()")
		try:
			self.comicImage.setVisible(False)
			self.removeControl(self.comicImage)
			self.getControl(self.CI_COMIC).setVisible(False)
			self.comicImage = None
			self.loadedImageSize = ()
#			deleteFile(self.filename)
		except: pass

	####################################################################################################################
	def setHeader(self, title="", desc=""):
		debug("setHeader()")
		self.getControl( self.CLBL_TITLE ).setLabel(title)
		self.getControl( self.CLBL_DESC ).setLabel(desc)

	####################################################################################################################
	def setAllFooterListsVisible(self, isFeedsVisible=False, isItemsVisible=False, isItemImagesVisible=False):
		debug("> setAllFooterListsVisible()")
		self.setListVisible( self.CLST_FEEDS, self.CGROUP_LIST_FEEDS, isFeedsVisible )
		self.setListVisible( self.CLST_ITEMS, self.CGROUP_LIST_ITEMS, isItemsVisible )
		self.setListVisible( self.CLST_ITEM_IMAGES, self.CGROUP_LIST_ITEM_IMAGES, isItemImagesVisible )
		debug("< setAllFooterListsVisible()")

	####################################################################################################################
	def setListVisible(self, listID, groupID, isVisible):
		debug("setListVisible() listID=%s groupID=%s isVisible=%s" % (listID, groupID, isVisible))
		try:
			if not isVisible:
				self.getControl( listID ).reset()
				self.getControl( listID ).selectItem(0)
			self.getControl( groupID ).setVisible(isVisible)
			self.getControl( listID ).setVisible(isVisible)
		except: pass

	####################################################################################################################
	def setControlVisible(self, id, isVisible):
		try:
			self.getControl( id ).setVisible(isVisible)
		except: pass

	##############################################################################################
	def mainMenu(self):
		debug("> mainMenu()")

		options = [__language__(500), __language__(503), __language__(504)]
		selectDialog = xbmcgui.Dialog()
		while True:
			selectedPos = selectDialog.select( __language__(501), options )
			if selectedPos <= 0:				# exit selected
				break
			elif selectedPos == 1:
				title = "%s: %s" % (__language__(0), __language__(503))
				fn = getReadmeFilename(mylanguage)
			elif selectedPos == 2:
				title = "%s: %s" % (__language__(0), __language__(504))
				fn = os.path.join( DIR_HOME, "changelog.txt" )

			tbd = TextBoxDialogXML("script-bbb-fullscreen-textbox.xml", DIR_RESOURCES, "Default")
			tbd.ask(title, doc)
			del tbd

		debug ("< mainMenu()")

	##############################################################################################
	def toggleFullscreen(self):
		debug("> toggleFullscreen()")

		self.IS_FULLSCREEN = (not self.IS_FULLSCREEN)
		debug("self.IS_FULLSCREEN now = " + str(self.IS_FULLSCREEN))

		if self.IS_FULLSCREEN:
			self.getControl( self.CGROUP_HEADER ).setVisible(False)
			self.getControl( self.CGROUP_FOOTER ).setVisible(False)

		imageX, imageY, imageW, imageH = self.calcImageDims()
		self.showImage(imageX, imageY, imageW, imageH)

		if not self.IS_FULLSCREEN:
			self.getControl( self.CGROUP_HEADER ).setVisible(True)
			self.getControl( self.CGROUP_FOOTER ).setVisible(True)
			self.setFocus(self.getControl( self.CLST_ITEMS ))
		debug("< toggleFullscreen()")


	############################################################################################################
	def getImageDisplayedDims(self):
		x, y = self.comicImage.getPosition()
		w =  self.comicImage.getWidth()
		h =  self.comicImage.getHeight()
		debug ("getImageDisplayedDims() X=%s Y=%s W=%s H=%s" % (x, y, w, h))
		return x, y, w, h

	############################################################################################################
	def moveImage(self, code):
		debug("> moveImage() code: " + str(code))

		redraw = False
		move = 40
		minBorder = 10

		imageX, imageY, imageW, imageH = self.getImageDisplayedDims()
		if code in (BUTTON_LEFT_STICK_RIGHT, REMOTE_RIGHT, KEYBOARD_RIGHT):
			if (imageX + move) < self.displayW-minBorder:
				imageX += move
				redraw = True
		elif code in (BUTTON_LEFT_STICK_LEFT, REMOTE_LEFT, KEYBOARD_LEFT):
			if (imageX + imageW) - move > minBorder:
				imageX -= move
				redraw = True
		elif code in (BUTTON_LEFT_STICK_UP, REMOTE_UP, KEYBOARD_UP):
			if (imageY + imageH) - move > minBorder:
				imageY -= move
				redraw = True
		elif code in (BUTTON_LEFT_STICK_DOWN, REMOTE_DOWN, KEYBOARD_DOWN):
			if (imageY + move) < (self.displayH - minBorder):
				imageY += move
				redraw = True
		elif code in MOVEMENT_SCROLL_UP + MOVEMENT_SCROLL_DOWN + MOVEMENT_RIGHT_STICK:
			# get 10% of orig image dims
			w, h = self.loadedImageSize
			value = int((w / 100) * 10)

			if code in MOVEMENT_SCROLL_UP + \
				   (BUTTON_RIGHT_STICK_DOWN, BUTTON_RIGHT_STICK_LEFT) + \
				   (ACTION_RIGHT_STICK_DOWN, ACTION_RIGHT_STICK_LEFT):
				value *= -1		# make neg

			imageW += value
			imageH += value
			redraw = True

		if redraw:
			self.showImage(imageX, imageY, imageW, imageH)
			time.sleep(.05)

		debug("< moveImage()")


	############################################################################################################
	def showImage(self, imageX, imageY, imageW, imageH):
		debug("> showImage() X=%s Y=%s W=%s H=%s" % (imageX, imageY, imageW, imageH))
		if self.comicImage:
			debug("update control image")
			self.comicImage.setPosition(int(imageX), int(imageY))
			self.comicImage.setWidth(int(imageW))
			self.comicImage.setHeight(int(imageH))
		else:
			debug("create new control image")
			self.comicImage = xbmcgui.ControlImage(int(imageX), int(imageY), int(imageW), int(imageH), self.filename)
			self.addControl(self.comicImage)
			self.comicImage.setAnimations([('WindowClose', 'effect=zoom end=0 center=auto time=200'),
										   ('visible', 'effect=zoom start=0 end=100 center=auto time=200'),
										   ('hidden', 'effect=zoom end=0 center=auto time=200')
										   ])
		self.comicImage.setVisible(True)
		self.getControl(self.CI_FS_GUIDE).setVisible(self.IS_FULLSCREEN)
		if self.IS_FULLSCREEN:
			self.setFocus(self.comicImage)
		debug("< showImage()")


	############################################################################################################
	def calcImageDims(self):
		debug("> calcImageDims()  image file=" + self.filename)
		dims = ()

		if not self.comicImage or not self.loadedImageSize:
			try:
#				fn, ext = os.path.splitext(self.filename)
				self.loadedImageSize = Image.open( self.filename ).size
			except:
				debug("unable to determine image size")
				self.loadedImageSize = (0,0)

		imageW, imageH = self.loadedImageSize
		debug( "imageSize=%s, %s" % (imageW, imageH))
		# make screen size
		if self.IS_FULLSCREEN:
			debug ("  setup FULLSCREEN display dims")
			# setup full scr dims
			imgDisplayX = 0
			imgDisplayY = 0
			# get w h of area being rendered into that windowXML thinks its using, not actual screen rez
			imgDisplayW = self.displayW
			imgDisplayH = self.displayH
		else:
			debug ("  setup WINDOWED display dims")
			imgDisplayX, imgDisplayY, imgDisplayW, imgDisplayH = self.imageNormalScreenDims

		# determine scaling
		if imageW != 0 and imageH != 0:
			# determine shortest scale side to fit display area
			imgScaleH = float(imgDisplayH / float(imageH))
			imgScaleW = float(imgDisplayW / float(imageW))
			debug("  imgScaleW: " + str(imgScaleW) + "  imgScaleH: " + str(imgScaleH))

			if (imgScaleH < imgScaleW):			# use height expansion scale
				debug("  Using height expansion scale")
				imageH = imageH*imgScaleH
				imageW = imageW*imgScaleH
			else:								# use width expansion scale
				debug("  Using width expansion scale")
				imageH = imageH*imgScaleW
				imageW = imageW*imgScaleW
			
			# calc X from center of display area
			displayHalfX = imgDisplayX + (imgDisplayW /2)
			imageX = displayHalfX - (imageW /2)

			# find center Y pos of display area in relation to screen
			displayHalfY = imgDisplayY + (imgDisplayH /2)
			# image Y in relation to center of display area Y
			imageY = displayHalfY - (imageH /2)
		else:
			debug("img of unknown size")
			imageX = imgDisplayX
			imageY = imgDisplayY

		dims = (imageX, imageY, imageW, imageH)
		debug("< calcImageDims()")
		return dims

	##############################################################################################
	def selectSource(self):
		debug("> selectSource()")
		success = False
		self.lastSourcePos = self.COMIC_SOURCE_IDX

		# create menu
		options = [__language__(500)]
		for source in self.sources:
			options.append(source.getName())

		selectDialog = xbmcgui.Dialog()
		header = "%s: %s" % (__language__(0), __language__(561))
		selectedPos = selectDialog.select( header, options )       
		debug( "selectedPos=%s" % selectedPos)
		if selectedPos > 0:
			selectedPos -= 1											# allow for exit
			if selectedPos != self.COMIC_SOURCE_IDX:                    # check not same as current
				self.COMIC_SOURCE_IDX = selectedPos
				success = True

		debug ("< selectSource() success="+str(success))
		return success

	###################################################################################################
	def switchSource(self):
		debug("> switchSource() COMIC_SOURCE_IDX: " + str(self.COMIC_SOURCE_IDX))

		sourceName = __language__(400) + self.sources[self.COMIC_SOURCE_IDX].getName()
		dialogProgress.create(sourceName, __language__(200) )
		success = (self.sources[self.COMIC_SOURCE_IDX].setupFeeds() > 0)
		dialogProgress.close()

		if success:
			self.clearAll()

			self.updateFeedsList()

			self.sourceName = sourceName
			self.getControl( self.CLBL_SOURCE ).setLabel(self.sourceName)
			self.setAllFooterListsVisible(True, False, False)
			self.setFocus(self.getControl( self.CLST_FEEDS ))
		else:
			messageOK(self.sourceName, __language__(104))
			self.COMIC_SOURCE_IDX = self.lastSourcePos

		debug("< switchSource() success="+str(success))
		return success

	##############################################################################################################
	def updateFeedsList(self):
		debug("> updateFeedsList()")

		list = self.sources[self.COMIC_SOURCE_IDX].getFeedsList()		# get list options
		control = self.getControl( self.CLST_FEEDS )
		for l in list:
			try:
				txt = l.encode()
			except:
				txt = l
			control.addItem( txt )

		debug("< updateFeedsList()")

	##############################################################################################################
	def feedSelected(self):
		debug("> feedSelected()")
		success = False

		pos = self.getControl( self.CLST_FEEDS ).getSelectedPosition()
		if pos == self.lastFeedsPos:
			debug("< same feed selected, do nothing")
			return False
		if pos < 0:
			pos = 0
		self.lastFeedsPos = pos
		self.lastItemsPos = -1
		self.lastItemImagesPos = -1
		self.newURLRequest = True

		self.clearComicImage()
		self.setAllFooterListsVisible(True, False, False)

		info = self.sources[self.COMIC_SOURCE_IDX].getInfo(pos)
		feedTitle = info.getElement(ELEMENT_TITLE)
		self.setHeader(feedTitle)

		dialogProgress.create(self.sourceName, __language__(201), feedTitle)
		success = (self.sources[self.COMIC_SOURCE_IDX].downloadFeed(pos) > 0)
		dialogProgress.close()

		if not success:
			messageOK(self.sourceName, feedTitle, __language__(105))
		else:
			# populate ITEMS list
			control = self.getControl( self.CLST_ITEMS )
			list = self.sources[self.COMIC_SOURCE_IDX].getItemsList()		# items list
			for l in list:
				try:
					txt = l.encode()
				except:
					txt = l
				control.addItem( txt )

			self.setListVisible(self.CLST_ITEMS, self.CGROUP_LIST_ITEMS, True)
#			self.setControlVisible( self.CGROUP_LIST_ITEMS, True )
			self.setFocus(control)

		debug("< feedSelected() success="+str(success))
		return success

	##############################################################################################################
	def itemSelected(self):
		debug("> itemSelected()")
		count = 0

		pos = self.getControl( self.CLST_ITEMS ).getSelectedPosition()
		if pos == self.lastItemsPos:
			debug("< itemSelected() same selected, do nothing")
			return 0
		if pos < 0:
			pos = 0
		self.lastItemsPos = pos
		self.lastItemImagesPos = -1

		self.clearComicImage()
		self.setAllFooterListsVisible(True, True, False)

		itemName = self.getControl( self.CLST_ITEMS ).getSelectedItem().getLabel()
		urlList = self.sources[self.COMIC_SOURCE_IDX].getItemLink(pos)
		self.getControl(self.CLBL_DESC).setLabel(itemName)

		if not urlList:
			messageOK(self.sourceName, itemName, __language__(108))
		else:
			# update Item Images list
			control = self.getControl( self.CLST_ITEM_IMAGES )
			for imgURL, title in urlList:
				if title:
					txt = title
				else:
					head, txt = os.path.split(imgURL)

				try:
					control.addItem(txt.encode())
				except:
					control.addItem(txt)

			self.setListVisible(self.CLST_ITEM_IMAGES, self.CGROUP_LIST_ITEM_IMAGES, True)
#			self.setControlVisible( self.CGROUP_LIST_ITEM_IMAGES, True )
			self.setFocus(control)

			count = len(urlList)
		debug("< itemSelected() count="+str(count))
		return count

	##############################################################################################################
	def itemImageSelected(self, pos=None):
		debug("> itemImageSelected() pos=%s" % pos)
		success=False

		if pos == None:
			pos = self.getControl( self.CLST_ITEM_IMAGES ).getSelectedPosition()
		if pos == self.lastItemImagesPos:
			debug("< itemImageSelected() same selected, do nothing")
			return False
		if pos < 0:
			pos = 0
		self.lastItemImagesPos = pos

		self.clearComicImage()
		imageURL, imgName = self.sources[self.COMIC_SOURCE_IDX].getItemImageLink(pos)
		itemName = self.getControl( self.CLST_ITEMS ).getSelectedItem().getLabel()
		itemImageOpt = self.getControl( self.CLST_ITEM_IMAGES ).getSelectedItem().getLabel()
		if imageURL:
			success = self.getImage(imageURL, title=itemName, msg=itemImageOpt)
		else:
			messageOK(_itemName, __language__(108), imgName)

#		self.setFocus(self.getControl( self.CLST_ITEM_IMAGES ))
		debug("< itemImageSelected() success="+str(success))
		return success

	##############################################################################################################
	def getImage(self, imageURL, title="", msg=""):
		debug("> getImage()")
		success = False
		self.filename = os.path.join(DIR_CACHE, os.path.basename(imageURL))
		success = fileExist(self.filename)
		if not success:
			dialogProgress.create(title, __language__(202), msg)
			success = fetchURL(imageURL, self.filename, isImage=True)
	#		success = fetchCookieURL(imageURL, self.filename, isImage=True, newRequest=self.newURLRequest)
			dialogProgress.close()
		else:
			debug("image filename exists")

		if success:
			imageX, imageY, imageW, imageH = self.calcImageDims()
			self.showImage(imageX, imageY, imageW, imageH)
			self.newURLRequest = False
		debug("< getImage() success="+str(success))
		return success

#################################################################################################################
class Items:
	def __init__(self, title, link):
		self.title	= title
		self.link	= link

	def getTitle(self):
		return self.title

	def getLink(self):
		return self.link

#################################################################################################################
class Comics:
	""" Class to scrape from Comics.com """
	def __init__(self):
		debug("******* Comics() init")
		self.source = "http://www.comics.com/mycomics/html/categories_alpha.html"
		self.linkprefix="http://www.comics.com/"
		self.feeds = []
		self.items = []
		self.feedsList = []
		self.itemsList = []
		self.reTodaysEdition = '<img src="([^"\'<>]+)" alt=\"(Today\'s Comic)\"'
		self.reCalender = 'href=\"([^\"\'<>]+)\"><FONT>(.+?)<'
		self.reFeed = '<option value="([^"\'<>]+)">([^<>]+)<'

	def getName(self):
		return "Comics.com"

	def setupFeeds(self):
		debug("> Comics().setupFeeds()")

		if not self.feeds:
			html = fetchURL(self.source)
			if html:
				matches = findAllRegEx(html, self.reFeed)
				for match in matches:
					if len(match) >= 2:	# must have title & link
						dict = {}				
						title = decodeEntities(cleanHTML(match[1]))
						dict[ELEMENT_LINK] = self.linkprefix+match[0]
						dict[ELEMENT_TITLE] = title
						self.feedsList.append(title)
						self.feeds.append(RSSNode(dict))

		sz = len(self.feeds)
		debug("< Comics().setupFeeds() Feeds: " + str(sz))
		return sz


	# Load selected feed from saved url
	def downloadFeed(self, pos):
		debug("> Comics().downloadFeed() pos: " + str(pos))

		self.items = []
		self.itemsList = []
		url = self.feeds[pos].getElement(ELEMENT_LINK)

		# download editions from link
		html = fetchURL(url)
		if html:
			debug ("  add TODAYS edition")
			self.addItemsFromHTML(html, self.reTodaysEdition, True)		# add todays edition 
			debug ("  add CALENDER editions")
			self.addItemsFromHTML(html, self.reCalender, True)			# add last 30 days editions

		sz = len(self.itemsList)
		debug("< Comics().downloadFeed() Items: " + str(sz))
		return sz


	def addItemsFromHTML(self, html, regex, addToItems):
		debug("> Comics().addItemsFromHTML() addToItems: " + str(addToItems))

		item = None
		matches = findAllRegEx(html, regex)
		for m in matches:
			url = self.linkprefix + m[0]
			title = decodeEntities(cleanHTML(m[1]))
			item = Items(title, url)

			# if not adding to items, stop processing after first match
			if addToItems:
				self.items.append(item)
				self.itemsList.append(title)
			else:
				break

		debug("< Comics().addItemsFromHTML()")
		return item


	def getItemLink(self, pos):
		debug("> Comics().getItemLink() pos: " + str(pos))

		self.imgLinks = []
		title=""
		link = self.items[pos].getLink()
		imgURL = isImageURL(link)
		if not imgURL:
			html = fetchURL(link)
			if html:
				# get todays edition, dont add to itemlist
				item = self.addItemsFromHTML(html, self.reTodaysEdition, False)
				if item:
					imgURL = item.getLink()
					title = item.getTitle()

		if imgURL:
			self.imgLinks.append((imgURL,title))

		debug("< Comics().getItemLink()")
		return self.imgLinks

	# create a feeds list of titles
	def getFeedsList(self):
		debug("Comics().getFeedsList()")
		return self.feedsList

	# create a items list of titles
	def getItemsList(self):
		debug("Comics().getItemsList()")
		return self.itemsList

	def getInfo(self, pos):
		debug("Comics().getInfo() pos: " + str(pos))
		return self.feeds[pos]

	def getItemImageLink(self, pos=0):
		debug("> getItemImageLink()")
		try:
			return self.imgLinks[pos]
		except:
			return []


#################################################################################################################
class Tapestry:
	""" Class to scrape from Tapestry.com. """
	def __init__(self):
		debug("******* Tapestry() init")
		self.source = "http://www.tapestrycomics.com/tapestry.xml"
		self.feeds = []
		self.items = []
		self.feedsList = []
		self.itemsList = []
		self.rssparser = None

		# used to parse the XML
		# just items, no item attributes
		self.feedElements = {ELEMENT_TITLE:[], ELEMENT_LINK:[],ELEMENT_DESC:[]}

	def getName(self):
		return "Tapestry"

	# Get feeds if not got them already
	def setupFeeds(self):
		debug("> Tapestry().setupFeeds()")
		self.rssparser = RSSParser2()
		self.feedsList = []
		self.feeds = []

		# Get an array of Feeds class
		if self.rssparser.feed(url=self.source):
			self.feeds = self.rssparser.parse("item", self.feedElements)
			if self.feeds:
				badFeeds = []
				for feed in self.feeds:
					url = feed.getElement(ELEMENT_LINK)
					title = decodeEntities(cleanHTML(feed.getElement(ELEMENT_TITLE)))
					if isRSSLink(url) or isHTMLLink(url):
						self.feedsList.append(title)
					else:
						badFeeds.append(feed)

				for b in badFeeds:
					self.feeds.remove(b)

		sz = len(self.feedsList)
		debug("< Tapestry().setupFeeds() Feeds: " + str(sz))
		return sz


	# Load selected feed from saved url
	def downloadFeed(self, pos):
		debug("> Tapestry().downloadFeed() pos: " + str(pos))

		# get the feed url
		url = self.feeds[pos].getElement(ELEMENT_LINK)
		debug("feed url: " + url)

		self.lastFeedsPos = pos				# save this Feed list selectedPos
		if isRSSLink(url):
			sz = self.downloadFeedRSS(url)
		else:
			messageOK("Unsupported Feed Type","Select a different feed")
			sz = -1

		debug("< Tapestry().downloadFeed() Items: " + str(sz))
		return sz

	def downloadFeedRSS(self, url):
		debug("> Tapestry().downloadFeedRSS()")

		self.items = []
		self.itemsList = []
		# get the feed url
		if self.rssparser.feed(url=url):
			rssItems = self.rssparser.parse("item", self.feedElements)

			debug("create Items from XML")
			for rssItem in rssItems:
				title = rssItem.getElement(ELEMENT_TITLE)
				link = rssItem.getElement(ELEMENT_LINK)
				imgURL = isImageURL(link)
				if not imgURL:
					# is img in desc ?
					desc = rssItem.getElement(ELEMENT_DESC)
					imgURL = isImageURL(desc)

				if imgURL:
					self.items.append(Items(title, imgURL))					# store title and link
				else:
					self.items.append(Items(title, link))					# store title and link
				self.itemsList.append(title)

		sz = len(self.itemsList)
		debug("< Tapestry().downloadFeedRSS() Items: " + str(sz))
		return sz


	def getImagesFromHTML(self, link):
		debug("> getImagesFromHTML()")
		reList = ['img src="([^"\']+\.jpg)" (?:width|height).*?(?:width|height)=["\']\d+["\'] alt=["\'](.*?)["\']', 
#			'img src="([^"\']+(?:\.jpg|\.png))" alt=["\'](.*?)["\']',
			'src="(/comics/.*?(?:\.jpg|\.png|\.gif))"()',
			'img src="([^"\']+(?:\.jpg|\.png|\.gif))"()']

		# return [(url, title)]
		images = []
		url = ""
		title = ""
		dialogProgress.create(__language__(0), __language__(303), link)
		html = fetchURL(link)
		if html:
			for regex in reList:
				debug("regex=" + regex)
				images = findAllRegEx(html, regex)
				if images:
					break
		dialogProgress.close()

		if images:
			sz = len(images)
		else:
			sz = 0
		debug("< getImagesFromHTML() sz=" +str(sz))
		return images

	def prefixURL(self, origURL):
		debug("> prefixURL() " + origURL)
		newURL = origURL
		if not origURL.startswith('http') and not origURL.startswith('www'):
			debug ("  NO url prefix, get FEED prefix and add to URL")
			url = self.feeds[self.lastFeedsPos].getElement(ELEMENT_LINK)
			prefix = searchRegEx(url, REGEX_URL_PREFIX, re.MULTILINE + re.IGNORECASE)
			if prefix:
				newURL = prefix + origURL
		debug("< prefixURL() "+newURL)
		return newURL

	def getItemLink(self, pos):
		debug("> Tapestry().getItemLink() pos: " + str(pos))

		imgURL = ""
		self.imgLinks = []
		title = ""
		link = self.items[pos].getLink()
		link = self.prefixURL(link)

		# if link contains direct image link, use that
		imgURL = isImageURL(link)
		if not imgURL:
			debug("not an image url, scrape HTML using image regex")
			images = self.getImagesFromHTML(link)
			for imgURL, title in images:
				imgURL = urljoin(link, imgURL)
				self.imgLinks.append((imgURL,decodeEntities(cleanHTML(title))))
		else:
			self.imgLinks.append((imgURL,""))

		debug("< Tapestry().getItemLink()")
		return self.imgLinks

	# create a feeds list of titles
	def getFeedsList(self):
		debug("Tapestry().getFeedsList()")
		return self.feedsList

	# create a items list of titles
	def getItemsList(self):
		debug("Tapestry().getItemsList()")
		return self.itemsList

	def getInfo(self, pos):
		debug("Tapestry().getInfo() pos: " + str(pos))
		return self.feeds[pos]

	def getItemImageLink(self, pos=0):
		debug("> getItemImageLink()")
		try:
			return self.imgLinks[pos]
		except:
			return []


#################################################################################################################
class MyComics:
	""" RSS Feeds and/or html pages from external file mycomics.xml """
	def __init__(self):
		debug("******* MyComics() init")
		self.source = os.path.join(DIR_RESOURCES, "MyComics.xml")
		self.rssparser = None
		self.feeds = []
		self.items = []
		self.feedsList = []
		self.itemsList = []
		self.lastFeedsPos = 0
		

		# used to parse the XML
		# just items, no item attributes
		self.feedElements = {ELEMENT_TITLE:[],
							ELEMENT_LINK:[],
							ELEMENT_DESC:[],
							ELEMENT_RE_ITEM:[],
							ELEMENT_RE_IMAGE:[] }

	def getName(self):
		return "MyComics"

	# Get feeds if not got them already
	def setupFeeds(self):
		debug("> MyComics().setupFeeds()")

		self.rssparser = RSSParser2()
		self.feedsList = []
		self.feeds = []
		# Get an array of Feeds class
		if self.rssparser.feed(file=self.source):
			self.feeds = self.rssparser.parse("feed", self.feedElements)
			if self.feeds:
				for feed in self.feeds:
					title = feed.getElement(ELEMENT_TITLE)
					self.feedsList.append(title)

		sz = len(self.feedsList)
		debug("< MyComics().setupFeeds() Feeds: " + str(sz))
		return sz


	# Load selected feed from saved url
	def downloadFeed(self, pos):
		debug("> MyComics().downloadFeed() pos: " + str(pos))

		# rss or HTML feed? 
		url = self.feeds[pos].getElement(ELEMENT_LINK)
		debug("feed url: " + url)

		self.lastFeedsPos = pos				# save this Feed list selectedPos
		if isRSSLink(url):
			sz = self.downloadFeedRSS(url)
		else:
			sz = self.downloadFeedHTML(url)

		debug("< MyComics().downloadFeed() Items: " + str(sz))
		return sz


	def downloadFeedRSS(self, url):
		debug("> MyComics().downloadFeedRSS()")

		self.items = []
		self.itemsList = []
		# get the feed url
		if self.rssparser.feed(url=url):
			rssNodes = self.rssparser.parse("item", self.feedElements)
			for node in rssNodes:
				imgURL = ""
				title = node.getElement(ELEMENT_TITLE)
				link = node.getElement(ELEMENT_LINK)
				imgURL = isImageURL(link)
				if not imgURL:
					# is img in desc ?
					desc = node.getElement(ELEMENT_DESC)
					imgURL = isImageURL(desc)

				if imgURL:
					self.items.append(Items(title, imgURL))					# store title and link
				else:
					self.items.append(Items(title, link))					# store title and link
				self.itemsList.append(title)			# add title to ItemList

		sz = len(self.itemsList)
		debug("< MyComics().downloadFeedRSS() Items: " + str(sz))
		return sz


	def downloadFeedHTML(self, url):
		debug("> MyComics().downloadFeedHTML()")

		self.items = []
		self.itemsList = []

		# ensure we have the ITEM extracting regex before we proceed
		regex = self.feeds[self.lastFeedsPos].getElement(ELEMENT_RE_ITEM)
		if not regex:
			regex = self.feeds[self.lastFeedsPos].getElement(ELEMENT_RE_IMAGE)
			debug( "reItem missing, use reImage")

		if not regex:
			errTxt = "Regular Expression(s) missing."
			errTxt += "\nProvide: BOTH 'reItem' and 'reImage' if giving a page containing page links to images."
			errTxt += "\nProvide: JUST 'reImage' if giving a page containing image."
			errTxt += "\nSee script header for examples."
			debug(errTxt)
			messageOK("Comics - Error",errTxt)
		else:
			html = fetchURL(url)
			if html:
				debug("finding reItem matches")
				findRe = re.compile(regex, re.MULTILINE + re.IGNORECASE)
				matches = findRe.findall(html)
				for match in matches:
					# must have title & link
					if len(match) < 2:
						debug("  ITEM ignored, not enough data in regex match")
						continue
					debug ("0: " + match[0] + "  1: " + match[1])
					title = decodeEntities(match[1])
					self.items.append(Items(title, match[0]))
					self.itemsList.append(title)

		sz = len(self.itemsList)
		debug("< MyComics().downloadFeedHTML() Items: " + str(sz))
		return sz


	def prefixURL(self, origURL):
		debug("> prefixURL() " + origURL)
		newURL = origURL
		if not origURL.startswith('http') and not origURL.startswith('www'):
			url = self.feeds[self.lastFeedsPos].getElement(ELEMENT_LINK)
			debug ("  NO url prefix, get FEED prefix and add to URL " + url)
			prefix = searchRegEx(url, REGEX_URL_PREFIX, re.MULTILINE + re.IGNORECASE)
			if prefix:
				newURL = prefix + origURL	
		debug("< prefixURL() "+newURL)
		return newURL

	def getItemLink(self, pos):
		debug("> MyComics().getItemLink() pos: " + str(pos))
		errTxt = ""

		self.imgLinks = []
		title = ""
		link = self.items[pos].getLink()
		link = self.prefixURL(link)

		# if link contains direct image link, use that
		debug("check if url contains an image link")
		imgURL = isImageURL(link)
		if not imgURL:
			debug("NOT FOUND, scrape HTML using image regex")
			regex = self.feeds[self.lastFeedsPos].getElement(ELEMENT_RE_IMAGE)
			if not regex:
				errTxt = "Missing Regular Expression 'reImage', used to find Images.\nAdd to config file then try again."
				debug(errTxt)
				messageOK("Comics - Error",errTxt)
			else:
				html = fetchURL(link)
				if html:
					imgURL = searchRegEx(html, regex, re.MULTILINE + re.IGNORECASE)

		if imgURL:
			self.imgLinks.append((self.prefixURL(imgURL),title))
	
		debug("< MyComics().getItemLink()")
		return self.imgLinks

	# create a feeds list of titles
	def getFeedsList(self):
		debug("MyComics().getFeedsList()")
		return self.feedsList

	# create a items list of titles
	def getItemsList(self):
		debug("MyComics().getItemsList()")
		return self.itemsList

	def getInfo(self, pos):
		debug("MyComics().getInfo() pos: " + str(pos))
		return self.feeds[pos]

	def getItemImageLink(self, pos=0):
		debug("> getItemImageLink()")
		try:
			return self.imgLinks[pos]
		except:
			return []


######################################################################################
def update_script(quite=False, notifyNotFound=False):
	xbmc.output( "> update_script() quite=%s" %quite)

	updated = False
	up = update.Update(__language__, __scriptname__)
	version = up.getLatestVersion(quite)
	xbmc.output("Current Version: " + __version__ + " Tag Version: " + version)
	if version != "-1":
		if __version__ < version:
			if xbmcgui.Dialog().yesno( __language__(0), 
								"%s %s %s." % ( __language__(1006), version, __language__(1002) ), \
								__language__(1003)):
				updated = True
				up.makeBackup()
				up.issueUpdate(version)
		elif notifyNotFound:
			dialogOK(__language__(0), __language__(1000))
#	elif not quite:
#		dialogOK(__language__(0), __language__(1030))				# no tagged ver found

	del up
	xbmc.output( "< _update_script() updated=%s" % updated)
	return updated


#############################################################################################
# BEGIN !
#############################################################################################
makeDir(DIR_CACHE)
comics = GUI("script-Comics-main.xml", DIR_RESOURCES)
comics.doModal()
del comics

debug("exiting script, housekeeping ...")
rmtree( DIR_CACHE, ignore_errors=True )

# remove modules/globals
moduleList = ['bbbLib', 'bbbSkinGUILib']
for m in moduleList:
	try:
		del sys.modules[m]
		xbmc.output("del sys.module: " + m)
	except: pass

# remove other globals
try:
	del dialogProgress
except: pass

# goto xbmc home window
#try:
#	xbmc.executebuiltin('XBMC.ReplaceWindow(0)')
#except: pass