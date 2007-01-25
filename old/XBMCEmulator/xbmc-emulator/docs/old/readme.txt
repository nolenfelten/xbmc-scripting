The scripts contained within this rar are designed to allow scripts written for 
XBMC to work on a PC. They are currently in a pre-alpha stage of development--I've 
just started. But they already work somewhat. You're free to use and distribute 
these files, but please give credit where it's due.

To contact me, visit the XBMC forums and message Alexpoet, or visit my website at:
http://members.cox.net/alexpoet/downloads/

To install the emulator, simply copy the files "xbmc.py" and "xbmcgui.py" along with 
the image file "controller.gif" into the "Lib" subfolder of your Python installation 
folder.

	NOTE: The emulator now REQUIRES that you have PIL installed for it to work 
	properly. If you don't have PIL installed on your PC, you can download it 
	free from this site: http://www.pythonware.com/products/pil/

The emulator doesn't need to be run; simply make these files available to your 
Python installation, and they'll allow scripts written for XBMC to operate on a PC.

For best use, I recommend using the following lines near the very beginning of your 
script (after importing xbmcgui):
try: Emulating = xbmcgui.Emulating
except: Emulating = False
to create a global boolean variable indicating whether or not the script is being 
run within XBMC.

Also, add the following line to the init function of any class that is a child of 
xbmcgui.Window:
if Emulating: xbmcgui.Window.__init__(self)

There should be, attached to these files, a PDF manual (it's only 6 pages) explaining 
some of these issues in more detail.
