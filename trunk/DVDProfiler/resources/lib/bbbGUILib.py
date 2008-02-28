"""
 Common GUI funcs and globals
""" 

import sys,os.path
import xbmc, xbmcgui

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__title__ = "bbbGUILib"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '21-01-2008'
xbmc.output("Imported From: " + __scriptname__ + " title: " + __title__ + " Date: " + __date__)

from bbbLib import *
try:
    DIR_GFX = sys.modules[ "__main__" ].DIR_GFX                 # should be in default.py
except:
    DIR_RESOURCES = sys.modules[ "__main__" ].DIR_RESOURCES     # should be in default.py
    DIR_GFX = os.path.join(DIR_RESOURCES,'gfx')


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
BTN_BACK_FILENAME = os.path.join(DIR_GFX,'backbutton.png')
LIST_HIGHLIGHT_FILENAME = os.path.join(DIR_GFX,'list_highlight.png')
FRAME_FOCUS_FILENAME = os.path.join(DIR_GFX,'frame_focus.png')
FRAME_NOFOCUS_FILENAME = os.path.join(DIR_GFX,'frame_nofocus.png')
FRAME_NOFOCUS_LRG_FILENAME = os.path.join(DIR_GFX,'frame_nofocus_large.png')
PANEL_FILENAME = os.path.join(DIR_GFX,'dialog-panel.png')
PANEL_FILENAME_MC360 = os.path.join(DIR_GFX,'dialog-panel_mc360.png')
MENU_FILENAME = os.path.join(DIR_GFX,'menu.png')

# rez GUI defined in
REZ_W = 720
REZ_H = 576

try: Emulating = xbmcgui.Emulating
except: Emulating = False


#################################################################################################################
# Dialog with options
#################################################################################################################
class DialogSelect(xbmcgui.WindowDialog):
	def __init__(self):
		if Emulating: xbmcgui.WindowDialog.__init__(self)

		setResolution(self)

		self.selectedPos = 0
		self.panelCI = None
		self.menuCL = None
		self.lastAction = 0

	def setup(self, title='',width=430, height=450, xpos=-1, ypos=-1, textColor='0xFFFFFFFF', \
			  imageWidth=0,imageHeight=22, itemHeight=22, rows=0, \
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
			self.panelCI = xbmcgui.ControlImage(xpos, ypos, width, height, panel)
			self.addControl(self.panelCI)
		except: pass

		if isDelete:
			title += " (Delete: Highlight & Press A)"

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
		if action == 0:
			return
#		debug("DialogSelect.onAction()")
		self.lastAction = action
		if action in [ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR]:
			self.selectedPos = -1
			self.close()
		elif (self.useY and action == ACTION_Y_BUTTON) or \
			 (self.useX and action == ACTION_X_BUTTON):
			self.selectedPos = self.menuCL.getSelectedPosition()
			self.close()

	def onControl(self, control):
		try:
			self.selectedPos = self.menuCL.getSelectedPosition()
		except: pass
		self.close()

	def setMenu(self, menu, icons=[]):
		debug("> DialogSelect.setMenu()")
		self.menuCL.reset()
#		self.menuCL.addItem("Exit")
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
			elif self.selectedPos < 0:
				self.selectedPos = 0
			self.menuCL.selectItem(self.selectedPos)
		debug("< DialogSelect.setMenu()")

	# show this dialog and wait until it's closed
	def ask(self, menu, selectIdx=0, icons=[]):
		debug ("> DialogSelect().ask() selectIdx=" +str(selectIdx))

		self.selectedPos = selectIdx
		self.setMenu(menu, icons)
		self.setFocus(self.menuCL)
		self.doModal()

		debug ("< DialogSelect.ask() selectedPos: " + str(self.selectedPos) + " lastAction: " + str(self.lastAction))
		return self.selectedPos, self.lastAction

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
		self.titleCL = xbmcgui.ControlLabel(xpos, ypos, width-35, 30, '', FONT14, \
											"0xFFFFFF99", alignment=XBFONT_CENTER_X|XBFONT_CENTER_Y)
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
		if action in [ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR]:
			self.close()

	def onControl(self, control):
		pass


######################################################################################
# establish default panel to use for dialogs
if isMC360():
	DIALOG_PANEL = os.path.join(DIR_GFX, PANEL_FILENAME_MC360)
else:
	DIALOG_PANEL = os.path.join(DIR_GFX, PANEL_FILENAME)
