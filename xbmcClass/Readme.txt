OBSOLETE, Use Nuka1195's language.lib insted. Code remains for reference purposes.
----------------------------------------------------------------------------------


XBMC Class
Last updated: December 14th 2006

class Language: To be able to use language files like the ones supplied in XBMC.
class Settings: Retrive any setting written in either guisettings.xml or advancedsettings.xml


Usage (Language):
-----------------
xbmcClass.Language().read() | reads all languagestrings
xbmcClass.Language().read(0) = returns string with ID 0
xbmcClass.Language().exists() | returns False if english language cant be read


Usage (Settings):
-----------------
xbmcClass.Setting('settingsname', 0/1/2).read() | 0: guisettings, 1: advancedsettings, 2: both. Returns selected setting, otherwise an errormessage.
For a list of readable settings see manual at: http://www.xboxmediacenter.com/


Credits:
Developing: blittan (blittan@xbmcscripts.com)
Ideas/codesamples: Donno (darkdonno@gmail.com)
                   Chunk_1970 (fylands@aol.com)
                   Rockstar (rocko@rockmetalemocore.de)

Visit http://www.xbmcscripts.com for updates on this class.
Join irc.freenode.com/#xbmc-scripting for help.


KNOWN ISSUES:
-------------
Doesn't return Error when encounter errors in the xml. (Language)
Doesn't return Error when encounter errors in the xml. (Settings)


ToDO:
-----
Better errorhandling when parsing. (Language)
Better errorhandling when parsing. (Settings)
Possible override of detecting XBMC's language (Language)
Returning settingsfile the setting is found in (Settings)


Changelog:
----------
added/fixed/changed: (dd-mm-yyyy, please specify date in CET) <developer> 

 - 31-01-2007 changed: 
 - 14-12-2006 changed: Merge two seperate libs into one <blittan>
 - 12-12-2006 initial release <blittan>
