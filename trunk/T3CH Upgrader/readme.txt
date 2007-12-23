T3CH Upgrader - Script to download, install and migrate to latest T3CH builds.

SETUP:
 Install to \scripts\T3CH Upgrader (keep sub folder structure intact)


USAGE: 
 run default.py

At startup Main Menu will indicate the availability of a new T3CH build.

Pre Installation Settings:
--------------------------

You can setup several aspects of the installation using the Settings Menu:

1) Which drive & location to install to

   eg. E:\apps

2) The location of your xbox shortcut that boots to the XBMC as a dashboard, and the name of the shortcut that your mod chip boot too
   It is this location that a new shortcut will be wrutten too inorder to boot to the newly installed T3CH build XBMC.
   It uses the TEAM XBMC Shortcut.xbe  and associated .cfg inorder to achieve this.

   eg. C:\xbmc

3) Maintain Copies;  
   This is a list of Folders and Files that you want to the post installation to be forced to COPY to new build.

4) Maintain Deletes;  
   This is a list of Folders and Files that you want to the post installation to be forced to DELETE from new build.


To Install a new T3CH Build
---------------------------

Select the Main Menu option "Download: <build_name>"

The following will happen;

1) Downloads T3CH rar
2) Extracts rar to location specified in Settings Menu.
3) Copies old build UserData (if still located within XBMC folder structure).
4) Copies Scripts (if they don't exist in new build) - same for vizualisations, skins etc.
5) Copies additional files/folders as per 'Maintain Copies'.
6) Deletes files/folders as per 'Maintain Deletes'.
7) Prompts to create and install new dash booting shortcuts.
   Backups are always made, named *.xbe_old and *.cfg_old on boot drive.
8) Prompt to Reboot

If all is well after reboot, you will be now running the latest T3CH build!


NB. *sometimes* the newly extracted rar folder strcture doesnt appear to exist, and the script won't continue.
This is known problem and the best thing to do is simply try again, your existing XBMC installation has not been touched.

If you're stuck, post in the appropiate forum at http://www.xboxmediacenter.com/forum/


Written By BigBellyBilly

Thanks to others for ideas, testing, graphics ... VERY MUCH APPRECIATED !

bigbellybilly AT gmail DOT com