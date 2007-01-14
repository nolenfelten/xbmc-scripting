###################################################################
#
#   Tetris v1.0
#		by asteron  
#
#	
###################################################################
import xbmc,xbmcgui
import onlinehighscores
import os, threading

MAX_SCORE_LENGTH = 10

ACTION_PARENT_DIR	= 9
ACTION_STOP		= 13
ACTION_PREVIOUS_MENU	= 10

COORD_PAL_4X3    = 6 

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
	LOG("KB1")
	kb = xbmc.Keyboard(default,header)
	LOG("KB2")
	kb.doModal()
	LOG("KB3")
	while (kb.isConfirmed()):
		text = kb.getText()
		if len(text) > 0:
			return text
		kb.doModal()
	return default

class SafeOnlineHighScores:
	def __init__(self):
		self.ohs = onlinehighscores.highscore()

	def get_user_id(self,u,p):
		LOG("GUI! - " + u+'-'+p)
		try:
			return self.ohs.get_user_id(u,p)
		except Exception:
			return "0"
	def create_new_user(self,u,p):
		LOG("CNU! -"+u+"|"+p)
		try:
			return self.ohs.create_new_user(u,p)
		except Exception:
			return "0"
	def insert_new_highscore(self,gi,ui,sc):
		LOG("INH!")
		try:
			return self.ohs.insert_new_highscore(gi,ui,sc)
		except Exception:
			return "0"
	def get_highscore(self,i):
		LOG("GHS - " + str(i))
		try:
			return self.ohs.get_highscore(i)
		except Exception:
			return ""
	def get_game_id(self,g):
		LOG("GGID - " + g)
		try:
			return self.ohs.get_game_id(g)
		except Exception:
			return "0"
	def create_new_game(self,g):
		LOG("CNG! - " +g)
		try:
			return self.ohs.create_new_game(g)
		except Exception:
			return "0"

ONLINEHIGHSCORE=SafeOnlineHighScores()

class SubmitDialog(xbmcgui.WindowDialog):
	def __init__(self,parent=None):
		self.setCoordinateResolution(COORD_PAL_4X3)
		self.parent = parent
		x = self.parent.posX + 50
		y = self.parent.posY + 130
		self.addControl(xbmcgui.ControlImage(x,y,243,113, self.parent.imagedir+'submit.png'))
		self.btnUsername = xbmcgui.ControlButton(x + 20, y+10, 100, 25, 'Username:', textYOffset=3)
		self.btnPassword = xbmcgui.ControlButton(x + 20, y+40, 100, 25, 'Password:', textYOffset=3)
		self.lblUsername = xbmcgui.ControlLabel(x+135, y+10+3, 100, 25, '')
		self.lblPassword = xbmcgui.ControlLabel(x+135, y+40+3, 100, 25, '')
		self.btnSubmit = xbmcgui.ControlButton(x+20, y+75, 100, 25, 'Submit')
		
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
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
		self.userID = "0"
		
	def setPassword(self,password):
		self.password = password
		self.lblPassword.setLabel('*'*len(password))
		self.userID = "0"
	
	def promptUsername(self):
		self.setUsername(unikeyboard(self.username, 'Enter Username'))
	
	def promptPassword(self):
		if self.username == '':
			self.setPassword(unikeyboard(self.password, 'Enter Password'))
		else:
			self.setPassword(unikeyboard(self.password, 'Enter Password for ' + self.username))
		
	def getUserID(self,refresh=True):
		if not self.userID == "0" and not refresh:
			return self.userID
		if self.username == "":	self.promptUsername()
		if self.username == "": return "0"
		if self.password == "":	self.promptPassword()			
		if self.password == "":	return "0"			
			
		userID = ONLINEHIGHSCORE.get_user_id(self.username,self.password)
		LOG("GUID ID="+userID)
		if userID == "0":
			if xbmcgui.Dialog().yesno(self.parent.gamename, 'Account for username '+self.username+' not found', 'Create new account?'):
				userID = ONLINEHIGHSCORE.create_new_user(self.username, self.password)
		return userID
	
	def	submitScore(self,score):
		LOG("SS " + str(score) + '-'+str(self.userID))
		if self.userID == "0":
			self.userID = self.getUserID()
		LOG("SS2 " + self.userID)
		if self.userID == "0":
			LOG("SS2.1")
			return False
		LOG("SS3")
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
			if self.submitScore(self.parent.score):
				xbmcgui.Dialog().ok(self.parent.gamename, 'Submission Successful!')
				self.close()
			else:
				xbmcgui.Dialog().ok(self.parent.gamename, 'Submission Failure')
			

	def onAction(self, action):
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()			
		
	
class HighScoreDialog(xbmcgui.WindowDialog):
	def __init__(self,parent=None):
		self.setCoordinateResolution(COORD_PAL_4X3)
		self.parent = parent
		self.posX = parent.posX -55
		self.posY = parent.posY + 30
		
		self.hsFileName = "T:\\"+self.parent.gamename+"_scores.txt"
		self.localHighScores = self.loadLocalHighScores()
		self.onlineHighScores = []
		
		self.buildGui()
		self.populateList(self.localHighScores)
		
		
		
	def buildGui(self):
		self.addControl(xbmcgui.ControlImage(self.posX,self.posY,270,380, self.parent.imagedir+'highscore.png'))
		self.btnLocal = xbmcgui.ControlButton(self.posX + 20, self.posY+20, 70, 25, 'Local')
		self.btnOnline = xbmcgui.ControlButton(self.posX + 100, self.posY+20, 70, 25, 'Online')
		self.btnRefresh = xbmcgui.ControlButton(self.posX + 180, self.posY+20, 70, 25, 'Refresh')
		self.lstHighScores = xbmcgui.ControlList(self.posX +20, self.posY + 50, 230, 320)
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
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
		self.btnRefresh.setVisible(False)
		self.setFocus(self.btnLocal)
		
	def isHighScore(self,score):
		scores = [s[1] for s in self.localHighScore]
		scores.append(score)
		scores.sort()
		if scores.index(score) < self.maxScoreLength:
			return True
		return False
	
	def parseScores(self, data):
		LOG('Parsing data ' + data)
		scores = []
		for line in data.split("\n"):
			nameScore = line.split("|")
			LOG(nameScore)
			if len(nameScore) == 2:
				scores.append((nameScore[0],nameScore[1]))
		LOG("scores")
		LOG(scores)
		return scores
	
	def populateList(self,scores):
		LOG("PL setting to "+str(scores))
		self.lstHighScores.reset()
		for name,score in scores:
			self.lstHighScores.addItem(xbmcgui.ListItem(name,str(score)))
	
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
		self.populateList(self.localHighScores)
		return True
	
	def addScore(self,name,score):
	
		LOG('AS1 - ' + str(name) + '|'+str(score))
		self.localHighScores.append((name,score)) #add
		LOG('AS2')
		self.localHighScores.sort(key=lambda x: int(x[1]),reverse=True) #sort
		LOG('AS3')
		self.localHighScores = self.localHighScores[0:min(len(self.localHighScores),self.parent.maxScoreLength)] #truncate
		LOG('AS4')
		self.populateList(self.localHighScores)
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
		LOG("\n".join(scoreStrings))
		output.write("\n".join(scoreStrings))
		output.close()
		
	def onControl(self, control):
		LOG('HS - OC1 - ' + str(control.getId()))
		if control == self.btnLocal:
			self.populateList(self.localHighScores)
			self.btnRefresh.setVisible(False)
		LOG('HS - OC2')
		if control == self.btnOnline:
			if len(self.onlineHighScores) == 0:
				LOG('HS - OC2.1')
				self.onlineHighScores = self.loadOnlineHighScores()
			LOG('HS - OC2.2')
			self.populateList(self.onlineHighScores)
			self.btnRefresh.setVisible(True)
		LOG('HS - OC3')
		if control == self.btnRefresh:
			self.onlineHighScores = self.loadOnlineHighScores()
			self.populateList(self.onlineHighScores)
		LOG('HS - OC4')
	
	def onAction(self, action):
		LOG('HS - OA1')
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()
	
WINDOW_GAME = 0
WINDOW_HIGHSCORE = 1
WINDOW_SUBMIT = 2
class GameDialog(xbmcgui.WindowDialog):
	def __init__(self, gamename='',x=100,y=100, imagedir='', maxScoreLength=10):
		self.setCoordinateResolution(COORD_PAL_4X3)
		self.posX = x
		self.posY = y
		self.focusWindow = WINDOW_GAME
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
		self.addControl(xbmcgui.ControlImage(self.posX,self.posY,270,150, self.imagedir+'panel.png'))
		self.btnUsername = xbmcgui.ControlButton(self.posX + 20, self.posY+10, 100, 25, 'Name:', textXOffset=10, textYOffset=3)
		self.lblUsername = xbmcgui.ControlLabel(self.posX+140, self.posY+13, 100, 25, '')
		self.lblScore	= xbmcgui.ControlLabel(self.posX+140, self.posY+40, 100, 25, '0')
		self.addControl(xbmcgui.ControlLabel(self.posX+30, self.posY+40, 100, 25, 'Score:'))
		self.btnNewGame = xbmcgui.ControlButton(self.posX + 20, self.posY+75, 100, 25, 'Play Again',textXOffset=10, textYOffset=3)
		self.btnHighScores = xbmcgui.ControlButton(self.posX + 130, self.posY+75, 120, 25, 'High Scores',textXOffset=10, textYOffset=3)
		self.btnSubmit = xbmcgui.ControlButton(self.posX + 130, self.posY+105, 120, 25, 'Submit Online',textXOffset=10, textYOffset=3)
		self.btnQuit = xbmcgui.ControlButton(self.posX + 20, self.posY+105, 100, 25, 'Quit',textXOffset=10, textYOffset=3)
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
		LOG("SD5")
		self.dlgHighScores.addScore(self.username,str(score))
		LOG("SD6")
		self.gameID = self.getGameID(self.gamename)
		xbmc.enableNavSounds(True)
		self.doModal()
		xbmc.enableNavSounds(False)
		LOG("SD7")
		self.dlgHighScores.saveHighScores()
		LOG("SD8")
		return self.retVal
		
		
		
	def getGameID(self,gamename):
		#TODO load gameID from XML
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
		if not self.focusWindow == WINDOW_GAME:
			return
		LOG('OC1 - ' + str(control.getId()))
		if control == self.btnUsername:
			oldname = self.username
			self.setUsername(unikeyboard(self.username, "Enter New Name"))
			self.dlgHighScores.replaceName(oldname, self.username, self.score)
			if self.dlgSubmit.username == '':
				self.dlgSubmit.setUsername(self.username)
		LOG('OC2')
		if control == self.btnNewGame:
			LOG('OC2.3')
			self.retVal = True
			self.close()
		LOG('OC3')
		if control == self.btnQuit:
			self.retVal = False
			self.close()
		LOG('OC4')
		if control == self.btnSubmit:
			self.focusWindow = WINDOW_SUBMIT
			self.dlgSubmit.doModal()
			self.focusWindow = WINDOW_GAME
		LOG('OC5')
		if control == self.btnHighScores:
			self.focusWindow = WINDOW_HIGHSCORE
			self.dlgHighScores.doModal()
			self.focusWindow = WINDOW_GAME
		LOG('OC6')

	def onAction(self, action):
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()