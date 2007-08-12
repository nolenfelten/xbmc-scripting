@Echo off

SET ScriptName=Apple Movie Trailers

:: Create Build folder
Echo ------------------------------
Echo Creating %ScriptName% Build Folder . . .
rmdir BUILD /S /Q
md BUILD
Echo.

:: Extract Revision # and set %Revision% variable
Echo ------------------------------
Echo Extracting revision number . . .
Echo.
FOR /F "Tokens=2 Delims=]" %%r IN ('TYPE ".svn\entries" ^| FIND /v /n "&_&_&_&" ^| FIND "[4]"') DO SET Revision=%%r
Echo.

:: Create exclude file
Echo ------------------------------
Echo Creating exclude.txt file . . .
Echo.
Echo .svn>"BUILD\exclude.txt"
Echo Thumbs.db>>"BUILD\exclude.txt"
Echo Desktop.ini>>"BUILD\exclude.txt"
Echo.

:: Create release version..
Echo ------------------------------
Echo Copying required files to \Build\%ScriptName%\ folder . . .
XCopy resources "BUILD\%ScriptName%\resources" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt
Copy default.tbn "BUILD\%ScriptName%\"

:: Create new default.py with __svn_revision__ embedded
Echo # Built with build.bat version 1.0 > "BUILD\%ScriptName%\default.py"
For /F "Delims=$" %%L In (default.py) Do (
    If /I "%%L"=="__svn_revision__ = 0" (
        Echo __svn_revision__ = "%Revision%" >> "BUILD\%ScriptName%\default.py"
    ) Else (
        Echo %%L >> "BUILD\%ScriptName%\default.py"
        )
    )
)
::copy default.py "BUILD\%ScriptName%\"
Echo.

:: Notify user of completion
Echo Build Complete - Scroll Up to check for errors.
Echo Final build is located in the BUILD folder.
Echo copy: \%ScriptName%\ folder in the \BUILD\ folder.
Echo to: /XBMC/scripts/ folder.
pause
