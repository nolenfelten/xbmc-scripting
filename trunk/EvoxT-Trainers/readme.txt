
Version: 0.8

Release notes:
EvoxT-Trainers is a Xbox trainer downloader script for XBMC. It grabs all
content from www.xboxtrainers.net and lists it.
The script displays the trainers, the nfo's and it downloads\unzips\installs
to a specified trainerpath.

Install:
1. build script. doubleclick the "Build.bat" in "EvoxT-Trainers\"
2. copy/ftp "EvoxT-Trainers" folder from "EvoxT-Trainers\BUILD\xbmc\scripts\"
   to your xbmc script dir ("q:\scripts\")
3. copy/ftp "evt_nfo.ttf" from "EvoxT-Trainers\BUILD\xbmc\media\Fonts\" to
   "q:\media\Fonts\"
4. copy/ftp "Font.xml" from "EvoxT-Trainers\BUILD\xbmc\skins\<skinname>\PAL\"
   to "q:\skins\<skinname>\PAL\". Maybe you want to rename the orig
   "Font.xml" first (e.g. "Font.xml-orig")
5. Done!

(q:\ = XBMC homedir)

NOTE: Step 3 & 4 are install steps for the nfo font. the script works without
      the font, but without displaying nfo's.

REQUIRED: XBMC-SVN_2007-04-29_rev8692-T3CH or later


Buttoncodes:

Gamedpad | Remote | Keyboard  = Action

Back     | Menu   | Esc       = Exit Script / Close Info
A        | Select | Return    = Install Trainer
Y        | Title  | Menu      = Show Info
White    |   --   | Backspace = Change Trainerpath


bootsy/EvoxT
