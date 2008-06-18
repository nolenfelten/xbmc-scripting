 The data can come from these locations;

  1) SMB:           eg smb://<user>:<pass>@PCNAME/DVDProfiler/collection.xml
  2) Local:         all data loaded from xbox folders. you must ftp data over.
  2) online:        http://www.intervocative.com/dvdcollection.aspx/<USER_ID>
                    http://www.invelos.com/dvdcollection.aspx/<USER_ID>

 SETUP:
 1) Unpack into xbox scripts folder, keeping folder structure intact (important)
 2) Enabled Sharing on C:\Program Files\InterVocative Software\DVD Profiler
 3) Export collection as a XML file to:
        C:\Program Files\InterVocative Software\DVD Profiler\EXPORT\collection.xml
 4) run script

 SMB SETUP:
 1) Define the base part of SMB upto PCNAME
   eg. smb://<user>:<pass>@PCNAME/

 2) Entere the shared folder for DVD Profiler
 3) Enter the subfolder from the DVDProfiler share, thats holds the collection.xml
    eg EXPORT
 4) Enter the subfolder from the DVDProfiler share, thats holds the cover images
    eg IMAGES
 5) Enter the name of the exported collection xml file

Define all the above makes a complete smb path to all the required parts.
  eg. smb://<user>:<pass>@PCNAME/DVDProfiler/EXPORTS/collection.xml

 6) If you have media files defined in the v3 XML location tag, then you need
    to give an additional share name of the media location.
    eg. MOVIES

  Using that share, and the XML <location> pressing A will make a final smb playback path,
  eg. smb://<user>:<pass>@PCNAME/MOVIES/click/click.avi


 USAGE: 
 run default.py

 On startup you will be present with the 'Startup Menu' with options:
   SMB			- Collection and images fetched from your SMB location.
   Local Collection	- Collection.xml is expected to be in the UserData\DVDProfiler\cache folder.
   Onlne Alias		- Looksup a collection from online using a user alias.

   Your preferred StartUp method can be set from the Settings Menu, which will bypass the Startup Menu.

 Once collection has been retrieved, it will be displayed.
 Press A to select Film Title to display information.
 Press A (again) to start film playback.  Only if file location stored using DVDProfiler v3
 Press Y on a title to do a IMDb lookup for additional information, images and gallery slideshow.
 Press X to select to Filter titles shown.  Press B to cancel Filters.
 Press B to view an online alias collection.  Press B to return to your collection.
 Press WHITE for Main Menu.  From here the several option and Settings Menu can be found.
 Press BACK to exit script.

 Available button options are displayed across bottom of screen and change according to current action/state.

 SPECIAL NOTES:
 ==============
 DVDProfiler v3 allows you store a 'location' against each dvd.
 If your SMB connected it will attempt to playback the media by joining the 'location' with your defined playback SMB.

 If in local only mode, it joins the Settings Menu 'Local Model Media Location' path to the 'location'
   'F\Videos'   + 'Cars.avi'  to make 'F\Videos\Cars.avi'

 A BigBellyBilly script.  Special thanks to beta testers and language translators.  Much appreciated.
 BigBellyBilly At gmail DOT com
 Enjoy!

 BBB

