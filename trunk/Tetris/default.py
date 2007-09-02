###################################################################
#
#   Tetris v1.1
#		by asteron  
#
#	
###################################################################

import re, random, math, threading, time, traceback
import xbmc, xbmcgui
import threading, os, re
sys.path.append( os.path.join( sys.path[0], 'resources', 'lib' ) )
import scores,language,update,guibuilder

_ = language.Language().string
VERSION = "1.1"




ACTION_MOVE_LEFT 	= 1	
ACTION_MOVE_RIGHT	= 2
ACTION_MOVE_UP		= 3
ACTION_MOVE_DOWN	= 4
ACTION_PAGE_UP		= 5
ACTION_PAGE_DOWN	= 6
ACTION_SELECT_ITEM      = 7
ACTION_HIGHLIGHT_ITEM	= 8
ACTION_PARENT_DIR	= 9
ACTION_PREVIOUS_MENU	= 10
ACTION_SHOW_INFO	= 11
ACTION_PAUSE		= 12
ACTION_STOP		= 13
ACTION_NEXT_ITEM	= 14
ACTION_PREV_ITEM	= 15
ACTION_SHOW_GUI = 18  #X Button
ACTION_SCROLL_UP	= 111
ACTION_SCROLL_DOWN	= 112

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

BUTTON_NAMES={
	256 : 'A',
	257 : 'B',
	258 : 'X',
	259 : 'Y',
	260 : 'Black',
	261 : 'White',
	270 : 'DPad Up',
	271 : 'DPad Down',
	272 : 'DPad Left',
	273 : 'DPad Right',
	266 : 'RThumb Up',
	267 : 'RThumb Down',
	268 : 'RThumb Left',
	269 : 'RThumb Right',
	276 : 'LThumb',
	277 : 'RThumb',
	280 : 'LThumb Up',
	281 : 'LThumb Down',
	282 : 'LThumb Left',
	283 : 'LThumb Right',
	278 : 'L Trig',
	279 : 'R Trig'}
GAME_ACTIONS = ['Move Left', 'Move Right', 'Turn Left', 'Turn Right',  
			    'Gravity', 'Drop', 'Near Drop', 'Pause']
GAME_QUIT = -1
GAME_NONE = -2
GAME_MOVE_LEFT, GAME_MOVE_RIGHT, GAME_ROTATE_CW, GAME_ROTATE_CCW, GAME_GRAVITY, GAME_DROP, GAME_NEAR_DROP, GAME_PAUSE = range(len(GAME_ACTIONS))

DEFAULT_KEYMAP = {
	256: GAME_DROP, 
	257: GAME_ROTATE_CCW, 
	258: GAME_ROTATE_CW, 
	259: GAME_PAUSE, 
	270: GAME_NEAR_DROP, 
	271: GAME_DROP, 
	272: GAME_MOVE_LEFT, 
	273: GAME_MOVE_RIGHT, 
	279: GAME_GRAVITY}
# a fall back map for buttons not in the allowed button list
ACTION_MAP = {  
	ACTION_MOVE_LEFT : GAME_MOVE_LEFT,
	ACTION_MOVE_RIGHT : GAME_MOVE_RIGHT,
	ACTION_MOVE_UP: GAME_NEAR_DROP,
	ACTION_MOVE_DOWN: GAME_DROP,
	ACTION_SELECT_ITEM: GAME_DROP,
	ACTION_PARENT_DIR: GAME_ROTATE_CW,
	ACTION_SCROLL_DOWN: GAME_GRAVITY,
	ACTION_PAUSE: GAME_PAUSE,
	ACTION_PREVIOUS_MENU: GAME_QUIT}


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

ROOT_DIR = os.getcwd()[:-1]+'\\'    
IMAGE_DIR = ROOT_DIR+"resources\\themes\\modern\\images\\"
SOUND_DIR = ROOT_DIR+"resources\\themes\\modern\\sounds\\"

MAX_LENGTH 		= 4
COLOR_NONE 		= 0
COLOR_BLUE 		= 1
COLOR_RED 		= 2
COLOR_GREEN 	= 3
COLOR_YELLOW 	= 4
COLOR_CYAN 		= 5
COLOR_MAGENTA 	= 6
COLOR_ORANGE 	= 7
COLOR_GHOST 	= 8
COLORS = ['none','blu','red','gre','yel','cya','mag','ora','ghost']

DO_LOGGING = 1
try:
	LOG_FILE.close()
except Exception:
	pass
if DO_LOGGING:
	LOG_FILE = open(ROOT_DIR+"log.txt",'w')
def LOG(message):
	if DO_LOGGING:
		LOG_FILE.write(str(message)+"\n")
		LOG_FILE.flush()	
def LOGCLOSE():
	if DO_LOGGING:
		LOG_FILE.close()

class PieceType:
	def __init__(self,squares,symmetry,color): 
		self.squares = squares
		self.size = int(math.sqrt(len(squares)))
		self.symmetry = symmetry
		self.color = color
		self.masks = [[squares[i*self.size:(i+1)*self.size] for i in range(self.size)]]
		for k in range(self.symmetry-1):
			self.masks.append([squares[i*self.size:(i+1)*self.size] for i in range(self.size)])
			for i in range(self.size):
				for j in range(self.size):
					self.masks[-1][i][j] = self.masks[-2][j][-1-i]
		
#		print '\n\n'.join(['\n'.join([''.join([str(x) for x in row]) for row in mask]) for mask in self.masks])+'\n\n\n'
PIECETYPE = [
		 	PieceType([	0,0,1,0,
						0,0,1,0,
						0,0,1,0,
						0,0,1,0],2,COLOR_RED),
		  
		 	PieceType([	0,1,0,
						1,1,0,
						0,1,0],4,COLOR_ORANGE),
		  
		 	PieceType([	1,1,0,
						0,1,1,
						0,0,0],2,COLOR_CYAN),
		  
		 	PieceType([	0,1,1,
						1,1,0,
						0,0,0],2,COLOR_GREEN),
		  		  
		 	PieceType([	1,1,0,
						0,1,0,
						0,1,0],4,COLOR_MAGENTA),
		  
		 	PieceType([	0,1,1,
						0,1,0,
						0,1,0],4,COLOR_YELLOW),
		 	
		 	PieceType([	1,1,
						1,1],1,COLOR_BLUE),
		 ]
		 
class Piece:
	def __init__(self,type):
		self.type = type
		self.color = type.color
		self.y = 0
		self.x = 0
		self.rotation = 0
	
	def getCollisionMask(self,rotation):
		return self.type.masks[rotation]
		
class Board:
	def __init__(self,width,height):
		self.width = width
		self.height = height
		self.blocks = []
		for i in range(self.height):
			self.blocks.append([COLOR_NONE]*self.width)

	def clear(self):
		LOG('Clear')
		self.blocks = []
		for i in range(self.height):
			self.blocks.append([COLOR_NONE]*self.width)

	def isCollision(self,piece,x,y,rotation):
		collisionMask = piece.getCollisionMask(rotation)
		for i in range(len(collisionMask[0])):
			for j in range(len(collisionMask)):
				if collisionMask[i][j]:
					if i+y < 0 or i+y >= self.height or j+x < 0 or j+x >= self.width:
						return True  #collided with wall
					if self.blocks[i+y][j+x]:
						return True  #collided with block
		return False
	
	def addPiece(self,piece):
		mask = piece.getCollisionMask(piece.rotation)
		for i in range(len(mask[0])):
			for j in range(len(mask)):
				if mask[i][j]:
					self.blocks[i+piece.y][j+piece.x] = piece.type.color
	
	def deleteRow(self,row):
		for i in range(row,0,-1):
			self.blocks[i] = self.blocks[i-1][:]
		self.blocks[0] = [0]*self.width

	def isRowFilled(self,row):
		return reduce(lambda x,y: x and y, self.blocks[row], True)
				
	
	def printBoard(self):
		print '\n'.join([''.join([str(x) for x in row]) for row in self.blocks])

class BoardController:
	def __init__(self, board):
		self.nLines = 0
		self.nPieceCount = [0]*len(PIECETYPE)
		self.nScore = 0
		self.nLevel = 1
		self.board = board
		self.nextPiece = Piece(PIECETYPE[random.randint(0,len(PIECETYPE)-1)])
		self.curPiece = Piece(PIECETYPE[random.randint(0,len(PIECETYPE)-1)])
		self.doNewPiece()

#	returns whether number 
	def dropPiece(self):
		LOG('DropPiece')
		if not self.board.isCollision(self.curPiece,self.curPiece.x,self.curPiece.y+1,self.curPiece.rotation):
			LOG('DP1')
			self.curPiece.y = self.curPiece.y + 1
			return EVENT_DROP,0
		else:
			LOG('DP2')
			self.board.addPiece(self.curPiece)
			self.nPieceCount[PIECETYPE.index(self.curPiece.type)] += 1
			rows = self.checkBoard()
			#gamestate = self.doNewPiece()
			self.nScore += self.nLevel * rows * rows
			if self.nLines >= 15*self.nLevel:
				self.nLevel += 1
				self.nScore += 15 * self.nLevel
				return EVENT_LEVEL_UP,rows
			LOG('DP3')
			return EVENT_NEW_PIECE,rows
			
	
	def checkBoard(self):
		LOG('  CheckBoard->')
		rows = 0
		for row in range(self.board.height):
			if board.isRowFilled(row):
				board.deleteRow(row)
				self.nLines += 1
				rows += 1
		LOG('  CheckBoard<-' + str(rows))
		return rows
		
	def movePiece(self,dx):
		if not self.board.isCollision(self.curPiece,self.curPiece.x+dx,self.curPiece.y,self.curPiece.rotation):
			self.curPiece.x = self.curPiece.x + dx
		return EVENT_MOVE

	def rotatePiece(self,dr):
		if not self.board.isCollision(self.curPiece,self.curPiece.x,self.curPiece.y,(self.curPiece.rotation + dr) % self.curPiece.type.symmetry):
			self.curPiece.rotation = (self.curPiece.rotation + dr) % self.curPiece.type.symmetry
		return EVENT_ROTATE
	
	def quickDrop(self, fromGround=2):
		while not self.board.isCollision(self.curPiece,self.curPiece.x,self.curPiece.y+fromGround+1,self.curPiece.rotation):
			self.dropPiece()
		return self.dropPiece()
	
	def getDroppedPieceCopy(self):
		copyPiece = Piece(self.curPiece.type)
		copyPiece.x,copyPiece.y,copyPiece.rotation = self.curPiece.x,self.curPiece.y,self.curPiece.rotation
		while not self.board.isCollision(copyPiece,copyPiece.x,copyPiece.y+1,copyPiece.rotation):
			copyPiece.y += 1
		copyPiece.color = COLOR_GHOST
		return copyPiece

	def doNewPiece(self):
		LOG('DN')
		self.curPiece = self.nextPiece
		self.curPiece.x = self.board.width/2 - self.curPiece.type.size / 2
		self.nextPiece = Piece(PIECETYPE[random.randint(0,len(PIECETYPE)-1)])
		if self.board.isCollision(self.curPiece,self.curPiece.x,self.curPiece.y,self.curPiece.rotation):
			LOG('DN2')
			self.gameOver()
			return EVENT_GAME_OVER
		return EVENT_NEW_PIECE

	def gameOver(self):
		LOG('GameOver')
		#self.newGame()

	def newGame(self):
		self.nLines = 0
		self.nLevel = 1
		self.nScore = 0	
		LOG('NewGame')
		self.board.clear()
		LOG('NG2')
		self.doNewPiece();
		self.doNewPiece();
		self.nPieceCount = [0]*len(PIECETYPE)
		

EVENT_NONE = 0
EVENT_NEW_PIECE = 1
EVENT_GAME_OVER = 2
EVENT_NEW_GAME = 3
EVENT_LEVEL_UP = 4
EVENT_MOVE = 5
EVENT_ROTATE = 6
EVENT_DROP = 7

GRAVITY_SPEED_DELAY = 4
GRAVITY_NEW_PIECE_DELAY = 0.4

STATE_READY = 0
STATE_PAUSED = 1
STATE_QUITTING = 2

#avoid stretching on different pixel aspect ratios
SX = 1.00
SY = 1.00

def noStretch(window):
	displayModes = {0: (16,9,1920,1080),
					1: (16,9,1280,720),
					2: (4,3,720,480),
					3: (16,9,720,480),
					4: (4,3,720,480),
					5: (16,9,720,480),
					6: (4,3,720,576),
					7: (16,9,720,576),
					8: (4,3,720,480),
					9: (16,9,720,480)}					
	currMode = displayModes[window.getResolution()]
	global SX,SY
	class C:
		def __init__(self, v): self.value = v
		def __mul__(self, r): return int(self.value * r)
	
	SY = C(float(currMode[3])/576.0)
	SX = C(float(currMode[1])/float(currMode[0])*4.0/3.0*float(currMode[2])/720.0)
	if (currMode[0] == 16) and (currMode[2] == 720):
		SX = C(1.0)
	#if window.getResolution() < 2: window.setCoordinateResolution(COORD_720P)
	#else: window.setCoordinateResolution(COORD_PAL_4X3)
	
class ConfigControlsDialog(xbmcgui.WindowDialog):
	def __init__(self,parent=None):
		self.parent = parent
		self.listen = True		
		self.posX = parent.blockX - 20
		self.posY = parent.blockY - 20
		self.currAction = 0
		self.pickButton = False
		self.discardNextAction = False
		LOG("CCD1")
		self.buildGui()
		self.imgButtons = []
		LOG("CCD2")		
		self.populate()
		self.setFocus(self.controls[0][0])
		LOG("CCD3")		
		
	def buildGui(self):
		self.addControl(xbmcgui.ControlImage(SX*self.posX,SY*self.posY,SX*270,SY*355, IMAGE_DIR+'highscore.png'))
		self.controls = []
		for i, action in enumerate(GAME_ACTIONS):
			button = xbmcgui.ControlButton(SX*(self.posX+25), SY*(self.posY+25 + i * 40), SX*100, SY*25, action, textYOffset=3,focusTexture=IMAGE_DIR+"button-focus.png",noFocusTexture=IMAGE_DIR+"button-nofocus.png")
			label = xbmcgui.ControlButton(SX*(self.posX+245), SY*(self.posY+25 + i * 40), SX*100, SY*25, "",font='font14',disabledColor='FFFFFFFF',textXOffset=0,focusTexture="",noFocusTexture="") #blank button = label    
			self.addControl(button)
			self.addControl(label)
			label.setEnabled(False)
			self.controls.append((button,label))
		for i in range(len(self.controls)):
			self.controls[i][0].controlUp(self.controls[(i-1)%len(self.controls)][0])
			self.controls[i][0].controlDown(self.controls[(i+1)%len(self.controls)][0])			

	def populate(self):
		xbmcgui.lock()
		for i in self.imgButtons:
			self.removeControl(i)
		self.imgButtons = []
		for action in range(len(GAME_ACTIONS)):
			buttons = [button for button in self.parent.keymap.keys() if self.parent.keymap[button] == action]
			for idx in range(len(buttons)):
				deltaX = min(30,100/len(buttons))
				image = xbmcgui.ControlImage(SX*(self.posX+225-idx*deltaX), SY*(self.posY+25 + action * 40), SX*32, SY*32, ROOT_DIR+"resources\\media\\buttons\\"+str(buttons[idx])+".png", aspectRatio=2)
				self.addControl(image)
				self.imgButtons.append(image)				
		xbmcgui.unlock()
			
			
	def colorButtons(self):
		for i in range(len(self.controls)):
			if not i == self.currAction:
				self.controls[i][0].setEnabled(not self.pickButton)		
			
	def onControl(self, control):
		if not self.listen or self.pickButton:
			return
		for i in range(len(self.controls)):
			if control == self.controls[i][0]:
				self.currAction = i
				self.pickButton = True
				self.controls[i][1].setDisabledColor('FFFFFF00')
				self.discardNextAction = True
		self.colorButtons()

	def exitPickButtonMode(self):
		self.pickButton = False
		self.colorButtons()
		self.populate()
		self.controls[self.currAction][1].setDisabledColor('FFFFFFFF')			
			
	def onAction(self, action):
		if not self.listen:
			return
		if self.discardNextAction:
			self.discardNextAction = False
			return
		if action.getId() == ACTION_PREVIOUS_MENU or action.getId() == ACTION_PAUSE:
			if self.pickButton:
				self.exitPickButtonMode()
			else:
				self.close()
		if self.pickButton:
			buttoncode = action.getButtonCode()
			if buttoncode in BUTTON_NAMES:
				if buttoncode in self.parent.keymap and self.parent.keymap[buttoncode] == self.currAction:
					self.parent.keymap[buttoncode] = GAME_NONE #clear mapping if already there
				else:
					self.parent.keymap[buttoncode] = self.currAction
				self.exitPickButtonMode()


class PauseDialog(xbmcgui.WindowDialog):
	def __init__(self,parent=None):
		noStretch(self)
		guibuilder.GUIBuilder( self, ROOT_DIR+"resources\\themes\\modern\\pause.xml", IMAGE_DIR, useDescAsKey = False, title = _( 0 ), fastMethod=True, language = _, debug = False )
		self.parent = parent
		self.listen = True
		self.lblHighScoreName = self.controls[10]['control']
		self.lblHighScore = self.controls[9]['control']
		self.chkGhostPiece = self.controls[14]['control']
		self.btnGhostPiece = self.controls[11]['control']
		self.btnConfigControls = self.controls[13]['control']
		self.btnUpdate = self.controls[89]['control']
		self.btnHighScores = self.controls[73]['control']
		self.dlgConfigControls = ConfigControlsDialog(parent=self.parent)
	
	def onControl(self,control):
		LOG("PW - Oc -->")
		if not self.listen:
			return
		if control == self.btnGhostPiece:
			self.parent.drawGhostPiece = not self.chkGhostPiece.getSelected()
			self.chkGhostPiece.setSelected(self.parent.drawGhostPiece)
		if control == self.btnConfigControls:
			self.listen = False
			self.dlgConfigControls.doModal()
			self.listen = True
		if control == self.btnHighScores:
			self.listen = False
			self.parent.dlgGame.dlgHighScores.doModal()
			self.listen = True			
		if control == self.btnUpdate:
			LOG("Up1")
			if updateProc(self.parent,VERSION,async=False):
				self.close()
		
		LOG("PW - Oc <--")
	
	def onAction(self, action):
		LOG("PW - OA")
		if not self.listen:
			return
		if action.getId() == ACTION_PREVIOUS_MENU or action.getId() == ACTION_PAUSE or action.getButtonCode() == KEY_BUTTON_START:
			xbmcgui.lock()
			self.close()

class Tetris(xbmcgui.WindowDialog):
	def __init__(self):
		noStretch(self)
		guibuilder.GUIBuilder( self, ROOT_DIR+"resources\\themes\\modern\\skin.xml", IMAGE_DIR, useDescAsKey = False, title = _( 0 ), fastMethod=True, language = _, debug = False )
		self.blockX,self.blockY = self.controls[25]['control'].getPosition()
		self.spacing = self.controls[25]['control'].getSpace()
		self.blockSize = self.controls[25]['control'].getItemHeight()
		self.drawGhostPiece = False
		self.keymap = DEFAULT_KEYMAP
		self.dlgPause = PauseDialog(parent=self)
		self.dlgGame= scores.GameDialog(gamename='Tetris',imagedir=IMAGE_DIR,x=self.blockX -20, y=self.blockY)
		self.gravityControl = 0 # 0 = let fall, 1 = wait to fall, >1 = new piece take a break
		self.version = VERSION
		self.state = STATE_READY
		self.imgBlocks = []
		self.imgPiece = []
		self.imgNextPiece = []
		self.imgGhostPiece = []
		self.timer = True
		self.renderLabels()
		self.renderPieces()
		
		
	def setController(self,controller):
		LOG('SC')
		self.controller = controller
		self.board = controller.board
		self.updatePiece()
		
	def drawBloom(self,msg,x,y,duration=45,font='font12'):
		def SubProc(window,msg,x,y,duration,font):
			LOG("dsb 3a")
			lbl = xbmcgui.ControlLabel(SX*x,SY*y,SX*200,SY*25,msg,font)
			window.addControl(lbl)
			amp = random.uniform(2,6)
			if random.randint(0,1): amp = -amp
			freq = random.uniform(8,15)
			offset = random.uniform(0,3)
			for i in range(0,duration):
				lock.acquire()
				if window.state == STATE_QUITTING:
					lock.release()
					return
				lbl.setPosition(SX*(x+int(amp*math.sin((offset+float(i))/freq))),SY*(y-i))
				lock.release()
				time.sleep(.016)
			window.removeControl(lbl)
		
		LOG("dsb 1 " + str(msg) + "-"+str(x)+"-"+str(y))
		screenx = x
		screeny = y
		LOG("dsb 2")

		thread = threading.Thread(target=SubProc, args=(self,msg,screenx,screeny,duration,font))
		thread.setDaemon(True)
		try:
			thread.start()
		except:
			LOG("Bloom - thread start fail")


	def startTimer(self):
		LOG('Start Timer')
		self.timer = True

		def timerProc(view,controller,delay):
			sleeptime = max(delay * (0.67**(controller.nLevel-1)),0.05)
			time.sleep(sleeptime)
			lock.acquire()
			while view.timer and not view.state == STATE_QUITTING:
				if not view.state == STATE_PAUSED:
					LOG('   TIMER lock acquired!')
					event,rows = controller.dropPiece()
					view.processEvent(event,rows)
					LOG('   TIMER: LOCK released!')
				lock.release()
				sleeptime = max(delay * (0.67**(controller.nLevel-1)),0.05)
				time.sleep(sleeptime)
				lock.acquire()
			lock.release()
		self.subThread = threading.Thread(target=timerProc, args=(self,self.controller,1.50))
		self.subThread.setDaemon(True)
		try:
			self.subThread.start()
		except:
			LOG("Timer - thread start fail")

	
	def stopTimer(self):
		LOG('ST: Killing Timer '+ str(self.subThread))
		self.timer = False
		self.subThread.join()
		LOG('ST: Thread joined')


	def renderPieces(self):
		self.lstNextPieceDescripter = None
		if 28 in self.controls:
			self.lstNextPieceDescripter = self.controls[28]['control']
		
		if self.lstPieceCount:
			if 27 in self.controls:
				fakelist = self.controls[27]['control']
				x,y = self.lstPieceCount.getPosition()
				step = self.lstPieceCount.getItemHeight() + self.lstPieceCount.getSpace()
				offsetx,offsety = fakelist.getPosition()
				space = fakelist.getSpace()
				size = fakelist.getItemHeight() - space
				for i in range(len(PIECETYPE)):
					piece = Piece(PIECETYPE[i])
					piece.rotation = (1,3,0,0,3,1,0)[i]
					self.rasterPiece(piece,x+offsetx - (space+size)*(PIECETYPE[i].size),y+offsety+step*i,space,size)
 
	def renderLabels(self):
		x = self.blockX - 100
		y = self.blockY + 60
		self.lblLines   = self.controls[30]['control']
		self.lblScore   = self.controls[31]['control']
		self.lblLevel   = self.controls[32]['control']
		self.lstPieceCount = None
		if 26 in self.controls:
			self.lstPieceCount = self.controls[26]['control']
			self.lstPieceCount.reset()
			for i in range(len(PIECETYPE)):
				self.lstPieceCount.addItem(xbmcgui.ListItem(" ",""))
 	
	def updateBlocks(self):
 		LOG('-> UB' + str(len(self.imgBlocks)))
		for i in self.imgBlocks:
			self.removeControl(i)
		self.imgBlocks = []
 		for i in range(self.board.height):
 			for j in range(self.board.width):
 				if self.board.blocks[i][j]:
 					LOG('UB3')
 					self.imgBlocks.append(self.blockImage(i,j,self.board.blocks[i][j],self.blockX,self.blockY,self.spacing,self.blockSize))
 					self.addControl(self.imgBlocks[-1])
 		LOG('<- UB4')

	def removeBlocks(self, blocks):
		for img in blocks:
 			self.removeControl(img)

 	def movePieces(self):
 		if self.imgGhostPiece:
 			self.movePiece(self.controller.getDroppedPieceCopy(),self.imgGhostPiece)
 		self.movePiece(self.controller.curPiece,self.imgPiece)

 	def movePiece(self, piece, imagepiece):
		mask = piece.getCollisionMask(piece.rotation)
		k = 0
 		for i in range(len(mask)):
 			for j in range(len(mask[0])):
 				if mask[i][j]:
 					imagepiece[k].setPosition(SX*(self.blockX + (self.blockSize+self.spacing)*(j+piece.x)),SY*(self.blockY + (self.blockSize+self.spacing)*(i+piece.y)))
					k+=1

 		
 	def updatePiece(self):
 		LOG('-> Update Piece')
		self.removeBlocks(self.imgGhostPiece)	
		self.imgGhostPiece = []
		if self.drawGhostPiece:
			self.imgGhostPiece = self.rasterPiece(self.controller.getDroppedPieceCopy(),self.blockX,self.blockY,self.spacing,self.blockSize)
		self.removeBlocks(self.imgPiece)
		self.imgPiece = self.rasterPiece(self.controller.curPiece,self.blockX,self.blockY,self.spacing,self.blockSize)

		self.removeBlocks(self.imgNextPiece)
		if self.lstNextPieceDescripter:
			x,y = self.lstNextPieceDescripter.getPosition()
			space = self.lstNextPieceDescripter.getSpace()
			size = self.lstNextPieceDescripter.getItemHeight()
			self.imgNextPiece = self.rasterPiece(self.controller.nextPiece,x - (space+size)*(self.controller.nextPiece.type.size),
				y-(space+size)*(self.controller.nextPiece.type.size)/2,space,size)
			
		self.lblLines.setLabel(str(self.controller.nLines))
		self.lblScore.setLabel(str(self.controller.nScore))
		self.lblLevel.setLabel(str(self.controller.nLevel))
		if self.lstPieceCount:
			self.lstPieceCount.reset()
			for i in range(len(PIECETYPE)):
				self.lstPieceCount.addItem(xbmcgui.ListItem(" ",str(self.controller.nPieceCount[i])))
 		LOG('<- Update Piece')

	def rasterPiece(self,piece,blockX,blockY,spacing,size):
		LOG('RasterPiece ->')
		mask = piece.getCollisionMask(piece.rotation)
		imgRaster = []
 		for i in range(len(mask)):
 			for j in range(len(mask[0])):
 				if mask[i][j]:
 					imgRaster.append(self.blockImage(i+piece.y,j+piece.x,piece.color,blockX,blockY,spacing,size))
 					self.addControl(imgRaster[-1])
 		return imgRaster
 		LOG('RasterPiece <-')
		

 	def blockImage(self,i,j,color,blockX,blockY,spacing,size):
 		return xbmcgui.ControlImage(SX*(blockX + (size + spacing)*j), SY*(blockY + (size + spacing)*i),
									SX*size, SY*size, IMAGE_DIR+"block_"+COLORS[color]+'.jpg')

	def processEvent(self,event,rows):
		xbmcgui.lock()
		LOG('ProcessEvent-> ' + str(event)+ ' ' + str(rows))
		entryEvent = event
		clearLev = bloomX = bloomY = 0
		if event == EVENT_NEW_PIECE or event == EVENT_LEVEL_UP:
			self.movePieces()			
			if rows>0 or True:
				clearLev = self.controller.nLevel - (event == EVENT_LEVEL_UP)
				bloomX = self.blockX + (self.blockSize + self.spacing)*(self.controller.curPiece.x+self.controller.curPiece.type.size/2)
				bloomY = self.blockY + (self.blockSize + self.spacing)*(self.controller.curPiece.y)
			self.imgBlocks.extend(self.imgPiece)
			self.imgPiece = []
			event = self.controller.doNewPiece()
			self.updatePiece()
		if event == EVENT_GAME_OVER:      #sound priority
			self.state = STATE_PAUSED
			xbmc.playSFX(SOUND_DIR+"gameover.wav")
			xbmcgui.unlock()
			doNewGame = self.dlgGame.showDialog(self.controller.nScore) #it unlocks and locks gui
			xbmcgui.lock()
			if doNewGame:
				self.state = STATE_READY
				self.controller.newGame()
				self.updateBlocks()
				self.updatePiece()
			else:
				self.state = STATE_QUITTING
				self.close()
			LOG('PE after GO - '+str(self.state))
		elif entryEvent == EVENT_LEVEL_UP:
			xbmc.playSFX(SOUND_DIR+"levelup.wav")
			self.updateBlocks()
			x,y = self.lblLevel.getPosition()
			x += 10
			self.drawBloom("Level Up! +"+str(self.controller.nLevel*15),x,y,font="font14",duration=90)
			self.drawBloom("+"+str(rows*rows*clearLev),bloomX,bloomY)
		elif rows > 0:
			xbmc.playSFX(SOUND_DIR+"clear"+str(rows)+".wav")
			self.updateBlocks()
			self.drawBloom("+"+str(rows*rows*clearLev),bloomX,bloomY)
		elif entryEvent == EVENT_NEW_PIECE:
			xbmc.playSFX(SOUND_DIR+"lock.wav")
		elif entryEvent == EVENT_MOVE:
			self.movePieces()
			xbmc.playSFX(SOUND_DIR+"move.wav")
		elif entryEvent == EVENT_ROTATE:
			self.movePieces()			
			xbmc.playSFX(SOUND_DIR+"rotate.wav")
		elif entryEvent == EVENT_DROP:
			self.movePieces()			
			xbmc.playSFX(SOUND_DIR+"drop.wav")
		LOG('ProcessEvent<-')
		xbmcgui.unlock()

	def togglePause(self):
		xbmcgui.lock()
		self.removeBlocks(self.imgBlocks + self.imgPiece + self.imgNextPiece + self.imgGhostPiece)
		xbmcgui.unlock()		
		self.state = STATE_PAUSED
		xbmc.playSFX(SOUND_DIR+"pause.wav")		
		name,score = self.dlgGame.dlgHighScores.getHighestScore()
		self.dlgPause.lblHighScore.setLabel(score)
		self.dlgPause.lblHighScoreName.setLabel(name)
		self.dlgPause.doModal() #leaves gui locked
		xbmc.playSFX(SOUND_DIR+"unpause.wav")
		self.state = STATE_READY
		for img in (self.imgBlocks + self.imgPiece + self.imgNextPiece + self.imgGhostPiece):
			self.addControl(img)
		self.updatePiece() #clears/enables ghost piece
		xbmcgui.unlock()
		
	# I had huge freezing problems with the incoming thread not being able to wait properly on a lock.  XBMC really want the
	# thread to return quickly so we spawn a child thread immediately
	def onAction(self, action):

		# The scroll actions have a very high freq
		# decrease this frequency so we dont get bogged down with extra threads		
		if action.getId() == ACTION_SCROLL_DOWN or action.getId() == ACTION_SCROLL_UP:  
			LOG ("ASD - " + str(self.gravityControl) +"="+ str(time.clock()+GRAVITY_SPEED_DELAY-self.gravityControl))
			if self.gravityControl >= GRAVITY_SPEED_DELAY: 
				#self.gravityControl -= 1
				if time.clock() + GRAVITY_SPEED_DELAY - self.gravityControl < GRAVITY_NEW_PIECE_DELAY:
					return
				self.gravityControl = 0
			else: 
				# this slows down the frequency			
				self.gravityControl = (1 + self.gravityControl) % GRAVITY_SPEED_DELAY 
				if not self.gravityControl == 0:
					return
				
		code = action.getButtonCode()
		gameAction = 0
		if code in self.keymap:
			gameAction = self.keymap[code]
		elif code == KEY_BUTTON_START:
			gameAction = GAME_PAUSE
			#supplemental actions for non-mappable keys/remote/keyboard
		else:
			gameAction = ACTION_MAP.get(action.getId(),GAME_NONE)
		if action == GAME_NONE:
			return	
		
		#launch thread
		def SubProc(view,action):
			view.onActionProc(action)		
		thread = threading.Thread(target=SubProc, args=(self,gameAction))
		thread.setDaemon(True)
		try:
			thread.start()
		except:
			LOG("OA - thread start failure")

	def onActionProc(self, action):
		lock.acquire()
		if self.state == STATE_QUITTING:
			lock.release()
			return
		LOG('   OnAct lock acquired!!')
		event = 0
		rows = 0
	 	if action == GAME_MOVE_LEFT: 
	 		event = controller.movePiece(-1)
	 	elif action == GAME_MOVE_RIGHT: 
	 		event = controller.movePiece(1)
	 	elif action == GAME_NEAR_DROP: 
	 		event,rows = controller.quickDrop(fromGround=2)
	 		if event == EVENT_DROP:
	 			event = EVENT_MOVE
	 	elif action == GAME_DROP: 
	 		event,rows = controller.quickDrop(fromGround=0)
	 	elif action == GAME_ROTATE_CW: 
			event = controller.rotatePiece(1)
	  	elif action == GAME_ROTATE_CCW: 
			event = controller.rotatePiece(-1)
		elif action == GAME_GRAVITY: 
			event,rows = controller.dropPiece()
			if event == EVENT_DROP:
	 			event = EVENT_MOVE
			# give it a break after you hit bottom
			if event == EVENT_NEW_PIECE:
				# if we hit the ground give gravity a break for a bit 			
				self.gravityControl = time.clock() + GRAVITY_NEW_PIECE_DELAY + GRAVITY_SPEED_DELAY
		elif action == GAME_PAUSE: 
	 		self.togglePause()
		elif action == GAME_QUIT: 
			LOG('OA2: lock released')
			self.state = STATE_QUITTING
			lock.release()
			self.close()
			return
		LOG('OA2')
		self.processEvent(event,rows)
		LOG('OA: lock released')
		lock.release()
		LOG('<- OnAction')

			
	def saveSettings(self):
		if not os.path.exists("P:\\script_data\\"): # changed by blittan
			os.mkdir("P:\\script_data\\") # changed by blittan
		keymap = self.keymap
		dict = {"username":self.dlgGame.dlgSubmit.username,
				"password":self.dlgGame.dlgSubmit.password,
				"userid":self.dlgGame.dlgSubmit.userID,
				"nickname":self.dlgGame.username,
				"gameid":self.dlgGame.gameID,
				"ghost":(self.drawGhostPiece and "True") or "False",  # like ? : operator
				"version":self.version
				}
		for button, action in keymap.items():
			if button in BUTTON_NAMES.keys() and action in range(len(GAME_ACTIONS)):
				dict["button"+str(button)]=str(action)
		curdat = "<tetris>\n" + "\n".join(["\t<"+key+">"+dict[key]+"</"+key+">" for key in dict.keys()])+ "\n</tetris>"
		LOG("Save settings : " + curdat)
		fb = open("P:\\script_data\\tetris_settings.xml",'w') # changed by blittan
		fb.write(curdat)
		fb.close()
	
	def loadSettings(self):
		if not os.path.exists("P:\\script_data\\tetris_settings.xml"): # changed by blittan
			return
		fb = open("P:\\script_data\\tetris_settings.xml",'r') # changed by blittan
		indat = fb.read()
		fb.close()
		LOG("LoadSettings: reading" + indat)
		regp = '<([^<]*)>([^</]*)</'
		save_info = re.compile(regp,re.IGNORECASE).findall(indat)
		dict = {"username":'',"password":'',"userid":'',"nickname":'',"gameid":'',"ghost":'False', "version":"0.0"}
		keymap = DEFAULT_KEYMAP
		for x in save_info:
			dict[x[0]] = x[1]
			if x[0].startswith("button"):
				try:
					button = int(x[0][len("button"):])
					if button in BUTTON_NAMES and int(x[1]) in range(len(GAME_ACTIONS)):
						keymap[button] = int(x[1])	
				except: pass	
		LOG("LoadSettings: 1")
		self.keymap.update(keymap)
		self.dlgPause.dlgConfigControls.populate()
		self.dlgGame.dlgSubmit.setUsername(dict["username"])
		self.dlgGame.dlgSubmit.setPassword(dict["password"])
		self.dlgGame.dlgSubmit.userID=dict["userid"]
		self.dlgGame.setUsername(dict["nickname"])
		self.dlgGame.gameID=dict["gameid"]
		self.drawGhostPiece=dict["ghost"]=="True"
		self.dlgPause.chkGhostPiece.setSelected(self.drawGhostPiece)
		LOG("LoadSettings: 2 " + str(keymap) + "\n" + str(self.keymap))		
		if self.version > dict["version"]:
			pass
			#TODO: Show about screen
		else:
			self.version = dict["version"]
		LOG("LoadSettings: EXIT")

			
	def doUpdateCheck(self):
		thread = threading.Thread(target=updateProc, args=(self,self.version))
		thread.setDaemon(True)
		try:
			thread.start()
		except:
			LOG("Update - thread start fail")

def updateProc(view,currentVersion,async=True):
	LOG("UP")
	up = update.Update(_,script='Tetris')
	LOG("UP2")
	version = up.getLatestVersion()
	LOG("UP3 "+version)
	if version == "-1":
		if not async: xbmcgui.Dialog().ok( _(0), _( 96 ) ) #error
		return
	if currentVersion < version:
		if async: 
			lock.acquire()				
			view.state = STATE_PAUSED
		if ( xbmcgui.Dialog().yesno( _(0), _( 91 ).replace("%s",version), _( 92 ) ) ): #want to upgrade?
			view.state = STATE_QUITTING
			if async: lock.release()
			up.makeBackup()
			up.issueUpdate(version)
			view.close()
			return True
		elif async: 
			xbmcgui.Dialog().ok( self.script, _( 99 ) % (self.version) ) #not be asked again
			view.state = STATE_READY
			lock.release()
	elif not async:
		xbmcgui.Dialog().ok( _(0), _( 95 ) ) # up to date
	return False
			
if __name__ == '__main__':
    try:
		#sys.stderr = open(ROOT_DIR+"err.txt",'w')
		xbmc.enableNavSounds(False)
		lock = threading.Lock()
		random.seed(time.time())
		board = Board(10,20)
		controller = BoardController(board)
		t = Tetris()
		t.loadSettings()
		t.setController(controller)
		t.startTimer()
		t.doModal()
		t.stopTimer()
		t.saveSettings()
		del t,controller,board
		xbmc.enableNavSounds(True)
    except:
        traceback.print_exc()

LOGCLOSE()