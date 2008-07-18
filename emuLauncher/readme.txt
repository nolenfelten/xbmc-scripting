emuLauncher Script for launching roms from XBMC
Version 0.9.9

http://www.xbmcscripts.com/modules/mod_docman/includes_frontend/index.php?option=com_docman&task=doc_download&gid=344&Itemid=36

Whats new:
	
	- Translation into different languages

	- Matching skins automatically (supported is PMIII, MC360 and Blackbolt Classic, more to come if requested)

	- Detects installdirectory by itself (default Q:\scripts\emuLauncher)

DO NOT REQUEST ADDING SUPPORT FOR EMULATORS, SINCE IT'S THE EMULATOR-DEVS
THAT NEED TO IMPLEMENT COMMANDLINE LAUNCHING IN THE EMULATOR.

IMPORTANT NOTES
===============
This is the the prerelease of emuLauncher, once a few things are worked out,
we will release v1.0, then work is in progress on v2.x which will autodetect
emulators and the settings of them by parsing necessary files. Also (if possible)
an installer will be included to make the corresponding changes to files in xbmc.
Support for more things will be added, like showing xboxgames in the list and also
homebrew games.

-------------------------------------------------------------------------------
Installation:
-------------
Copy this script, default.tbn, config.xml, readme.txt and the images directory
(which contain: bkg-emuLauncher.png, button-focus.png, button-nofocus.png) to
wherever you like.
Edit the config.xml to suite your needs. (See sample for icon-example).
More icons are available at http://xbox.nugnugnug.com which also hosts alot of
other interesting stuff for emulation.

NOTE: subdirs are not supported yet (W.I.P) and also multiple rom extensions,
in this release we only support one (recommended are .zip).
Run it from filemanager or the scriptsmanager or even better, modifiy the skin
to launch this instead of opening the emulator bookmark.

For a nice integration into MC360 and other skins, look at http://forums.xbox-scene.com

KNOWN ISSUES:
-------------------
- 07-08-2006 Romextensions only take one (solution: use .zip)
- 07-08-2006 Subdirectories of roms do NOT work (solution: dont use it)
- 07-08-2006 Translation isn't complete in german, norwegian and spanish. (solution: will be fixed as soon as translators are finished)

Changelog:
----------
added/fixed/changed: (dd-mm-yyyy, please specify date in CET) <developer> 

 - 05-12-2006 added: Background animation for MC360 skin <CHI3f>
 - 03-12-2006 fixed: Stretching of images in add emulator screen <CHI3f>
 - 03-12-2006 fixed: Position of list item icon in blackbolt classic skin <CHI3f>
 - 03-12-2006 added: Background for list item icon in blackbolt classic skin <CHI3f>
 - 03-12-2006 fixed: Position of whitewash-glass-bottoms in MC360 skin <CHI3f>
 - 03-12-2006 changed: Positon of lists, icon and # of files label in MC360 <CHI3f>
 - 03-12-2006 added: Support for custom blades for the supermod users <CHI3f>
 - 03-12-2006 fixed: Spanish translation <CHI3f>
 - 03-12-2006 fixed: German translation <CHI3f>
 - 03-12-2006 added: Blackbolt Classic skin support. (thx to CHI3f)
 - 02-12-2006 changed: EmuLauncher is now available from SVN
              (svn checkout http://xbmc-python.googlecode.com/svn/trunk/ xbmc-python)
 - 07-08-2006 fixed: addEmu function working.
 - 07-08-2006 fixed: search showed subdirs.
 - 07-08-2006 fixed: emulator started even when canceled "start emulator"
 - 07-08-2006 fixed: addEmu function now uses skins
 - 07-08-2006 added: more strings in translation (addEmu function)
 - 07-08-2006 fixed: forgot to add focus/nofocus texture to emuList 
 - 07-08-2006 changed: background for default skin (1 image instead of 3) 
 - 07-08-2006 fixed: Typo in german translation strings 
 - 07-08-2006 added: Spanish translation strings 
 - 05-08-2006 fixed: Console image loads appropriate console in search results
 - 05-08-2006 added: AddEmu function (not tested yet, probably buggy)
 - 05-08-2006 added: Y-button invokes search routine
 - 05-08-2006 added: Norwegian translation strings
 - 05-08-2006 fixed: Typo in english strings
 - 05-08-2006 fixed: German translation strings
 - 04-08-2006 added: Label/Image updating when holding L/R triggers
 - 04-08-2006 fixed: use SetImage() method on ControlImages instead
 - 04-08-2006 fixed: renamed to default.py, for better handling in xbmc
 - 04-08-2006 fixed: removed emuindex that showed up when searching
 - 03-08-2006 fixed: alignment of controls in default skin
 - 03-08-2006 fixed: alignment of controls in MC360 skin
 - 03-08-2006 fixed: translation of the whole script
 - 02-08-2006 fixed: moved some controls in PMIII skin
 - 26-08-2006 added: default skin
 - 25-07-2006 added: MC360 skin
 - 24-07-2006 added: PMIII skin 
 - 23-07-2006 added: translation of interface
 - 23-07-2006 added: skinswitching based on xbmc
 - 23-07-2006 fixed: detects basedirectory for the script

Developers:
blittan
bjs1400

Translations (x-s forums username):
-------------
Swedish: blittan
Norwegian: spiff
German: Solo0815
Spanish: fmalucard
English: bjs1400, blittan

Thanks:
-------
spiff, for pointing out things and listening to our needs and preys
Donno, for programming some great script and give me ideas
MattAAron, graphics help and providing new ideas to the community
inthepit, integrating it into MC360 (http://forums.xbox-scene.com/index.php?showtopic=536677)

   From Blittan:
   -------------
	My family, for giving me love and support
	All users for pointing out bugs and giving suggestions.

   From bjs1400:
   -------------
	XBMC and all developers for making THE best media center application
