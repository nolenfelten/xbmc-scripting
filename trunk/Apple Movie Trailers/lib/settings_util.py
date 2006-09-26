import os

def getSettings():
	try:
		settings = {}
		f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'r' )
		s = f.read().split('|')
		f.close()
		settings['trailer quality'] = int( s[0] )
		settings['mode'] = int( s[1] )
		settings['skin'] = s[2]
		settings['save folder'] = s[3]
	except:
		settings = {'trailer quality' : 2, 'mode' : 0, 'skin' : 'default', 'save folder' : 'f:\\'}
	return settings

def saveSettings( settings ):
	try:
		f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'w' )
		strSettings = '%d|%d|%s|%s' % ( settings['trailer quality'], settings['mode'], settings['skin'], settings['save folder'], )
		f.write(strSettings)
		f.close()
	except:
		return False
	else:
		return True
