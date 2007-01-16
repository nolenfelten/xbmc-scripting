      ##########################
      #                        #                      
      #   XBOX InBOX (V.0.1)   #         
      #     By Stanley87       #         
      #                        #
#######                        #######             
#                                    #
#                                    #
#   A pop3 email client for XBMC     #
#                                    #
######################################



Features:

**Fully customisable settings via GUI
**Master Password on start-up option
**Email notification sounds
**Parsing of HTML emails
**Fully updated visual FX's!
**SSL Support
**Script now uses previous settings.xml file, or creates one if one is not present.
**Back button in settings menu now takes you back to main menu instead of exiting script.
**Script downloads and stores emails
**Delete email function (B BUTTON)
**- Script downloads and stores emails 
  - ALL EMAILS are kept intact on server
  - Emails can be deleted from XBOX inBOX - but won't be deleted off server
** Back button in password setup's now returns user back to previous menu.
** Fixed - MC360 Settings menu - selection would not highlight.
** Fixed - Emails without "Subject" would cause script to fault
** Password's hidden in settings menu
** Passwords ***'s out when entering (XBMC SVN 7559 or newer)
   - if SVN older than above-reverts back to showing password when entering.
** New email system - Checks for new emails (quick)
	            - Notifies on how many new emails
                    - Downloads emails with progress bar (speed depends on number of emails and size)
** Removed ISP field in settings menu (was not needed)
** Temp folder is now cleared after exit of script.

__________________________________________________________________________________________________________

This project has a new name (XBOX InBOX) as supposed as to the old name (XBMCMail (SSS)).

_______________________________________________________________________________________________________

SSL is for Incoming Pop3 Email, most pop3 email accounts do NOT use SSL.
Try checking the email without SSL enabled. If no luck, then find out from your Email
provider your SSL incoming pop3 port number (usually 995 - Gmail uses this)

Please DO NOT edit the Settings.xml unless you know what you are doing.
All settings (eg. Username, Password, Pop3 address etc.) can be changed via the scripts GUI.
_______________________________________________________________________________________________________

GMAIL USERS:

To set up your account:

Server = pop.gmail.com
User   = USERNAME@gmail.com
Pass   = USERPASSWORD
SSL    = 995

Note: That "@gmail.com" has to be included in the username.

Also, make sure your Gmail POP settings are set up properly (do this via your Gmail account on the internet)

_________________________________________________________________________________________________________

Installation: FRESH

Just transfer XBOX InBOX folder to your XBMC/Scripts folder.
Run default.py script from XBMC.


Installation: UPDATE

Just replace your old XBMCMail (SSS) or XBOX InBOX folder with the new one.

_______________________________________________________________________________________________________

This script at present works best with PM III skin with screen res 576 x 720 (pal or ntsc)
_______________________________________________________________________________________________________

Enjoy.

Thanks to burriko for his original XBMCMail script.
Thanks to blittan - emuLauncher script for some references
Thanks to "The Test Team":
		-Woggle
		-Sollie
		-resnostyle 
                -jonkersm 

Thanks to my partner Chloe for not getting too angry at my scripting affair.
And a BIG thanks to wwww.xbmcscripts.com for hosting my script

______________________________________________________________________________________________________

Support SICKCYCLE!!, visit www.myspace.com/sickcyclenz, Drum n' Bass MASSIVE!!

______________________________________________________________________________________________________

To change the email notification sound:

Replace the file default.wav in "scripts/XBOX InBOX/Src/Sounds" folder with the new .wav file

_____________________________________________________________________________________________________


Bug Reports/Feature Suggestions/Fan Mail/Comments???
PM ME : www.xboxmediacenter.com/forum   
			- username Stanley87