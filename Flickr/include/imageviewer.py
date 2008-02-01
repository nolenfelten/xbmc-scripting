# ScriptName    : imageviewer.py
# Version         = '0.5'
# Author        : Van der Phunck aka Aslak Grinsted. as@phunck.cmo <- not cmo but com
# Desc          : image viewer for xbmc python
#
# 
# 
#


import xbmc, xbmcgui
import Image,ImageFile
import sys, traceback
import os.path

ACTION_MOVE_LEFT        =  1    
ACTION_MOVE_RIGHT       =  2
ACTION_MOVE_UP          =  3
ACTION_MOVE_DOWN        =  4
ACTION_PAGE_UP          =  5 #left trigger
ACTION_PAGE_DOWN        =  6 #right trigger
ACTION_SELECT_ITEM      =  7 #A button
ACTION_HIGHLIGHT_ITEM   =  8 
ACTION_PARENT_DIR       =  9 #B button
ACTION_PREVIOUS_MENU    = 10 #back button
ACTION_SHOW_INFO        = 11
ACTION_PAUSE            = 12
ACTION_STOP             = 13
ACTION_NEXT_ITEM        = 14
ACTION_PREV_ITEM        = 15
ACTION_XBUTTON		= 18 #Y Button
ACTION_WHITEBUTTON	= 117 

ScriptPath              = os.getcwd()
if ScriptPath[-1]==';': ScriptPath=ScriptPath[0:-1]
if ScriptPath[-1]!='\\': ScriptPath=ScriptPath+'\\'


try: Emulating = xbmcgui.Emulating #Thanks alot to alexpoet for the xbmc.py,xmbcgui.py emulator. Very useful!
except: Emulating = False


def message(title, line1, line2='', line3=''):
	dialog = xbmcgui.Dialog()
	dialog.ok(title, line1, line2, line3)

def printLastError():
	e=sys.exc_info()
	traceback.print_exception(e[0],e[1],e[2])

def lastErrorString():
	return sys.exc_info()[1]

####################################################################################

def ViewImage(imagefile, ScreenAspectRatio=4.0/3.0, photo=None):
	iv=ImageViewer()
	iv.setPhoto(photo)
	iv.setImagefile(imagefile, ScreenAspectRatio)
	iv.doModal()
	del iv

class ImageViewer(xbmcgui.Window):
	def __init__(self):
		if Emulating: xbmcgui.Window.__init__(self)  #for emulator to work
		self.image = None
		self.photo = None
		self.title = self.description = self.tags = None
		self.showinfo = True
		
	def setPhoto(self, photo):
		self.photo = photo
		
	def setImagefile(self,imagefile,ScreenAspectRatio):
		try:
			self.imagefile = imagefile
			self.ScreenAspectRatio = ScreenAspectRatio
			im = Image.open(imagefile)
			self.imagesize = [ im.size[0], im.size[1] ]
	
			w = self.getWidth()
			h = self.getHeight()
			#Ratio - positions are then used given as percent
			self.xratio = float(w / 100.0)
			self.yratio = float(h / 100.0)
	
			self.asp = w / float(h * self.ScreenAspectRatio) #used for stretching images
	
			scalex = float(self.getWidth()) * .9 / float(im.size[0] * self.asp)
			scaley = float(self.getHeight()) * .9 / float(im.size[1])
			if scalex > scaley: scalex = scaley #keep aspect ratio
	
			self.zoom = scalex
			self.fullzoom = scalex
			self.center = [ 0, 0 ]
			
		
			#---------- SetUpControls ------------
					
			#PAL/NTSC Support:
	
			self.ShowImage()
		except:
			self.close()
			raise
		

	def ShowImage(self):
		if not (self.image is None):
			self.removeControl(self.image)
			self.image = None
		PicSize = (int(float(self.imagesize[0] * self.asp) * self.zoom), int(float(self.imagesize[1]) * self.zoom))
		w = self.getWidth()
		h = self.getHeight()
		
		dw = (w - PicSize[0]) * .5 * self.center[0]
		dh = (h - PicSize[1]) * .5 * self.center[1]
		
		self.image = xbmcgui.ControlImage(int(dw + (w - PicSize[0]) / 2), int(dh + (h - PicSize[1]) / 2), int(PicSize[0]), int(PicSize[1]), self.imagefile)
		self.addControl(self.image)

		if not (self.photo is None):
			if not (self.title is None):
				self.removeControl(self.title)
				self.removeControl(self.description)
				self.removeControl(self.tags)
				self.title = self.description = self.tags = None

			if self.showinfo:
				self.title = xbmcgui.ControlFadeLabel(10, 20, 800, 20, font='font16', textColor='0xFFCCCCCC')
				self.description = xbmcgui.ControlFadeLabel(10, 500, 600, 20, textColor='0xFFFFFF00')
				self.tags = xbmcgui.ControlFadeLabel(10, 520, 600, 20, textColor='0xFFFFFF00')
				self.addControl(self.title)
				self.addControl(self.description)
				self.addControl(self.tags)
				self.title.addLabel(self.photo.title)
				self.description.addLabel(self.photo.description)
				self.tags.addLabel(u' '.join(self.photo.tags))

		self.setFocus(self.image)


	def onAction(self, action):
		if (action == ACTION_PREVIOUS_MENU) or (action == ACTION_PARENT_DIR):
			self.close()
			return
		try:
			if action == ACTION_PAGE_UP:
				self.zoom = max(self.zoom / 1.5, self.fullzoom)  #zoom crashes?
				
			if action == ACTION_PAGE_DOWN:
				self.zoom = self.zoom * 1.5
				
			if action == ACTION_MOVE_LEFT:
				self.center[0] = max(self.center[0] - (.5 * self.fullzoom / self.zoom), -1.3)
				
			if action == ACTION_MOVE_RIGHT:
				self.center[0] = min(self.center[0] + (.5 * self.fullzoom / self.zoom), 1.3)

			if action == ACTION_MOVE_UP:
				self.center[1] = max(self.center[1] - (.5 * self.fullzoom / self.zoom), -1.3)
				
			if action == ACTION_MOVE_DOWN:
				self.center[1] = min(self.center[1] + (.5 * self.fullzoom / self.zoom), 1.3)
				
			if action == ACTION_SHOW_INFO:
				# message(self.photo.title, self.photo.description, u' '.join(self.photo.tags))
				self.showinfo = not self.showinfo
				
			#print(str((self.zoom, self.center)))
			self.ShowImage()
		except: 
			try:
				self.close()
				print('Error!') 
				printLastError()
			except: 
				pass

	def onControl(self,control):
		pass
