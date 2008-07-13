@Echo off

SET ScriptName=Youtube

:: Create Build folder
Echo ------------------------------
Echo Creating %ScriptName% Build Folder . . .
rmdir BUILD /S /Q
md BUILD
Echo.

:: Create exclude file
Echo ------------------------------
Echo Creating exclude.txt file . . .
Echo.
Echo .svn>"BUILD\exclude.txt"
Echo Thumbs.db>>"BUILD\exclude.txt"
Echo Desktop.ini>>"BUILD\exclude.txt"
Echo BUILD.BAT>>"BUILD\exclude.txt"
Echo.

Echo ------------------------------
Echo Copying required files to \Build\%ScriptName%\ folder . . .
xcopy gfx "BUILD\%ScriptName%\gfx" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt
xcopy *.* "BUILD\%ScriptName%\" /EXCLUDE:BUILD\exclude.txt
Echo.

Echo Build Complete - Scroll Up to check for errors.
Echo Final build is located in the BUILD folder.
Echo copy: \%ScriptName%\ folder in the \BUILD\ folder.
Echo to: /XBMC/scripts/ folder.
pause
