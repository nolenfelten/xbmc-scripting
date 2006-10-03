'''
This module creates your scripts GUI from a standard XBMC skinfile.xml. It works for both Windows and
WindowDialogs. Hopefully it will make it easier to skin your scripts for different XBMC skins.

There is one optional tag you may use, <resolution>. This tag is used in place of the folder structure XBMC
skinning engine uses. It's used for setCoordinateResolution().  It is suggested you use the <resolution> tag.
<resolution> can be one of (1080i, 720p, 480p, 480p16x9, ntsc, ntsc16x9, pal, pal16x9, pal60, pal6016x9)
e.g. <resolution>pal</resolution>

GUI Builder sets initial focus to the <control> with <id> equal to <defaultcontrol>.

You may use <include> tags and references.xml will be used for default values if no tag is given.
(Unless you use fastMethod=True) All unsupported tags will be ignored. (e.g. <animation>)

GUI Builder sets up navigation based on the <onup>, <ondown>, <onleft> and <onright> tags.

The <control> <type> fadelabel takes multiple <label> and/or <info> tags.

The <control> <type> listcontrol supports an additional tag <label2> for use as the second column.
GUI Builder creates a listitem from multiple <label>, <label2> and <image> tags. In most cases these
tags won't be used as your code will populate a listcontrol.

You may pass an optional path for any custom textures. If you precede the <texture> tags value with a
backslash (\) in the xml, it will use the imagePath.
e.g. <texture>\button.png</texture> will use imagePath

You may pass an optional progress dialog, with an optional first line and percent finished as a continuation
for your scripts initialization. GUI Builder will begin at percent finished and finish at 100 percent.

You may pass fastMethod=True. If True, no dialogs will be displayed, GUI Builder will not resolve <include> tags
and will not use default values from references.xml for missing tags. If you do include all necessary tags in the
xml file and no <include> tags, this can speed up GUI creation slightly.

If you are having problems, pass debug=True and progress will be output to the scripts info window and
if <loglevel> is at one (1) or higher to xbmc.log.

You need to pass your Window or WindowDialog Class as self and a skin xml file. All other arguments are optional.

**************************************************************************************
class GUIBuilder:
GUIBuilder(win, skinXML[, imagePath, useDescAsKey, title, line1, dlg, pct, fastMethod, debug])

win					: class - Your Window or WindowDialog class passed as self.
skinXML				: string - The xml file including path you want to use.
imagePath			: [opt] string - The path to any custom images.
useDescAsKey		: [opt] bool - True=<description> as key / False=<id> for key.
title					: [opt] string - Title you want to use for a new progress dialog.
line1					: [opt] string - The first line of the progress dialog.
dialog				: [opt] progress dialog - A current progress dialog.
pct					: [opt] integer - The percent already completed. (0-100)
fastMethod			: [opt] bool - True=no dialogs, no <include> tags and no defaults from references.xml.
useLocal				: [opt] bool - True=use a local language file / False=use XBMC language files
debug				: [opt] bool - True=output debug information / False=no logging.

*Note, 	You may use the above as keywords for arguments and skip certain optional arguments.
			Once you use a keyword, all following arguments require the keyword.

example:
	- import guibuilder
	- guibuilder.GUIBuilder(self,  'Project Mayhem III.xml', fastMethod=True)
**************************************************************************************


GUI Builder sets self.SUCCEEDED to True if the window creation succeeded or False if something failed. You may
want to check this before the call to doModal().

GUI Builder creates two variables: self.coordinates[x, y] and self.controls{key : {}}
	1.	self.coordinates[x, y], a list variable of offsets, for a <coordinates> based window.
		All control x, y positions will be based on these values if they exist. Defaults to [0, 0]
	2.	self.controls[key] = { # a dictionary of your controls, with the controls <id> or <description> as the key.
			'id'				: integer - <id> tag.
			'controlId'	: integer - Id# XBMC uses for the control.
			'control' 		: <control object> - The control itself.
			'posx'		 	: integer - x coordinate of control.
			'posy'			: integer - y coordinate of control.
			'width'		: integer - width of control.
			'height'		: integer - height of control.
			'visible' 		: string - <visible> condition.
			'animation' 	: dictionary - <animation> (not used yet).
			'onclick' 		: string - <onclick> event. (eg <onclick>self.exitScript(True)</onclick>)
			'onfocus' 	: string - <onfocus> event (eg <onfocus>self.slidePad(True)</onfocus>)
		}

	example: How to center zoom a control 20%. w/useDescAsKey=True
		width = self.controls['Play Button']['width'] * 1.2
		height = self.controls['Play Button']['height'] * 1.2
		widthOffset = int((width - self.controls['Play Button']['width']) / 2)
		heightOffset = int((height - self.controls['Play Button']['height']) / 2)
		x = self.controls['Play Button']['posx'] + self.coordinates[0] - widthOffset
		y = self.controls['Play Button']['posy'] + self.coordinates[1] - heightOffset
		self.controls['Play Button']['control'].setPosition(x, y)
		self.controls['Play Button']['control'].setWidth(width)
		self.controls['Play Button']['control'].setWidth(height)

	example: [visible] w/useDescAsKey=False
		- self.controls[300]['control'].setVisible(xbmc.getCondVisibility(self.controls[300]['visible']))

	example: [onclick] w/useDescAsKey=True
		- exec self.controls['Play Button]['onclick']

Post a message at http://www.xbmc.xbox-scene.com/forum/ with any suggestions.

Credits:
GetConditionalVisibility(), GetSkinPath(), LoadReferences(), LoadIncludes(), ResolveInclude()
The above functions were translated from Xbox Media Center's source, thanks Developers.
A special thanks to elupus for shaming me into doing it the right way. :)

Nuka1195
'''

import xbmc, xbmcgui
import xml.dom.minidom
import re, os

try: import language
except: pass

class GUIBuilder:
	def __init__(self, win, skinXML, imagePath='', useDescAsKey=False, title='GUI Builder', line1='', dlg=None,
						pct=0, fastMethod=False, useLocal=False, debug=False):
		try:
			self.debug									= debug
			self.debugWrite('guibuilder.py', 2)
			self.win 										= win
			self.win.SUCCEEDED						= True
			self.skinXML 								= skinXML[skinXML.rfind('\\') + 1:]
			self.useDescAsKey						= useDescAsKey
			self.fastMethod							= fastMethod
			self.useLocal								= useLocal
			self.pct 										= pct
			self.lineno 									= line1 != ''
			self.lines 									= [''] * 3
			self.lines[0] 								= line1
			self.lines[self.lineno] 					= 'Creating GUI from %s.' % (self.skinXML,)
			self.initVariables()
			try:
				if ( self.useLocal ): self.language = language.Language()
			except: self.useLocal = False
			if (not self.fastMethod):	
				if (dlg): self.dlg = dlg
				else: 
					self.dlg = xbmcgui.DialogProgress()
					self.dlg.create(title)
				self.dlg.update(self.pct, self.lines[0], self.lines[1], self.lines[2])
				self.pct1 = int((100 - pct) * 0.333)
				self.includesExist = self.LoadIncludes()
				self.referencesExist = self.LoadReferences()
			else:
				self.includesExist = False
			self.pct1 = int((100 - self.pct) * 0.333)
			self.parseSkinFile(imagePath, skinXML)
			if (self.win.SUCCEEDED): self.setNav()
			if (not self.win.SUCCEEDED): raise
			else:
				if (self.defaultControl and self.win.controls.has_key(self.navigation[self.defaultControl][0])):
					self.win.setFocus(self.win.controls[self.navigation[self.defaultControl][0]]['control'])
				self.setCondVisibility()
				if (self.includesExist): self.incdoc.unlink()
				self.clearVariables()
			if (not self.fastMethod): self.dlg.close()
		except:
			self.win.SUCCEEDED = False
#			if (not self.fastMethod):
#				if (dlg): dlg.close()
#				dlg = xbmcgui.Dialog()
#				dlg.ok(title, 'There was an error setting up controls.', 'Check your skin file:', skinXML)
#				self.dlg.close()


	def debugWrite(self, function, action, lines=[], values=[]):
		if (self.debug):
			Action = ('Failed', 'Succeeded', 'Started')
			Highlight = ('__', '__', '<<<<< ', '__', '__', ' >>>>>')
			xbmc.output('%s%s%s : (%s)\n' % (Highlight[action], function, Highlight[action + 3], Action[action]))
			try:
				for cnt, line in enumerate(lines):
					fLine = '%s\n' % (line,)
					xbmc.output(fLine % values[cnt])
			except: pass


	def initVariables(self):
		self.win.SUCCEEDED		 		= True
		self.win.controls 					= {}
		#self.win.controlKey					= {}
		self.navigation						= {}
		self.m_references	 				= {}
		self.resPath 						= {}
		self.resolutions = {'1080i' : 0, '720p' : 1, '480p' : 2, '480p16x9' : 3, 'ntsc' : 4, 'ntsc16x9' : 5, 'pal' : 6, 'pal16x9' : 7, 'pal60' : 8, 'pal6016x9' : 9}
		for key, value in self.resolutions.items(): self.resPath[value] = key
		self.currentResolution 			= self.win.getResolution()
		self.resolution						= self.resolutions['pal']
		self.debugWrite('initVariables', True)


	def clearVariables(self):
		self.navigation						= None
		self.m_references	 				= None
		self.resPath 						= None
		self.resolutions 					= None
		self.resPath						= None
		self.currentResolution 			= None
		self.resolution						= None
		
	def GetConditionalVisibility(self, conditions):
		if (len(conditions) == 0): return 'true'
		if (len(conditions) == 1): return conditions[0]
		else:
			# multiple conditions should be anded together
			conditionString = "["
			for i in range(len(conditions) - 1):
				conditionString += conditions[i] + "] + ["
			conditionString += conditions[len(conditions) - 1] + "]"
		return conditionString


	def addCtl(self, control):
		try:
			control['special'] = ''
			if (self.useDescAsKey): key = control['description']
			else: key = int(control['id'])
			if (control['type'] == 'image'):
				if (control.has_key('info')): 
					if (control['info'][0] != ''): control['texture'] = xbmc.getInfoImage(control['info'][0])
				ctl = (xbmcgui.ControlImage(x=int(control['posx']) + self.posx,\
					y=int(control['posy']) + self.posy, width=int(control['width']), height=int(control['height']),\
					filename=control['texture'], colorKey=control['colorkey'], aspectRatio=int(control['aspectratio'])))#,\
					#colorDiffuse=control['colordiffuse']))
				self.win.addControl(ctl)
			elif (control['type'] == 'label'):
				if (control.has_key('info')):
					if (control['info'][0] != ''): control['label'][0] = xbmc.getInfoLabel(control['info'][0])
				ctl = (xbmcgui.ControlLabel(x=int(control['posx']) + self.posx,\
					y=int(control['posy']) + self.posy, width=int(control['width']), height=int(control['height']), label=control['label'][0],\
					font=control['font'], textColor=control['textcolor'], disabledColor=control['disabledcolor'], alignment=control['align'],\
					hasPath=control['haspath'], angle=int(control['angle'])))#, shadowColor=control['shadowcolor']))
				self.win.addControl(ctl)
			elif (control['type'] == 'button'):
				if (control.has_key('info')):
					if (control['info'][0] != ''): control['label'][0] = xbmc.getInfoLabel(control['info'][0])
				ctl = (xbmcgui.ControlButton(x=int(control['posx']) + self.posx,\
					y=int(control['posy']) + self.posy, width=int(control['width']), height=int(control['height']), label=control['label'][0],\
					font=control['font'], textColor=control['textcolor'], disabledColor=control['disabledcolor'], alignment=control['align'],\
					angle=int(control['angle']), shadowColor=control['shadowcolor'], focusTexture=control['texturefocus'],\
					noFocusTexture=control['texturenofocus'], textXOffset=int(control['textoffsetx']), textYOffset=int(control['textoffsety'])))
				self.win.addControl(ctl)
			elif (control['type'] == 'checkmark'):
				if (control.has_key('info')):
					if (control['info'][0] != ''): control['label'][0] = xbmc.getInfoLabel(control['info'][0])
				ctl = (xbmcgui.ControlCheckMark(x=int(control['posx']) + self.posx,\
					y=int(control['posy']) + self.posy, width=int(control['width']), height=int(control['height']), label=control['label'][0],\
					font=control['font'], textColor=control['textcolor'], disabledColor=control['disabledcolor'], alignment=control['align'],\
					focusTexture=control['texturecheckmark'], noFocusTexture=control['texturecheckmarknofocus'],\
					checkWidth=int(control['markwidth']), checkHeight=int(control['markheight'])))
				self.win.addControl(ctl)
			elif (control['type'] == 'textbox'):
				ctl = (xbmcgui.ControlTextBox(x=int(control['posx']) + self.posx,\
					y=int(control['posy']) + self.posy, width=int(control['width']), height=int(control['height']), font=control['font'],\
					textColor=control['textcolor']))
				self.win.addControl(ctl)
				if (control.has_key('label')): ctl.setText(control['label'][0])
			elif (control['type'] == 'fadelabel'):
				ctl = (xbmcgui.ControlFadeLabel(x=int(control['posx']) + self.posx,\
					y=int(control['posy']) + self.posy, width=int(control['width']), height=int(control['height']), font=control['font'],\
					textColor=control['textcolor'], alignment=control['align']))#, shadowColor=control['shadowcolor']))
				self.win.addControl(ctl)
				if (control.has_key('info')):
					for item in control['info']:
						if (item != ''): ctl.addLabel(xbmc.getInfoLabel(item))
				if (control.has_key('label')):
					for item in control['label']:
						if (item != ''): ctl.addLabel(item)
			elif (control['type'] == 'listcontrol'):
				ctl = (xbmcgui.ControlList(x=int(control['posx']) + self.posx,\
					y=int(control['posy']) + self.posy, width=int(control['width']), height=int(control['height']), font=control['font'],\
					textColor=control['textcolor'], alignmentY=control['aligny'], buttonTexture=control['texturenofocus'],\
					buttonFocusTexture=control['texturefocus'], selectedColor=control['selectedcolor'], imageWidth=int(control['itemwidth']),\
					imageHeight=int(control['itemheight']), itemTextXOffset=int(control['textxoff']), itemTextYOffset=int(control['textyoff']),\
					itemHeight=int(control['textureheight']), space=int(control['spacebetweenitems'])))#, shadowColor=control['shadowcolor']))
				self.win.addControl(ctl)
				ctl.setPageControlVisible( not control['hidespinner'] )
				fheight = int(control['textureheight']) + int(control['spacebetweenitems'])
				ftotalheight = int(control['height']) - 20
				control['special'] = int(float(ftotalheight) / float(fheight))
				if (control.has_key('label')):
					for cnt, item in enumerate(control['label']):
						if (item != ''): 
							if (cnt < len(control['label2'])): tmp = control['label2'][cnt]
							else: tmp = ''
							if (cnt < len(control['image'])): tmp2 = control['image'][cnt]
							elif control['image']:	tmp2 = control['image'][len(control['image']) - 1]
							else: tmp2 = ''
							l = xbmcgui.ListItem(item, tmp, '', tmp2)
							ctl.addItem(l)
			
			try:
				self.win.controls[key] = {
					'id'				: int(control['id']),
					'controlId'	: ctl.getId(),
					'control' 		: ctl,
					'special'		: control['special'],
					'posx'		 	: int(control['posx']),
					'posy'			: int(control['posy']),
					'width'		: int(control['width']),
					'height'		: int(control['height']),
					'visible' 		: control['visible'].lower(),
					'animation' 	: control['animation'],
					'onclick' 		: control['onclick'],
					'onfocus' 	: control['onfocus']
				}
				#self.win.controlKey[ctl.getId()] = key
				self.navigation[int(control['id'])] = (key, int(control['onup']), int(control['ondown']), int(control['onleft']), int(control['onright']))
				ctl.setVisible(xbmc.getCondVisibility(control['visible']))
			except: pass
		except:
			if (not self.fastMethod): self.dlg.close()
			self.win.SUCCEEDED = False
			self.controlsFailed += str(key) + ', ' # control['id']
			self.controlsFailedCnt += 1


	def setResolution(self):
		try:
			offset = 0
			# if current and skinned resolutions differ and skinned resolution is not
			# 1080i or 720p (they have no 4:3), calculate widescreen offset
			if ((not (self.currentResolution == self.resolution)) and self.resolution > 1):
				# check if current resolution is 16x9
				if (self.currentResolution == 0 or self.currentResolution % 2): iCur16x9 = 1
				else: iCur16x9 = 0
				# check if skinned resolution is 16x9
				if (self.resolution % 2): i16x9 = 1
				else: i16x9 = 0
				# calculate widescreen offset
				offset = iCur16x9 - i16x9
			self.win.setCoordinateResolution(self.resolution + offset)
			self.debugWrite('setResolution', True, ['Current resolution: %i-%s', 'Skinned at resolution: %i-%s',\
				'Set coordinate resolution at: %i-%s'], [(self.currentResolution, self.resPath[self.currentResolution],),\
				(self.resolution, self.resPath[self.resolution],), (self.resolution + offset, self.resPath[self.resolution + offset],)])
		except: self.debugWrite('setResolution', False)


	def parseSkinFile(self, imagePath, filename):
		try:
			cnt = -1
			self.controlsFailed = ''
			self.controlsFailedCnt = 0
			if (not self.fastMethod):
				self.lines[self.lineno + 1]	= 'loading %s file...' % (self.skinXML,)
				self.dlg.update(self.pct, self.lines[0], self.lines[1], self.lines[2])
			# load and parse skin.xml file
			skindoc = xml.dom.minidom.parse(filename)
			root = skindoc.documentElement
			# make sure this is a valid <window> xml file
			if (not root or root.tagName != 'window'): raise

			self.posx = 0
			self.posy = 0

			# check for <defaultcontrol> and <coordinates> based system
			try:
				default = self.FirstChildElement(root, 'defaultcontrol')
				if (default and default.firstChild): self.defaultControl = int(default.firstChild.nodeValue)
				else: self.defaultControl = None
				coordinates = self.FirstChildElement(root, 'coordinates')
				if (coordinates and coordinates.firstChild):
					systemBase = self.FirstChildElement(coordinates, 'system')
					if (systemBase and systemBase.firstChild): 
						system = int(systemBase.firstChild.nodeValue)
						if (system == 1):
							posx = self.FirstChildElement(coordinates, 'posx')
							if (posx and posx.firstChild): self.posx = int(posx.firstChild.nodeValue)
							posy = self.FirstChildElement(coordinates, 'posy')
							if (posy and posy.firstChild): self.posy = int(posy.firstChild.nodeValue)
			except: pass
			self.win.coordinates = [self.posx, self.posy]

			# check for a <resolution> tag and setCoordinateResolution()
			resolution = self.FirstChildElement(root, 'resolution')
			if (resolution and resolution.firstChild): self.resolution = self.resolutions.get(resolution.firstChild.nodeValue.lower(), 6)
			self.setResolution()

			# make sure <controls> block exists and resolve if necessary
			controls = self.FirstChildElement(root, 'controls')
			if (controls and controls.firstChild):
				if (self.includesExist): controls = self.ResolveInclude(controls)
			else: raise

			# parse and resolve each <control>
			data = controls.getElementsByTagName('control')
			if (not data): raise
			if (not self.fastMethod):
				self.lines[self.lineno + 1]	= 'parsing %s file...' % (self.skinXML,)
				t = len(data)
			for cnt, control in enumerate(data):
				if (not self.fastMethod): self.dlg.update(int((float(self.pct1) / float(t) * (cnt + 1)) + self.pct), self.lines[0], self.lines[1], self.lines[2])
				if (self.includesExist): tmp = self.ResolveInclude(control)
				else: tmp = control
				ctl 		= {}
				node 	= self.FirstChildElement(tmp, None)
				lbl1 		= []
				lbl2 		= []
				ifo 		= []
				img		= []
				vis 		= []
				anim		= {}
				ctype 	= ''
				# loop thru control and find all tags
				while (node):
					# key node so save to the dictionary
					if (node.tagName.lower() == 'label'): 
						try:
							v = node.firstChild.nodeValue
							if ( self.useLocal ):
								ls = self.language.string(int(v))
							else: ls = xbmc.getLocalizedString(int(v))
							if (ls): lbl1.append(ls)
							else: raise
						except: 
							if (node.hasChildNodes()): lbl1.append(node.firstChild.nodeValue)
					elif (node.tagName.lower() == 'label2'):
						try: 
							v = node.firstChild.nodeValue
							if ( self.useLocal ):
								ls = self.language.string(int(v))
							else: ls = xbmc.getLocalizedString(int(v))
							if (ls): lbl2.append(ls)
							else: raise
						except:
							if (node.hasChildNodes()): lbl2.append(node.firstChild.nodeValue)
					elif (node.tagName.lower() == 'info'):
						if (node.hasChildNodes()): ifo.append(node.firstChild.nodeValue)
					elif (node.tagName.lower() == 'image'):
						if (node.hasChildNodes()): img.append(node.firstChild.nodeValue)
					elif (node.tagName.lower() == 'visible'):
						if (node.hasChildNodes()): vis.append(node.firstChild.nodeValue)
					elif (node.tagName.lower() == 'animation'):
						if (node.hasChildNodes()): 
							anim['type'] = node.firstChild.nodeValue
							if (node.hasAttributes()):
								anim['effect']			= node.getAttribute('effect')
								anim['time']			= node.getAttribute('time')
								anim['delay']			= node.getAttribute('delay')
								anim['start']			= node.getAttribute('start')
								anim['end']				= node.getAttribute('end')
								anim['acceleration']	= node.getAttribute('acceleration')
								anim['center']			= node.getAttribute('center')
								anim['condition']		= node.getAttribute('condition')
								anim['reversible']		= node.getAttribute('reversible')
					elif (node.hasChildNodes()): 
						if (node.tagName.lower() == 'type'): ctype = node.firstChild.nodeValue
						ctl[node.tagName.lower()] = node.firstChild.nodeValue
					node = self.NextSiblingElement(node, None)

				# setup the controls settings and defaults if necessary
				if (ctype):
					# the following apply to all controls
					if (not ctl.has_key('id')): ctl['id'] = self.m_references.get(ctype + '_id', '0')
					if (not ctl.has_key('description')): ctl['description'] = self.m_references.get(ctype + '_description', 'none')
					if (not ctl.has_key('posx')): ctl['posx'] = self.m_references.get(ctype + '_posx', '0')
					if (not ctl.has_key('posy')): ctl['posy'] = self.m_references.get(ctype + '_posy', '0')
					if (not ctl.has_key('width')): ctl['width'] = self.m_references.get(ctype + '_width', '100')
					if (not ctl.has_key('height')): ctl['height'] = self.m_references.get(ctype + '_height', '100')
					if (not ctl.has_key('onup')): ctl['onup'] = self.m_references.get(ctype + '_onup', ctl['id'])
					if (not ctl.has_key('ondown')): ctl['ondown'] = self.m_references.get(ctype + '_ondown', ctl['id'])
					if (not ctl.has_key('onleft')): ctl['onleft'] = self.m_references.get(ctype + '_onleft', ctl['id'])
					if (not ctl.has_key('onright')): ctl['onright'] = self.m_references.get(ctype + '_onright', ctl['id'])
					if (vis): ctl['visible'] = self.GetConditionalVisibility(vis)
					else: ctl['visible'] = self.m_references.get(ctype + '_visible', 'true')
					
					if (not ctl.has_key('onclick')): ctl['onclick'] = ''
					if (not ctl.has_key('onfocus')): ctl['onfocus'] = ''
					if (anim): ctl['animation'] = anim
					else: ctl['animation'] = ''
						
					if (ctype == 'image' or ctype == 'label' or ctype == 'fadelabel' or ctype == 'button' or ctype == 'checkmark' or ctype == 'textbox'):
						if (ifo): ctl['info'] = ifo
						else: ctl['info'] = [self.m_references.get(ctype + '_info', '')]

					if (ctype == 'label' or ctype == 'fadelabel' or ctype == 'button' or ctype == 'checkmark' or ctype == 'textbox' or ctype == 'listcontrol'):
						if (lbl1): ctl['label'] = lbl1
						else: ctl['label'] = [self.m_references.get(ctype + '_label', '')]
						if (not ctl.has_key('shadowcolor')): ctl['shadowcolor'] = self.m_references.get(ctype + '_shadowcolor', '')
						if (not ctl.has_key('font')): ctl['font'] = self.m_references.get(ctype + '_font', 'font12')
						if (not ctl.has_key('textcolor')): ctl['textcolor'] = self.m_references.get(ctype + '_textcolor', '0xFF000000')

					if (ctype == 'label' or ctype == 'fadelabel' or ctype == 'button' or ctype == 'checkmark' or ctype == 'listcontrol'):
						if (not ctl.has_key('align')): ctl['align'] = self.m_references.get(ctype + '_align', 0)
						if (ctl['align'] == 'left'): ctl['align'] = 0
						elif (ctl['align'] == 'right'): ctl['align'] = 1
						elif (ctl['align'] == 'center'): ctl['align'] = 2
						else: ctl['align'] = 0
						if (not ctl.has_key('aligny')): ctl['aligny'] = self.m_references.get(ctype + '_aligny', 0)
						if (ctl['aligny'] == 'center'): ctl['aligny'] = 4
						else: ctl['aligny'] = 0
						ctl['align'] += ctl['aligny']
							
					if (ctype == 'label' or ctype == 'button' or ctype == 'checkmark'):
						if (not ctl.has_key('disabledcolor')): ctl['disabledcolor'] = self.m_references.get(ctype + '_disabledcolor', '0x60000000')

					if (ctype == 'label' or ctype == 'button'):
						if (not ctl.has_key('angle')): ctl['angle'] = self.m_references.get(ctype + '_angle', '0')

					if (ctype == 'listcontrol' or ctype == 'button'):
						if (not ctl.has_key('texturefocus')): ctl['texturefocus'] = self.m_references.get(ctype + '_texturefocus', '')
						elif (ctl['texturefocus'][0] == '\\'): ctl['texturefocus'] = os.path.join(imagePath, ctl['texturefocus'][1:])
						if (not ctl.has_key('texturenofocus')): ctl['texturenofocus'] = self.m_references.get(ctype + '_texturenofocus', '')
						elif (ctl['texturenofocus'][0] == '\\'): ctl['texturenofocus'] = os.path.join(imagePath, ctl['texturenofocus'][1:])
						
					if (ctype == 'image'):
						if (not ctl.has_key('aspectratio')): ctl['aspectratio'] = self.m_references.get(ctype + '_aspectratio', 0)
						if (ctl['aspectratio'] == 'stretch'): ctl['aspectratio'] = 0
						elif (ctl['aspectratio'] == 'scale'): ctl['aspectratio'] = 1
						elif (ctl['aspectratio'] == 'keep'): ctl['aspectratio'] = 2
						else: ctl['aspectratio'] = 0
						if (not ctl.has_key('colorkey')): ctl['colorkey'] = self.m_references.get(ctype + '_colorkey', '')
						if (not ctl.has_key('colordiffuse')): ctl['colordiffuse'] = self.m_references.get(ctype + '_colordiffuse', '0xFFFFFFFF')
						if (not ctl.has_key('texture')): ctl['texture'] = self.m_references.get(ctype + '_texture', '')
						elif (ctl['texture'][0] == '\\'): ctl['texture'] = os.path.join(imagePath, ctl['texture'][1:])
					if (ctype == 'label'):
						if (not ctl.has_key('haspath')): ctl['haspath'] = self.m_references.get(ctype + '_haspath', 0)
						if (ctl['haspath'] == 'false' or ctl['haspath'] == 'no'): ctl['haspath'] = 0
						elif (ctl['haspath'] == 'true' or ctl['haspath'] == 'yes'): ctl['haspath'] = 1
						else: ctl['haspath'] = 0
						if (ctl.has_key('number')): ctl['label'][0] = [ctl['number']]

					if (ctype == 'button'):
						if (not ctl.has_key('textoffsetx')): ctl['textoffsetx'] = self.m_references.get(ctype + '_textoffsetx', '0')
						if (not ctl.has_key('textoffsety')): ctl['textoffsety'] = self.m_references.get(ctype + '_textoffsety', '0')
							
					if (ctype == 'checkmark'):
						if (not ctl.has_key('texturecheckmark')): ctl['texturecheckmark'] = self.m_references.get(ctype + '_texturecheckmark', '')
						elif (ctl['texturecheckmark'][0] == '\\'): ctl['texturecheckmark'] = os.path.join(imagePath, ctl['texturecheckmark'][1:])
						if (not ctl.has_key('texturecheckmarknofocus')): ctl['texturecheckmarknofocus'] = self.m_references.get(ctype + '_texturecheckmarknofocus', '')
						elif (ctl['texturecheckmarknofocus'][0] == '\\'): ctl['texturecheckmarknofocus'] = os.path.join(imagePath, ctl['texturecheckmarknofocus'][1:])
						if (not ctl.has_key('markwidth')): ctl['markwidth'] = self.m_references.get(ctype + '_markwidth', '20')
						if (not ctl.has_key('markheight')): ctl['markheight'] = self.m_references.get(ctype + '_markheight', '20')

					if (ctype == 'listcontrol'):
						ctl['label2'] = lbl2
						ctl['image'] = img
						if (not ctl.has_key('selectedcolor')): ctl['selectedcolor'] = self.m_references.get(ctype + '_selectedcolor', '0xFFFFFFFF')
						if (not ctl.has_key('itemwidth')): ctl['itemwidth'] = self.m_references.get(ctype + '_itemwidth', '20')
						if (not ctl.has_key('itemheight')): ctl['itemheight'] = self.m_references.get(ctype + '_itemheight', '20')
						if (not ctl.has_key('textureheight')): ctl['textureheight'] = self.m_references.get(ctype + '_textureheight', '20')
						if (not ctl.has_key('textxoff')): ctl['textxoff'] = self.m_references.get(ctype + '_textxoff', '0')
						if (not ctl.has_key('textyoff')): ctl['textyoff'] = self.m_references.get(ctype + '_textyoff', '0')
						if (not ctl.has_key('spacebetweenitems')): ctl['spacebetweenitems'] = self.m_references.get(ctype + '_spacebetweenitems', '0')
						if (not ctl.has_key('hidespinner')): ctl['hidespinner'] = 'false'
						if (ctl['hidespinner'] == 'false' or ctl['hidespinner'] == 'no'): ctl['hidespinner'] = 0
						elif (ctl['hidespinner'] == 'true' or ctl['hidespinner'] == 'yes'): ctl['hidespinner'] = 1
						else: ctl['hidespinner'] = 0
						if (not ctl['image']): ctl['image'] = [self.m_references.get(ctype + '_image', ' ')]
						for i in range(len(ctl['image'])):
							if (ctl['image'][i][0] == '\\'): ctl['image'][i] = os.path.join(imagePath, ctl['image'][i][1:])

				self.addCtl(ctl)
			self.pct += self.pct1
		except:
			if (not self.fastMethod): self.dlg.close()
			self.win.SUCCEEDED = False
		try: skindoc.unlink()
		except: pass
		if (self.win.SUCCEEDED):
			self.debugWrite('parseSkinFile', self.win.SUCCEEDED, ['Parsed %i control(s) from %s'], [(cnt + 1, self.skinXML,)])
		else:
			if (not self.controlsFailed): self.controlsFailed = self.skinXML + ' is corrupted--'
			self.debugWrite('parseSkinFile', self.win.SUCCEEDED, ['Parsed %i control(s) from %s', 'Control(s) Failed: %s'],\
				[((cnt + 1 - self.controlsFailedCnt), self.skinXML), self.controlsFailed[:-2]])


	def setNav(self):
		try: #self.navigation[int(control['id'])] = (key, int(control['onup']), int(control['ondown']), int(control['onleft']), int(control['onright']))
			if (not self.fastMethod): 
				self.lines[self.lineno + 1]	= 'setting up navigation...'
				t = len(self.navigation)
			for cnt, item in enumerate(self.navigation.values()):
				if (not self.fastMethod): self.dlg.update(int((float(self.pct1) / float(t) * (cnt + 1)) + self.pct), self.lines[0], self.lines[1], self.lines[2])
				if (self.navigation.has_key(item[1]) and self.win.controls.has_key(self.navigation[item[1]][0])):
					self.win.controls[item[0]]['control'].controlUp(self.win.controls[self.navigation[item[1]][0]]['control'])
				if (self.navigation.has_key(item[2]) and self.win.controls.has_key(self.navigation[item[2]][0])):
					self.win.controls[item[0]]['control'].controlDown(self.win.controls[self.navigation[item[2]][0]]['control'])
				if (self.navigation.has_key(item[3]) and self.win.controls.has_key(self.navigation[item[3]][0])):
					self.win.controls[item[0]]['control'].controlLeft(self.win.controls[self.navigation[item[3]][0]]['control'])
				if (self.navigation.has_key(item[4]) and self.win.controls.has_key(self.navigation[item[4]][0])):
					self.win.controls[item[0]]['control'].controlRight(self.win.controls[self.navigation[item[4]][0]]['control'])
			self.pct += self.pct1
			self.debugWrite('setNavigation', True)
			
		except:
			if (not self.fastMethod): self.dlg.close()
			self.win.SUCCEEDED = False
			self.debugWrite('setNavigation', False)
			
			
	def setCondVisibility(self):
		if (not self.fastMethod): 
			self.lines[self.lineno + 1]	= 'setting up visibility...'
			t = len(self.win.controls)
		pattern1 	= 'control.hasfocus\(([0-9]+)\)'
		pattern2 	= 'control.isvisible\(([0-9]+)\)'
		for cnt, key in enumerate(self.win.controls.keys()):
			if (not self.fastMethod): self.dlg.update(int((float(self.pct1) / float(t) * (cnt + 1)) + self.pct), self.lines[0], self.lines[1], self.lines[2])
			try:
				visible = self.win.controls[key]['visible']
				visibleChanged = False
				# fix Control.HasFocus(id) visibility condition
				items = re.findall(pattern1, visible)
				for item in items:
					visibleChanged = True
					if (self.win.controls.has_key(self.navigation[int(item)][0])):
						actualId = self.win.controls[self.navigation[int(item)][0]]['controlId']
						visible = re.sub(pattern1, 'control.hasfocus(%d)' % actualId, visible)
				# fix Control.IsVisible(id) visibility condition
				items = re.findall(pattern2, visible)
				for item in items:
					visibleChanged = True
					if (self.win.controls.has_key(self.navigation[int(item)][0])):
						actualId = self.win.controls[self.navigation[int(item)][0]]['controlId']
						visible = re.sub(pattern2, 'control.isvisible(%d)' % actualId, visible)
				# set the controls new visible condition
				if (visibleChanged): self.win.controls[key]['visible'] = visible
				# set the controls initial visibility
				self.win.controls[key]['control'].setVisible(xbmc.getCondVisibility(visible))
			except: pass
		self.debugWrite('setCondVisibility', True)


	def GetSkinPath(self, filename):
		from os import path
		default = 6
		defaultwide = 7
		try:
			fname = os.path.join('Q:\\skin', xbmc.getSkinDir(), 'skin.xml')
			skindoc = xml.dom.minidom.parse(fname)
			root = skindoc.documentElement
			if (not root or root.tagName != 'skin'): raise
			strDefault = self.FirstChildElement(root, 'defaultresolution')
			if (strDefault and strDefault.firstChild): default = self.resolutions.get(strDefault.firstChild.nodeValue.lower(), default)
			strDefaultWide = self.FirstChildElement(root, 'defaultresolutionwide')
			if (strDefaultWide and strDefaultWide.firstChild): defaultwide = self.resolutions.get(strDefaultWide.firstChild.nodeValue.lower(), defaultwide)
			skindoc.unlink()
		except: pass
		fname = os.path.join('Q:\\skin', xbmc.getSkinDir(), self.resPath[self.currentResolution], filename)
		if (path.exists(fname)):
			if (filename == 'references.xml'): self.resolution = self.currentResolution
			self.debugWrite('GetSkinPath', True, ['Found path for %s at %s'], [(filename, fname,)])
			return fname
		# if we're in 1080i mode, try 720p next
		if (self.currentResolution == 0):
			fname = os.path.join('Q:\\skin', xbmc.getSkinDir(), self.resPath[1], filename)
			if (path.exists(fname)):
				if (filename == 'references.xml'): self.resolution = 1
				self.debugWrite('GetSkinPath', True, ['Found path for %s at %s'], [(filename, fname,)])
				return fname
		# that failed - drop to the default widescreen resolution if we're in a widemode
		if (self.currentResolution % 2):
			fname = os.path.join('Q:\\skin', xbmc.getSkinDir(), self.resPath[defaultwide], filename)
			if (path.exists(fname)):
				if (filename == 'references.xml'): self.resolution = defaultwide
				self.debugWrite('GetSkinPath', True, ['Found path for %s at %s'], [(filename, fname,)])
				return fname
		# that failed - drop to the default resolution
		fname = os.path.join('Q:\\skin', xbmc.getSkinDir(), self.resPath[default], filename)
		if (path.exists(fname)):
			if (filename == 'references.xml'): self.resolution = default
			self.debugWrite('GetSkinPath', True, ['Found path for %s at %s'], [(filename, fname,)])
			return fname
		else:
			self.debugWrite('GetSkinPath', False, ['No path for %s found'], [(filename,)])
			return None

	
	def LoadReferences(self):
		if (not self.fastMethod): 
			self.lines[self.lineno + 1]	= 'loading references.xml file...'
			self.dlg.update(self.pct, self.lines[0], self.lines[1], self.lines[2])
			self.pct += self.pct1
		# get the references.xml file location if it exists
		referenceFile = self.GetSkinPath('references.xml')
		# load and parse references.xml file
		try: refdoc = xml.dom.minidom.parse(referenceFile)
		except: 
			self.debugWrite('LoadReferences', False)
			return False
		root = refdoc.documentElement
		if (not root or root.tagName != 'controls'): 
			refdoc.unlink()
			self.debugWrite('LoadReferences', False)
			return False
		data = refdoc.getElementsByTagName('control')
		for control in data:
			if (self.includesExist): tmp = self.ResolveInclude(control)
			else: tmp = control
			t = tmp.getElementsByTagName('type')
			if (t[0].hasChildNodes()): 
				tagName = t[0].firstChild.nodeValue
				node = self.FirstChildElement(tmp, None)
				while (node):
					# key node so save to the dictionary
					if (node.tagName.lower() != 'type'):
						if (node.hasChildNodes()): 
							self.m_references[tagName + '_' + node.tagName.lower()] = node.firstChild.nodeValue
					node = self.NextSiblingElement(node, None)
		refdoc.unlink()
		self.debugWrite('LoadReferences', True)
		return True


	def FirstChildElement(self, root, value = 'include'):
		node = root.firstChild
		while (node):
			if (node and node.nodeType == 1):
				if (node.tagName == value or not value): return node
			node = node.nextSibling
		return None


	def NextSiblingElement(self, node, value = 'include'):
		while (node):
			node = node.nextSibling
			if (node and node.nodeType == 1):
				if (node.tagName == value or not value): return node
		return None


	def LoadIncludes(self):
		if (not self.fastMethod):
			self.lines[self.lineno + 1]	= 'loading includes.xml file...'
			self.dlg.update(self.pct, self.lines[0], self.lines[1], self.lines[2])
			self.pct += self.pct1
		# make sure our include map is cleared.
		self.m_includes = {}
		# get the includes.xml file location if it exists
		includeFile = self.GetSkinPath('includes.xml')
		# load and parse includes.xml file
		try: self.incdoc = xml.dom.minidom.parse(includeFile)
		except:
			self.debugWrite('LoadIncludes', False)
			return False
		root = self.incdoc.documentElement
		if (not root or root.tagName != 'includes'):
			self.incdoc.unlink()
			self.debugWrite('LoadIncludes', False)
			return False
		node = self.FirstChildElement(root)
		while (node):
			if (node.attributes["name"] and node.firstChild):
				# key node so save to the dictionary
				tagName = node.attributes["name"].value
				self.m_includes[tagName] = node
			node = self.NextSiblingElement(node)
		self.debugWrite('LoadIncludes', True)
		return True


	def ResolveInclude(self, node):
		# we have a node, find any <include>tagName</include> tags and replace
		# recursively with their real includes
		if (not node): return None
		include = self.FirstChildElement(node)
		while (include and include.firstChild):
			# have an include tag - grab it's tag name and replace it with the real tag contents
			tagName = include.firstChild.toxml()
			try: 
				element = self.m_includes[tagName].cloneNode(True)
				# found the tag(s) to include - let's replace it
				for tag in element.childNodes:
					# we insert before the <include> element to keep the correct
					# order (we render in the order given in the xml file)
					if (tag.nodeType == 1): result = node.insertBefore(tag, include)
			except: pass # invalid include
			result = node.removeChild(include)
			include.unlink()
			include = self.FirstChildElement(node)
		return node

