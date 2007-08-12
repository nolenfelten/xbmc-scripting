@ECHO off
CLS
COLOR 1B

SET ScriptName=Apple Movie Trailers

TITLE %ScriptName% Build Script!

:: Create Build folder
ECHO ------------------------------
ECHO Creating %ScriptName% Build Folder . . .
RMDIR BUILD /S /Q
MD BUILD
ECHO.

:: Extract Revision # and SET %Revision% variable
ECHO ------------------------------
ECHO Extracting revision number . . .
ECHO.
FOR /F "Tokens=2* Delims=]" %%r IN ('FIND /v /n "&_&_&_&" ".svn\entries" ^| FIND "[11]"') DO SET Revision=%%r

:: Create exclude file
ECHO ------------------------------
ECHO Creating exclude.txt file . . .
ECHO.
ECHO .svn>"BUILD\exclude.txt"
ECHO Thumbs.db>>"BUILD\exclude.txt"
ECHO Desktop.ini>>"BUILD\exclude.txt"

:: Create release version..
ECHO ------------------------------
ECHO Copying required files to \Build\%ScriptName%\ folder . . .
XCOPY resources "BUILD\%ScriptName%\resources" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt
COPY default.tbn "BUILD\%ScriptName%\"

:: Create new default.py with __svn_revision__ embedded
ECHO # Built with build.bat version 1.0 - Script Revision: %Revision%> "BUILD\%ScriptName%\default.py"
FOR /F "Tokens=1,2* Delims=]" %%L IN ('FIND /v /n "&_&_&_&" default.py') DO (
    IF /I "%%M"=="__svn_revision__ = 0" (
        ECHO __svn_revision__ = "%Revision%" >> "BUILD\%ScriptName%\default.py"
    ) ELSE IF "%%M"=="" (
        ECHO. >> "BUILD\%ScriptName%\default.py"
    ) ELSE (
        ECHO %%M >> "BUILD\%ScriptName%\default.py"
        )
    )
)
ECHO.
ECHO.

DEL "BUILD\exclude.txt"

:: Notify user of completion
ECHO ------------------------------
ECHO Build Complete - Scroll Up to check FOR errors.
ECHO Final build is located IN the BUILD folder.
ECHO COPY: \%ScriptName%\ folder IN the \BUILD\ folder.
ECHO to: /XBMC/scripts/ folder.
PAUSE
