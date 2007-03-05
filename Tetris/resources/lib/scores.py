###################################################################
#
#   Tetris v1.0
#		by asteron  
#
#  This module is pretty much entirely self contained, the interface to it is the showDialog on the gameDialog class
#  You do have to load its settings manually though.
###################################################################
import xbmc,xbmcgui
import onlinehighscores
import os, threading, traceback
import language

_ = language.Language().string


MAX_SCORE_LENGTH = 10

ACTION_PARENT_DIR	= 9
ACTION_STOP		= 13
ACTION_PREVIOUS_MENU	= 10

COORD_720P    = 1
COORD_PAL_4X3    = 6 

SX = 1.00
SY = 1.00

DO_LOGGING = 0
try:
	LOG_FILE.close()
except Exception:
	pass
if DO_LOGGING:
	LOG_FILE = open(os.getcwd()[:-1]+"\\scorelog.txt",'w')
def LOG(message):
	if DO_LOGGING:
		LOG_FILE.write(str(message)+"\n")
		LOG_FILE.flush()	
def LOGCLOSE():
	if DO_LOGGING:
		LOG_FILE.close()
		
def unikeyboard(default,header=""):
	"""
		Opens XBMC Virtual Keyboard
		Give it the Default value and header and it will return the value entered
		If user cancelled it will return the default text.
	"""
	kb = xbmc.Keyboard(default,header)
	kb.doModal()
	while (kb.isConfirmed()):
		text = kb.getText()
		if len(text) > 0:
			return text
		kb.doModal()
	return default

#avoid stretching on different pixel aspect ratios
SX=1.00
SY=1.00
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
	#stupid pal 16x9
	if (currMode[0] == 16) and (currMode[2] == 720):
		SX = C(1.0)	
	#if window.getResolution() < 2: window.setCoordinateResolution(COORD_720P)
	#else: window.setCoordinateResolution(COORD_PAL_4X3)
	
# I had problems with onlinehighscores giving exceptions if network unplugged...  wrap it up to be safe
class SafeOnlineHighScores:
	def __init__(self):
		self.ohs = onlinehighscores.highscore()

	def get_user_id(self,u,p):
		LOG("GUI! - " + u+'-'+p)
		try:
			return str(self.ohs.get_user_id(u,p))
		except Exception:
			return "0"
	def create_new_user(self,u,p):
		LOG("CNU! -"+u+"|"+p)
		try:
			return str(self.ohs.create_new_user(u,p))
		except Exception:
			return "0"
	def insert_new_highscore(self,gi,ui,sc):
		LOG("INH!")
		try:
			return str(self.ohs.insert_new_highscore(gi,ui,sc+"|correct"))
		except Exception:
			traceback.print_exc()
			return "0"
	def get_highscore(self,i):
		LOG("GHS - " + str(i))
		try:
			return str(self.ohs.get_highscore(i,quantity=10,hold=1))
		except Exception:
			LOG("GHS error")
			traceback.print_exc()
			return ""
	def get_game_id(self,g):
		LOG("GGID - " + g)
		try:
			return str(self.ohs.get_game_id(g))
		except Exception:
			traceback.print_exc()
			return "0"
	def create_new_game(self,g):
		LOG("CNG! - " +g)
		try:
			return str(self.ohs.create_new_game(g))
		except Exception:
			traceback.print_exc()
			return "0"

ONLINEHIGHSCORE=SafeOnlineHighScores()

class SubmitDialog(xbmcgui.WindowDialog):
	def __init__(self,parent=None):
		noStretch(self)
		self.parent = parent
		x = self.parent.posX + 50
		y = self.parent.posY + 130
		imagedir = self.parent.imagedir
		self.addControl(xbmcgui.ControlImage(SX*(x),SY*y,SX*243,SY*113, imagedir+'submit.png'))
		self.btnUsername = xbmcgui.ControlButton(SX*(x + 20), SY*(y+10), SX*100, SY*25, _(47), textYOffset=3,focusTexture=imagedir+"button-focus.png",noFocusTexture=imagedir+"button-nofocus.png")
		self.btnPassword = xbmcgui.ControlButton(SX*(x + 20), SY*(y+40), SX*100, SY*25, _(48), textYOffset=3,focusTexture=imagedir+"button-focus.png",noFocusTexture=imagedir+"button-nofocus.png")
		self.lblUsername = xbmcgui.ControlLabel(SX*(x+135), SY*(y+10+3), SX*100, SY*25, '')
		self.lblPassword = xbmcgui.ControlLabel(SX*(x+135), SY*(y+40+3), SX*100, SY*25, '')
		self.btnSubmit = xbmcgui.ControlButton(SX*(x+20), SY*(y+75), SX*100, SY*25, _(49),focusTexture=imagedir+"button-focus.png",noFocusTexture=imagedir+"button-nofocus.png")
		
		for control in (self.btnUsername, self.btnPassword, self.btnSubmit, self.lblUsername, self.lblPassword):
			self.addControl(control)
		
		self.btnUsername.controlUp(self.btnSubmit)
		self.btnPassword.controlUp(self.btnUsername)
		self.btnSubmit.controlUp(self.btnPassword)
		self.btnUsername.controlDown(self.btnPassword)
		self.btnPassword.controlDown(self.btnSubmit)
		self.btnSubmit.controlDown(self.btnUsername)
		self.setFocus(self.btnSubmit)
		
		self.username = ''
		self.password = ''
		self.userID = "0"
	
	def setUsername(self,username):
		self.username = username
		self.lblUsername.setLabel(username)
		self.setPassword('')
		
	def setPassword(self,password):
		self.password = password
		self.lblPassword.setLabel('*'*len(password))
		self.userID = "0"
	
	def promptUsername(self):
		self.setUsername(unikeyboard(self.username, _(50)))
	
	def promptPassword(self):
		if self.username == '':
			self.setPassword(unikeyboard(self.password, _(51)))
		else:
			self.setPassword(unikeyboard(self.password, _(52).replace('%s',self.username)))
		
	def getUserID(self,refresh=True):
		if not self.userID == "0" and not self.userID == "-1" and not refresh:
			return self.userID
		if self.username == "":	self.promptUsername()
		if self.username == "": return "0"
		if self.password == "":	self.promptPassword()			
		if self.password == "":	return "0"			
			
		userID = ONLINEHIGHSCORE.get_user_id(self.username,self.password)
		LOG("GUID ID="+userID)
		if userID == "0":
			if xbmcgui.Dialog().yesno(_(0), _(53).replace('%s',self.username), _(54)):
				userID = ONLINEHIGHSCORE.create_new_user(self.username, self.password)
				if userID == "-1":
					xbmcgui.Dialog().ok(_(55), _(56))
					return "0"
		return userID
	
	def	submitScore(self,score):
		LOG("SS " + str(score) + '-'+str(self.userID))
		if self.userID in ("0","-1"):
			self.userID = self.getUserID()
		LOG("SS2 " + self.userID)
		if self.userID == "0":
			LOG("SS2.1")
			return "0"
		retVal = ONLINEHIGHSCORE.insert_new_highscore(self.parent.gameID, self.userID, str(score))
		LOG("SS4 " + str(retVal))	
		return retVal
		
	def onControl(self, control):
		LOG('SD - OC1 - ' + str(control.getId()))
		if control == self.btnUsername:
			self.promptUsername()
		elif control == self.btnPassword:
			self.promptPassword()
		elif control == self.btnSubmit:
			if not self.submitScore(self.parent.score) == "0":
				self.parent.btnSubmit.setEnabled(False)
				self.parent.setFocus(self.parent.btnNewGame)
				xbmcgui.Dialog().ok(self.parent.gamename, _(57))
				self.parent.dlgHighScores.populateList(1)
				self.close()
			else:
				xbmcgui.Dialog().ok(self.parent.gamename, _(58))
			

	def onAction(self, action):
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()			
		
	
class HighScoreDialog(xbmcgui.WindowDialog):
	def __init__(self,parent=None):
		noStretch(self)
		self.parent = parent
		self.posX = parent.posX -55
		self.posY = parent.posY + 30
		
		self.hsFileName = "T:\\"+self.parent.gamename+"_scores.txt"
		self.localHighScores = self.loadLocalHighScores()
		self.onlineHighScores = []
		
		self.buildGui()
		self.populateList(0)
		
		
		
	def buildGui(self):
		self.addControl(xbmcgui.ControlImage(SX*self.posX,SY*self.posY,SX*270,SY*355, self.parent.imagedir+'highscore.png'))
		self.imgtabLocal = [
			xbmcgui.ControlImage(SX*(self.posX + 20), SY*(self.posY+9), SX*80, SY*32,self.parent.imagedir+'tab-noselect-nofocus.png'),
			xbmcgui.ControlImage(SX*(self.posX + 20), SY*(self.posY+9), SX*80, SY*32,self.parent.imagedir+'tab-noselect-focus.png'),
			xbmcgui.ControlImage(SX*(self.posX + 20), SY*(self.posY+9), SX*80, SY*32,self.parent.imagedir+'tab-select-nofocus.png'),
			xbmcgui.ControlImage(SX*(self.posX + 20), SY*(self.posY+9), SX*80, SY*32,self.parent.imagedir+'tab-select-focus.png')]
		self.imgtabOnline = [
			xbmcgui.ControlImage(SX*(self.posX + 80), SY*(self.posY+9), SX*80, SY*32,self.parent.imagedir+'tab-noselect-nofocus.png'),
			xbmcgui.ControlImage(SX*(self.posX + 80), SY*(self.posY+9), SX*80, SY*32,self.parent.imagedir+'tab-noselect-focus.png'),
			xbmcgui.ControlImage(SX*(self.posX + 80), SY*(self.posY+9), SX*80, SY*32,self.parent.imagedir+'tab-select-nofocus.png'),
			xbmcgui.ControlImage(SX*(self.posX + 80), SY*(self.posY+9), SX*80, SY*32,self.parent.imagedir+'tab-select-focus.png')]
		# This adds the textures so that the select textures are in front of the unselected textures... this way tabs can have a little overlap and it looks nicer
		for i in range(0,4):  
			self.addControl(self.imgtabLocal[i])
			self.imgtabLocal[i].setVisible(False)
			self.addControl(self.imgtabOnline[i])
			self.imgtabOnline[i].setVisible(False)
		self.addControl(xbmcgui.ControlImage(SX*(self.posX+5),SY*(self.posY+38),SX*263,SY*4, self.parent.imagedir+'seperator.png'))
		self.btnLocal = xbmcgui.ControlButton(SX*(self.posX + 20), SY*(self.posY+12), SX*70, SY*25, _(60),focusTexture='',noFocusTexture='',textXOffset=SX*10)
		self.btnOnline = xbmcgui.ControlButton(SX*(self.posX + 80), SY*(self.posY+12), SX*70, SY*25, _(61),focusTexture='',noFocusTexture='',textXOffset=SX*10)
		self.btnRefresh = xbmcgui.ControlButton(SX*(self.posX + 180), SY*(self.posY+10), SX*70, SY*25, _(62),focusTexture=self.parent.imagedir+"button-focus.png",noFocusTexture=self.parent.imagedir+"button-nofocus.png",textXOffset=SX*10)
		self.lstHighScores = xbmcgui.ControlList(SX*(self.posX +20), SY*(self.posY + 50), SX*230, SY*320, itemHeight=SY*16, space=SY*12)
		self.addControl(self.btnLocal)
		self.addControl(self.btnOnline)
		self.addControl(self.lstHighScores)
		self.addControl(self.btnRefresh)
		
		self.btnLocal.controlLeft(self.btnRefresh)
		self.btnRefresh.controlLeft(self.btnOnline)
		self.btnOnline.controlLeft(self.btnLocal)
		self.btnLocal.controlRight(self.btnOnline)
		self.btnRefresh.controlRight(self.btnLocal)
		self.btnOnline.controlRight(self.btnRefresh)
		#self.btnRefresh.setVisible(False)
		self.lstHighScores.setEnabled(False)
		self.btnRefresh.setEnabled(False)
		self.setFocus(self.btnLocal)
		self.imgtabLocal[3].setVisible(True)
		self.imgtabOnline[0].setVisible(True)
		
	def isHighScore(self,score):
		scores = [s[1] for s in self.localHighScore]
		scores.append(score)
		scores.sort()
		if scores.index(score) < self.maxScoreLength:
			return True
		return False
	
	def parseScores(self, data):
		LOG('Parsing data ')
		scores = []
		for line in data.split("\n"):
			nameScore = line.split("|")
			if len(nameScore) == 2:
				scores.append((nameScore[0],nameScore[1]))
		LOG("scores")
		LOG(scores)
		return scores
	
	def populateList(self,scoreList):
		self.currentTab = scoreList
		scores = (self.localHighScores, self.onlineHighScores)[scoreList]
		xbmcgui.lock()
		self.updateTabImages()
		self.lstHighScores.reset()
		for name,score in scores:
			self.lstHighScores.addItem(xbmcgui.ListItem(name,str(score)))
		xbmcgui.unlock()
	
	def loadLocalHighScores(self):
		data = ''
		if os.path.exists(self.hsFileName):
			input = open(self.hsFileName,'r')
			data = input.read()
			input.close()		
		return self.parseScores(data)
		
	def loadOnlineHighScores(self):
		LOG("LOH")
		scores = self.parseScores(ONLINEHIGHSCORE.get_highscore(self.parent.gameID))
		LOG("LOH score: " + str(scores))
		return scores
	
	def replaceName(self, oldName, newName, score):
		try: idx = self.localHighScores.index((oldName,score))
		except: return False
		self.localHighScores[idx] = (newName,score)
		self.populateList(0)
		return True
	
	def addScore(self,name,score):
	
		LOG('AS1 - ' + str(name) + '|'+str(score))
		self.localHighScores.append((name,score)) #add
		self.localHighScores.sort(key=lambda x: int(x[1]),reverse=True) #sort
		self.localHighScores = self.localHighScores[0:min(len(self.localHighScores),self.parent.maxScoreLength)] #truncate
		self.populateList(0)
		LOG('AS5')
		try:
			return self.localHighScores.index((name,score)) #return index or -1
		except Exception:
			return -1
	
	def getHighestScore(self):
		if len(self.localHighScores) > 0:
			return self.localHighScores[0]
		else:
			return ('-------','0')
	
	def saveHighScores(self):
		output = open(self.hsFileName,'w')
		LOG("Scores:" + str(self.localHighScores))
		scoreStrings = [str(x[0]) +"|"+str(x[1]) for x in self.localHighScores]
		output.write("\n".join(scoreStrings))
		output.close()
	
	def updateTabImages(self):
		LOG("UTI1")
		focusControl = self.getFocus()
		imgidx = [0,0]
		if focusControl == self.btnLocal:
			if self.currentTab == 0: imgidx = [3,0]
			else: imgidx = [1,2]
		elif focusControl == self.btnOnline:
			if self.currentTab == 1: imgidx = [0,3]
			else: imgidx = [2,1]		
		else:
			if self.currentTab == 0: imgidx = [2,0]
			else: imgidx = [0,2]
		LOG("UTI2 " + str(imgidx))
		for i in range(4):
			self.imgtabLocal[i].setVisible(i==imgidx[0])
			self.imgtabOnline[i].setVisible(i==imgidx[1])
		
	def onControl(self, control):
		LOG('HS - OC1 - ' + str(control.getId()))
		if control == self.btnLocal:
			self.populateList(0)
			self.btnRefresh.setEnabled(False)
		LOG('HS - OC2')
		if control == self.btnOnline:
			if len(self.onlineHighScores) == 0:
				LOG('HS - OC2.1')
				self.onlineHighScores = self.loadOnlineHighScores()
			LOG('HS - OC2.2')
			self.populateList(1)
			self.btnRefresh.setEnabled(True)
		LOG('HS - OC3')
		if control == self.btnRefresh:
			self.onlineHighScores = self.loadOnlineHighScores()
			self.populateList(1)
		LOG('HS - OC4')
	
	def onAction(self, action):
		self.updateTabImages()
		LOG('HS - OA1')
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()
	
WINDOW_GAME = 0
WINDOW_HIGHSCORE = 1
WINDOW_SUBMIT = 2
class GameDialog(xbmcgui.WindowDialog):
	def __init__(self, gamename='',x=100,y=100, imagedir='', maxScoreLength=10):
		noStretch(self)
		self.posX = x
		self.posY = y
		# I had a problem with different window dialogs having duplicate  ControlIDs
		# This generated two differen onControl events,  use self.listen as a lock
		self.listen = True 
		self.imagedir = imagedir
		self.score = "0"
		self.buildGui()
		self.gamename = gamename
		self.gameID = ''
		LOG("init gameID is " + str(self.gameID))
		self.maxScoreLength = maxScoreLength
		self.retVal = True
		
		self.username = ''
		self.dlgSubmit = SubmitDialog(parent=self)
		self.dlgHighScores = HighScoreDialog(parent=self)
		
	def buildGui(self):
		self.addControl(xbmcgui.ControlImage(SX*(self.posX),SY*(self.posY),SX*270,SY*150, self.imagedir+'panel.png'))
		self.btnUsername = xbmcgui.ControlButton(SX*(self.posX + 20), SY*(self.posY+10), SX*100, SY*25, _(70), textXOffset=SX*10, textYOffset=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		self.lblUsername = xbmcgui.ControlLabel(SX*(self.posX+140), SY*(self.posY+13), SX*100, SY*25, '')
		self.lblScore	= xbmcgui.ControlLabel(SX*(self.posX+140), SY*(self.posY+40), SX*100, SY*25, '0')
		self.addControl(xbmcgui.ControlLabel(SX*(self.posX+30), SY*(self.posY+40), SX*100, SY*25, _(71)))
		self.btnNewGame = xbmcgui.ControlButton(SX*(self.posX + 20), SY*(self.posY+75), SX*100, SY*25, _(72),textXOffset=SX*10, textYOffset=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		self.btnHighScores = xbmcgui.ControlButton(SX*(self.posX + 130), SY*(self.posY+75), SX*120, SY*25, _(73),textXOffset=SX*10, textYOffset=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		self.btnSubmit = xbmcgui.ControlButton(SX*(self.posX + 130), SY*(self.posY+105), SX*120, SY*25, _(74),textXOffset=SX*10, textYOffset=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		self.btnQuit = xbmcgui.ControlButton(SX*(self.posX + 20), SY*(self.posY+105), SX*100, SY*25, _(75),textXOffset=SX*10, textYOffset=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		for control in (self.btnNewGame, self.btnHighScores, self.btnQuit, self.btnSubmit, self.btnUsername, self.lblUsername, self.lblScore):
			self.addControl(control)
		self.btnNewGame.setNavigation(self.btnUsername, self.btnQuit, self.btnHighScores, self.btnHighScores)
		self.btnHighScores.setNavigation(self.btnUsername, self.btnSubmit, self.btnNewGame, self.btnNewGame)
		self.btnQuit.setNavigation(self.btnNewGame, self.btnUsername, self.btnSubmit, self.btnSubmit)
		self.btnSubmit.setNavigation(self.btnHighScores, self.btnUsername, self.btnQuit, self.btnQuit)
		self.btnUsername.controlDown(self.btnNewGame)
		self.setFocus(self.btnNewGame)
		
	def showDialog(self,score):
		LOG("Show Dialog")
		self.score = str(score)
		self.lblScore.setLabel(str(score))
		while self.username == '':
			self.setUsername(unikeyboard(self.username, "Enter New Player Name"))
			if self.dlgSubmit.username == '':
				self.dlgSubmit.setUsername(self.username)
		self.dlgHighScores.addScore(self.username,str(score))
		self.gameID = self.getGameID(self.gamename)
		self.btnSubmit.setEnabled(True)
		xbmc.enableNavSounds(True)
		self.listen = True
		self.doModal() #leaves xbmcgui locked
		xbmc.enableNavSounds(False)
		LOG("SD7")
		self.dlgHighScores.saveHighScores()
		xbmcgui.unlock()
		LOG("SD8")
		return self.retVal
		
		
		
	def getGameID(self,gamename):
		LOG('gGID ' +self.gameID)
		if self.gameID == '':
			self.gameID = ONLINEHIGHSCORE.get_game_id(gamename)		
		if self.gameID == "0":
			LOG("game not found");
			self.gameID = ONLINEHIGHSCORE.create_new_game(gamename)
		return self.gameID

		
	def setUsername(self,username):
		self.username = username
		self.lblUsername.setLabel(username)
	
	def onControl(self, control):
		if not self.listen:
			return
		LOG('OC1 - ' + str(control.getId()))
		if control == self.btnUsername:
			oldname = self.username
			self.setUsername(unikeyboard(self.username, _(76)))
			self.dlgHighScores.replaceName(oldname, self.username, self.score)
			if self.dlgSubmit.username == '':
				self.dlgSubmit.setUsername(self.username)
		LOG('OC2')
		if control == self.btnNewGame:
			LOG('OC2.3')
			self.retVal = True
			xbmcgui.lock()
			self.close()
		LOG('OC3')
		if control == self.btnQuit:
			self.retVal = False
			xbmcgui.lock()
			self.close()
		LOG('OC4')
		if control == self.btnSubmit:
			self.listen = False
			self.dlgSubmit.doModal()
			self.listen = True
		LOG('OC5')
		if control == self.btnHighScores:
			self.listen = False
			self.dlgHighScores.doModal()
			self.listen = True
		LOG('OC6')

	def onAction(self, action):
		if not self.listen:
			return
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()