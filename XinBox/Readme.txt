      ##########################
      #                        #                      
      #   XinBox (V.0.2)       #         
      #     By Stanley87       #         
      #                        #
#######                        #######             
#                                    #
#                                    #
#   A pop3 email client for XBMC     #
#                                    #
######################################


THIS README WILL ONLY CHANGE WHEN A PUBLIC RELEASE IS RELEASED!

Note: This is the old XBOX inBOX script - Please do a FRESH install!!
					- Old settings.xml file should work tho.


NEW FEATURES:

**Multi Language support (English, Dutch, German, Swedish - more to come soon)
**New "MINI MODE" - this will minimize the XinBox GUI and the script will continue to check
	for new emails, if a new email is received into any of the set up XinBox's, a
	notification dialog will popup, press Back while the dialog is up to open XinBox,
	or press any other button to close the dialog and the mini mode will continue to run
	and continue to notify user of new emails. (if nothing is pressed, dialog closes after
	8seconds and continues to run)
	NOTE: Popup is for every SINGLE new email. Best to check and download emails in gui
	      first before running mini mode to stop mini mode notifying user of every new
	      email :-D
**New XinBox method. On first click of XinBox 1 or 2, all emails that have been downloaded
	previously will show, user can browse these. The label if the XinBox is changed
	to "Check For New". If this is then clicked, new emails for this Xinbox are downloaded.
	"XinBox Empty" is displayed if no emails are in the XinBox.
	Also, the Username for the Xinbox is displayed at the top of the sceen!
**New - "New!" is added to all new emails that are received. The "NEW!" is removed
	when the XinBox is next checked for new emails.
**NEW - MUCH Better screen resolution support! 



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

This project has a new name (XinBox) as supposed as to the old names (Xbox Inbox & XBMCMail (SSS)).

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

Installation: 

Run the build.bat file included, then transfer the XinBox folder in the /Build dir
to your XBMC/Scripts folder.

_______________________________________________________________________________________________________

_______________________________________________________________________________________________________

Enjoy.

Thanks to the translators:
		Swedish by blittan
		German by Rockstarr
		Dutch by jonkersm 
		Spanish by El Piranna
Thanks to burriko for his original XBMCMail script.
Thanks to blittan - emuLauncher script for some references
Thanks to Donno - Space Invaders script for some references
		- Hosting my SVN :-D
			http://xbmc-scripting.googlecode.com/svn/trunk/XinBox
		
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

Replace the file default.wav in "scripts/XinBox/Src/Sounds" folder with the new .wav file

_____________________________________________________________________________________________________


Bug Reports/Feature Suggestions/Fan Mail :-p /Comments???
PM ME : www.xboxmediacenter.com/forum   
			- username Stanley87