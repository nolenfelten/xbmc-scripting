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
