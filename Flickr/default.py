#########################################################################
# Flickr BETA
# 
# Author:	Jon Maddox
# http://www.jonsthoughtsoneverything.com
# http://xbmc.blogspot.com
# Version:	BETA
# Date:		07-09-05
# Access all of your stored photos directly from flickr
#
# Modified by IceAge to fix URL paths after Flickr server udpates
# Contact IceAge at dc_coder@hotmail.com
# Version:	BETA.01
# Date:		02-27-07
#
# Modified by Gigantisch to use FlickrClient 0.2 and urllib2 to handle HTTP 302 status
# Contact Gigantisch at gigantisch@gmail.com
# Version:	BETA.02
# Date:		12-18-07
#
# To install:
# Place entire Flickr directory in your Scripts folder and launch default.py
# Enter your email address in the settings panel to access your photos (requires restart)
#
# Sign up for flickr here:
# http://www.flickr.com/
#
#########################################################################
# Contributions
#
# Universal Feed Parser
# Copyright 2002-4 by Mark Pilgrim
# http://feedparser.org
#
# FlickrClient
# Copyright (c) 2004 Michele Campeotto
# http://micampe.it/things/flickrclient
#
# imageviewer.py
# Copyright (c) 2004 Aslak Grinsted
#
# settingsmgr.py
# Copyright (c) 2004 Aslak Grinsted
#
# xmltramp
# Copyright (c) 2003 Aaron Swartz. GNU GPL 2.
# http://www.aaronsw.com/
#
# Thanks to these guys for the scripts
# Thanks to alexpoet for his tutorial
#
# 
##########################################

import os, string, re, sys
import urllib
#import urllib2
import xbmc, xbmcgui

ROOT = os.getcwd().replace(";","")+"\\"
sys.path.insert(0, ROOT+'include')
import xbmc, xbmcgui
try: Emulating = xbmcgui.Emulating
except: Emulating = False
import imageviewer
import settingsmgr
from FlickrClient import *
from math import fmod

# Get Action Codes
ACTION_MOVE_LEFT 		= 1
ACTION_MOVE_RIGHT		= 2
ACTION_MOVE_UP			= 3
ACTION_MOVE_DOWN		= 4
ACTION_PAGE_DOWN        = 5
ACTION_PAGE_UP        	= 6
ACTION_PREVIOUS_MENU	= 10
ACTION_PARENT_DIR		= 9
ACTION_NEXT_ITEM		= 14
ACTION_PREV_ITEM		= 15

# GLOBALS
client = FlickrClient(API_KEY)
CACHE = ROOT + "\\cache\\"
SETTINGS_FILE = ROOT + "include\\settings.xml"
settings=settingsmgr.ReadSettings(SETTINGS_FILE)
SKIN_FOLDER = settings['skin']
if settings['aspect'] == 0:
	SCREEN_ASPECT=16.0/9.0
else:
	SCREEN_ASPECT=4.0/3.0

set_hash = {}
setChoice_hash = []
photo_hash = {}
buttons = {}
images = {}
loginError = 0

try:
	# collect all of the current user's information
	userID = settings['email']
	tmpUser = client.flickr_people_findByEmail(find_email=userID)
	user = client.flickr_people_getInfo(user_id=tmpUser('nsid'))
	# add this to keep the code cleaner
	userID = user('nsid')
except:
	loginError = 1
	okError = xbmcgui.Dialog()
	if userID == "Change Me":
		okError.ok("Flickr","Oops. Enter an email address and restart.")
	else:
		okError.ok("Flickr","Invalid or incorrect email address.")

class Flickr(xbmcgui.Window):
	def __init__(self):
	
		if Emulating: xbmcgui.Window.__init__(self)
		self.X = ( float(self.getWidth())  / float(720) )
		self.Y = ( float(self.getHeight()) / float(480) )
	
		self.addControl(xbmcgui.ControlImage(0,0,int(720*self.X),int(576*self.Y),ROOT + "skins\\" + SKIN_FOLDER + "\\background.png"))
		self.addControl(xbmcgui.ControlImage(int(75*self.X),int(40*self.Y),int(111*self.X),int(65*self.Y),ROOT + "skins\\" + SKIN_FOLDER + "\\logo.png"))
		self.buddyShadow = xbmcgui.ControlImage(int(229*self.X),int(44*self.Y),int(60*self.X),int(60*self.Y),ROOT + "skins\\" + SKIN_FOLDER + "\\button_nofocus.png")
		self.addControl(self.buddyShadow)
		self.myPhotos = xbmcgui.ControlButton(int((70*self.X)),int(115*self.Y),int(120*self.X),int(26*self.Y),"My Photos")
		self.addControl(self.myPhotos)
		self.myFavorites = xbmcgui.ControlButton(int((70*self.X)),int(145*self.Y),int(120*self.X),int(26*self.Y),"My Favorites")
		self.addControl(self.myFavorites)
		self.photoSets = xbmcgui.ControlButton(int((70*self.X)),int(175*self.Y),int(120*self.X),int(26*self.Y),"My Photo Sets")
		self.addControl(self.photoSets)
		self.publicPhotos = xbmcgui.ControlButton(int((70*self.X)),int(205*self.Y),int(120*self.X),int(26*self.Y),"Public Photos")
		self.addControl(self.publicPhotos)
		self.settingsButton = xbmcgui.ControlButton(int((70*self.X)),int(235*self.Y),int(120*self.X),int(26*self.Y),"Settings")
		self.addControl(self.settingsButton)
		self.nextArrow = xbmcgui.ControlButton(int(530*self.X),int(410*self.Y),int(63*self.X),int(28*self.Y),"",ROOT + "skins\\" + SKIN_FOLDER + "\\arrow_next_focus.png",ROOT + "skins\\" + SKIN_FOLDER + "\\arrow_next.png")
		self.addControl(self.nextArrow)
		self.previousArrow = xbmcgui.ControlButton(int(290*self.X),int(410*self.Y),int(63*self.X),int(28*self.Y),"",ROOT + "skins\\" + SKIN_FOLDER + "\\arrow_previous_focus.png",ROOT + "skins\\" + SKIN_FOLDER + "\\arrow_previous.png")
		self.addControl(self.previousArrow)

		# dialogs
		if (not Emulating): self.progress = xbmcgui.DialogProgress()
		self.okBox = xbmcgui.Dialog()

		self.selectedControl = "myPhotos"
		self.currentPage = 1;
		self.maxPages = 1;
		self.currentType = "";
		self.setFocus(self.myPhotos)
		self.photoSetId = "";

		print str(loginError)
		
		if loginError == 0 :
			self.buddyName = xbmcgui.ControlLabel(int(290*self.X),int(78*self.Y),int(200*self.X),int(30*self.Y),str(user.username) + "'s Photos")
			self.addControl(self.buddyName)
			self.makedir(userID)
			self.setBuddyIcon()
			self.setPhotoSetList(userID)
			self.setMyPhotos(1);

	
	def onAction(self, action):
		if action == ACTION_PREVIOUS_MENU:
			self.close()
		
		if action == ACTION_PARENT_DIR: 		
			self.buddyName.setLabel(self.currentType)
			self.turnPage( "forward")

		if action in ( ACTION_PAGE_UP, ACTION_NEXT_ITEM ):
			# self.buddyName.setLabel("right trigger")
			self.turnPage("forward")

		if action in ( ACTION_PAGE_DOWN, ACTION_PREV_ITEM ):
			# self.buddyName.setLabel("left trigger")
			self.turnPage("back")
			
		if action == ACTION_MOVE_RIGHT: 
			if self.selectedControl == "myPhotos":
				self.selectedControl = "myButton0"
				self.setFocus(buttons[0])
			elif self.selectedControl == "myFavorites":
				self.selectedControl = "myButton0"
				self.setFocus(buttons[0])
			elif self.selectedControl == "photoSets":
				self.selectedControl = "myButton0"
				self.setFocus(buttons[0])
			elif self.selectedControl == "publicPhotos":
				self.selectedControl = "myButton0"
				self.setFocus(buttons[0])
			elif self.selectedControl == "settingsButton":
				self.selectedControl = "myButton0"
				self.setFocus(buttons[0])
			elif self.selectedControl == "myFavorites":
				self.selectedControl = "myButton0"
				self.setFocus(buttons[0])
			elif self.selectedControl == "myButton0" and buttons.has_key(1):
				self.selectedControl = "myButton1"
				self.setFocus(buttons[1])
			elif self.selectedControl == "myButton1" and buttons.has_key(2):
				self.selectedControl = "myButton2"
				self.setFocus(buttons[2])
			elif self.selectedControl == "myButton2" and buttons.has_key(3):
				self.selectedControl = "myButton3"
				self.setFocus(buttons[3])
			elif self.selectedControl == "myButton4" and buttons.has_key(5):
				self.selectedControl = "myButton5"
				self.setFocus(buttons[5])
			elif self.selectedControl == "myButton5" and buttons.has_key(6):
				self.selectedControl = "myButton6"
				self.setFocus(buttons[6])
			elif self.selectedControl == "myButton6" and buttons.has_key(7):
				self.selectedControl = "myButton7"
				self.setFocus(buttons[7])
			elif self.selectedControl == "myButton8" and buttons.has_key(9):
				self.selectedControl = "myButton9"
				self.setFocus(buttons[9])
			elif self.selectedControl == "myButton9" and buttons.has_key(10):
				self.selectedControl = "myButton10"
				self.setFocus(buttons[10])
			elif self.selectedControl == "myButton10" and buttons.has_key(11):
				self.selectedControl = "myButton11"
				self.setFocus(buttons[11])
			elif self.selectedControl == "nextArrow":
				self.selectedControl = "previousArrow"
				self.setFocus(self.previousArrow)
			elif self.selectedControl == "previousArrow":
				self.selectedControl = "nextArrow"
				self.setFocus(self.nextArrow)

		if action == ACTION_MOVE_DOWN: 
			if self.selectedControl == "myButton0" and buttons.has_key(4):
				self.selectedControl = "myButton4"
				self.setFocus(buttons[4])
			elif self.selectedControl == "myButton4" and buttons.has_key(8):
				self.selectedControl = "myButton8"
				self.setFocus(buttons[8])
			elif self.selectedControl == "myButton1" and buttons.has_key(5):
				self.selectedControl = "myButton5"
				self.setFocus(buttons[5])
			elif self.selectedControl == "myButton5" and buttons.has_key(9):
				self.selectedControl = "myButton9"
				self.setFocus(buttons[9])
			elif self.selectedControl == "myButton2" and buttons.has_key(6):
				self.selectedControl = "myButton6"
				self.setFocus(buttons[6])
			elif self.selectedControl == "myButton6" and buttons.has_key(10):
				self.selectedControl = "myButton10"
				self.setFocus(buttons[10])
			elif self.selectedControl == "myButton3" and buttons.has_key(7):
				self.selectedControl = "myButton7"
				self.setFocus(buttons[7])
			elif self.selectedControl == "myButton7" and buttons.has_key(11):
				self.selectedControl = "myButton11"
				self.setFocus(buttons[11])
			elif self.selectedControl == "myButton8" or self.selectedControl == "myButton9" :
				self.selectedControl = "previousArrow"
				self.setFocus(self.previousArrow)				
			elif self.selectedControl == "previousArrow":
				self.selectedControl = "myButton0"
				self.setFocus(buttons[0])				
			elif self.selectedControl == "myButton10" or self.selectedControl == "myButton11" :
				self.selectedControl = "nextArrow"
				self.setFocus(self.nextArrow)
			elif self.selectedControl == "myPhotos":
				self.selectedControl = "myFavorites"
				self.setFocus(self.myFavorites)
			elif self.selectedControl == "myFavorites":
				self.selectedControl = "photoSets"
				self.setFocus(self.photoSets)
			elif self.selectedControl == "photoSets":
				self.selectedControl = "publicPhotos"
				self.setFocus(self.publicPhotos)
			elif self.selectedControl == "publicPhotos":
				self.selectedControl = "settingsButton"
				self.setFocus(self.settingsButton)
			elif self.selectedControl == "settingsButton":
				self.selectedControl = "myPhotos"
				self.setFocus(self.myPhotos)

		if action == ACTION_MOVE_UP: 
			if self.selectedControl == "myButton8" and buttons.has_key(4):
				self.selectedControl = "myButton4"
				self.setFocus(buttons[4])
			elif self.selectedControl == "myButton4" and buttons.has_key(0):
				self.selectedControl = "myButton0"
				self.setFocus(buttons[0])
			elif self.selectedControl == "myButton0":
				self.selectedControl = "previousArrow"
				self.setFocus(self.previousArrow)
			elif self.selectedControl == "myButton9" and buttons.has_key(5):
				self.selectedControl = "myButton5"
				self.setFocus(buttons[5])
			elif self.selectedControl == "myButton5" and buttons.has_key(1):
				self.selectedControl = "myButton1"
				self.setFocus(buttons[1])
			elif self.selectedControl == "myButton10" and buttons.has_key(6):
				self.selectedControl = "myButton6"
				self.setFocus(buttons[6])
			elif self.selectedControl == "myButton6" and buttons.has_key(2):
				self.selectedControl = "myButton2"
				self.setFocus(buttons[2])
			elif self.selectedControl == "myButton11" and buttons.has_key(7):
				self.selectedControl = "myButton7"
				self.setFocus(buttons[7])
			elif self.selectedControl == "myButton7" and buttons.has_key(3):
				self.selectedControl = "myButton3"
				self.setFocus(buttons[3])
			elif self.selectedControl == "myPhotos":
				self.selectedControl = "settingsButton"
				self.setFocus(self.settingsButton)
			elif self.selectedControl == "myFavorites":
				self.selectedControl = "myPhotos"
				self.setFocus(self.myPhotos)
			elif self.selectedControl == "photoSets":
				self.selectedControl = "myFavorites"
				self.setFocus(self.myFavorites)
			elif self.selectedControl == "publicPhotos":
				self.selectedControl = "photoSets"
				self.setFocus(self.photoSets)
			elif self.selectedControl == "settingsButton":
				self.selectedControl = "publicPhotos"
				self.setFocus(self.publicPhotos)
			elif self.selectedControl == "previousArrow":
				self.selectedControl = "myButton8"
				self.setFocus(buttons[8])				
			elif self.selectedControl == "nextArrow" and buttons.has_key(10):
				self.selectedControl = "myButton10"
				self.setFocus(buttons[10])				
			elif self.selectedControl == "nextArrow" and buttons.has_key(9):
				self.selectedControl = "myButton9"
				self.setFocus(buttons[9])				
			elif self.selectedControl == "nextArrow" and buttons.has_key(8):
				self.selectedControl = "myButton8"
				self.setFocus(buttons[8])				
				


		if action == ACTION_MOVE_LEFT: 
			if self.selectedControl == "myButton3" and buttons.has_key(2):
				self.selectedControl = "myButton2"
				self.setFocus(buttons[2])
			elif self.selectedControl == "myButton2" and buttons.has_key(1):
				self.selectedControl = "myButton1"
				self.setFocus(buttons[1])
			elif self.selectedControl == "myButton1" and buttons.has_key(0):
				self.selectedControl = "myButton0"
				self.setFocus(buttons[0])
			elif self.selectedControl == "myButton0":
				self.selectedControl = "myPhotos"
				self.setFocus(self.myPhotos)
			elif self.selectedControl == "myButton7" and buttons.has_key(6):
				self.selectedControl = "myButton6"
				self.setFocus(buttons[6])
			elif self.selectedControl == "myButton6" and buttons.has_key(5):
				self.selectedControl = "myButton5"
				self.setFocus(buttons[5])
			elif self.selectedControl == "myButton5" and buttons.has_key(4):
				self.selectedControl = "myButton4"
				self.setFocus(buttons[4])
			elif self.selectedControl == "myButton4":
				self.selectedControl = "myPhotos"
				self.setFocus(self.myPhotos)
			elif self.selectedControl == "myButton11" and buttons.has_key(10):
				self.selectedControl = "myButton10"
				self.setFocus(buttons[10])
			elif self.selectedControl == "myButton10" and buttons.has_key(9):
				self.selectedControl = "myButton9"
				self.setFocus(buttons[9])
			elif self.selectedControl == "myButton9" and buttons.has_key(8):
				self.selectedControl = "myButton8"
				self.setFocus(buttons[8])
			elif self.selectedControl == "myButton8":
				self.selectedControl = "myPhotos"
				self.setFocus(self.myPhotos)
			elif self.selectedControl == "nextArrow":
				self.selectedControl = "previousArrow"
				self.setFocus(self.previousArrow)
			elif self.selectedControl == "previousArrow":
				self.selectedControl = "nextArrow"
				self.setFocus(self.nextArrow)
				
				

	def onControl(self, control):
		if control == self.photoSets:
			self.choosePhotoSet()
		if control == self.publicPhotos:
			self.setPublicPhotos(1)
		if control == self.myPhotos:
			self.setMyPhotos(1)
		if control == self.myFavorites:
			self.setMyFavorites(1)
		if control == self.settingsButton:
			if(settingsmgr.OpenControlPanel(SETTINGS_FILE)):
			    settings = settingsmgr.ReadSettings(SETTINGS_FILE)
			    # user = loadUserData(settings['email'])
		if self.selectedControl == "myButton0" and buttons.has_key(0):
			self.showPhoto(photo_hash[0])
		elif self.selectedControl == "myButton1" and buttons.has_key(1):
			self.showPhoto(photo_hash[1])
		elif self.selectedControl == "myButton2" and buttons.has_key(2):
			self.showPhoto(photo_hash[2])
		elif self.selectedControl == "myButton3" and buttons.has_key(3):
			self.showPhoto(photo_hash[3])
		elif self.selectedControl == "myButton4" and buttons.has_key(4):
			self.showPhoto(photo_hash[4])
		elif self.selectedControl == "myButton5" and buttons.has_key(5):
			self.showPhoto(photo_hash[5])
		elif self.selectedControl == "myButton6" and buttons.has_key(6):
			self.showPhoto(photo_hash[6])
		elif self.selectedControl == "myButton7" and buttons.has_key(7):
			self.showPhoto(photo_hash[7])
		elif self.selectedControl == "myButton8" and buttons.has_key(8):
			self.showPhoto(photo_hash[8])
		elif self.selectedControl == "myButton9" and buttons.has_key(9):
			self.showPhoto(photo_hash[9])
		elif self.selectedControl == "myButton10" and buttons.has_key(10):
			self.showPhoto(photo_hash[10])
		elif self.selectedControl == "myButton11" and buttons.has_key(11):
			self.showPhoto(photo_hash[11])
		elif self.selectedControl == "nextArrow":
			self.turnPage("forward")
		elif self.selectedControl == "previousArrow":
			self.turnPage("back")




	#def initSettings(self):
		

	def showPhoto(self, photoData):

		photoStuff = string.split(photoData,'_')
		photoID = photoStuff[0]
		photoSecret = photoStuff[1]
 		# photo = client.flickr_photos_getInfo(photo_id=photoID, secret=photoSecret)
 		photo = client.getPhotoInfo(photoID, photoSecret)
		photoSizes = client.flickr_photos_getSizes(photo_id=photoID)
		# loop through to find the Medium-size image
		for size in photoSizes:
#			if (size('label') == "Large") or (size('label') == "Original"):
			if (size('label') == "Medium"):
				original = size('source')

		url = string.split(original,'/')
		filename = url[4]

		# Doesn't support stuff other than gif and jpg yet because of the imageviewer class, test and give notice
		tmpName = string.split(filename,'.')
		if string.upper(tmpName[1]) == "JPG" or string.upper(tmpName[1]) == "GIF":
			# open progress dialog			
			if (not Emulating): self.progress.create("Flickr", "Downloading image...")
			photoPath = userID + "\\" + filename
			#download image
			self.downloadPhoto(original,photoPath)
			if (not Emulating): self.progress.close()
			#display image
			imageviewer.ViewImage((CACHE + photoPath).encode(), SCREEN_ASPECT, photo)
		else:
			self.okBox.ok("Flickr","The Flickr plugin only supports GIF and JPG.")
		
		
	def makedir(self,path):
		try:
			os.mkdir((CACHE + path).encode())
		except:
			print "Dir Exists"

	def setBuddyIcon(self):
		if user('iconserver') > 0:
			photoURL = "http://static.flickr.com/" + user('iconserver') + "/buddyicons/" + userID + ".jpg"
		else:
			photoURL = "http://www.flickr.com/images/buddyicon.jpg"

		print "photoURL: " + photoURL
		photoPath = userID + "\\" + userID + "_s.jpg"
		self.downloadPhotoNoCache(photoURL,photoPath)
		
		self.buddyIcon = xbmcgui.ControlImage(int(235*self.X),int(50*self.Y),int(48*self.X),int(48*self.Y),CACHE + photoPath)
		self.addControl(self.buddyIcon)
    
	def getPhotoSets(self,userID):
		photoSets = client.flickr_photosets_getList(user_id=userID)
		return photoSets	

	def setPhotoSetList(self,userID):
		setCounter = 0;
		photoSets = self.getPhotoSets(userID);
		for set in photoSets:
			set_hash[setCounter] = set('id')
			setChoice_hash.append(str(set.title))
			setCounter = setCounter + 1;

	def choosePhotoSet(self):
		dialog = xbmcgui.Dialog() 
		choice = dialog.select("Choose a photo set", setChoice_hash)
		page=1
		self.photoSetId = set_hash[choice]
		self.setPhotoSet(self.photoSetId, page)

			
	def downloadPhoto(self,photoURL,photoPath):
		loc = urllib.FancyURLopener()
		if not os.path.exists((CACHE + photoPath).encode()):
			try:
				loc.retrieve(photoURL, (CACHE + photoPath).encode())
			except:
				print "download failed on" + photoURL
			loc.close()
		else:
			print "photo exists"			

	def downloadPhotoNoCache(self,photoURL,photoPath):
		loc = urllib.FancyURLopener()
		loc.retrieve(photoURL, (CACHE + photoPath).encode())
		loc.close()

	def turnPage(self, direction):
		if direction == "back" and not self.currentPage == 1:
			self.currentPage = self.currentPage - 1
		elif direction == "forward" and not self.currentPage == self.maxPages:
			self.currentPage = self.currentPage + 1 

		if self.currentType == "myPhotos":
			self.setMyPhotos(self.currentPage)
		elif self.currentType == "myFavorites":
			self.setMyFavorites(self.currentPage)
		elif self.currentType == "publicPhotos":
			self.setPublicPhotos(self.currentPage)
		elif self.currentType == "photoSet":
			self.setPhotoSet(self.photoSetId, self.currentPage)
		

	def setPhotoSet(self, photoSetID, page):
		if not self.currentType == "photoSet":
			self.currentType = "photoSet"
			page = 1
			self.currentPage = 1

		# clean up photo view
		self.unsetPhotos()
		
 		photos_all = client.flickr_photosets_getPhotos(photoset_id=photoSetID)
 		photos = photos_all[min((page-1)*12,len(photos_all)-1):min(page*12,len(photos_all))]
		self.setPhotos(photos)

	def setPublicPhotos(self, page):
		if not self.currentType == "publicPhotos":
			self.currentType = "publicPhotos"
			page = 1
			self.currentPage = 1

		# clean up photo view
		self.unsetPhotos()

		photos = client.flickr_photos_getRecent(per_page=12, page=page)
		self.setPhotos(photos)

	def setMyPhotos(self, page):
		if not self.currentType == "myPhotos":
			self.currentType = "myPhotos"
			page = 1
			self.currentPage = 1
	
		# clean up photo view
		self.unsetPhotos()

		photos = client.flickr_people_getPublicPhotos(user_id=userID,per_page=12, page=page)
		self.setPhotos(photos)

	def setMyFavorites(self, page):
		if not self.currentType == "myFavorites":
			self.currentType = "myFavorites"
			page = 1
			self.currentPage = 1

		# clean up photo view
		self.unsetPhotos()

		photos = client.flickr_favorites_getPublicList(user_id=userID,per_page=12, page=page)
		self.setPhotos(photos)

	
	def setPhotos(self, photos):

		# open progress dialog			
		if (not Emulating): self.progress.create("Flickr", "Downloading images...")
		photoCount = 1
		numPhotos = len(photos)
		for photo in photos:
			# update progress
			percent = int((photoCount*100)/numPhotos)
			if (not Emulating): self.progress.update(percent)
			# changed by IceAge
			# updated the URL to use the farm info
			photoURL = "http://farm" + photo('farm') + ".static.flickr.com/" + photo('server') + "/" + photo('id') + "_" + photo('secret') + "_s.jpg"
			photoPath = userID + "\\" + photo('id') + "_" + photo('secret') + "_s.jpg"

			self.downloadPhoto(photoURL, photoPath)
			photoCount = photoCount + 1
	
		if (not Emulating): self.progress.close()

		if (len(photos) > 12):
			numPhotos = 12
		else:
			numPhotos = len(photos)

		for i in range(0, numPhotos):
			photo = photos[i]
			imgURL = CACHE + userID + "\\" + photo('id') + "_" + photo('secret') + "_s.jpg" 
			#print imgURL
			buttons[i] = xbmcgui.ControlButton(int((225*self.X) + (int(fmod(i,4))*115)),int((105+100*int(i/4))*self.Y),int(95*self.X),int(95*self.Y),"",ROOT + "skins\\" + SKIN_FOLDER + "\\button_focus.png",ROOT + "skins\\" + SKIN_FOLDER + "\\button_nofocus.png")
			self.addControl(buttons[i]);
			images[i] = xbmcgui.ControlImage(int((235*self.X) + (int(fmod(i,4))*115)),int((115+100*int(i/4))*self.Y),int(75*self.X),int(75*self.Y),imgURL)
			self.addControl(images[i]);
			photo_hash[i] = photo('id') + "_" + photo('secret')
				
		
		p = re.compile('photoSet')
		m = p.match(self.currentType)

		if not m :
			self.maxPages = int(photos('pages'))


	def unsetPhotos(self):
		numPhotos = len(images)
		for i in range(0, numPhotos):
			self.removeControl(buttons[i])
			self.removeControl(images[i])
			del buttons[i]
			del images[i]
			del photo_hash[i]
			
			
myDisplay = Flickr()
myDisplay.doModal()
del myDisplay
	
