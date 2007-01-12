###################################################################
#
#   Tetris v1.0
#		by asteron  
#
#	
###################################################################
import xbmc,xbmcgui
import onlinehighscores
import os
ONLINEHIGHSCORE=onlinehighscores.highscore()
MAX_SCORE_LENGTH = 10

ACTION_PARENT_DIR	= 9
ACTION_STOP		= 13
ACTION_PREVIOUS_MENU	= 10

"""
HighScoreDialog:
	How to use it -
	hsDialog = HighScoreDialog("MyGame",maxScoreLength=10)
	rank = hsDialog.addScore('bob',300)
	ASSERT(hsDialog.localHighScores[rank] == ('bob',300))
"""

def unikeyboard(default,header=""):
	"""
		Opens XBMC Virtual Keyboard
		Give it the Default value and header and it will return the value entered
		If user cancelled it will return the default text.
	"""
	kb = xbmc.Keyboard(default,header)
	kb.doModal()
	if (kb.isConfirmed()):
		return kb.getText()
	else:
		return default

class SubmitDialog(xbmcgui.WindowDialog):
	def __init__(self,title='',parent=None):
		self.parent = parent
		x = self.parent.posX + 100
		y = self.parent.posY + 100
		self.addControl(xbmcgui.ControlImage(x,y,213,113, os.getcwd()[:-1]+'\\images\\controls.png'))
		self.btnUsername = xbmcgui.ControlButton(x + 20, y+20, 60, 25, 'Username:')
		self.btnPassword = xbmcgui.ControlButton(x + 20, y+50, 60, 25, 'Password:')
		self.lblUsername = xbmcgui.ControlLabel(x+100, y+20, 100, 25, '')
		self.lblPassword = xbmcgui.ControlLabel(x+100, y+50, 100, 25, '')
		self.btnSubmit = xbmcgui.ControlButton(x+20, y+80, 60, 25, 'Submit')
		
		for control in (self.btnUsername, self.btnPassword, self.lblUsername, self.lblPassword, self.btnSubmit):
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
		self.userID = 0
	
	def setUsername(self,username):
		self.username = username
		self.lblUsername.setLabel(username)
		
	def setPassword(self,password):
		self.password = password
		self.lblPassword.setLabel('*'*len(password))
		
	def getUserID(self,refresh=True):
		if not self.userID == 0 and not refresh:
			return self.userID
		userID = ONLINEHIGHSCORE.get_user_id(self.username,self.password)
		if userID == 0:
			if xbmcgui.Dialog.yesno(self.parent.gamename, 'Account for username '+self.username+' not found', 'Create new account?'):
				userID = ONLINEHIGHSCORE.create_new_user(self.username, self.password)
		return userID
	
	def	submitScore(self,score):
		if self.userID == 0:
			self.userID = self.getUserID()
		if self.userID == 0:
			return 0
		retVal = ONLINEHIGHSCORE.insert_new_highscore(self.parent.gameID, self.userID, str(score))
		return retVal
		
	def onControl(self,control):
		if control == self.btnSubmit:
			if self.submitScore(self.parent.score):
				xbmcgui.Dialog.ok(self.parent.gamename, 'Submission successful')
			else:
				xbmcgui.Dialog.ok(self.parent.gamename, 'Submission failure')
		if control == self.btnUsername:
			self.setUsername(unikeyboard(self.username, 'Enter Username'))
		if control == self.btnPassword:
			self.setPassword(unikeyboard(self.password, 'Enter Password'))

	def onAction(self, action):
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()			
		
	
class HighScoreDialog(xbmcgui.WindowDialog):
	def __init__(self,title='',parent=None):
		self.parent = parent
		self.posX = parent.posX 
		self.posY = parent.posY + 30
		
		self.hsFileName = "T:\\"+self.parent.gamename+"_scores.txt"
		self.localHighScores = self.loadLocalHighscores()
		self.onlineHighScores = []
		
		self.buildGui()
		self.populateList(self.localHighScores)
		
		
		
	def buildGui(self):
		self.addControl(xbmcgui.ControlImage(self.posX,self.posY,213,210, os.getcwd()[:-1]+'\\images\\controls.png'))
		self.btnLocal = xbmcgui.ControlButton(self.posX + 20, self.posY+20, 50, 25, 'Local')
		self.btnOnline = xbmcgui.ControlButton(self.posX + 80, self.posY+20, 50, 25, 'Online')
		self.btnRefresh = xbmcgui.ControlButton(self.posX + 140, self.posY+20, 50, 25, 'Refresh')
		self.lstHighScores = xbmcgui.ControlList(self.posX +20, self.posY + 50, 170, 170)
		self.addControl(self.btnLocal)
		self.addControl(self.btnOnline)
		self.addControl(self.btnRefresh)
		self.addControl(self.lstHighScores)
		
		self.btnLocal.controlLeft(self.btnRefresh)
		self.btnRefresh.controlLeft(self.btnOnline)
		self.btnOnline.controlLeft(self.btnLocal)
		self.btnLocal.controlRight(self.btnOnline)
		self.btnRefresh.controlRight(self.btnLocal)
		self.btnOnline.controlRight(self.btnRefresh)
		self.setFocus(self.btnLocal)
		
	def isHighScore(self,score):
		scores = [s[1] for s in self.localHighScore]
		scores.append(score)
		scores.sort()
		if scores.find(score) < self.maxScoreLength:
			return True
		return False
	
	def parseScores(self, data):
		scores = ''
		for line in data.split("\n"):
			nameScore = line.split("|")
			if len(nameScore) == 2:
				scores.append(nameScore)
		return scores
	
	def populateList(self,scores):
		self.lstHighScores.reset()
		for name,score in scores:
			self.lstHighScores.addItem(xbmcgui.ListItem(name,score))
	
	def loadLocalHighscores(self):
		data = ''
		if os.path.exists(self.hsFileName):
			input = open(self.hsFileName,'r')
			data = input.read()
			input.close()		
		return self.parseScores(data)
		
	def loadOnlineHighscores(self):
		return self.parseScores(ONLINEHIGHSCORE.get_highscore(self.parent.gameID))
	
	def replaceName(self, oldName, newName, score):
		idx = self.localHighScores.find((oldName,score))
		if idx == -1:
			return False
		self.localHighScores[idx][0] = newName
		self.populateList(self.localHighScores)
		return True
	
	def addScore(self,name,score):
		self.localHighScores.append((name,score)) #add
		self.localHighScores.sort(key=lambda x: x[1]) #sort
		self.localHighScores = self.localHighScores[0:min(len(scoreStrings),self.maxScoreLength)] #truncate
		return self.localHighScores.find((name,score)) #return index or -1
	
	def saveHighScores(self):
		output = open(self.hsFileName,'w')
		scoreStrings = [x[0] +"|"+x[1] for x in self.localHighScores]
		output.write("\n".join(scoreStrings))
		output.close()
		
	def onControl(self,control):
		if control == self.btnLocal:
			self.populateList(self.localHighScores)
			self.btnRefresh.setVisible(False)
		elif control == self.btnOnline:
			if len(self.onlineHighScores) == 0:
				self.onlineHighscores = self.loadOnlineHighScores()
			self.populateList(self.onlineHighScores)
			self.btnRefresh.setVisible(True)
		elif control == self.btnRefresh:
			self.onlineHighscores = self.loadOnlineHighScores()
			self.populateList(self.onlineHighScores)
	
	def onAction(self, action):
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()
	
class GameDialog(xbmcgui.WindowDialog):
	def __init__(self, title='',x=100,y=100, maxScoreLength=10):
		self.posX = x
		self.posY = y
		self.score = 0
		self.buildGui()
		self.addControl(xbmcgui.ControlImage(self.posX,self.posY,213,113, os.getcwd()[:-1]+'\\images\\controls.png'))
		self.gamename = title
		self.gameID = ''
		self.gameID = self.getGameID(self.gamename)
		self.maxScoreLength = maxScoreLength
		self.retVal = True
		
		self.username = ''
		self.dlgSubmit = SubmitDialog(title='',parent=self)
		self.dlgHighScores = HighScoreDialog(title='',parent=self)
		
	def buildGui(self):
		self.btnUsername = xbmcgui.ControlButton(self.posX + 20, self.posY+20, 50, 25, 'Name:')
		self.lblUsername = xbmcgui.ControlLabel(self.posX+100, self.posY+20, 100, 25, '')
		self.lblScore	= xbmcgui.ControlLabel(self.posX+100, self.posY+50, 100, 25, '0')
		self.addControl(self.btnUsername)
		self.addControl(self.lblScore)
		self.btnNewGame = xbmcgui.ControlButton(self.posX + 20, self.posY+80, 50, 25, 'New Game')
		self.btnHighScores = xbmcgui.ControlButton(self.posX + 80, self.posY+80, 50, 25, 'High Scores')
		self.btnSubmit = xbmcgui.ControlButton(self.posX + 140, self.posY+80, 50, 25, 'Submit Score')
		self.btnQuit = xbmcgui.ControlButton(self.posX + 200, self.posY+80, 50, 25, 'Quit')
		controls = (self.btnNewGame, self.btnHighScores, self.btnSubmit, self.btnQuit)
		for control in controls:
			self.addControl(control)
		for i in range(-1,3):
			controls[i].controlRight(controls[i+1])
			controls[i+1].controlLeft(controls[i])
			controls[i].controlUp(self.btnUsername)
		self.btnUsername.controlDown(self.btnNewGame)
		
	def showDialog(self,score):
		self.score = score
		self.lblScore.setLabel(str(score))
		while self.username == '':
			self.setUsername(unikeyboard(self.username, "Enter new name"))
			if self.dlgSubmit.username == '':
				self.dlgSubmit.username = self.username
		self.dlgHighScores.addScore(self.username,score)
		self.doModal()
		self.dlgHighScores.saveHighScores()
		return self.retVal
		
		
		
	def getGameID(self,gamename):
		#TODO load gameID from XML
		gameID = 0
		if self.gameID == 0:
			gameID = ONLINEHIGHSCORE.get_game_id(gamename)
		if gameID == 0:
			gameID = ONLINEHIGHSCORE.create_new_game(gamename)
		return gameID
		
	def setUsername(self,username):
		self.username = username
		self.lblUsername.setLabel(username)
	
	def onControl(self, control):
		if control == self.btnUsername:
			oldname = self.username
			self.setUsername(unikeyboard(self.username, "Enter new name"))
			self.dlgHighScores.replaceName(oldname, self.username, self.score)
			if self.dlgSubmit.username == '':
				self.dlgSubmit.username = self.username
		if control == self.btnNewgame:
			self.retVal = True
			self.close()
		if control == self.btnQuit:
			self.retVal = False
			self.close()
		if control == self.btnSubmit:
			self.dlgSubmit.doModal()
		if control == self.btnHighScores:
			self.dlgHighScores.doModal()