###################################################################
#
#   Tetris v1.0
#		by asteron  
#
#	
###################################################################

import urllib, re, random, math, threading, time
import xbmc, xbmcgui
import threading, os

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
IMAGE_DIR = ROOT_DIR+"images\\"
SOUND_DIR = ROOT_DIR+"sounds\\"

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
		LOG('GCM')
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
		LOG('CL2')
		for i in range(self.height):
			self.blocks.append([COLOR_NONE]*self.width)
		LOG('CL4')

	def isCollision(self,piece,x,y,rotation):
		collisionMask = piece.getCollisionMask(rotation)
		for i in range(len(collisionMask[0])):
			for j in range(len(collisionMask)):
				if collisionMask[i][j]:
					if i+y < 0 or i+y >= self.height or j+x < 0 or j+x >= self.width:
						return True
					if self.blocks[i+y][j+x]:
						return True
		return False
	
	def addPiece(self,piece):
		mask = piece.getCollisionMask(piece.rotation)
		for i in range(len(mask[0])):
			for j in range(len(mask)):
				if mask[i][j]:
					self.blocks[i+piece.y][j+piece.x] = piece.type.color
	
	def deleteRow(self,row):
		LOG('DeleteRow')
		for i in range(row,0,-1):
			LOG('DR1' + str(i))
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
			return EVENT_NONE,0
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
				LOG('CB2')
				board.deleteRow(row)
				self.nLines += 1
				rows += 1
		LOG('  CheckBoard<-')
		return rows
		
	def movePiece(self,dx):
		if not self.board.isCollision(self.curPiece,self.curPiece.x+dx,self.curPiece.y,self.curPiece.rotation):
			self.curPiece.x = self.curPiece.x + dx

	def rotatePiece(self,dr):
		if not self.board.isCollision(self.curPiece,self.curPiece.x,self.curPiece.y,(self.curPiece.rotation + dr) % self.curPiece.type.symmetry):
			self.curPiece.rotation = (self.curPiece.rotation + dr) % self.curPiece.type.symmetry
	
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
		self.newGame()

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

GRAVITY_SPEED_DELAY = 2
GRAVITY_NEW_PIECE_DELAY = 1

class PauseDialog(xbmcgui.WindowDialog):
	def setPosition(self,x,y):
		self.setCoordinateResolution(COORD_PAL_4X3)
		self.addControl(xbmcgui.ControlImage(x,y,213,113, IMAGE_DIR+'pause.png'))
	
	def onAction(self, action):
		if action in (ACTION_PREVIOUS_MENU, ACTION_PAUSE):
			self.close()

class Tetris(xbmcgui.WindowDialog):
	def __init__(self):
		self.setCoordinateResolution(COORD_PAL_4X3)
		self.blockSize = 17
		self.spacing = 3
		self.blockX = 400
		self.blockY = 70
		self.pauseDialog = PauseDialog()
		self.pauseDialog.setPosition(self.blockX-20,self.blockY + 70)
		self.gravityControl = 0 # 0 = let fall, 1 = wait to fall, >1 = new piece take a break
		
		self.addControl(xbmcgui.ControlImage(self.blockX-111,self.blockY-20,320,445, IMAGE_DIR+'background.png'))
		self.imgBlocks = []
		self.imgPiece = []
		self.imgNextPiece = []
		self.imgGhostPiece = []
		self.mutex = True
		self.pendingAction = None
		self.timer = True
		self.renderPieces()
		self.renderLabels()
		
	def setController(self,controller):
		LOG('SC')
		self.controller = controller
		self.board = controller.board
		self.updatePiece()

	def startTimer(self):
		LOG('Start Timer')
		self.timer = True

		def timerProc(view,controller,delay):
			sleeptime = max(delay * (0.6**(controller.nLevel-1)),0.05)
			LOG('TIMER sleep')
			time.sleep(sleeptime)		
			while view.timer:
				LOG('-> TIMER attempting lock')
				lock.acquire()
				LOG('   TIMER lock acquired!')
				event,rows = controller.dropPiece()
				view.processEvent(event,rows)
				if self.gravityControl >= GRAVITY_SPEED_DELAY:
					self.gravityControl -= 1
				LOG('   TIMER: LOCK released!')
				lock.release()
				sleeptime = max(delay * (0.6**(controller.nLevel-1)),0.05)
				LOG('TIMER sleep')
				time.sleep(sleeptime)		


			
			
		self.subThread = threading.Thread(target=timerProc, args=(self,self.controller,1.50))
		self.subThread.setDaemon(True)
		self.subThread.start()
	
	def stopTimer(self):
		LOG('ST: Killing Timer '+ str(self.subThread))
		self.timer = False
		self.subThread.join()
		LOG('ST: Thread joined')


	def renderPieces(self):
		for i in range(len(PIECETYPE)):
			piece = Piece(PIECETYPE[i])
			piece.rotation = (1,3,0,0,3,1,0)[i]
			self.rasterPiece(piece,self.blockX-50-12*(PIECETYPE[i].size),self.blockY+130+40*i,2,10)
 
	def renderLabels(self):
		x = self.blockX - 100
		y = self.blockY + 60
		self.addControl(xbmcgui.ControlLabel(x,y,455,20,'Lines:','font12','FFFFFF00'))
		self.lblLines   = xbmcgui.ControlLabel(x+80,y,40,20,'','font12','FFFFFFFF',alignment=XBFONT_RIGHT)
		self.addControl(self.lblLines)
		self.addControl(xbmcgui.ControlLabel(x,y+20,455,20,'Score:','font12','FFFFFF00'))
		self.lblScore   = xbmcgui.ControlLabel(x+80,y+20,40,20,'','font12','FFFFFFFF',alignment=XBFONT_RIGHT)
		self.addControl(self.lblScore)
		self.addControl(xbmcgui.ControlLabel(x,y+40,455,20,'Level:','font12','FFFFFF00'))
		self.lblLevel   = xbmcgui.ControlLabel(x+80,y+40,40,20,'','font12','FFFFFFFF',alignment=XBFONT_RIGHT)
		self.addControl(self.lblLevel)
		self.lblPieceCount = []
		for i in range(len(PIECETYPE)):
			self.lblPieceCount.append(xbmcgui.ControlLabel(x+80,self.blockY+130+40*i,40,20,'','font12','FFFFFFFF',alignment=XBFONT_RIGHT))
			self.addControl(self.lblPieceCount[-1])
			
 	
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
 		
 	def updatePiece(self):
 		LOG('-> Update Piece')
		self.removeBlocks(self.imgGhostPiece)	
		self.imgGhostPiece = self.rasterPiece(self.controller.getDroppedPieceCopy(),self.blockX,self.blockY,self.spacing,self.blockSize)
		
		self.removeBlocks(self.imgPiece)
		self.imgPiece = self.rasterPiece(self.controller.curPiece,self.blockX,self.blockY,self.spacing,self.blockSize)

		self.removeBlocks(self.imgNextPiece)
		self.imgNextPiece = self.rasterPiece(self.controller.nextPiece,
			self.blockX-40-self.controller.nextPiece.type.size*12,self.blockY+18-self.controller.nextPiece.type.size*6,2,10)


			
		self.lblLines.setLabel(str(self.controller.nLines))
		self.lblScore.setLabel(str(self.controller.nScore))
		self.lblLevel.setLabel(str(self.controller.nLevel))
		for i in range(len(PIECETYPE)):
			self.lblPieceCount[i].setLabel(str(self.controller.nPieceCount[i]))
 		LOG('<- Update Piece')
 		

	def rasterPiece(self,piece,blockX,blockY,spacing,size):
		LOG('RasterPiece ->')
		mask = piece.getCollisionMask(piece.rotation)
		LOG('RP2')
		imgRaster = []
 		for i in range(len(mask)):
 			for j in range(len(mask[0])):
 				if mask[i][j]:
 					LOG('RP3')
 					imgRaster.append(self.blockImage(i+piece.y,j+piece.x,piece.color,blockX,blockY,spacing,size))
 					self.addControl(imgRaster[-1])
 		return imgRaster
 		LOG('RasterPiece <-')
		

 	def blockImage(self,i,j,color,blockX,blockY,spacing,size):
 		return xbmcgui.ControlImage(blockX + (size + spacing)*j, blockY + (size + spacing)*i,
									size, size, IMAGE_DIR+"block_"+COLORS[color]+'.jpg')

	def processEvent(self,event,rows):
		xbmcgui.lock()
		LOG('ProcessEvent-> ' + str(event)+ ' ' + str(rows))
		self.updatePiece()
		entryEvent = event
		if event == EVENT_NEW_PIECE or event == EVENT_LEVEL_UP:
			self.imgBlocks.extend(self.imgPiece)
			self.imgPiece = []
			event = self.controller.doNewPiece()
			self.updatePiece()
		if event == EVENT_GAME_OVER or rows > 0:
			self.updateBlocks()
			
		if event == EVENT_GAME_OVER:      #sound priority
			xbmc.playSFX(SOUND_DIR+"gameover.wav")
		elif entryEvent == EVENT_LEVEL_UP:
			xbmc.playSFX(SOUND_DIR+"levelup.wav")
		elif rows > 0:
			xbmc.playSFX(SOUND_DIR+"clear"+str(rows)+".wav")
		elif entryEvent == EVENT_NEW_PIECE:
			xbmc.playSFX(SOUND_DIR+"lock.wav")
		else:
			xbmc.playSFX(SOUND_DIR+"drop.wav")
		LOG('ProcessEvent<-')
		xbmcgui.unlock()

	def togglePause(self):
		xbmcgui.lock()
		self.removeBlocks(self.imgBlocks + self.imgPiece + self.imgNextPiece + self.imgGhostPiece)
		self.pauseDialog.show()
		xbmcgui.unlock()
		self.stopTimer()
		xbmc.playSFX(SOUND_DIR+"pause.wav")
		self.pauseDialog.doModal()
		xbmc.playSFX(SOUND_DIR+"unpause.wav")
		xbmcgui.lock()
		for img in (self.imgBlocks + self.imgPiece + self.imgNextPiece + self.imgGhostPiece):
			self.addControl(img)
		self.startTimer()
		xbmcgui.unlock()
		
 
	def onAction(self, action):
		def SubProc(view,action):
			view.onActionProc(action)
		
		thread = threading.Thread(target=SubProc, args=(self,action))
		thread.setDaemon(True)
		thread.start()

	def onActionProc(self, action):
		lock.acquire()
		LOG('   OnAct lock acquired!!')
		event = 0
		rows = 0
	 	if action == ACTION_MOVE_LEFT:
	 		controller.movePiece(-1)
			xbmc.playSFX(SOUND_DIR+"move.wav")
	 	elif action == ACTION_MOVE_RIGHT:
	 		controller.movePiece(1)
			xbmc.playSFX(SOUND_DIR+"move.wav")
	 	elif action == ACTION_MOVE_UP:
	 		event,rows = controller.quickDrop(fromGround=2)
	 	elif action == ACTION_MOVE_DOWN or action == ACTION_SELECT_ITEM:
	 		event,rows = controller.quickDrop(fromGround=0)
	 	elif action == ACTION_SHOW_GUI:
			controller.rotatePiece(1)
			xbmc.playSFX(SOUND_DIR+"rotate.wav")
		elif action == ACTION_SCROLL_DOWN:
			if self.gravityControl < GRAVITY_SPEED_DELAY: 
				# this slows down the frequency			
				self.gravityControl = (1 + self.gravityControl) % GRAVITY_SPEED_DELAY 
				if self.gravityControl == 0:
					event,rows = controller.dropPiece()
					# give it a break after you hit bottom
					if event == EVENT_NEW_PIECE:
						# if we hit the ground give gravity a break for a bit				
						self.gravityControl = GRAVITY_SPEED_DELAY + GRAVITY_NEW_PIECE_DELAY - 1 
		elif action == ACTION_PAUSE:
	 		self.togglePause()
	  	elif action == ACTION_PARENT_DIR:
			xbmc.playSFX(SOUND_DIR+"rotate.wav")
			controller.rotatePiece(-1)
		elif action == ACTION_PREVIOUS_MENU:
			LOG('OA2: lock released')
			lock.release()
			self.close()
			return
		LOG('OA2')
		self.processEvent(event,rows)
		LOG('OA: lock released')
		lock.release()
		LOG('<- OnAction')

xbmc.enableNavSounds(False)
lock = threading.Lock()
random.seed()
board = Board(10,20)
controller = BoardController(board)
t = Tetris()
t.setController(controller)
t.startTimer()
t.doModal()
t.stopTimer()
del t,controller,board
xbmc.enableNavSounds(True)
LOGCLOSE()