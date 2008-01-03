"""
 bbbLib.py

 General functions.
 
"""

import sys, os.path
import xbmc, xbmcgui
import os, re, unicodedata, traceback
import urllib, urllib2, socket
from string import strip, replace, find, rjust
import ConfigParser

# cookie stuff
import cookielib

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__title__ = "bbbLib"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '04-01-2008'
xbmc.output("Imported From: " + __scriptname__ + " title: " + __title__ + " Date: " + __date__)

DIR_HOME = sys.modules[ "__main__" ].DIR_HOME
DIR_RESOURCES = sys.modules[ "__main__" ].DIR_RESOURCES
DIR_RESOURCES_LIB = sys.modules[ "__main__" ].DIR_RESOURCES_LIB
DIR_GFX = sys.modules[ "__main__" ].DIR_GFX
DIR_USERDATA = sys.modules[ "__main__" ].DIR_USERDATA

__language__ = sys.modules[ "__main__" ].__language__

# setup cookiejar
cookiejar = cookielib.LWPCookieJar()       # This is a subclass of FileCookieJar that has useful load and save methods
urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
urllib2.install_opener(urlopener)

socket.setdefaulttimeout( 15 )

# KEYPAD CODES
ACTION_UNKNOWN			= 0
ACTION_MOVE_LEFT 	    = 1 	# Dpad
ACTION_MOVE_RIGHT	    = 2		# Dpad
ACTION_MOVE_UP		    = 3		# Dpad
ACTION_MOVE_DOWN	    = 4		# Dpad
ACTION_SCROLL_UP		= 5		# trigger up
ACTION_SCROLL_DOWN		= 6		# trigger down
ACTION_SELECT_ITEM	    = 7     # A
ACTION_HIGHLIGHT_ITEM	= 8		#
ACTION_PARENT_DIR	    = 9     # B
ACTION_PREVIOUS_MENU	= 10	# back btn
ACTION_REMOTE_INFO		= 11	# info on remote
ACTION_PAUSE		    = 12	# remote
ACTION_STOP		        = 13	# remote
ACTION_NEXT_ITEM	    = 14	# remote Skip Next
ACTION_PREV_ITEM	    = 15	# remote Skip Previous
ACTION_X_BUTTON 	    = 18    # X
ACTION_PAGE_UP		    = 111	# trigger left
ACTION_PAGE_DOWN	    = 112	# trigger right
ACTION_SHOW_INFO	    = 117	# white button
ACTION_Y_BUTTON 	    = 34	# Y

KEY_BUTTON_A                        = 256
KEY_BUTTON_B                        = 257
KEY_BUTTON_X                        = 258
KEY_BUTTON_Y                        = 259
KEY_BUTTON_BLACK                    = 260
KEY_BUTTON_WHITE                    = 261
KEY_BUTTON_LEFT_TRIGGER             = 262
KEY_BUTTON_RIGHT_TRIGGER            = 263
KEY_BUTTON_LEFT_THUMB_STICK         = 264
KEY_BUTTON_RIGHT_THUMB_STICK        = 265
KEY_BUTTON_RIGHT_THUMB_STICK_UP     = 266 # right thumb stick directions
KEY_BUTTON_RIGHT_THUMB_STICK_DOWN   = 267 # for defining different actions per direction
KEY_BUTTON_RIGHT_THUMB_STICK_LEFT   = 268
KEY_BUTTON_RIGHT_THUMB_STICK_RIGHT  = 269
KEY_BUTTON_DPAD_UP                  = 270
KEY_BUTTON_DPAD_DOWN                = 271
KEY_BUTTON_DPAD_LEFT                = 272
KEY_BUTTON_DPAD_RIGHT               = 273
KEY_BUTTON_START                    = 274
KEY_BUTTON_BACK                     = 275
KEY_BUTTON_LEFT_THUMB_BUTTON        = 276
KEY_BUTTON_RIGHT_THUMB_BUTTON       = 277
KEY_BUTTON_LEFT_ANALOG_TRIGGER      = 278
KEY_BUTTON_RIGHT_ANALOG_TRIGGER     = 279
KEY_BUTTON_LEFT_THUMB_STICK_UP      = 280 # left thumb stick  directions
KEY_BUTTON_LEFT_THUMB_STICK_DOWN    = 281 # for defining different actions per direction
KEY_BUTTON_LEFT_THUMB_STICK_LEFT    = 282
KEY_BUTTON_LEFT_THUMB_STICK_RIGHT   = 283

# ACTION CODE GROUPS
SELECT_ITEM = ( ACTION_SELECT_ITEM, ACTION_REMOTE_INFO, KEY_BUTTON_A, 61453, )
EXIT_SCRIPT = ( ACTION_PREVIOUS_MENU, 247, KEY_BUTTON_BACK, 61467, )
CANCEL_DIALOG = EXIT_SCRIPT + (ACTION_PARENT_DIR, 216, KEY_BUTTON_B, 61448, )
TOGGLE_DISPLAY = ( 216, KEY_BUTTON_B, 61448, )
CONTEXT_MENU = ( 229, KEY_BUTTON_WHITE, 61533, )
MOVEMENT_UP = ( ACTION_MOVE_UP, KEY_BUTTON_LEFT_THUMB_STICK_UP, KEY_BUTTON_RIGHT_THUMB_STICK_UP, KEY_BUTTON_DPAD_UP, 61478, )
MOVEMENT_DOWN = ( ACTION_MOVE_DOWN, KEY_BUTTON_LEFT_THUMB_STICK_DOWN,KEY_BUTTON_RIGHT_THUMB_STICK_DOWN, KEY_BUTTON_DPAD_DOWN, 61480, )
MOVEMENT_LEFT = ( ACTION_MOVE_LEFT, KEY_BUTTON_LEFT_THUMB_STICK_LEFT, KEY_BUTTON_RIGHT_THUMB_STICK_LEFT,KEY_BUTTON_DPAD_LEFT, 61477, )
MOVEMENT_RIGHT = (  ACTION_MOVE_RIGHT, KEY_BUTTON_LEFT_THUMB_STICK_RIGHT, KEY_BUTTON_RIGHT_THUMB_STICK_RIGHT, KEY_BUTTON_DPAD_RIGHT, 61479, )
MOVEMENT = MOVEMENT_UP + MOVEMENT_DOWN + MOVEMENT_LEFT + MOVEMENT_RIGHT

XBFONT_LEFT       = 0x00000000
XBFONT_RIGHT      = 0x00000001
XBFONT_CENTER_X   = 0x00000002
XBFONT_CENTER_Y   = 0x00000004
XBFONT_TRUNCATED  = 0x00000008

KBTYPE_ALPHA = -1
KBTYPE_NUMERIC = 0
KBTYPE_DATE = 1
KBTYPE_TIME = 2
KBTYPE_IP = 3

# xbmc skin FONT NAMES
FONT10 = 'font10'
FONT11 = 'font11'
FONT12 = 'font12'
FONT13 = 'font13'
FONT14 = 'font14'
FONT18 = 'font18'

# GFX - for library funcs
BACKGROUND_FILENAME = os.path.join(DIR_GFX,'background.png')
HEADER_FILENAME = os.path.join(DIR_GFX,'header.png')
FOOTER_FILENAME = os.path.join(DIR_GFX,'footer.png')
LOGO_FILENAME = os.path.join(DIR_GFX,'logo.png')
BTN_A_FILENAME = os.path.join(DIR_GFX,'abutton.png')
BTN_B_FILENAME = os.path.join(DIR_GFX,'bbutton.png')
BTN_X_FILENAME = os.path.join(DIR_GFX,'xbutton.png')
BTN_Y_FILENAME = os.path.join(DIR_GFX,'ybutton.png')
BTN_WHITE_FILENAME = os.path.join(DIR_GFX,'whitebutton.png')
LIST_HIGHLIGHT_FILENAME = os.path.join(DIR_GFX,'list_highlight.png')
FRAME_FOCUS_FILENAME = os.path.join(DIR_GFX,'frame_focus.png')
FRAME_NOFOCUS_FILENAME = os.path.join(DIR_GFX,'frame_nofocus.png')
FRAME_NOFOCUS_LRG_FILENAME = os.path.join(DIR_GFX,'frame_nofocus_large.png')
README_FILENAME = os.path.join(DIR_HOME , 'readme.txt')
CHANGELOG_FILENAME = os.path.join(DIR_HOME , 'changelog.txt')
PANEL_FILENAME = 'dialog-panel.png'
PANEL_FILENAME_MC360 = 'dialog-panel_mc360.png'

dialogProgress = xbmcgui.DialogProgress()
# rez GUI defined in
REZ_W = 720
REZ_H = 576

try: Emulating = xbmcgui.Emulating
except: Emulating = False

#######################################################################################################################    
# DEBUG - display indented information
#######################################################################################################################    
DEBUG = False
debugIndentLvl = 0	# current indentation level
def debug( value ):
	global debugIndentLvl
	if (DEBUG and value):
		try:
			if value[0] == ">": debugIndentLvl += 2
			pad = rjust("", debugIndentLvl)
			print pad + str(value)
			if value[0] == "<": debugIndentLvl -= 2
		except:
			print value

#################################################################################################################
def messageOK(title='', line1='', line2='',line3=''):
	xbmcgui.Dialog().ok(title ,line1,line2,line3)


#################################################################################################################
def dialogOK(title, line1='', line2='',line3=''):
	xbmcgui.Dialog().ok(title ,line1,line2,line3)

#################################################################################################################
def dialogYesNo(title="", line1="", line2="",line3="", yesButton="", noButton=""):
	if not title:
		title = __language__( 0 )
	if not yesButton:
		yesButton= __language__( 500 )
	if not noButton:
		noButton= __language__( 501 )
	return xbmcgui.Dialog().yesno(title, line1, line2, line3, noButton, yesButton)

#################################################################################################################
def handleException(txt=''):
	try:
		title = "EXCEPTION: " + txt
		e=sys.exc_info()
		list = traceback.format_exception(e[0],e[1],e[2],3)
		text = ''
		for l in list:
			text += l
		messageOK(title, text)
	except: pass

#################################################################################################################
def makeScriptDataDir():
	# make userdata script_data location
	dir = "T:\script_data"
	makeDir(dir)
	
	dir = os.path.join(dir, __scriptname__)
	makeDir(dir)

#################################################################################################################
def makeDir( dir ):
	try:
		os.mkdir( dir )
		debug( "made dir: " + dir)
	except: pass

#################################################################################################################
# delete a single file
def deleteFile(filename):
	try:
		os.remove(filename)
		debug("file deleted: " + filename)
#	except OSError, ex:
#		if ex[0] == 13:		# perm denied
#			errCodeStr = str(ex[0]) + ", " + str(ex[1])
#			dialogOK("File Delete Error",errCodeStr,filename)
	except: pass


#################################################################################################################
def readFile(filename):
	try:
		return file(filename).read()
	except:
		return ""

#################################################################################################################
def fileExist(filename):
	exist = False
	try:
		if os.path.isfile(filename) and os.path.getsize(filename) > 0:
			exist = True
	except:
		pass
	return exist

#################################################################################################################
def isFileNewer(oldFilename, newFilename):
	new = False
	try:
		# returns secs since epoch
		oldFileTime = os.path.getmtime(oldFilename)
		newFileTime = os.path.getmtime(newFilename)
		if newFileTime > oldFileTime:
			new = True
	except:
		new = True	# incase old doesnt exist

	return new

##############################################################################################
def doKeyboard(currentValue='', heading='', kbType=KBTYPE_ALPHA):
	if currentValue == None:
		currentValue = ''
	value = currentValue
	if kbType == KBTYPE_ALPHA:
		keyboard = xbmc.Keyboard(currentValue, heading)
		keyboard.doModal()
		if keyboard.isConfirmed:
			value = keyboard.getText().strip()
		else:
			value = None
	else:
		d = xbmcgui.Dialog()
		value = d.numeric(kbType, heading, currentValue)

	return value

##############################################################################################
# if current and skinned resolutions differ and skinned resolution is not
# 1080i or 720p (they have no 4:3), calculate widescreen offset
##############################################################################################
def setResolution(win):
	try:
		# '1080i'=0, '720p'=1, '480p'=2, '480p16x9'=3, 'ntsc'=4, 'ntsc16x9'=5, 'pal'=6, 'pal16x9'=7, 'pal60'=8, 'pal6016x9'=9}
		rez = 6		# PAL
		currRez = win.getResolution()
		if (currRez != rez) and rez > 1:
			# If resolutions differ calculate widescreen offset
			# check if current resolution is 16x9
			if (currRez == 0 or currRez % 2): iCur16x9 = 1
			else: iCur16x9 = 0

			# check if skinned resolution is 16x9
			if (rez == 0 or rez % 2): iSkin16x9 = 1
			else: iSkin16x9 = 0

			# calculate offset
			offset = iCur16x9 - iSkin16x9
			rez += offset
	except:
		handleException()

	win.setCoordinateResolution(rez)
	debug("setResolution() curr Rez=" + str(currRez) + " new Rez="+str(rez))


#################################################################################################################
# Dialog with options
#################################################################################################################
class DialogSelect(xbmcgui.WindowDialog):
	def __init__(self):
		if Emulating: xbmcgui.WindowDialog.__init__(self)

		setResolution(self)

		self.selectedPos = -1		# EXIT option
		self.panelCI = None
		self.menuCL = None
		self.lastAction = 0

	def setup(self, title='Menu',width=430, height=450, xpos=-1, ypos=-1, textColor='0xFFFFFFFF', \
			  imageWidth=0,imageHeight=22, itemHeight=22, rows=0,
			  useY=False, useX=False, isDelete=False, panel='', banner=''):
		debug("> DialogSelect().setup() useY="+str(useY) + " useX=" + str(useX) + " isDelete=" + str(isDelete))

		if not panel:
			panel = DIALOG_PANEL
		self.useY = useY
		self.useX = useX
		self.isDelete = isDelete
		offsetLabelX = 15
		offsetListX = 20
		listW = width - offsetListX - 5
		if imageHeight > itemHeight:
			itemHeight = imageHeight

		if banner:
			bannerH = 40
		else:
			bannerH = 0

		if title:
			titleH = 25
		else:
			titleH = 0

		# calc height based on rows, otherwise use supplied height
		if rows > 0:
			rows += 3		 # add 'exit' + extra rows
			listH = (rows * itemHeight)
		else:
			listH = height

		if height > listH:
			height = listH						# shrink height to fit list
		elif height < listH:
			listH = height-itemHeight			# shrink list to height, minus 1 line

		height += titleH + bannerH				# add space onto for title + gap

		# center on screen
		if xpos < 0:
			xpos = int((REZ_W /2) - (width /2))
		if ypos < 0:
			ypos = int((REZ_H /2) - (height /2)) + 10

		bannerY = ypos + 10
		titleY = bannerY + bannerH 
		listY = titleY + titleH

		try:
			self.removeControl(self.panelCI)
		except: pass
		try:
			self.panelCI = xbmcgui.ControlImage(xpos, ypos, width, height, DIALOG_PANEL)
			self.addControl(self.panelCI)
		except: pass

		if isDelete:
			title += " " + __language__(699)

		if title:
			self.titleCL = xbmcgui.ControlLabel(xpos+offsetLabelX, titleY, listW, titleH, \
												title, FONT13, '0xFFFFFF00', alignment=XBFONT_CENTER_X)
			self.addControl(self.titleCL)

		if bannerH:
			try:
				self.removeControl(self.bannerCI)
			except: pass
			try:
				self.bannerCI = xbmcgui.ControlImage(xpos+offsetListX, bannerY,
													listW, bannerH, banner, aspectRatio=2)
				self.addControl(self.bannerCI)
			except:
				debug("failed to place banner")

		try:
			self.removeControl(self.menuCL)
		except: pass
		if not self.isDelete:
			self.menuCL = xbmcgui.ControlList(xpos+offsetListX, listY, \
											listW, listH, textColor=textColor, \
											imageWidth=imageWidth, imageHeight=imageHeight, \
											itemHeight=itemHeight, \
											itemTextXOffset=0, space=0, alignmentY=XBFONT_CENTER_Y)
		else:
			self.menuCL = xbmcgui.ControlList(xpos+offsetListX, listY, \
											listW, listH, textColor=textColor, \
											imageWidth=imageWidth, imageHeight=imageHeight, \
											itemHeight=itemHeight, buttonFocusTexture=LIST_HIGHLIGHT_FILENAME, \
											itemTextXOffset=0, space=0, alignmentY=XBFONT_CENTER_Y)
		self.addControl(self.menuCL)
		self.menuCL.setPageControlVisible(False)
		debug("< DialogSelect().setup()")

	def onAction(self, action):
		debug("DialogSelect.onAction()")
		if action == 0:
			return
		self.lastAction = action
		if action in [ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR]:
			self.selectedPos = -1
			self.close()
		elif (self.useY and action == ACTION_Y_BUTTON) or \
			 (self.useX and action == ACTION_X_BUTTON):
			self.selectedPos = self.menuCL.getSelectedPosition()
			self.close()

	def onControl(self, control):
		debug("DialogSelect.onControl()")
		try:
			self.selectedPos = self.menuCL.getSelectedPosition()
		except: pass
		self.close()

	def setMenu(self, menu, icons=[]):
		debug("> DialogSelect.setMenu()")
		self.menuCL.reset()
		self.menuCL.addItem("Exit")
		if menu:
			for idx in range(len(menu)):
				opt = menu[idx]
				try:
					img = icons[idx]
				except:
					img = ''

				if isinstance(opt, xbmcgui.ListItem):
					# associate an img with listitems that have them
					if img:
						opt.setIconImage(img)
						opt.setThumbnailImage(img)
					self.menuCL.addItem(opt)
				elif isinstance(opt, list) or isinstance(opt, tuple):
					# option is itself a list [lbl1, lbl2]
					l1 = opt[0].strip()
					try:
						l2 = opt[1].strip()
					except:
						l2 = ''
					self.menuCL.addItem(xbmcgui.ListItem(l1, l2, img, img))
				else:
					# single string value
					self.menuCL.addItem(xbmcgui.ListItem(opt.strip(), '', img, img))

			if self.selectedPos > len(menu):
				self.selectedPos = len(menu)-1
			self.menuCL.selectItem(self.selectedPos)
		debug("< DialogSelect.setMenu()")

	# show this dialog and wait until it's closed
	def ask(self, menu, selectIdx=-1, icons=[]):
		debug ("> DialogSelect().ask() selectIdx=" +str(selectIdx))

		self.selectedPos = selectIdx+1	# allow for exit option
		self.setMenu(menu, icons)
		self.setFocus(self.menuCL)
		self.doModal()
		self.selectedPos -= 1

		debug ("< DialogSelect.ask() selectedPos: " + str(self.selectedPos) + " lastAction: " + str(self.lastAction))
		return self.selectedPos, self.lastAction

#######################################################################################################################    
def parseDocList(doc, regex, startStr='', endStr=''):
	# find section
	startPos = -1
	endPos = -1
	if startStr:
		startPos = find(doc,startStr)
		if startPos == -1:
			print "parseDocList() start not found"

	if endStr:
		endPos = find(doc, endStr, startPos+1)
		if endPos == -1:
			print "parseDocList() end not found"

	if startPos < 0:
		startPos = 0
	if endPos < 0 or endPos <= startPos:
		endPos = len(doc)-1

	# do regex on section
	try:
		findRe = re.compile(regex, re.DOTALL + re.MULTILINE + re.IGNORECASE)
		matchList = findRe.findall(doc[startPos:endPos])
	except:
		matchList = []

	if matchList:
		sz = len(matchList)
	else:
		sz = 0
	debug( "parseDocList() matches = " +str(sz))
	return matchList

#################################################################################################################
# look for html between < and > chars and remove it
def cleanHTML(data):
	try:
		reobj = re.compile('<.+?>', re.IGNORECASE+re.DOTALL+re.MULTILINE)
		return (re.sub(reobj, '', data)).strip()
	except:
		return data

#################################################################################################################
def HTTPErrorCode(e):
	if hasattr(e, 'code'):
		code = str(e.code)
	else:
		try:
			code = str(e[0])
		except:
			code = 'Unknown'
	title = 'HTTPError, Code: ' + code

	if hasattr(e, 'reason'):
		txt = e.reason
	else:
		try:
			txt = str(e[1])
		except:
			txt = 'Unknown reason'
	debug("HTTPErrorCode: " + str(code) + " " + txt)
	messageOK(title, txt)


#################################################################################################################
# Convert a text string containing &#x<hex_value> to ascii ch
#################################################################################################################
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
		debug("urlTextToASCII() DONE")
	except:
		debug("urlTextToASCII() exception")
	return text


#################################################################################################################
# Thanks to Arboc for this
#################################################################################################################
def unicodeToAscii(txt, charset='utf8'):
	try:
		newtxt = txt.decode(charset)
		newtxt = unicodedata.normalize('NFKD', newtxt).encode('ASCII','replace')
		return newtxt
	except:
		return txt

#################################################################################################################
# Thanks to Arboc for contributing most of the translation in this function. 
#################################################################################################################
def decodeEntities(txt, removeNewLines=True):
	txt = txt.replace('\t','')

# % values
	if find(txt,'%') >= 0:
		txt = txt.replace('%21', "!")
		txt = txt.replace('%22', '"')
		txt = txt.replace('%25', "%")
		txt = txt.replace('%26', "&")
		txt = txt.replace('%27', "'")
		txt = txt.replace('%28', "(")
		txt = txt.replace('%29', ")")
		txt = txt.replace('%2a', "*")
		txt = txt.replace('%2b', "+")
		txt = txt.replace('%2c', ",")
		txt = txt.replace('%2d', "-")
		txt = txt.replace('%2e', ".")
		txt = txt.replace('%3a', ":")
		txt = txt.replace('%3b', ";")
		txt = txt.replace('%3f', "?")
		txt = txt.replace('%40', "@")

# 
	if find(txt,"&#") >= 0:
		txt = txt.replace('&#034;','"')
		txt = txt.replace('&#039;','\'')
		txt = txt.replace('&#13;&#10;','\n')
		txt = txt.replace('&#10;','\n')
		txt = txt.replace('&#13;','\n')
		txt = txt.replace('&#146;', "'")
		txt = txt.replace('&#156;', "oe")
		txt = txt.replace('&#160;', " ") # no-break space = non-breaking space U+00A0 ISOnum
		txt = txt.replace('&#161;', "!") # inverted exclamation mark U+00A1 ISOnum
		txt = txt.replace('&#162;', "c") # cent sign U+00A2 ISOnum
		txt = txt.replace('&#163;', "p") # pound sign U+00A3 ISOnum
		txt = txt.replace('&#164;', "$") # currency sign U+00A4 ISOnum
		txt = txt.replace('&#165;', "y") # yen sign = yuan sign U+00A5 ISOnum
		txt = txt.replace('&#166;', "|") # broken bar = broken vertical bar U+00A6 ISOnum
		txt = txt.replace('&#167;', "S") # section sign U+00A7 ISOnum
		txt = txt.replace('&#168;', "''") # diaeresis = spacing diaeresis U+00A8 ISOdia
		txt = txt.replace('&#169;', "(c)") # copyright sign U+00A9 ISOnum
		txt = txt.replace('&#170;', "e") # feminine ordinal indicator U+00AA ISOnum
		txt = txt.replace('&#171;', '"') # left-pointing double angle quotation mark = left pointing guillemet U+00AB ISOnum
		txt = txt.replace('&#172;', "-.") # not sign U+00AC ISOnum
		txt = txt.replace('&#173;', "-") # soft hyphen = discretionary hyphen U+00AD ISOnum
		txt = txt.replace('&#174;', "(R)") # registered sign = registered trade mark sign U+00AE ISOnum
		txt = txt.replace('&#175;', "-") # macron = spacing macron = overline = APL overbar U+00AF ISOdia
		txt = txt.replace('&#176;', "o") # degree sign U+00B0 ISOnum
		txt = txt.replace('&#177;', "+-") # plus-minus sign = plus-or-minus sign U+00B1 ISOnum
		txt = txt.replace('&#178;', "2") # superscript two = superscript digit two = squared U+00B2 ISOnum
		txt = txt.replace('&#179;', "3") # superscript three = superscript digit three = cubed U+00B3 ISOnum
		txt = txt.replace('&#180;', " ") # acute accent = spacing acute U+00B4 ISOdia
		txt = txt.replace('&#181;', "u") # micro sign U+00B5 ISOnum
		txt = txt.replace('&#182;', "|p") # pilcrow sign = paragraph sign U+00B6 ISOnum
		txt = txt.replace('&#183;', ".") # middle dot = Georgian comma = Greek middle dot U+00B7 ISOnum
		txt = txt.replace('&#184;', " ") # cedilla = spacing cedilla U+00B8 ISOdia
		txt = txt.replace('&#185;', "1") # superscript one = superscript digit one U+00B9 ISOnum
		txt = txt.replace('&#186;', "o") # masculine ordinal indicator U+00BA ISOnum
		txt = txt.replace('&#187;', '"') # right-pointing double angle quotation mark = right pointing guillemet U+00BB ISOnum
		txt = txt.replace('&#188;', "1/4") # vulgar fraction one quarter = fraction one quarter U+00BC ISOnum
		txt = txt.replace('&#189;', "1/2") # vulgar fraction one half = fraction one half U+00BD ISOnum
		txt = txt.replace('&#190;', "3/4") # vulgar fraction three quarters = fraction three quarters U+00BE ISOnum
		txt = txt.replace('&#191;', "?") # inverted question mark = turned question mark U+00BF ISOnum
		txt = txt.replace('&#192;', "A") # latin capital letter A with grave = latin capital letter A grave U+00C0 ISOlat1
		txt = txt.replace('&#193;', "A") # latin capital letter A with acute U+00C1 ISOlat1
		txt = txt.replace('&#194;', "A") # latin capital letter A with circumflex U+00C2 ISOlat1
		txt = txt.replace('&#195;', "A") # latin capital letter A with tilde U+00C3 ISOlat1
		txt = txt.replace('&#196;', "A") # latin capital letter A with diaeresis U+00C4 ISOlat1
		txt = txt.replace('&#197;', "A") # latin capital letter A with ring above = latin capital letter A ring U+00C5 ISOlat1
		txt = txt.replace('&#198;', "AE") # latin capital letter AE = latin capital ligature AE U+00C6 ISOlat1
		txt = txt.replace('&#199;', "C") # latin capital letter C with cedilla U+00C7 ISOlat1
		txt = txt.replace('&#200;', "E") # latin capital letter E with grave U+00C8 ISOlat1
		txt = txt.replace('&#201;', "E") # latin capital letter E with acute U+00C9 ISOlat1
		txt = txt.replace('&#202;', "E") # latin capital letter E with circumflex U+00CA ISOlat1
		txt = txt.replace('&#203;', "E") # latin capital letter E with diaeresis U+00CB ISOlat1
		txt = txt.replace('&#204;', "I") # latin capital letter I with grave U+00CC ISOlat1
		txt = txt.replace('&#205;', "I") # latin capital letter I with acute U+00CD ISOlat1
		txt = txt.replace('&#206;', "I") # latin capital letter I with circumflex U+00CE ISOlat1
		txt = txt.replace('&#207;', "I") # latin capital letter I with diaeresis U+00CF ISOlat1
		txt = txt.replace('&#208;', "D") # latin capital letter ETH U+00D0 ISOlat1
		txt = txt.replace('&#209;', "N") # latin capital letter N with tilde U+00D1 ISOlat1
		txt = txt.replace('&#210;', "O") # latin capital letter O with grave U+00D2 ISOlat1
		txt = txt.replace('&#211;', "O") # latin capital letter O with acute U+00D3 ISOlat1
		txt = txt.replace('&#212;', "O") # latin capital letter O with circumflex U+00D4 ISOlat1
		txt = txt.replace('&#213;', "O") # latin capital letter O with tilde U+00D5 ISOlat1
		txt = txt.replace('&#214;', "O") # latin capital letter O with diaeresis U+00D6 ISOlat1
		txt = txt.replace('&#215;', "x") # multiplication sign U+00D7 ISOnum
		txt = txt.replace('&#216;', "O") # latin capital letter O with stroke = latin capital letter O slash U+00D8 ISOlat1
		txt = txt.replace('&#217;', "U") # latin capital letter U with grave U+00D9 ISOlat1
		txt = txt.replace('&#218;', "U") # latin capital letter U with acute U+00DA ISOlat1
		txt = txt.replace('&#219;', "U") # latin capital letter U with circumflex U+00DB ISOlat1
		txt = txt.replace('&#220;', "U") # latin capital letter U with diaeresis U+00DC ISOlat1
		txt = txt.replace('&#221;', "Y") # latin capital letter Y with acute U+00DD ISOlat1
		txt = txt.replace('&#222;', "D") # latin capital letter THORN U+00DE ISOlat1
		txt = txt.replace('&#223;', "SS") # latin small letter sharp s = ess-zed U+00DF ISOlat1
		txt = txt.replace('&#224;', "a") # latin small letter a with grave = latin small letter a grave U+00E0 ISOlat1
		txt = txt.replace('&#225;', "a") # latin small letter a with acute U+00E1 ISOlat1
		txt = txt.replace('&#226;', "a") # latin small letter a with circumflex U+00E2 ISOlat1
		txt = txt.replace('&#227;', "a") # latin small letter a with tilde U+00E3 ISOlat1
		txt = txt.replace('&#228;', "a") # latin small letter a with diaeresis U+00E4 ISOlat1
		txt = txt.replace('&#229;', "a") # latin small letter a with ring above = latin small letter a ring U+00E5 ISOlat1
		txt = txt.replace('&#230;', "ae") # latin small letter ae = latin small ligature ae U+00E6 ISOlat1
		txt = txt.replace('&#231;', "c") # latin small letter c with cedilla U+00E7 ISOlat1
		txt = txt.replace('&#232;', "e") # latin small letter e with grave U+00E8 ISOlat1
		txt = txt.replace('&#233;', "e") # latin small letter e with acute U+00E9 ISOlat1
		txt = txt.replace('&#234;', "e") # latin small letter e with circumflex U+00EA ISOlat1
		txt = txt.replace('&#235;', "e") # latin small letter e with diaeresis U+00EB ISOlat1
		txt = txt.replace('&#236;', "i") # latin small letter i with grave U+00EC ISOlat1
		txt = txt.replace('&#237;', "i") # latin small letter i with acute U+00ED ISOlat1
		txt = txt.replace('&#238;', "i") # latin small letter i with circumflex U+00EE ISOlat1
		txt = txt.replace('&#239;', "i") # latin small letter i with diaeresis U+00EF ISOlat1
		txt = txt.replace('&#240;', "d") # latin small letter eth U+00F0 ISOlat1
		txt = txt.replace('&#241;', "n") # latin small letter n with tilde U+00F1 ISOlat1
		txt = txt.replace('&#242;', "o") # latin small letter o with grave U+00F2 ISOlat1
		txt = txt.replace('&#243;', "o") # latin small letter o with acute U+00F3 ISOlat1
		txt = txt.replace('&#244;', "o") # latin small letter o with circumflex U+00F4 ISOlat1
		txt = txt.replace('&#245;', "o") # latin small letter o with tilde U+00F5 ISOlat1
		txt = txt.replace('&#246;', "o") # latin small letter o with diaeresis U+00F6 ISOlat1
		txt = txt.replace('&#247;', "/") # division sign U+00F7 ISOnum
		txt = txt.replace('&#248;', "o") # latin small letter o with stroke = latin small letter o slash U+00F8 ISOlat1
		txt = txt.replace('&#249;', "u") # latin small letter u with grave U+00F9 ISOlat1
		txt = txt.replace('&#250;', "u") # latin small letter u with acute U+00FA ISOlat1
		txt = txt.replace('&#251;', "u") # latin small letter u with circumflex U+00FB ISOlat1
		txt = txt.replace('&#252;', "u") # latin small letter u with diaeresis U+00FC ISOlat1
		txt = txt.replace('&#253;', "y") # latin small letter y with acute U+00FD ISOlat1
		txt = txt.replace('&#254;', "d") # latin small letter thorn U+00FE ISOlat1
		txt = txt.replace('&#255;', "y") # latin small letter y with diaeresis U+00FF ISOlat1
		txt = txt.replace('&#338;', "OE") # latin capital ligature OE U+0152 ISOlat2
		txt = txt.replace('&#339;', "oe") # latin small ligature oe U+0153 ISOlat2
		txt = txt.replace('&#34;', '"') # quotation mark = APL quote U+0022 ISOnum
		txt = txt.replace('&#352;', "S") # latin capital letter S with caron U+0160 ISOlat2
		txt = txt.replace('&#353;', "s") # latin small letter s with caron U+0161 ISOlat2
		txt = txt.replace('&#376;', "Y") # latin capital letter Y with diaeresis U+0178 ISOlat2
		txt = txt.replace('&#38;', "&") # ampersand U+0026 ISOnum
		txt = txt.replace('&#39;','\'')
		txt = txt.replace('&#402;', "f") # latin small f with hook = function = florin U+0192 ISOtech
		txt = txt.replace('&#60;', "<") # less-than sign U+003C ISOnum
		txt = txt.replace('&#62;', ">") # greater-than sign U+003E ISOnum
		txt = txt.replace('&#710;', "") # modifier letter circumflex accent U+02C6 ISOpub
		txt = txt.replace('&#732;', "~") # small tilde U+02DC ISOdia
		txt = txt.replace('&#8194;', "") # en space U+2002 ISOpub
		txt = txt.replace('&#8195;', " ") # em space U+2003 ISOpub
		txt = txt.replace('&#8201;', " ") # thin space U+2009 ISOpub
		txt = txt.replace('&#8204;', "|") # zero width non-joiner U+200C NEW RFC 2070
		txt = txt.replace('&#8205;', "|") # zero width joiner U+200D NEW RFC 2070
		txt = txt.replace('&#8206;', "") # left-to-right mark U+200E NEW RFC 2070
		txt = txt.replace('&#8207;', "") # right-to-left mark U+200F NEW RFC 2070
		txt = txt.replace('&#8211;', "--") # en dash U+2013 ISOpub
		txt = txt.replace('&#8212;', "---") # em dash U+2014 ISOpub
		txt = txt.replace('&#8216;', '"') # left single quotation mark U+2018 ISOnum
		txt = txt.replace('&#8217;', '"') # right single quotation mark U+2019 ISOnum
		txt = txt.replace('&#8218;', '"') # single low-9 quotation mark U+201A NEW
		txt = txt.replace('&#8220;', '"') # left double quotation mark U+201C ISOnum
		txt = txt.replace('&#8221;', '"') # right double quotation mark U+201D ISOnum
		txt = txt.replace('&#8222;', '"') # double low-9 quotation mark U+201E NEW
		txt = txt.replace('&#8224;', "|") # dagger U+2020 ISOpub
		txt = txt.replace('&#8225;', "||") # double dagger U+2021 ISOpub
		txt = txt.replace('&#8226;', "o") # bullet = black small circle U+2022 ISOpub
		txt = txt.replace('&#8230;', "...") # horizontal ellipsis = three dot leader U+2026 ISOpub
		txt = txt.replace('&#8240;', "%0") # per mille sign U+2030 ISOtech
		txt = txt.replace('&#8242;', "'") # prime = minutes = feet U+2032 ISOtech
		txt = txt.replace('&#8243;', "''") # double prime = seconds = inches U+2033 ISOtech
		txt = txt.replace('&#8249;', '"') # single left-pointing angle quotation mark U+2039 ISO proposed
		txt = txt.replace('&#8250;', '"') # single right-pointing angle quotation mark U+203A ISO proposed
		txt = txt.replace('&#8254;', "-") # overline = spacing overscore U+203E NEW
		txt = txt.replace('&#8260;', "/") # fraction slash U+2044 NEW
		txt = txt.replace('&#8364;', "EU$") # euro sign U+20AC NEW
		txt = txt.replace('&#8465;', "|I") # blackletter capital I = imaginary part U+2111 ISOamso
		txt = txt.replace('&#8472;', "|P") # script capital P = power set = Weierstrass p U+2118 ISOamso
		txt = txt.replace('&#8476;', "|R") # blackletter capital R = real part symbol U+211C ISOamso
		txt = txt.replace('&#8482;', "tm") # trade mark sign U+2122 ISOnum
		txt = txt.replace('&#8501;', "%") # alef symbol = first transfinite cardinal U+2135 NEW
		txt = txt.replace('&#8592;', "<-") # leftwards arrow U+2190 ISOnum
		txt = txt.replace('&#8593;', "^") # upwards arrow U+2191 ISOnum
		txt = txt.replace('&#8594;', "->") # rightwards arrow U+2192 ISOnum
		txt = txt.replace('&#8595;', "v") # downwards arrow U+2193 ISOnum
		txt = txt.replace('&#8596;', "<->") # left right arrow U+2194 ISOamsa
		txt = txt.replace('&#8629;', "<-'") # downwards arrow with corner leftwards = carriage return U+21B5 NEW
		txt = txt.replace('&#8656;', "<=") # leftwards double arrow U+21D0 ISOtech
		txt = txt.replace('&#8657;', "^") # upwards double arrow U+21D1 ISOamsa
		txt = txt.replace('&#8658;', "=>") # rightwards double arrow U+21D2 ISOtech
		txt = txt.replace('&#8659;', "v") # downwards double arrow U+21D3 ISOamsa
		txt = txt.replace('&#8660;', "<=>") # left right double arrow U+21D4 ISOamsa
		txt = txt.replace('&#8764;', "~") # tilde operator = varies with = similar to U+223C ISOtech
		txt = txt.replace('&#8773;', "~=") # approximately equal to U+2245 ISOtech
		txt = txt.replace('&#8776;', "~~") # almost equal to = asymptotic to U+2248 ISOamsr
		txt = txt.replace('&#8800;', "!=") # not equal to U+2260 ISOtech
		txt = txt.replace('&#8801;', "==") # identical to U+2261 ISOtech
		txt = txt.replace('&#8804;', "<=") # less-than or equal to U+2264 ISOtech
		txt = txt.replace('&#8805;', ">=") # greater-than or equal to U+2265 ISOtech
		txt = txt.replace('&#8901;', ".") # dot operator U+22C5 ISOamsb
		txt = txt.replace('&#913;', "Alpha") # greek capital letter alpha U+0391
		txt = txt.replace('&#914;', "Beta") # greek capital letter beta U+0392
		txt = txt.replace('&#915;', "Gamma") # greek capital letter gamma U+0393 ISOgrk3
		txt = txt.replace('&#916;', "Delta") # greek capital letter delta U+0394 ISOgrk3
		txt = txt.replace('&#917;', "Epsilon") # greek capital letter epsilon U+0395
		txt = txt.replace('&#918;', "Zeta") # greek capital letter zeta U+0396
		txt = txt.replace('&#919;', "Eta") # greek capital letter eta U+0397
		txt = txt.replace('&#920;', "Theta") # greek capital letter theta U+0398 ISOgrk3
		txt = txt.replace('&#921;', "Iota") # greek capital letter iota U+0399
		txt = txt.replace('&#922;', "Kappa") # greek capital letter kappa U+039A
		txt = txt.replace('&#923;', "Lambda") # greek capital letter lambda U+039B ISOgrk3
		txt = txt.replace('&#924;', "Mu") # greek capital letter mu U+039C
		txt = txt.replace('&#925;', "Nu") # greek capital letter nu U+039D
		txt = txt.replace('&#926;', "Xi") # greek capital letter xi U+039E ISOgrk3
		txt = txt.replace('&#927;', "Omicron") # greek capital letter omicron U+039F
		txt = txt.replace('&#928;', "Pi") # greek capital letter pi U+03A0 ISOgrk3
		txt = txt.replace('&#929;', "Rho") # greek capital letter rho U+03A1
		txt = txt.replace('&#931;', "Sigma") # greek capital letter sigma U+03A3 ISOgrk3
		txt = txt.replace('&#932;', "Tau") # greek capital letter tau U+03A4
		txt = txt.replace('&#933;', "Upsilon") # greek capital letter upsilon U+03A5 ISOgrk3
		txt = txt.replace('&#934;', "Phi") # greek capital letter phi U+03A6 ISOgrk3
		txt = txt.replace('&#935;', "Chi") # greek capital letter chi U+03A7
		txt = txt.replace('&#936;', "Psi") # greek capital letter psi U+03A8 ISOgrk3
		txt = txt.replace('&#937;', "Omega") # greek capital letter omega U+03A9 ISOgrk3
		txt = txt.replace('&#945;', "alpha") # greek small letter alpha U+03B1 ISOgrk3
		txt = txt.replace('&#946;', "beta") # greek small letter beta U+03B2 ISOgrk3
		txt = txt.replace('&#947;', "gamma") # greek small letter gamma U+03B3 ISOgrk3
		txt = txt.replace('&#948;', "delta") # greek small letter delta U+03B4 ISOgrk3
		txt = txt.replace('&#949;', "epsilon") # greek small letter epsilon U+03B5 ISOgrk3
		txt = txt.replace('&#950;', "zeta") # greek small letter zeta U+03B6 ISOgrk3
		txt = txt.replace('&#951;', "eta") # greek small letter eta U+03B7 ISOgrk3
		txt = txt.replace('&#952;', "theta") # greek small letter theta U+03B8 ISOgrk3
		txt = txt.replace('&#953;', "iota") # greek small letter iota U+03B9 ISOgrk3
		txt = txt.replace('&#954;', "kappa") # greek small letter kappa U+03BA ISOgrk3
		txt = txt.replace('&#955;', "lambda") # greek small letter lambda U+03BB ISOgrk3
		txt = txt.replace('&#956;', "mu") # greek small letter mu U+03BC ISOgrk3
		txt = txt.replace('&#957;', "nu") # greek small letter nu U+03BD ISOgrk3
		txt = txt.replace('&#958;', "xi") # greek small letter xi U+03BE ISOgrk3
		txt = txt.replace('&#959;', "omicron") # greek small letter omicron U+03BF NEW
		txt = txt.replace('&#960;', "pi") # greek small letter pi U+03C0 ISOgrk3
		txt = txt.replace('&#961;', "rho") # greek small letter rho U+03C1 ISOgrk3
		txt = txt.replace('&#962;', "sigma") # greek small letter final sigma U+03C2 ISOgrk3
		txt = txt.replace('&#963;', "sigma") # greek small letter sigma U+03C3 ISOgrk3
		txt = txt.replace('&#964;', "tau") # greek small letter tau U+03C4 ISOgrk3
		txt = txt.replace('&#965;', "upsilon") # greek small letter upsilon U+03C5 ISOgrk3
		txt = txt.replace('&#966;', "phi") # greek small letter phi U+03C6 ISOgrk3
		txt = txt.replace('&#967;', "chi") # greek small letter chi U+03C7 ISOgrk3
		txt = txt.replace('&#968;', "psi") # greek small letter psi U+03C8 ISOgrk3
		txt = txt.replace('&#969;', "omega") # greek small letter omega U+03C9 ISOgrk3
		txt = txt.replace('&#977;', "theta") # greek small letter theta symbol U+03D1 NEW
		txt = txt.replace('&#978;', "upsilon") # greek upsilon with hook symbol U+03D2 NEW
		txt = txt.replace('&#982;', "pi") # greek pi symbol U+03D6 ISOgrk3
		# remove any uncaught &#<number>;
		if find(txt,"&#") >= 0:
			reHash = re.compile('&#.+?;', re.IGNORECASE)
			txt = re.sub(reHash, '', txt)

	if find(txt,'&') >= 0:
		txt = txt.replace('&Aacute;', "A") # latin capital letter A with acute U+00C1 ISOlat1
		txt = txt.replace('&aacute;', "a") # latin small letter a with acute U+00E1 ISOlat1
		txt = txt.replace('&Acirc;', "A") # latin capital letter A with circumflex U+00C2 ISOlat1
		txt = txt.replace('&acirc;', "a") # latin small letter a with circumflex U+00E2 ISOlat1
		txt = txt.replace('&acute;', " ") # acute accent = spacing acute U+00B4 ISOdia
		txt = txt.replace('&AElig;', "AE") # latin capital letter AE = latin capital ligature AE U+00C6 ISOlat1
		txt = txt.replace('&aelig;', "ae") # latin small letter ae = latin small ligature ae U+00E6 ISOlat1
		txt = txt.replace('&Agrave;', "A") # latin capital letter A with grave = latin capital letter A grave U+00C0 ISOlat1
		txt = txt.replace('&agrave;', "a") # latin small letter a with grave = latin small letter a grave U+00E0 ISOlat1
		txt = txt.replace('&alefsym;', "%") # alef symbol = first transfinite cardinal U+2135 NEW
		txt = txt.replace('&Alpha;', "Alpha") # greek capital letter alpha U+0391
		txt = txt.replace('&alpha;', "alpha") # greek small letter alpha U+03B1 ISOgrk3
		txt = txt.replace('&amp;amp;','&')
		txt = txt.replace('&amp;;','&')
		txt = txt.replace('&amp;', "&") # ampersand U+0026 ISOnum		
		txt = txt.replace('&amp','&')		
		txt = txt.replace('&apos;', "'")
		txt = txt.replace('&Aring;', "A") # latin capital letter A with ring above = latin capital letter A ring U+00C5 ISOlat1
		txt = txt.replace('&aring;', "a") # latin small letter a with ring above = latin small letter a ring U+00E5 ISOlat1
		txt = txt.replace('&asymp;', "~~") # almost equal to = asymptotic to U+2248 ISOamsr
		txt = txt.replace('&Atilde;', "A") # latin capital letter A with tilde U+00C3 ISOlat1
		txt = txt.replace('&atilde;', "a") # latin small letter a with tilde U+00E3 ISOlat1
		txt = txt.replace('&auml;', "a")
		txt = txt.replace('&Auml;', "A")
		txt = txt.replace('&Auml;', "A") # latin capital letter A with diaeresis U+00C4 ISOlat1
		txt = txt.replace('&auml;', "a") # latin small letter a with diaeresis U+00E4 ISOlat1
		txt = txt.replace('&bdquo;', '"') # double low-9 quotation mark U+201E NEW
		txt = txt.replace('&Beta;', "Beta") # greek capital letter beta U+0392
		txt = txt.replace('&beta;', "beta") # greek small letter beta U+03B2 ISOgrk3
		txt = txt.replace('&brvbar;', "|") # broken bar = broken vertical bar U+00A6 ISOnum
		txt = txt.replace('&bull;', "o") # bullet = black small circle U+2022 ISOpub
		txt = txt.replace('&Ccedil;', "C") # latin capital letter C with cedilla U+00C7 ISOlat1
		txt = txt.replace('&ccedil;', "c") # latin small letter c with cedilla U+00E7 ISOlat1
		txt = txt.replace('&cedil;', " ") # cedilla = spacing cedilla U+00B8 ISOdia
		txt = txt.replace('&cent;', "c") # cent sign U+00A2 ISOnum
		txt = txt.replace('&Chi;', "Chi") # greek capital letter chi U+03A7
		txt = txt.replace('&chi;', "chi") # greek small letter chi U+03C7 ISOgrk3
		txt = txt.replace('&circ;', "") # modifier letter circumflex accent U+02C6 ISOpub
		txt = txt.replace('&cong;', "~=") # approximately equal to U+2245 ISOtech
		txt = txt.replace('&copy;', "(c)") # copyright sign U+00A9 ISOnum
		txt = txt.replace('&crarr;', "<-'") # downwards arrow with corner leftwards = carriage return U+21B5 NEW
		txt = txt.replace('&curren;', "$") # currency sign U+00A4 ISOnum
		txt = txt.replace('&dagger;', "|") # dagger U+2020 ISOpub
		txt = txt.replace('&Dagger;', "||") # double dagger U+2021 ISOpub
		txt = txt.replace('&darr;', "v") # downwards arrow U+2193 ISOnum
		txt = txt.replace('&dArr;', "v") # downwards double arrow U+21D3 ISOamsa
		txt = txt.replace('&deg;', "o") # degree sign U+00B0 ISOnum
		txt = txt.replace('&Delta;', "Delta") # greek capital letter delta U+0394 ISOgrk3
		txt = txt.replace('&delta;', "delta") # greek small letter delta U+03B4 ISOgrk3
		txt = txt.replace('&divide;', "/") # division sign U+00F7 ISOnum
		txt = txt.replace('&Eacute;', "E") # latin capital letter E with acute U+00C9 ISOlat1
		txt = txt.replace('&eacute;', "e") # latin small letter e with acute U+00E9 ISOlat1
		txt = txt.replace('&Ecirc;', "E") # latin capital letter E with circumflex U+00CA ISOlat1
		txt = txt.replace('&ecirc;', "e") # latin small letter e with circumflex U+00EA ISOlat1
		txt = txt.replace('&Egrave;', "E") # latin capital letter E with grave U+00C8 ISOlat1
		txt = txt.replace('&egrave;', "e") # latin small letter e with grave U+00E8 ISOlat1
		txt = txt.replace('&emsp;', " ") # em space U+2003 ISOpub
		txt = txt.replace('&ensp;', " ") # en space U+2002 ISOpub
		txt = txt.replace('&Epsilon;', "Epsilon") # greek capital letter epsilon U+0395
		txt = txt.replace('&epsilon;', "epsilon") # greek small letter epsilon U+03B5 ISOgrk3
		txt = txt.replace('&equiv;', "==") # identical to U+2261 ISOtech
		txt = txt.replace('&Eta;', "Eta") # greek capital letter eta U+0397
		txt = txt.replace('&eta;', "eta") # greek small letter eta U+03B7 ISOgrk3
		txt = txt.replace('&ETH;', "D") # latin capital letter ETH U+00D0 ISOlat1
		txt = txt.replace('&eth;', "d") # latin small letter eth U+00F0 ISOlat1
		txt = txt.replace('&Euml;', "E") # latin capital letter E with diaeresis U+00CB ISOlat1
		txt = txt.replace('&euml;', "e") # latin small letter e with diaeresis U+00EB ISOlat1
		txt = txt.replace('&euro;', "EU$") # euro sign U+20AC NEW
		txt = txt.replace('&fnof;', "f") # latin small f with hook = function = florin U+0192 ISOtech
		txt = txt.replace('&frac12;', "1/2") # vulgar fraction one half = fraction one half U+00BD ISOnum
		txt = txt.replace('&frac14;', "1/4") # vulgar fraction one quarter = fraction one quarter U+00BC ISOnum
		txt = txt.replace('&frac34;', "3/4") # vulgar fraction three quarters = fraction three quarters U+00BE ISOnum
		txt = txt.replace('&frasl;', "/") # fraction slash U+2044 NEW
		txt = txt.replace('&Gamma;', "Gamma") # greek capital letter gamma U+0393 ISOgrk3
		txt = txt.replace('&gamma;', "gamma") # greek small letter gamma U+03B3 ISOgrk3
		txt = txt.replace('&ge;', ">=") # greater-than or equal to U+2265 ISOtech
		txt = txt.replace('&gt;', ">") # greater-than sign U+003E ISOnum
		txt = txt.replace('&hArr;', "<=>") # left right double arrow U+21D4 ISOamsa
		txt = txt.replace('&harr;', "<->") # left right arrow U+2194 ISOamsa
		txt = txt.replace('&hellip;', "...") # horizontal ellipsis = three dot leader U+2026 ISOpub
		txt = txt.replace('&Iacute;', "I") # latin capital letter I with acute U+00CD ISOlat1
		txt = txt.replace('&iacute;', "i") # latin small letter i with acute U+00ED ISOlat1
		txt = txt.replace('&Icirc;', "I") # latin capital letter I with circumflex U+00CE ISOlat1
		txt = txt.replace('&icirc;', "i") # latin small letter i with circumflex U+00EE ISOlat1
		txt = txt.replace('&iexcl;', "!") # inverted exclamation mark U+00A1 ISOnum
		txt = txt.replace('&Igrave;', "E") # latin capital letter I with grave U+00CC ISOlat1
		txt = txt.replace('&igrave;', "i") # latin small letter i with grave U+00EC ISOlat1
		txt = txt.replace('&image;', "|I") # blackletter capital I = imaginary part U+2111 ISOamso
		txt = txt.replace('&Iota;', "Iota") # greek capital letter iota U+0399
		txt = txt.replace('&iota;', "iota") # greek small letter iota U+03B9 ISOgrk3
		txt = txt.replace('&iquest;', "?") # inverted question mark = turned question mark U+00BF ISOnum
		txt = txt.replace('&Iuml;', "I") # latin capital letter I with diaeresis U+00CF ISOlat1
		txt = txt.replace('&iuml;', "i") # latin small letter i with diaeresis U+00EF ISOlat1
		txt = txt.replace('&Kappa;', "Kappa") # greek capital letter kappa U+039A
		txt = txt.replace('&kappa;', "kappa") # greek small letter kappa U+03BA ISOgrk3
		txt = txt.replace('&Lambda;', "Lambda") # greek capital letter lambda U+039B ISOgrk3
		txt = txt.replace('&lambda;', "lambda") # greek small letter lambda U+03BB ISOgrk3
		txt = txt.replace('&laquo;', '"') # left-pointing double angle quotation mark = left pointing guillemet U+00AB ISOnum
		txt = txt.replace('&larr;', "<-") # leftwards arrow U+2190 ISOnum
		txt = txt.replace('&lArr;', "<=") # leftwards double arrow U+21D0 ISOtech
		txt = txt.replace('&ldquo;', '"') # left double quotation mark U+201C ISOnum
		txt = txt.replace('&le;', "<=") # less-than or equal to U+2264 ISOtech
		txt = txt.replace('&lrm;', "") # left-to-right mark U+200E NEW RFC 2070
		txt = txt.replace('&lsaquo;', '"') # single left-pointing angle quotation mark U+2039 ISO proposed
		txt = txt.replace('&lsquo;', '"') # left single quotation mark U+2018 ISOnum
		txt = txt.replace('&lt;', "<") # less-than sign U+003C ISOnum
		txt = txt.replace('&macr;', "-") # macron = spacing macron = overline = APL overbar U+00AF ISOdia
		txt = txt.replace('&mdash;', "---") # em dash U+2014 ISOpub
		txt = txt.replace('&micro;', "u") # micro sign U+00B5 ISOnum
		txt = txt.replace('&middot;', ".") # middle dot = Georgian comma = Greek middle dot U+00B7 ISOnum
		txt = txt.replace('&Mu;', "Mu") # greek capital letter mu U+039C
		txt = txt.replace('&mu;', "mu") # greek small letter mu U+03BC ISOgrk3
		txt = txt.replace('&nbsp;&nbsp;',' ')
		txt = txt.replace('&nbsp;', " ") # no-break space = non-breaking space U+00A0 ISOnum
		txt = txt.replace('&ndash;', "--") # en dash U+2013 ISOpub
		txt = txt.replace('&ne;', "!=") # not equal to U+2260 ISOtech
		txt = txt.replace('&not;', "-.") # not sign U+00AC ISOnum
		txt = txt.replace('&Ntilde;', "N") # latin capital letter N with tilde U+00D1 ISOlat1
		txt = txt.replace('&ntilde;', "n") # latin small letter n with tilde U+00F1 ISOlat1
		txt = txt.replace('&Nu;', "Nu") # greek capital letter nu U+039D
		txt = txt.replace('&nu;', "nu") # greek small letter nu U+03BD ISOgrk3
		txt = txt.replace('&Oacute;', "O") # latin capital letter O with acute U+00D3 ISOlat1
		txt = txt.replace('&oacute;', "o") # latin small letter o with acute U+00F3 ISOlat1
		txt = txt.replace('&Ocirc;', "O") # latin capital letter O with circumflex U+00D4 ISOlat1
		txt = txt.replace('&ocirc;', "o") # latin small letter o with circumflex U+00F4 ISOlat1
		txt = txt.replace('&OElig;', "OE") # latin capital ligature OE U+0152 ISOlat2
		txt = txt.replace('&oelig;', "oe") # latin small ligature oe U+0153 ISOlat2
		txt = txt.replace('&Ograve;', "O") # latin capital letter O with grave U+00D2 ISOlat1
		txt = txt.replace('&ograve;', "o") # latin small letter o with grave U+00F2 ISOlat1
		txt = txt.replace('&oline;', "-") # overline = spacing overscore U+203E NEW
		txt = txt.replace('&Omega;', "Omega") # greek capital letter omega U+03A9 ISOgrk3
		txt = txt.replace('&omega;', "omega") # greek small letter omega U+03C9 ISOgrk3
		txt = txt.replace('&Omicron;', "Omicron") # greek capital letter omicron U+039F
		txt = txt.replace('&omicron;', "omicron") # greek small letter omicron U+03BF NEW
		txt = txt.replace('&ordf;', "e") # feminine ordinal indicator U+00AA ISOnum
		txt = txt.replace('&ordm;', "o") # masculine ordinal indicator U+00BA ISOnum
		txt = txt.replace('&Oslash;', "O") # latin capital letter O with stroke = latin capital letter O slash U+00D8 ISOlat1
		txt = txt.replace('&oslash;', "o") # latin small letter o with stroke = latin small letter o slash U+00F8 ISOlat1
		txt = txt.replace('&Otilde;', "O") # latin capital letter O with tilde U+00D5 ISOlat1
		txt = txt.replace('&otilde;', "o") # latin small letter o with tilde U+00F5 ISOlat1
		txt = txt.replace('&Ouml;', "O") # latin capital letter O with diaeresis U+00D6 ISOlat1
		txt = txt.replace('&ouml;', "o") # latin small letter o with diaeresis U+00F6 ISOlat1
		txt = txt.replace('&para;', "|p") # pilcrow sign = paragraph sign U+00B6 ISOnum
		txt = txt.replace('&permil;', "%0") # per mille sign U+2030 ISOtech
		txt = txt.replace('&Phi;', "Phi") # greek capital letter phi U+03A6 ISOgrk3
		txt = txt.replace('&phi;', "phi") # greek small letter phi U+03C6 ISOgrk3
		txt = txt.replace('&Pi;', "Pi") # greek capital letter pi U+03A0 ISOgrk3
		txt = txt.replace('&pi;', "pi") # greek small letter pi U+03C0 ISOgrk3
		txt = txt.replace('&piv;', "pi") # greek pi symbol U+03D6 ISOgrk3
		txt = txt.replace('&plusmn;', "+-") # plus-minus sign = plus-or-minus sign U+00B1 ISOnum
		txt = txt.replace('&pound;', "p") # pound sign U+00A3 ISOnum
		txt = txt.replace('&Prime;', "''") # double prime = seconds = inches U+2033 ISOtech
		txt = txt.replace('&prime;', "'") # prime = minutes = feet U+2032 ISOtech
		txt = txt.replace('&Psi;', "Psi") # greek capital letter psi U+03A8 ISOgrk3
		txt = txt.replace('&psi;', "psi") # greek small letter psi U+03C8 ISOgrk3
		txt = txt.replace('&quot;', '"') # quotation mark = APL quote U+0022 ISOnum
		txt = txt.replace('&raquo;', '"') # right-pointing double angle quotation mark = right pointing guillemet U+00BB ISOnum
		txt = txt.replace('&rArr;', "=>") # rightwards double arrow U+21D2 ISOtech
		txt = txt.replace('&rarr;', "->") # rightwards arrow U+2192 ISOnum
		txt = txt.replace('&rdquo;', '"') # right double quotation mark U+201D ISOnum
		txt = txt.replace('&real;', "|R") # blackletter capital R = real part symbol U+211C ISOamso
		txt = txt.replace('&reg;', "(R)") # registered sign = registered trade mark sign U+00AE ISOnum
		txt = txt.replace('&Rho;', "Rho") # greek capital letter rho U+03A1
		txt = txt.replace('&rho;', "rho") # greek small letter rho U+03C1 ISOgrk3
		txt = txt.replace('&rlm;', "") # right-to-left mark U+200F NEW RFC 2070
		txt = txt.replace('&rsaquo;', '"') # single right-pointing angle quotation mark U+203A ISO proposed
		txt = txt.replace('&rsquo;', '"') # right single quotation mark U+2019 ISOnum
		txt = txt.replace('&sbquo;', '"') # single low-9 quotation mark U+201A NEW
		txt = txt.replace('&Scaron;', "S") # latin capital letter S with caron U+0160 ISOlat2
		txt = txt.replace('&scaron;', "s") # latin small letter s with caron U+0161 ISOlat2
		txt = txt.replace('&sdot;', ".") # dot operator U+22C5 ISOamsb
		txt = txt.replace('&sect;', "S") # section sign U+00A7 ISOnum
		txt = txt.replace('&shy;', "-") # soft hyphen = discretionary hyphen U+00AD ISOnum
		txt = txt.replace('&Sigma;', "Sigma") # greek capital letter sigma U+03A3 ISOgrk3
		txt = txt.replace('&sigma;', "sigma") # greek small letter sigma U+03C3 ISOgrk3
		txt = txt.replace('&sigmaf;', "sigma") # greek small letter final sigma U+03C2 ISOgrk3
		txt = txt.replace('&sim;', "~") # tilde operator = varies with = similar to U+223C ISOtech
		txt = txt.replace('&sup1;', "1") # superscript one = superscript digit one U+00B9 ISOnum
		txt = txt.replace('&sup2;', "2") # superscript two = superscript digit two = squared U+00B2 ISOnum
		txt = txt.replace('&sup3;', "3") # superscript three = superscript digit three = cubed U+00B3 ISOnum
		txt = txt.replace('&szlig;', "SS") # latin small letter sharp s = ess-zed U+00DF ISOlat1
		txt = txt.replace('&Tau;', "Tau") # greek capital letter tau U+03A4
		txt = txt.replace('&tau;', "tau") # greek small letter tau U+03C4 ISOgrk3
		txt = txt.replace('&Theta;', "Theta") # greek capital letter theta U+0398 ISOgrk3
		txt = txt.replace('&theta;', "theta") # greek small letter theta U+03B8 ISOgrk3
		txt = txt.replace('&thetasym;', "theta") # greek small letter theta symbol U+03D1 NEW
		txt = txt.replace('&thinsp;', " ") # thin space U+2009 ISOpub
		txt = txt.replace('&THORN;', "D") # latin capital letter THORN U+00DE ISOlat1
		txt = txt.replace('&thorn;', "d") # latin small letter thorn U+00FE ISOlat1
		txt = txt.replace('&tilde;', "~") # small tilde U+02DC ISOdia
		txt = txt.replace('&times;', "x") # multiplication sign U+00D7 ISOnum
		txt = txt.replace('&trade;', "tm") # trade mark sign U+2122 ISOnum
		txt = txt.replace('&Uacute;', "U") # latin capital letter U with acute U+00DA ISOlat1
		txt = txt.replace('&uacute;', "u") # latin small letter u with acute U+00FA ISOlat1
		txt = txt.replace('&uarr;', "^") # upwards arrow U+2191 ISOnum
		txt = txt.replace('&uArr;', "^") # upwards double arrow U+21D1 ISOamsa
		txt = txt.replace('&Ucirc;', "U") # latin capital letter U with circumflex U+00DB ISOlat1
		txt = txt.replace('&ucirc;', "u") # latin small letter u with circumflex U+00FB ISOlat1
		txt = txt.replace('&Ugrave;', "U") # latin capital letter U with grave U+00D9 ISOlat1
		txt = txt.replace('&ugrave;', "u") # latin small letter u with grave U+00F9 ISOlat1
		txt = txt.replace('&uml;', "''") # diaeresis = spacing diaeresis U+00A8 ISOdia
		txt = txt.replace('&upsih;', "upsilon") # greek upsilon with hook symbol U+03D2 NEW
		txt = txt.replace('&Upsilon;', "Upsilon") # greek capital letter upsilon U+03A5 ISOgrk3
		txt = txt.replace('&upsilon;', "upsilon") # greek small letter upsilon U+03C5 ISOgrk3
		txt = txt.replace('&Uuml;', "U") # latin capital letter U with diaeresis U+00DC ISOlat1
		txt = txt.replace('&uuml;', "u") # latin small letter u with diaeresis U+00FC ISOlat1
		txt = txt.replace('&weierp;', "P") # script capital P = power set = Weierstrass p U+2118 ISOamso
		txt = txt.replace('&Xi;', "Xi") # greek capital letter xi U+039E ISOgrk3
		txt = txt.replace('&xi;', "xi") # greek small letter xi U+03BE ISOgrk3
		txt = txt.replace('&Yacute;', "Y") # latin capital letter Y with acute U+00DD ISOlat1
		txt = txt.replace('&yacute;', "y") # latin small letter y with acute U+00FD ISOlat1
		txt = txt.replace('&yen;', "y") # yen sign = yuan sign U+00A5 ISOnum
		txt = txt.replace('&Yuml;', "Y") # latin capital letter Y with diaeresis U+0178 ISOlat2
		txt = txt.replace('&yuml;', "y") # latin small letter y with diaeresis U+00FF ISOlat1
		txt = txt.replace('&Zeta;', "Zeta") # greek capital letter zeta U+0396
		txt = txt.replace('&zeta;', "zeta") # greek small letter zeta U+03B6 ISOgrk3
		txt = txt.replace('&zwj;', "|") # zero width joiner U+200D NEW RFC 2070
		txt = txt.replace('&zwnj;', " ") # zero width non-joiner U+200C NEW RFC 2070

	if removeNewLines:
		txt = txt.replace('\n','')
		txt = txt.replace('\r','')

	return txt


#################################################################################################################
def isFloat(s):
	try:
		float(s)
		return True
	except:
		return False

#################################################################################################################
def isInt(s):
	try:
		int(s)
		return True
	except:
		return False

#################################################################################################################
# if success: returns the html page given in url as a string
# else: return -1 for Exception None for HTTP timeout, '' for empty page otherwise page data
#################################################################################################################
def fetchURL(url, file='', params='', headers={}, isImage=False, encodeURL=True):
	if encodeURL:
		safe_url = urllib.quote_plus(url,'/:&?=+#@')
	else:
		safe_url = url
	if not safe_url.startswith('http://'):
		safe_url = 'http://' + safe_url
	debug("> fetchURL() " + safe_url)

	def _report_hook( count, blocksize, totalsize ):
		# just update every x%
		percent = int( float( count * blocksize * 100) / totalsize )
		if (percent % 5) == 0:
			dialogProgress.update( percent )
		if ( dialogProgress.iscanceled() ): raise

	data = None
	# create temp file if needed
	if not file:
		file = os.path.join(DIR_USERDATA, "temp.html")
	debug("file: " + file)

	# remove destination file if exists already
	deleteFile(file)

	# fetch from url
	try:
		opener = urllib.FancyURLopener()

		# add headers if supplied
		if headers:
			if not headers.has_key('User-Agent'):
				headers['User-Agent'] = 'Mozilla/5.0'
			for name, value  in headers.items():
				opener.addheader(name, value)

		if DEBUG:
			print "params=", params
			print "headers=", headers

		if params:
			fn, resp = opener.retrieve(safe_url, file, _report_hook, data=params)
		else:
			fn, resp = opener.retrieve(safe_url, file, _report_hook)
		if DEBUG:
			print fn
			print resp
		opener.close()
		urllib.urlcleanup()
	except IOError, errobj:
		HTTPErrorCode(errobj)
	except:
		handleException("fetchURL()")
	else:
		if not isImage:
			data = readFile(file)		# read retrieved file
		else:
			data = fileExist(file)		# check image file exists

	debug( "< fetchURL success=" + str(data != None))
	return data

#################################################################################################################
# fetch using urllib2 and Cookies
#################################################################################################################
def fetchCookieURL(url, fn='', params=None, headers={}, isImage=False, encodeURL=True, newRequest=True):
	if encodeURL:
		safe_url = urllib.quote_plus(url,'/:&?=+#@')
	else:
		safe_url = url
	if not safe_url.startswith('http://'):
		safe_url = 'http://' + safe_url
	debug("> fetchCookieURL() ")

	data = None
	if fn:
		deleteFile(fn)		# remove destination file if exists already

	try:
		if DEBUG:
			print "safe_url=", safe_url
			print "fn=", fn
			print "params=", params
			print "headers=", headers
			print "isImage=", isImage

		if newRequest:
			debug("create new Request")
			if not headers.has_key('User-Agent') and not headers.has_key('User-agent'):
				headers['User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
			req = urllib2.Request(safe_url, params, headers)       # create a request object
			handle = urllib2.urlopen(req)
		else:
			handle = urllib2.urlopen(safe_url)					# open new url using existing req

		if DEBUG:
			print handle.info()
			showCookies()

		urllib.urlcleanup()
	except IOError, errobj:
		HTTPErrorCode(errobj)
	except:
		handleException("fetchCookieURL()")
	else:
		debug("reading from url ...")
		data = handle.read()
		# write to file if required
		if fn and data:
			debug("writing to file ...")
			if isImage:
				mode = "wb"
			else:
				mode = "w"
			try:
				f = open(fn,mode)
				f.write(data)
				f.close()
			except:
				data = None

	debug("< fetchCookieURL()")
	return data


#################################################################################################################
def showCookies():
	try:
		for index, cookie in enumerate(cookiejar):
			print index, '  :  ', cookie
	except:
		print "no cookiejar"

#################################################################################################################
# extract URL and name from data
def extractURLName(data):
	# URL and name
	link = ''
	name = ''
	matches = re.search("href=[\"'](.*?)[\"'](?:.*?)>(.*?)<", data, re.IGNORECASE)
	if matches:
		link = matches.group(1)
		name = matches.group(2)
	else:
		name = cleanHTML(data)
	return link, name

#################################################################################################################
def searchRegEx(data, regex, flags=re.IGNORECASE):
	try:
		value = re.search(regex, data, flags).group(1)
	except:
		value = ""
	return value

#################################################################################################################
def findAllRegEx(data, regex, flags=re.MULTILINE+re.IGNORECASE):
	try:
		matchList = re.compile(regex, flags).findall(data)
	except:
		matchList = []

	if matches:
		sz = len(matches)
	else:
		sz = 0
	debug ("findAllRegEx() matches= " + str(sz))
	return matches

#############################################################################################################
def safeFilename(path):
	head, tail = os.path.split(path.replace( "\\", "/" ))
	return  os.path.join(head, re.sub(r'[\'\";:?*<>|+\\/,=]', '_', tail))

#################################################################################################################
# Does a direct image URL exist in any RSS object elements?
def isImageURL(url):
	match = re.search('([^"\'<>]+)(?<=(?:\.gif|\.jpg|\.bmp))', url, re.IGNORECASE)
	try:
		url = match.group(1)
	except:
		url = ''
	debug("isImageURL() " + str(url != ''))
	return url

#################################################################################################################
def isRSSLink(url):
	debug("isRSSLink()")
	return searchRegEx(url, '(rss|rdf|xml)$')

#################################################################################################################
def isHTMLLink(url):
	debug("isHTMLLink()")
	return searchRegEx(url, '(html|htm)$')

#################################################################################################################
class TextBoxDialog(xbmcgui.WindowDialog):
	def __init__(self):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		setResolution(self)

	def _setupDisplay(self, width, height):
		debug( "TextBoxDialog()._setupDisplay()" )

		xpos = int((REZ_W /2) - (width /2))
		ypos = int((REZ_H /2) - (height /2))

		try:
			self.addControl(xbmcgui.ControlImage(xpos, ypos, width, height, DIALOG_PANEL))
		except: pass

		xpos += 25
		ypos += 10
		self.titleCL = xbmcgui.ControlLabel(xpos, ypos, width-35, 30, '', \
											FONT14, "0xFFFFFF99", alignment=XBFONT_CENTER_X|XBFONT_CENTER_Y)
		self.addControl(self.titleCL)
		ypos += 25
		self.descCTB = xbmcgui.ControlTextBox(xpos, ypos, width-44, height-85, FONT10, '0xFFFFFFEE')
		self.addControl(self.descCTB)

	def ask(self, title, text="", file=None, width=685, height=560):
		debug( "> TextBoxDialog().ask()" )
		self._setupDisplay(width, height)
		if not title and file:
			head, title = os.path.split(file)
		self.titleCL.setLabel(title)
		if file:
			text = readFile(file)
		self.descCTB.setText(text)
		self.setFocus(self.descCTB)
		self.doModal()
		debug( "< TextBoxDialog().ask()" )

	def onAction(self, action):
		if action in CANCEL_DIALOG:
			self.close()

	def onControl(self, control):
		debug("onControl()")

#############################################################################################################
# detect if using MC360 style skin - any theme
def isMC360():
	try:
		sd = xbmc.getSkinDir()
		state = (find(sd,'360') >= 0)
	except:
		state = False
	debug("bbbLib.isMC360() " +str(state))

######################################################################################
def loadFileObj( filename, dataType ):
    debug( "loadFileObj() " + filename)
    try:
        file_handle = open( filename, "r" )
        loadObj = eval( file_handle.read() )
        file_handle.close()
    except:
        # reset to empty according to dataType
        if isinstance(dataType, dict):
            loadObj = {}
        elif isinstance(dataType, list):
            loadObj = []
        else:
            loadObj = None
    return loadObj

######################################################################################
def saveFileObj( filename, saveObj ):
    debug( "saveFileObj() " + filename)
    try:
        file_handle = open( filename, "w" )
        file_handle.write( repr( saveObj ) )
        file_handle.close()
    except:
        handleException( "_save_file_obj()" )

# establish default panel to use for dialogs
if isMC360():
	DIALOG_PANEL = os.path.join(DIR_GFX, PANEL_FILENAME_MC360)
else:
	DIALOG_PANEL = os.path.join(DIR_GFX, PANEL_FILENAME)

