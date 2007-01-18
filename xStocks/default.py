###################################################################
#
#   xStocks v2.5
#		by Asteron  
#
#   A stock script for Yahoo Finance
#
#   EDIT the values below to suit your preferrences, though you
#     can do everything in the script
#	
###################################################################

# list of comma diliminated stocks, these the defaults and are only 
# used if the portfolio config cant be loaded or is empty
# 	the name of each portfolio is on the left
global STOCKS, stockData, indexData
STOCKS = [
		  ['Technology',"MSFT,IBM,AAPL,YHOO,GOOG,NVDA,INTC,AMD,DELL,HPQ,SUNW,CSCO,MMM,ORCL,QCOM,SNE,ERTS"],
		  ['Transportation',"JBLU,DAL,AWA,ALK,CAL,NWAC,LUV,AMR,CSX,FDX,JBHT,UNP"],
		  ['Automotive',"GM,F,HMC,NSANY,GT,TM"],
		  ['BioTech',"AMGN,CRA,DNA,GENZ,HGSI,IMCL,MEDI"],
		  ['Food',"EAT,HRL,MCD,OSI,TSN,WEN,BUD,CPB,CCE,GIS,HNZ,HSY,KO,SLE,PEP,SBUX"],
		  ['Products',"CL,EL,JNJ,PYX,CLX,AVP,G,PG,TUP,UP"],
		  ['Retail',"AMZN,BBY,BGP,CC,COST,BCF,CVS,KSS,LTD,LOW,NKE,PETM,RSH,SWY,ODP,JWN,S,TOY,KR,SPLS,TSA,TGT,HD,PBY"],		  
		  ['Drugs/Health',"ABT,AGN,AMGN,AZN,BAX,BMY,LLY,MRK,JNJ,PFE,SIAL,AET,CI"],
		  ['Energy',"APA,AEP,AES,DUK,TXU,CVX,XOM,HAL,KMG,MRO,SUN,UNP,VLO"]
#		  ,		  ['Currencies',"USDEUR=x,USDGBP=x,USDJPY=x,GBPEUR=x,GBPJPY=x,GBPUSD=x,EURGBP=x,EURJPY=x,EURUSD=x,JPYEUR=x,JPYGBP=x,JPYUSD=x"]
		 ]
		  

# Should we show the market index info on the side?
SHOW_INDEX_DATA = True
INDEX_NAMES = ['Dow J','Nasdaq','S&P']
INDEXS = '^DJI,^IXIC,^GSPC,'

# Max rows of stocks to be displayed in the list (11 default)
MAX_STOCKS = 11

###################################################################
#
#
# possible future ideas:
#	 - save adv chart settings?
#
# version history:
#    11/07/04 - AST - Initial creation
#    11/09/04 - AST - Got the table looking alright
#    11/15/04 - AST - 'Add Stock' button
#    11/31/04 - AST - Colorized labels
#    12/05/04 - AST - Added full-screen mode with graph
#    12/08/04 - AST - Added market data, column labels
#    12/10/04 - AST - Added delete stock, SAVING PORTFOLIO!
#    12/13/04 - AST - Spelling fix, a little cleaning up
#    12/13/04 - AST - Added scrolling but window.getFocus() is BROKEN :(
#    12/20/04 - AST - Just put in a stupid PageUp PageDown for now
#    01/20/05 - AST - Perfected scrolling using manual navigation
#    01/22/05 - AST - Sorting, stored stocks in list not string
#    02/10/05 - AST - Added framework for portfolio.. now needs a GUI
#    02/15/05 - AST - Code cleanup, alignment issues
#    02/18/05 - AST - Added portfolio screen
#    02/18/05 - AST - Added default portfolio data
#    03/10/05 - AST - Fixed a bug in sorting by price after refresh
#    04/02/05 - AST - Changed button back to a list.. PM3 looks better now
#    06/04/05 - AST - Label alignment, truncation issues, remember selected port
#    06/10/05 - AST - Modularized all the screens... clean up code
#    06/11/05 - AST - Allowed custom backgrounds
#    06/12/05 - AST - Checkmark groups, switchable lists
#    06/19/05 - AST - Super advanced settings!! New screen
#    07/18/05 - AST - Reverse sorts by double clicking sort button
#    07/19/05 - AST - fixed wrong time range, redownloading image
#    02/01/06 - AST - Updated HTML scraping, stability issues, cleaned up code
#    01/17/07 - AST - parsing was a little broken, changed settings location, static skin
#


from string import *
import urllib, re, random
import xbmc, xbmcgui
import threading, os

HTTP_TIMEOUT = 10.0		# Max. seconds to wait for a response when fetching webpages

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
ACTION_SCROLL_UP	= 111
ACTION_SCROLL_DOWN	= 112

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
IMAGE_DIR = ROOT_DIR + 'images\\'
CONFIG_DIR = "P:\\Scripts\\"
LOGO_FILE = "default.tbn"
CONFIG_NAME = "stocks.cfg"
DEF_IMAGE_NAME = "stock.png"

PORT_TITLE_FILE = "screen-port.png"
CHART_TITLE_FILE = "screen-chart.png"
ADV_TITLE_FILE = "screen-adv.png"

BACKGROUND_NAME = "background.png"
BACKGROUND_FILE = IMAGE_DIR + BACKGROUND_NAME

DO_LOGGING = 0
try:
	LOG_FILE.close()
except Exception:
	DO_LOGGING = DO_LOGGING  #dummy statement needed?
if DO_LOGGING:
	LOG_FILE = open(ROOT_DIR+"log.txt",'w')
def LOG(message):
	if DO_LOGGING:
		LOG_FILE.write(str(message)+"\n")
		LOG_FILE.flush()	
def LOGCLOSE():
	if DO_LOGGING:
		LOG_FILE.close()


# yahoo finance URL
YahooFinanceURL = "http://finance.yahoo.com/q/cq?d=v1&s="

# global progress dialog
dialogProgress = xbmcgui.DialogProgress()

# list for saving parse results, the first three stocks is reserver for the market data
portfolioNames = []
portfolio = []
curPortfolio = 0

stockData = []
indexData = []

#colors used in prices
COLORS = ['FFFFFFFF','FF66FF66','FFFF6666']

# Stock class
class Stock:
	def __init__(self, name):
		self.name = name
		self.date = ''
		self.price = ''
		self.change = ''
		self.perchange = ''
		self.volume = ''

REVERSE = 1
def comp_by_name( first, second ):
	return REVERSE*cmp(first.name, second.name)
def comp_by_price( first, second ):
	return REVERSE*cmp(float(second.price), float(first.price))
def comp_by_change( first, second ):
	return REVERSE*cmp(float(second.change), float(first.change))
def comp_by_perchange( first, second ): #remove %s and cast to float
	return REVERSE*cmp(float(second.perchange.rstrip('%')), float(first.perchange.rstrip('%')))	
def comp_by_volume( first, second ):  #remove ','s and cast to int for compare
	return REVERSE*cmp(int("".join(second.volume.split(','))), int("".join(first.volume.split(','))))	
	
# Utility func to get a color index, also ensures '+' and '-' is 
# consistant for change and perchange
def GetColorFromStock(stock):
	color = 0
	if stock.change == '0.00':
		color = 0
	elif stock.perchange.startswith('+'):
		color = 1
	elif stock.perchange.startswith('-'):
		color = 2
	return color

# A color label is actually 3 labels of different colors that have the visibilities toggled
#  this part was A LOT smaller before I decided to make the '+' or '-' its own label 
#  for alignment reasons  
class ColorLabel:
	def __init__(self, parent, x, y, w, h, font, showSign):
		self.labels = []
		self.signs = []
		for i in range(0,3):
			self.signs.append(xbmcgui.ControlLabel(x,y,15,h,'',font,COLORS[i]))
			if showSign:
				self.labels.append(xbmcgui.ControlLabel(x+10,y,w-10,h,'',font,COLORS[i]))
				parent.addControl(self.signs[i])			
			else:
				self.labels.append(xbmcgui.ControlLabel(x,y,w,h,'',font,COLORS[i]))							
			parent.addControl(self.labels[i])
			
	def setLabel(self, text):
		sign = text[0]
		number = text[1:]
		if sign != '+' and sign != '-':
			sign = ' '
			number = text
		for i in range(0,3):
			self.labels[i].setLabel(number)
			self.signs[i].setLabel(sign)			
			
	def setVisible(self,color,visible):
		self.labels[color].setVisible(visible)
		self.signs[color].setVisible(visible)
		for i in range(0,3):
			if i != color:
				self.labels[i].setVisible(False)
				self.signs[i].setVisible(False)				


# a single row contains all the stock labels and a blank button (really a list) behind it
class StockRow:
	def __init__(self, parent, row):
		row_height = 29
		yLoc = 100+ int(row)*int(row_height)
		height = row_height
		
		self.stock = ''
		#make the list super tall to hide the spin control offscreen
		self.btnBack		= xbmcgui.ControlList(204, yLoc - 4, 441, 5000, buttonFocusTexture=IMAGE_DIR+'list-focus.png',buttonTexture=IMAGE_DIR+'list-nofocus.png')
		parent.addControl(self.btnBack)
		
		self.btnBack.addItem(" ")
		self.btnBack.setVisible(False)
	
		self.nameLabel		= xbmcgui.ControlLabel(211, yLoc, 90,height,'','font13','FFFFFFFF')
		self.priceLabel		= xbmcgui.ControlLabel(355, yLoc, 80,height,'','font13','FFFFFFFF',alignment=XBFONT_RIGHT)
		self.volumeLabel	= xbmcgui.ControlLabel(625, yLoc, 115,height,'','font13','FFFFFFFF',alignment=XBFONT_RIGHT)
		
		parent.addControl(self.nameLabel)
		parent.addControl(self.priceLabel)
		parent.addControl(self.volumeLabel)		

		self.color = 0
		
		self.changeColorLabel = ColorLabel(parent,380,yLoc,70,height,'font13',False)
		self.changePerColorLabel = ColorLabel(parent,450,yLoc,68,height,'font13',True)		

		

	def setToStock(self,s):
		self.stock = s.name
		
		self.color = GetColorFromStock(s)

		self.nameLabel.setLabel(s.name)
		self.priceLabel.setLabel(s.price)
		self.volumeLabel.setLabel(s.volume)
		self.changeColorLabel.setLabel(s.change)
		self.changePerColorLabel.setLabel(s.perchange)

		
	def setVisible(self,visible):
		self.btnBack.setVisible(visible)
		self.nameLabel.setVisible(visible)
		self.priceLabel.setVisible(visible)
		self.volumeLabel.setVisible(visible)	
		self.changeColorLabel.setVisible(self.color,visible)
		self.changePerColorLabel.setVisible(self.color,visible)		
	

#  a market label has nearly the same stuff as a stockrow but is in the corner
class MarketLabel:
	def __init__(self, parent, row, name):
	
		height = 275

		self.index = row
		self.changeColorLabel = ColorLabel(parent,130, (height + 50*row),70,20,'font12',True)
	
		self.priceLabel		= xbmcgui.ControlLabel(60, (height + 20 + 50*row), 140,20,'','font12','FFFFFFFF')	
		parent.addControl(self.priceLabel)
		parent.addControl(xbmcgui.ControlLabel(60, (height + 50*row), 60,20,name,'font12','FFFFFFFF'))

	def update(self):
		if len(indexData) < 3:
			print 'Error: market data not present'
			return
		s = indexData[self.index]

		color = GetColorFromStock(s)
			
		self.priceLabel.setLabel(s.price)
		self.changeColorLabel.setLabel(s.change)
		self.changeColorLabel.setVisible(color,True)


#  a manager for the stock rows, enforces a maximum number, 
#  handles scrolling issues, keeps track of selection.. you get the idea
class StockTable:
	def __init__(self, parent, rows):
		self.sRows = []
		self.parent = parent
		self.numVisible = 0
		self.scrollAmount = 0
		self.selected = 0
		for i in range(0,rows):
			self.sRows.append(StockRow(parent,i))
		
	def setToStocks(self):
		self.numVisible = min([len(self.sRows),len(stockData)])
		if self.scrollAmount >= len(stockData) - self.numVisible:
			self.scrollAmount = len(stockData) - self.numVisible
		for i in range(0,self.numVisible):
			self.sRows[i].setToStock(stockData[self.scrollAmount+i])
			self.sRows[i].setVisible(True)
		
		for i in range(self.numVisible,len(self.sRows)):
			self.sRows[i].setVisible(False)
			
	def upAction(self, delta=1, changeFocus = True):
		if self.scrollAmount <= 0:
			if self.selected == 0 and changeFocus:
				self.setFocus(self.numVisible - 1)
				self.scrollAmount = len(stockData) - self.numVisible
			elif self.selected > delta:
				self.setFocus(self.selected - delta)
			else:
				self.setFocus(0)
		elif delta > 1:
			if self.scrollAmount > delta:
				self.scrollAmount = self.scrollAmount - delta
			else:
				self.scrollAmount = 0
		else:
			if self.selected == 0:
				self.scrollAmount = self.scrollAmount - 1
			else:
				self.setFocus(self.selected - 1)
		self.setToStocks()
			
	def downAction(self, delta=1, changeFocus = True):
		if self.scrollAmount >= len(stockData) - self.numVisible:
			if self.selected == self.numVisible - 1 and changeFocus:
				self.setFocus(0)
				self.scrollAmount = 0
			elif self.selected + delta < self.numVisible - 1:
				self.setFocus(self.selected + delta)
			else:
				self.setFocus(self.numVisible - 1)
		elif delta > 1:
			if self.scrollAmount + delta < len(stockData) - self.numVisible:
				self.scrollAmount = self.scrollAmount + delta
			else:
				self.scrollAmount = len(stockData) - self.numVisible
		else:
			if self.selected == self.numVisible - 1:
				self.scrollAmount = self.scrollAmount + 1
			else:
				self.setFocus(self.selected + 1)			
		self.setToStocks()
	
	def setFocus(self, row):
		self.selected = row
		if self.numVisible == 0:
			return
		if self.selected > self.numVisible - 1:
			self.selected = self.numVisible - 1
		elif self.selected < 0:
			self.selected = 0
		self.parent.setFocus(self.sRows[self.selected].btnBack)


			
def FetchHtmlPage(url):
	print('fetching htmlpage')
	dialogProgress.create("Retrieving", url)
	
	def SubthreadProc(url, result):
		try:
			f = urllib.urlopen(url)
		except Exception:
			# Could be a socket error or an HTTP error--either way, we
			# don't care--it's a failure to us.
			result.append(-1)
		else:
			result.append(f)

	result = []
	subThread = threading.Thread(target=SubthreadProc, args=(url, result))
	subThread.setDaemon(True)
	subThread.start()
	subThread.join(HTTP_TIMEOUT)

	if [] == result:
		# Subthread hasn't give a result yet.  Consider it timed out.
		dialogProgress.close()
		xbmcgui.Dialog().ok('TIMEOUT','Failed to retrieve page')
		return ''
	elif -1 == result[0]:
		dialogProgress.close()
		xbmcgui.Dialog().ok('ERROR','Failed to retrieve page')
		return ''
	else:
		f = result[0]
		data = f.read()
		if data == None:
			data = ''
		f.close()
		dialogProgress.close()
		if len(data) < 100:
			xbmcgui.Dialog().ok('SIZE ERROR','Failed to retrieve page')

	return data
	



	

def makeRegExFromTags(tags):
	regExStr = ''
	for tagNest in tags:
		backTags = tagNest[::-1]
		backTags = ['/'+x for x in backTags if not x == 'img']
		for tag in tagNest[:-1]:
			if not tag == 'img':
				regExStr += "[^<]*<"+tag+"[^>]*>"
			else:
				regExStr += "(?:<img[^>]*?alt=\"([^\"]*)\">)?"
		regExStr += "(?P<"+tagNest[-1]+">[^<]*)"
		for tag in backTags[1:]:
				regExStr += "[^<]*<"+tag+">"		
	return regExStr
		
# parse Web page

def ParsePage(data):

	print('Parsing data for stock : ')
	
	# this is my first reg exp I've ever wrote and so looks pretty ugly
	# parses one row in the stock table and puts the results into a list
	# 0 = symbol, 1 = date, 2 = price, 3 = xxx, 4 = change, 5 = percentChange, 6 = volume
	tags = [['td','b','a','name'],
			['td','date'],
			['td','b','price'],
			['td','img','b','change'],
			['td','img','b','perchange'],
			['td','vol']]
	reg = makeRegExFromTags(tags)
	LOG( 'REG IS ' + reg)
	p = re.compile(reg,re.IGNORECASE|re.DOTALL)

	stockLines = re.findall(p, data)
	LOG(stockLines)

	global stockData, indexData
	stockData[:] = []
	indexData[:] = []
	#1 = name, 2 = date, 	3=price 4=up/down 5=difference 6=perdiff 7=volume
	for stock in stockLines:
		s = Stock(stock[0])
		s.date = stock[1]
		s.price = stock[2]
		s.change = stock[4]
		s.perchange = stock[6]
		s.volume = stock[7]
		
		if stock[5] == 'Down':
			s.perchange = '-' +s.perchange 
		else:
			s.perchange = '+' + s.perchange 
		if s.change == '0.00' and s.perchange.startswith('+'):	
 			s.perchange = s.perchange[1:]	
		elif s.perchange.startswith('+') and not s.change.startswith('+'):
			s.change = '+' + s.change
		elif s.perchange.startswith('-') and not s.change.startswith('-'):
			s.change = '-' + s.change			
		
		stockData.append(s)

	if len(stockData) >= len(INDEX_NAMES):
		indexData = stockData[0:len(INDEX_NAMES)]
		stockData[0:len(INDEX_NAMES)] = []
	print('found ' + str(len(stockData)) + ' stocks')
	

# starts the parsing
def Parse(url):
	# retrieve yahoo finance web page
	LOG("fetching "+ url)
	data = FetchHtmlPage(url)
	ParsePage(data)

# A check group is a group of vertically aligned checkmark controls that have 
#   a maximum number and minimum number of checks selected
class CheckGroup:
	def __init__(self,window,x,y,width,height,minSelected,maxSelected,labels,font,name=''):

		LOG("fine here in CG")
		self.parent = window
		self.labels = labels
		self.minSelected = minSelected
		self.maxSelected = maxSelected
		self.selected = []
		self.cmChoices = []
		self.cmCheckMarks = []
		self.name = name
		LOG("fine here in CG2 "+ str(labels))
		i = 0
		for label in labels:
			self.cmCheckMarks.append(xbmcgui.ControlCheckMark(x,y,width,height,checkWidth=15,checkHeight=15,label=label[1],font=font,textColor='0xffffffff',alignment=XBFONT_CENTER_Y|XBFONT_RIGHT))
			self.parent.addControl(self.cmCheckMarks[-1])
			self.cmChoices.append(xbmcgui.ControlButton(x-10,y-4,width,height,"",focusTexture=IMAGE_DIR+'focus.png',noFocusTexture=''))
			self.parent.addControl(self.cmChoices[-1])
			y += height
			if i < self.minSelected:
				self.onControl(self.cmChoices[-1])
				i = i + 1

		LOG("fine here in CG3")
		for i in range(len(self.cmChoices)-1):
			self.cmChoices[i].controlDown(self.cmChoices[i+1])
			self.cmChoices[i+1].controlUp(self.cmChoices[i])
	
	def controlUp(self,control):
		LOG("fine here in CGUP")
		try:
			self.cmChoices[0].controlUp(control.cmChoices[-1])
		except:
			self.cmChoices[0].controlUp(control)

	def controlDown(self,control):
		LOG("fine here in CGDOW")
		try:
			self.cmChoices[-1].controlDown(control.cmChoices[0])
		except:
			self.cmChoices[-1].controlDown(control)

	def controlRight(self,control):
		try:
			for i in range(min(len(self.cmChoices),len(control.cmChoices))):
				self.cmChoices[i].controlRight(control.cmChoices[i])
				control.cmChoices[i].controlLeft(self.cmChoices[i])
		except:
			for c in self.cmChoices:
				c.controlRight(control)
		
	def controlLeft(self,control):
		try:
			for i in range(min(len(self.cmChoices),len(control.cmChoices))):
				self.cmChoices[i].controlLeft(control.cmChoices[i])
				control.cmChoices[i].controlRight(self.cmChoices[i])
		except:
			for c in self.cmChoices:
				c.controlLeft(control)	
			
	def onControl(self,control):
		for i in range(len(self.cmChoices)):
			if self.cmChoices[i] == control:
				LOG("Click on " + str(self.labels[i]) + " " + str(self.selected))
				if self.labels[i][0] in self.selected:
					if len(self.selected) > self.minSelected:    #deselected
						self.selected.remove(self.labels[i][0])
				else:
					if len(self.selected) != self.maxSelected:
						self.selected.append(self.labels[i][0])
					elif self.maxSelected > 0:               #keeps the last maxSelected choices
						self.selected = self.selected[1:] + [self.labels[i][0]]

		for i in range(len(self.cmChoices)):
			if self.labels[i][0] in self.selected:
				self.cmCheckMarks[i].setSelected(True)
			else:
				self.cmCheckMarks[i].setSelected(False)
		return self.selected			
	
	def setVisible(self,visible):
		for c in self.cmChoices:
			c.setVisible(visible)
	
	def getSelected(self):
		return self.selected			
				

#  Each option is
#    [Group value header, Group Title, Min Num Selected, Max NumSelected,  [value, display name, HelpName]*]*			
CHART_OPTIONS =	[
		['q','Chart Type',1,1,[
			('l','Line', 'Line Chart'),
			('b','Bar', 'Bar Chart'),
			('c','Candle', 'Candlestick Chart')]],
		['l','Chart Scale',1,1,[
			('on','Log', 'Logarithmic Scale'),
			('off','Linear', 'Linear Scale')]],
		#['z','Chart Size',1,1,[('m','Medium'),('l','Large')]],
		['p','Overlays',0,5,[
			('b','BB','Bollinger Bands'),
			('p','PSAR','Parabolic SAR (Stop and Reverse)'),
			('s','Splits','Splits'),
			('v','Volume','Volume'),
			('m5','5d MA','5-day Moving Average'),
			('m20','20d MA','20-day Moving Average'),
			('m100','100d MA','100-day Moving Average'),
			('e5','5d EMA','5-day Exponential Moving Average'),
			('e20','20d EMA','20-day Exponential Moving Average'),
			('e100','100d EMA','100-day Exponential Moving Average'),
			]],
		['a','Analysis',1,3,[
			('v','Volume','Volume'),
			('vm','VolMA','Volume and Moving Average'),
			('m26','MACD','Moving Average Convergence Divergence'),
			('f14','MFI','Money Flow Index'),
			('p12','ROC','Rate of Change'),
			('r14','RSI','Relative Strength Index'),
			('ss','SS','Slow Stochastic'),
			('fs','FS','Fast Stochastic'),
			('w14','W%R','Williams %R')
			]]
	]

GraphTitles = ['1 Day','5 Day','3 Month','6 Month','1 Year','2 Year','5 Year','Max']
GraphSymbols =['1d','5d','3m','6m','1y','2y','5y','my']
YahooChartUrlN = "http://ichart.finance.yahoo.com/z?s="

# This code is shared by the adv options screen and chart screen
# There is an option to keep the aspect ratio of the chart image or ignor it
CURRENT_URL = ''
def updateImage(window,url,numAnalysis,x,y,width,height,resize):
	if resize:
		imageHeights = [288,365,444,523,602]
		imageHeight = 288
		if numAnalysis >= 1 and numAnalysis <= 5:
			imageHeight = imageHeights[numAnalysis - 1] 
		imageWidth = 512
		
		imageRatio = float(imageHeight )/ float(imageWidth)
		givenRatio = float(height) / float(width)
		LOG("Values x=" + str(x) + " y=" + str(y) + " w=" + str(width) + " h=" + str(height)  
			+ " gr=" + str(givenRatio) + " ir=" + str(imageRatio))
		if givenRatio >= imageRatio:  #area is too tall for image
			y = int(y + (height - imageRatio*width) / 2)
			height = int(imageRatio * width)
		else:                         #area is too wide for image
			x = int(x + (width - (height/imageRatio))/ 2)
			width = int(height / imageRatio)
		LOG("Values x=" + str(x) + " y=" + str(y))	
	
	filename = "T:\\stock.png"
	
	global CURRENT_URL
	if not url == CURRENT_URL:
		CURRENT_URL = url
		urllib.urlretrieve(url, filename)

	xbmcgui.lock()
	if window.showingImage:
		window.removeControl(window.image)
		window.showingImage = False
	
	window.image = xbmcgui.ControlImage(x,y,width,height, filename)

	window.addControl(window.image)
	window.showingImage = True
	xbmcgui.unlock()

# Has a bunch of checkgroups in it, a live chart, 2 lists for the compared stocks
#    the stocks can be moved back and forth between the lists
class ChartOptionsScreen(xbmcgui.Window):
	def __init__(self):
		self.setCoordinateResolution(COORD_NTSC_4X3)
		self.addControl(xbmcgui.ControlImage(0,0, 720,480, BACKGROUND_FILE))

		LOG("fine here in COM")
		self.setupGroups()
		self.compareUnselected = []
		self.compareSelected = []
		self.showingImage = False
		LOG("fine here in COM3")

		self.lblHelp = xbmcgui.ControlLabel(325, 440, 335, 60,'Line Chart','font12','FFFFFFFF')
		self.addControl(self.lblHelp)
		self.lblDir = xbmcgui.ControlLabel(488, 355, 20, 60,'>','font12','FFFFFFFF')
		self.addControl(self.lblDir)
		self.addControl(xbmcgui.ControlLabel(230, 440, 335, 60,'Setting Help:','font12','FFFFFF00'))

		self.addControl(xbmcgui.ControlLabel(350, 250, 500, 30,'Compare To','font14','FFFFFFFF'))
		self.addControl(xbmcgui.ControlLabel(350, 275, 500, 30,'Unselected','font12','FFFFFFFF'))
		self.addControl(xbmcgui.ControlLabel(500, 275, 500, 30,'Selected','font12','FFFFFFFF'))
		self.lstCompareUnselected = xbmcgui.ControlList(350, 290, 135, 180, buttonFocusTexture=IMAGE_DIR+'list-focus.png',buttonTexture=IMAGE_DIR+'list-nofocus.png')
		self.lstCompareSelected = xbmcgui.ControlList(500, 290, 135, 180, buttonFocusTexture=IMAGE_DIR+'list-focus.png',buttonTexture=IMAGE_DIR+'list-nofocus.png')
		self.addControl(self.lstCompareUnselected)
		self.addControl(self.lstCompareSelected)
		self.lstCompareUnselected.setPageControlVisible(False)
		self.lstCompareSelected.setPageControlVisible(False)
		
		self.groups[-1].controlRight(self.lstCompareUnselected)
		self.lstCompareUnselected.controlRight(self.lstCompareSelected)
		self.lstCompareSelected.controlLeft(self.lstCompareUnselected)
		self.lstCompareUnselected.controlLeft(self.groups[3].cmChoices[0])
		self.lstCompareSelected.controlRight(self.groups[2].cmChoices[0])
		self.groups[2].controlLeft(self.lstCompareSelected)

		self.setFocus(self.groups[0].cmChoices[0])

		# the cool new logo and Title
		self.addControl(xbmcgui.ControlImage(65, 20, 188, 77,ROOT_DIR + LOGO_FILE))
		self.addControl(xbmcgui.ControlImage(260, 30, 390, 50,IMAGE_DIR + ADV_TITLE_FILE))
		
		self.lock = False

	def setParent(self,parent):
		self.parent = parent

	def updateImage(self):
		updateImage(self,self.parent.getImageURL(),self.getNumAnalysis(),350,90,285,160,False)

	def getNumAnalysis(self):
		return len(self.groups[3].getSelected())
		
	def makeGroup(self,x,y,width,num):
		self.addControl(xbmcgui.ControlLabel(x, y, width, 30,CHART_OPTIONS[num][1],'font14','FFFFFFFF'))
		self.groups.append(CheckGroup(self,x+15,y+25,width,25,CHART_OPTIONS[num][2],CHART_OPTIONS[num][3],CHART_OPTIONS[num][4],'font12',CHART_OPTIONS[num][0]))		
	
	def setupGroups(self):
		self.groups = []
		LOG("fine here in COM2")
		self.makeGroup(80,90,100,0)
		self.makeGroup(220,90,100,1)
		self.makeGroup(80,190,100,2)
		self.makeGroup(220,180,100,3)

		
		self.groups[0].controlDown(self.groups[2])
		self.groups[0].controlUp(self.groups[2])
		self.groups[1].controlDown(self.groups[3])
		self.groups[1].controlUp(self.groups[3])				
		self.groups[2].controlDown(self.groups[0])
		self.groups[2].controlUp(self.groups[0])
		self.groups[3].controlDown(self.groups[1])
		self.groups[3].controlUp(self.groups[1])
		self.groups[0].controlRight(self.groups[1])
		self.groups[1].controlLeft(self.groups[0])
		self.groups[2].controlRight(self.groups[3])
		self.groups[3].controlLeft(self.groups[2])
		
	
	def setCompareList(self,compareList):
		LOG("Compare List!! " + str(compareList))	
		self.compareUnselected = compareList
		for c in self.compareSelected[:]:
			if c not in self.compareUnselected:
				self.compareSelected.remove(c)
			else:
				self.compareUnselected.remove(c)
		LOG("Selected List " + str(self.compareSelected))	
		LOG("Unselected List " + str(self.compareUnselected))	
		
		self.updateLists()

	def updateLists(self):
		self.lstCompareUnselected.setEnabled(len(self.compareUnselected) > 0)
		self.lstCompareUnselected.reset()
		for c in self.compareUnselected:
			self.lstCompareUnselected.addItem(c)
		
		self.lstCompareSelected.setEnabled(len(self.compareSelected) > 0)
		self.lstCompareSelected.reset()
		for c in self.compareSelected:
			self.lstCompareSelected.addItem(c)
						
		
	def getString(self):
		strArgs = '&'.join([group.name + '=' + ','.join(group.getSelected()) for group in self.groups])
		if len(self.compareSelected) > 0:
			strArgs += '&c=' + ','.join(self.compareSelected)
		return strArgs
		
	def updateHelp(self,control):
		self.lblHelp.setLabel('')
		for i in range(len(self.groups)):
			for j in range(len(self.groups[i].cmChoices)):
				if control == self.groups[i].cmChoices[j]:
					self.lblHelp.setLabel(CHART_OPTIONS[i][4][j][2])
		if control == self.lstCompareSelected:
			self.lblHelp.setLabel('Stocks Selected for Compare')
			self.lblDir.setLabel('<')
		if control == self.lstCompareUnselected:
			self.lblHelp.setLabel('Stocks not Selected for Compare')
			self.lblDir.setLabel('>')
		
	def onAction(self,action):
		if action == ACTION_PREVIOUS_MENU:
			self.parent.updateImage()
			self.close()
		elif (action == ACTION_MOVE_LEFT or action == ACTION_MOVE_RIGHT 
		or action == ACTION_MOVE_UP or action == ACTION_MOVE_DOWN):
		
			# This is really stupid by getFocus() does not return the current control
			# always.. the fix is to just wait a tenth of a second.
			def SubthreadUpdate(self):
				self.updateHelp(self.getFocus())
		
			subThread = threading.Thread(target=SubthreadUpdate, args=[self])
			subThread.setDaemon(True)
			subThread.start()
			subThread.join(0.1)	
		
	def onControl(self,control):
		if self.lock:
			return
		self.lock = True
		for group in self.groups:
			group.onControl(control)
		
		if control == self.lstCompareSelected and len(self.compareSelected) > 0:
			self.moveItem(self.lstCompareSelected,self.lstCompareUnselected,self.compareSelected,self.compareUnselected)
		if control == self.lstCompareUnselected and len(self.compareUnselected) > 0:
			self.moveItem(self.lstCompareUnselected,self.lstCompareSelected,self.compareUnselected,self.compareSelected)
		self.updateImage()
		self.lock = False
				
	def moveItem(self,listS,listD,arrS,arrD):
		item = arrS[listS.getSelectedPosition()]
		position = listS.getSelectedPosition()
		arrS.remove(item)
		arrD.append(item)

		
		self.updateLists()
		
		if len(arrS) == 0:
			self.setFocus(listD)
		elif position == len(arrS):
			listS.selectItem(position - 1)
		else:
			listS.selectItem(position)
		
# Has a chart on it and a range of time values,  all other options of the graph come
#  from the advanced options screen				
class ChartScreen(xbmcgui.Window):
	def __init__(self):
		LOG("fine here in CS")
		self.setCoordinateResolution(COORD_NTSC_4X3)

		self.selectedStock = ''
		self.addControl(xbmcgui.ControlImage(0,0, 720,480, BACKGROUND_FILE))
		
		self.buildFullScreen()
		self.listPosition = 0
		
		self.wChartOptions = ChartOptionsScreen()
		self.wChartOptions.setParent(self)

		self.lstRange.controlRight(self.btnAdvanced)
		self.lstRange.controlLeft(self.btnAdvanced)
		self.lstRange.controlDown(self.btnAdvanced)
		self.btnAdvanced.controlUp(self.lstRange)
		self.btnAdvanced.controlDown(self.lstRange)
		self.btnAdvanced.controlLeft(self.lstRange)
		self.btnAdvanced.controlRight(self.lstRange)
		self.setFocus(self.lstRange)
		
		# the cool new logo
		self.addControl(xbmcgui.ControlImage(65, 20, 188, 77,ROOT_DIR + LOGO_FILE))
		self.addControl(xbmcgui.ControlImage(260, 30, 390, 50,IMAGE_DIR + CHART_TITLE_FILE))
		self.lock = False

	def updateImage(self):
		updateImage(self,self.getImageURL(),self.wChartOptions.getNumAnalysis(),210,90,450,335,True)
		
	# fullscreen mode... has a list a graph (image) and a title
	def buildFullScreen(self):
		self.lstRange    = xbmcgui.ControlList(60, 132, 140, 1000, buttonFocusTexture=IMAGE_DIR+'list-focus.png',buttonTexture=IMAGE_DIR+'list-nofocus.png')
		self.fsTitle     = xbmcgui.ControlLabel( 70, 110, 335, 60,'','font14','FFFFFFFF')
		self.btnAdvanced = xbmcgui.ControlButton(60, 392, 140, 30, "Advanced", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')
		
		self.addControl(self.lstRange)
		self.addControl(self.btnAdvanced)
		self.addControl(self.fsTitle)		
		
		for i in GraphTitles:
			self.lstRange.addItem(i)
		
		self.showingImage = False
		self.selectedStock = ''
	
	def setStock(self,selectedStock):
		self.selectedStock = selectedStock
		self.fsTitle.setLabel('Graphs for ' + self.selectedStock)
		compareList = portfolio[curPortfolio][:]
		compareList.remove(selectedStock)
		self.wChartOptions.setCompareList(compareList)
		
	
	def showFullScreen(self, visible):
		self.fsOverlay.setVisible(visible)
		self.fsTitle.setVisible(visible)		
		self.lstRange.setVisible(visible)
		self.inFullScreen = visible
		self.inStocks = not visible
		if visible:
			self.fsTitle.setLabel('Graphs for ' + self.selectedStock.upper())
			self.setFocus(self.lstRange)
		else:
			if self.showingImage:
				self.removeControl(self.image)
				self.showingImage = False
			self.inStocks = True
			self.stockTable.setFocus(self.stockTable.selected)	

	def getImageURL(self):
			i = self.lstRange.getSelectedPosition()
			url = YahooChartUrlN + self.selectedStock + '&t=' + GraphSymbols[self.listPosition] +'&'+ self.wChartOptions.getString()			
			return url

	def onControl(self,control):
		if self.lock:
			return
		self.lock = True #not a safe lock but good enough
		if control == self.lstRange:
			self.listPosition = self.lstRange.getSelectedPosition()
			self.updateImage()
		elif control == self.btnAdvanced:
			self.wChartOptions.updateImage()
			self.wChartOptions.doModal()
		self.lock = False

#Manages all the portfolio stuff.
# has buttons for copying, adding, renaming, and deleting
class PortScreen(ChartScreen):
#class PortScreen:
	def __init__(self):
		LOG("fine here in PS1")
		self.setCoordinateResolution(COORD_NTSC_4X3)
		self.addControl(xbmcgui.ControlImage(0,0, 720,480, BACKGROUND_FILE))
		
		self.buildPortScreen()
		self.setFocus(self.lstPorts)

		# the cool new logo
		self.addControl(xbmcgui.ControlImage(65, 20, 188, 77,ROOT_DIR + LOGO_FILE))
		self.addControl(xbmcgui.ControlImage(260, 30, 390, 50,IMAGE_DIR + PORT_TITLE_FILE))

	# the portfolio screen...
	def buildPortScreen(self):
		LOG("fine here in PS2")
		
		self.btnPortRename  = xbmcgui.ControlButton(60, 100, 140, 30, "Rename", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')
		self.btnPortAdd     = xbmcgui.ControlButton(60, 132, 140, 30, "Add", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')
		self.btnPortCopy    = xbmcgui.ControlButton(60, 164, 140, 30, "Copy", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')		
		self.btnPortRemove  = xbmcgui.ControlButton(60, 196, 140, 30, "Delete", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')
		self.btnPortDefault = xbmcgui.ControlButton(60, 244, 140, 30, "Default", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')
		
		self.lstPorts       = xbmcgui.ControlList(204, 100, 441, 440, buttonFocusTexture=IMAGE_DIR+'list-focus.png',buttonTexture=IMAGE_DIR+'list-nofocus.png')
		
		self.addControl(self.btnPortRename)
		self.addControl(self.btnPortAdd)
		self.addControl(self.btnPortCopy)
		self.addControl(self.btnPortRemove)
		self.addControl(self.btnPortDefault)
		self.addControl(self.lstPorts)

		self.lstPorts.setPageControlVisible(False)

		self.btnPortRename.controlUp(self.btnPortDefault)
		self.btnPortRename.controlRight(self.lstPorts)
		self.btnPortRename.controlDown(self.btnPortAdd)
		self.btnPortAdd.controlUp(self.btnPortRename)
		self.btnPortAdd.controlRight(self.lstPorts)
		self.btnPortAdd.controlDown(self.btnPortCopy)
		self.btnPortCopy.controlUp(self.btnPortAdd)
		self.btnPortCopy.controlRight(self.lstPorts)
		self.btnPortCopy.controlDown(self.btnPortRemove)
		self.btnPortRemove.controlUp(self.btnPortCopy)
		self.btnPortRemove.controlRight(self.lstPorts)
		self.btnPortRemove.controlDown(self.btnPortDefault)
		self.btnPortDefault.controlUp(self.btnPortRemove)
		self.btnPortDefault.controlRight(self.lstPorts)
		self.btnPortDefault.controlDown(self.btnPortRename)
		self.lstPorts.controlLeft(self.btnPortAdd)
		self.updatePortList()
		LOG("fine here in PS3")
				
		self.portSelect = False

	# all the buttons that require a portfolio selection (copy, delete, rename) 
	# share the code to go into selection mode and out of it
	def enterPortSelect(self,control):
		self.portSelect = True
		self.portSelectButton = control
		self.lstPorts.controlLeft(self.lstPorts)
		if control != self.btnPortRename: self.btnPortRename.setEnabled(False)
		if control != self.btnPortAdd: self.btnPortAdd.setEnabled(False)
		if control != self.btnPortCopy: self.btnPortCopy.setEnabled(False)
		if control != self.btnPortRemove: self.btnPortRemove.setEnabled(False)
		self.setFocus(self.lstPorts)
		
	def exitPortSelect(self):
		self.portSelect = False
		self.lstPorts.controlLeft(self.btnPortAdd)
		self.btnPortRename.setEnabled(True)
		self.btnPortAdd.setEnabled(True)
		self.btnPortCopy.setEnabled(True)
		self.btnPortRemove.setEnabled(True)
		self.setFocus(self.portSelectButton)

	def updatePortList(self):
		self.lstPorts.reset()
		for i in portfolioNames:
			self.lstPorts.addItem(i)


	def onAction(self,action):
		if action == ACTION_PREVIOUS_MENU:
			if self.portSelect:	
				self.exitPortSelect()
			else:
				w.getStocks()
				self.close()
				
		
	def onControl(self,control):
		global curPortfolio,portfolio,portfolioNames
		
		if control == self.btnPortRename or control == self.btnPortCopy or control == self.btnPortRemove:
			self.enterPortSelect(control)

		elif control == self.btnPortDefault:
			if xbmcgui.Dialog().yesno("xStocks: Warning", "This will overwrite any changes you've made.\nAre you sure you want to proceed?"):
				portfolio[:] = []
				portfolioNames[:] = []
				for s in STOCKS:
					portfolio.append(s[1].split(','))
					portfolioNames.append(s[0])
				self.updatePortList()
			

		elif control == self.btnPortAdd:
			xbmc.Keyboard().doModal()
			if xbmc.Keyboard().isConfirmed():
				newPortfolio = xbmc.Keyboard().getText()
				if len(newPortfolio) > 0:
					portfolioNames.append(newPortfolio)
					portfolio.append([])
					self.updatePortList()

		elif control == self.lstPorts:
			#we clicked on a portfolio
			port = self.lstPorts.getSelectedPosition()
			if self.portSelect:
				#we are either renaming, copying, or deleting...
				if self.portSelectButton == self.btnPortRename:
					xbmc.Keyboard(portfolioNames[port]).doModal()
					if xbmc.Keyboard().isConfirmed():
						newName = xbmc.Keyboard().getText()					
						if len(newName) > 0:
							portfolioNames[port] = newName
				if self.portSelectButton == self.btnPortCopy:
					xbmc.Keyboard(portfolioNames[port]).doModal()
					if xbmc.Keyboard().isConfirmed():
						newName = xbmc.Keyboard().getText()					
						if len(newName) > 0:
							portfolioNames.append(newName)
							portfolio.append(portfolio[port][:])
				if self.portSelectButton == self.btnPortRemove:
					if len(portfolioNames) > 1:
						del portfolioNames[port]
						del portfolio[port]
						if curPortfolio >= port:
							curPortfolio = curPortfolio - 1
				self.updatePortList()
				self.exitPortSelect()
			else:
				#we should switch to the portfolio
				curPortfolio = port
				w.getStocks()
				self.close()



# the main screen	
class StockBrowser(xbmcgui.Window):
	def __init__(self):
		LOG("fine here in SB")
		self.setCoordinateResolution(COORD_NTSC_4X3)
		
		xbmcgui.lock()
		self.addControl(xbmcgui.ControlImage(0,0, 720, 480, BACKGROUND_FILE))

		self.buildHeaderRow()

		# add side buttons
		self.btnRefresh     = xbmcgui.ControlButton(60, 100, 140, 30, "Refresh    ", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')
		self.btnAdd         = xbmcgui.ControlButton(60, 132, 140, 30, "Add Stock  ", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')
		self.btnRemove      = xbmcgui.ControlButton(60, 164, 140, 30, "Remove Stock", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')
		self.btnPortfolio   = xbmcgui.ControlButton(60, 212, 140, 30, "Portfolio", textXOffset=10, focusTexture=IMAGE_DIR+'button-focus.png', noFocusTexture=IMAGE_DIR+'button-nofocus.png')
	
		self.addControl(self.btnRefresh)
		self.addControl(self.btnAdd)
		self.addControl(self.btnRemove)
		self.addControl(self.btnPortfolio)

		
		# current portfolio label
		self.lblPortfolio   = xbmcgui.ControlLabel(75, 242, 125, 30, '','font12','FFFFFFFF')
		self.addControl(self.lblPortfolio)	
    
		self.markets = []
		if SHOW_INDEX_DATA:
			for i in range(0,len(INDEX_NAMES)):
				self.markets.append(MarketLabel(self,i,INDEX_NAMES[i]))

		self.stockTable = StockTable(self,MAX_STOCKS)

		self.sortType = -1


		self.fsOverlay = xbmcgui.ControlImage(0,0, 720,480, BACKGROUND_FILE)
		self.inFullScreen = False
		#self.buildFullScreen()
		self.wPortScreen = PortScreen()
		LOG("fine here in CSSS")
		self.wChartScreen = ChartScreen()
		
				

		#self.buildPortScreen()	

		# the cool new logo
		self.addControl(xbmcgui.ControlImage(65, 20, 188, 77,ROOT_DIR + LOGO_FILE))
				
		self.select(self.btnRefresh)
		
		# bool for if the stock table is selected (the nav for the stock table is done manually
		self.inStocks = False
		# are we currently removing a stock?
		self.removingStock = False
		self.show()
		
		xbmcgui.unlock()

	# this builds the table header... 
	def buildHeaderRow(self):
		self.btnSym  = xbmcgui.ControlButton(205, 70, 90, 27,textXOffset=5,textYOffset=5,label='Symbol',font='font14',textColor='FFFFFFFF',alignment=XBFONT_LEFT)	
		self.btnPri  = xbmcgui.ControlButton(295, 70, 80, 27,textXOffset=5,textYOffset=5,label='Price',font='font14',textColor='FFFFFFFF',alignment=XBFONT_LEFT)	
		self.btnCha  = xbmcgui.ControlButton(375, 70, 75, 27,textXOffset=5,textYOffset=5,label='Change',font='font14',textColor='FFFFFFFF',alignment=XBFONT_LEFT)	
		self.btnPer  = xbmcgui.ControlButton(450, 70, 75, 27,textXOffset=5,textYOffset=5,label='%',font='font14',textColor='FFFFFFFF',alignment=XBFONT_LEFT)	
		self.btnVol  = xbmcgui.ControlButton(525, 70, 120, 27,textXOffset=20,textYOffset=5,label='Volume',font='font14',textColor='FFFFFFFF',alignment=XBFONT_RIGHT)

		self.addControl(self.btnSym)
		self.addControl(self.btnPri)
		self.addControl(self.btnCha)				
		self.addControl(self.btnPer)						
		self.addControl(self.btnVol)				

		self.btnSym.controlLeft(self.btnVol)
		self.btnSym.controlRight(self.btnPri)
		self.btnPri.controlLeft(self.btnSym)		
		self.btnPri.controlRight(self.btnCha)	
		self.btnCha.controlLeft(self.btnPri)
		self.btnCha.controlRight(self.btnPer)
		self.btnPer.controlLeft(self.btnCha)
		self.btnPer.controlRight(self.btnVol)
		self.btnVol.controlLeft(self.btnPer)		
		self.btnVol.controlRight(self.btnSym)		

	def populateList(self):
		global portfolio,curPortfolio
		
		#Make sure Yahoo didnt drop tons of our stocks for some reason
		if len(portfolio[curPortfolio]) - len(stockData) < 4:
			portfolio[curPortfolio][:] = []
			portfolio[curPortfolio] = [s.name for s in stockData]

		xbmcgui.lock()
		self.stockTable.setToStocks()
		if SHOW_INDEX_DATA:
			for m in self.markets:
				m.update()
		xbmcgui.unlock()			
	
	def enterRemove(self):
		self.removingStock = True
		self.inStocks = True
		#self.btnRefresh.setLabel("Refresh    ", "font12", "60ffffff")
		#self.btnAdd.setLabel(    "Add Stock  ", "font12", "60ffffff")		
		self.btnRefresh.setEnabled(False)
		self.btnAdd.setEnabled(False)
		self.stockTable.setFocus(self.stockTable.selected)		
	
	def exitRemove(self):
		self.removingStock = False
		self.inStocks = False
		self.btnRefresh.setEnabled(True)
		self.btnAdd.setEnabled(True)				
		self.select(self.btnRemove)
	
	
	def onAction(self, action):
		if action == ACTION_PREVIOUS_MENU:
			if self.removingStock:
				self.exitRemove()
			else:	
				self.close()
		
		if action == ACTION_MOVE_UP:
			if self.inStocks:
				self.stockTable.upAction()
			else:
				if   self.selected == self.btnRefresh:			self.select(self.btnSym)
				elif self.selected == self.btnAdd:				self.select(self.btnRefresh)				
				elif self.selected == self.btnRemove:			self.select(self.btnAdd)				
				elif self.selected == self.btnPortfolio:		self.select(self.btnRemove)						
				elif self.selected == self.btnSym:				self.select(self.btnPortfolio)						
			
		if action == ACTION_MOVE_DOWN:
			if self.inStocks:
				self.stockTable.downAction()
			else:
				if   self.selected == self.btnRefresh:			self.select(self.btnAdd)
				elif self.selected == self.btnAdd:				self.select(self.btnRemove)				
				elif self.selected == self.btnRemove:			self.select(self.btnPortfolio)				
				elif self.selected == self.btnPortfolio:		self.select(self.btnSym)				
				elif self.selected == self.btnSym:
					self.inStocks = True
					self.stockTable.setFocus(0)									
					
		
		if action == ACTION_SCROLL_UP:
			if self.inStocks:			
				self.stockTable.upAction(1, False)


		if action == ACTION_SCROLL_DOWN:
			if self.inStocks:			
				self.stockTable.downAction(1, False)

		if action == ACTION_PAGE_UP:
			if self.inStocks:			
				self.stockTable.upAction(self.stockTable.numVisible, False)

		if action == ACTION_PAGE_DOWN:
			if self.inStocks:
				self.stockTable.downAction(self.stockTable.numVisible, False)
			
		if action == ACTION_MOVE_RIGHT:
			if not self.inStocks:
				if self.selected == self.btnRefresh or self.selected == self.btnAdd or self.selected == self.btnRemove or self.selected == self.btnPortfolio: 
					self.inStocks = True
					self.stockTable.setFocus(self.stockTable.selected)
		
		if action == ACTION_MOVE_LEFT:
			if self.inStocks and not self.removingStock:
				self.inStocks = False
				self.select(self.btnRefresh)
		
	def onControl(self, control):
		global portfolio,curPortfolio
		if control == self.btnRefresh:
			self.getStocks()
		
		elif control == self.btnAdd:
			xbmc.Keyboard().doModal()
			if xbmc.Keyboard().isConfirmed():
				newStock = xbmc.Keyboard().getText()
				portfolio[curPortfolio].append(newStock)
				self.getStocks()
			
				
		elif control == self.btnRemove:
			self.enterRemove()
		
		#sort the stocks by one of the fields..
		elif control == self.btnSym: self.sortStocks(0)
		elif control == self.btnPri: self.sortStocks(1)
		elif control == self.btnCha: self.sortStocks(2)
		elif control == self.btnPer: self.sortStocks(3)
		elif control == self.btnVol: self.sortStocks(4)
			

			
		elif control == self.btnPortfolio:
			self.wPortScreen.doModal()
				
		else:

			for s in self.stockTable.sRows:
				if control == s.btnBack:
					# we clicked on a stock row
					self.wChartScreen.setStock(s.stock)
					if self.removingStock == False:
						# since we arent removing it show a graph
						self.wChartScreen.updateImage()
						self.wChartScreen.doModal()
					else:
						#remove the stock and refresh
						if len(stockData) > 0:
							portfolio[curPortfolio].remove(s.stock)
						self.exitRemove()
						self.getStocks()

	def select(self, control):
		self.selected = control
		self.setFocus(control)

	def sortStocks(self, type):
		global stockData, REVERSE
		
		if type == self.sortType:
			REVERSE = REVERSE * -1
		else:
			self.sortType = type
			REVERSE = 1
		
		if   type == 0: stockData.sort(comp_by_name)
		elif type == 1:	stockData.sort(comp_by_price)
		elif type == 2:	stockData.sort(comp_by_change)		
		elif type == 3:	stockData.sort(comp_by_perchange)
		elif type == 4:	stockData.sort(comp_by_volume)	
		self.populateList()

	def getStocks(self):
		self.lblPortfolio.setLabel('- ' + portfolioNames[curPortfolio])
		stockString = ','.join(portfolio[curPortfolio])
		dialogProgress.create("Fetching Stocks...", "Contacting Yahoo Finance for "+ stockString)
		Parse(YahooFinanceURL + INDEXS + stockString)
		dialogProgress.close()
		self.populateList()

def saveSettings():
	if not os.path.exists(CONFIG_DIR):
		os.mkdir(CONFIG_DIR)
	f = open(CONFIG_DIR + CONFIG_NAME,'w')
	for i in range(0,len(portfolio)):
		f.write('#'+portfolioNames[i]+','+",".join(portfolio[i])+"\n")
	f.write('%'+str(curPortfolio)+"\n")
	f.close()

def loadSettings():
	global curPortfolio, portfolio, portfolioNames
	if os.access(CONFIG_DIR + CONFIG_NAME, os.F_OK)==1: #if config exists
		print "reading config"
		try:
			f = open(CONFIG_DIR + CONFIG_NAME,'r')
			for line in f:
				if line.startswith('%'):
					curPortfolio = int(line.strip('%\n'))
				else:
					p = line.rstrip("\n").split(',')
					if len(p) >0:
						portfolio.append(p)
			f.close()	
		except:
			print "failed reading config"
	
		for i in range(0,len(portfolio)):
			if portfolio[i][0].startswith('#'):
				portfolioNames.append(portfolio[i][0].lstrip('#'))
				portfolio[i] = portfolio[i][1:]
			else:
				portfolioNames.append('Portfolio ' + str(i))

loadSettings()

if len(portfolio) == 0:
	for s in STOCKS:
		portfolio.append(s[1].split(','))
		portfolioNames.append(s[0])
LOG("fine here")


w = StockBrowser()
w.getStocks()
w.doModal()
saveSettings()
LOGCLOSE()
del w, STOCKS, portfolio, portfolioNames, stockData, indexData