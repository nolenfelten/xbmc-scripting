 
@Echo off
CLS
COLOR 1B
SET ScriptName=XinBox
:: Create Build folder
Echo ------------------------------
Echo Creating %ScriptName% Build Folder . . .
IF EXIST BUILD (
    RD BUILD /S /Q
)
md BUILD
Echo.
:: Create exclude file
Echo ------------------------------
Echo Creating exclude.txt file . . .
Echo .svn>"BUILD\exclude.txt"
Echo Thumbs.db>>"BUILD\exclude.txt"
Echo Desktop.ini>>"BUILD\exclude.txt"
Echo.
Echo ------------------------------
Echo Copying required files to \Build\%ScriptName%\ folder . . .
xcopy src "BUILD\%ScriptName%\Src" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt
copy default.* "BUILD\%ScriptName%\"
copy ReadMe.txt "BUILD\%ScriptName%\"
Echo.
Echo ------------------------------
ECHO Cleaning up . . .
DEL "BUILD\exclude.txt"
ECHO.
Echo ------------------------------
Echo Build Complete - Scroll Up to check for errors.
Echo Final build is located in the BUILD folder.
Echo copy: \%ScriptName%\ folder in the \BUILD\ folder.
Echo to: /XBMC/scripts/ folder.
pause