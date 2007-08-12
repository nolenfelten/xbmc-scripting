@ECHO off
CLS
COLOR 1B

:: Set script name based on current directory
FOR /F "Delims=" %%D IN ('ECHO %CD%') DO SET ScriptName=%%~nD

:: Set window title
TITLE %ScriptName% Build Script!

:: Create Build folder
ECHO ------------------------------
ECHO Creating \BUILD\%ScriptName%\ folder . . .
IF EXIST BUILD (
    RD BUILD /S /Q
)
MD BUILD
ECHO.

:: Extract Revision # and SET %Revision% variable
ECHO ------------------------------
ECHO Extracting revision number . . .
ECHO.
FOR /F "Tokens=2* Delims=]" %%R IN ('FIND /v /n "&_&_&_&" ".svn\entries" ^| FIND "[11]"') DO SET Revision=%%R

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
ECHO # Built with build.bat version 1.0 - %ScriptName% script revision: %Revision%> "BUILD\%ScriptName%\default.py"
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

:: Delete exclude.txt file
DEL "BUILD\exclude.txt"

:Finish
:: Notify user of completion
ECHO ------------------------------
ECHO Build Complete - Scroll up to check for errors.
ECHO.
ECHO Final build is located in the the \BUILD\ folder.
ECHO.
ECHO copy: \%ScriptName%\ folder from the \BUILD\ folder.
ECHO to: /XBMC/scripts/ folder.
ECHO.
PAUSE
