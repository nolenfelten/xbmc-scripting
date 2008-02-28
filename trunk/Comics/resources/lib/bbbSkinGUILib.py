"""

 bbbSkinGUILib - Skinned (windowXML/dialogXML) objects.

"""
import xbmc, xbmcgui, sys

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__title__ = "bbbSkinGUILib"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '28-02-2008'
xbmc.output("Imported From: " + __scriptname__ + " title: " + __title__ + " Date: " + __date__)

TEXTBOX_DIALOG_XML = "script-bbb-fullscreen-textbox.xml"

#################################################################################################################
class TextBoxDialogXML( xbmcgui.WindowXML ):
	""" Create a skinned textbox window """
	def __init__( self, *args, **kwargs):
		pass
		
	def onInit( self ):
		xbmc.output( "TextBoxDialogXML.onInit()" )
		self.getControl( 3 ).setLabel( self.title )
		self.getControl( 5 ).setText( self.text )

	def onClick( self, controlId ):
		pass

	def onFocus( self, controlId ):
		pass

	def onAction( self, action ):
		if not action:
			return
		buttonCode =  action.getButtonCode()
		actionID   =  action.getId()
#		print( "TextBoxDialogXML.onAction(): actionID=%i buttonCode=%i " % ( actionID, buttonCode) )
		EXIT_CODES = (9, 10, 257, 275, 216, 61506, 61467)
		if actionID in EXIT_CODES or buttonCode in EXIT_CODES:
			self.close()

	def ask(self, title, text ):
		xbmc.output("TextBoxDialogXML.ask()")
		self.title = title
		self.text = text
		self.doModal()		# causes window to be drawn

