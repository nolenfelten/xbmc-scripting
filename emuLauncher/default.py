#
# coding: utf-8

import os, xbmc, xbmcgui, sys, string
try:
    Emulating = xbmcgui.Emulating
except:
    Emulating = False

    #
######   You may use and modify at your own free will just
#######
######   INCLUDE A CREDITS SECTION, FOUND IN THE README.TXT
    #

## Constants
CONFIG_FILE = "config.xml"
CUT_FILE = "launch.cut"
SHOW_XBOX_GAMES = True #Not implemented (yet)
XBOX_GAMES_DIR = ["F:\\games\\", "E:\\games\\"]    # Add more to the list if games are stored in other dirs

## Constants (NO NEED TO CHANGE)
VERSION = "0.9.9"                                   # version of emuLauncher, format (major change.minor change.internal build)
HOME_DIR = os.getcwd().replace(";","")+"\\"         # get homedirectory for the script
XBMC_SKIN = 'default'                               # skin used in xbmc, set to default for now
XBMC_LANGUAGE = 'english'                           # language in xbmc, set to english for now
## JUNK, REMOVE BEFORE RELEASE!


## Set language and Skin (falls back to DEFAULT and english)
try:
    fh = open("Q:\\UserData\\guisettings.xml")
    for line in fh.readlines():
        theLine = line.lower()
        theLine = theLine.strip()
        if theLine.count("<language>") > 0:
            XBMC_LANGUAGE = theLine[10:-11]
        if theLine.count("<skin>") > 0:
            XBMC_SKIN = theLine[6:-7]
    fh.close()
except IOError:
  pass

if XBMC_SKIN != "mc360" and XBMC_SKIN != "project mayhem iii" and XBMC_SKIN != "blackbolt classic":
	XBMC_SKIN = "default"
if XBMC_LANGUAGE != "swedish" and XBMC_LANGUAGE != "english" and XBMC_LANGUAGE != "german" and XBMC_LANGUAGE != "spanish":
	XBMC_LANGUAGE = "english"

## translation, NOTE! another way of doing this ? (since I am no python guru..)
engstrings = {0:'Emulators',1:'Full Screen Visualization',2:'Full Screen Video',3:'Choose',4:'Back',5:'Launch Emulator',6:'Launch Rom',7:'Name of emulator:',8:'Select an Emulator',9:'Items',10:'Search',11:'Add Emulator',12:'Remove Emulator',13:'Error writing config file',14:'Confirm',15:'Are you sure you want to remove:\n',16:'All',17:'Which emulator(s)?',18:'Enter Keywords to Search For',19:'Selected function not currently available',20:'Title:',21:'Path (.xbe):',22:'ROMS dir:',23:'Path (icon):',24:'Rom extension:',25:'Accept:',26:'Type...',27:'Browse...',28:'OK',29:'Cancel',30:'Specify an emulator title!',31:'Specify the emulator path!',32:'Specify the roms path!',33:'Specify the system-icon!',34:'Specify the rom extention!'} 
swestrings = {0:'Emulatorer',1:'Helskärmsvisualisering',2:'Helskärmsvideo',3:'Välj',4:'Bakåt',5:'Starta emulator',6:'Starta rom',7:'Emulatornamn:',8:'Välj en emulator',9:'Objekt',10:'Sök emulator',11:'Lägg till emulator',12:'Ta bort emulator',13:'Fel vid skrivning av configfil',14:'Bekräfta',15:'Är du säker att du vill ta bort:\n',16:'Alla',17:'Vilka emulatorer',18:'Sök efter...',19:'Vald funktion är inte tillgänglig nu',20:'Titel:',21:'Sökväg (.xbe):',22:'ROMS mapp:',23:'Sökväg (ikon):',24:'Rom filändelse:',25:'Acceptera:',26:'Skriv...',27:'Bläddra...',28:'OK',29:'Avbryt',30:'Ange en emulatortitel!',31:'Ange emulator sökväg!',32:'Ange roms sökväg!',33:'Ange sökväg till ikon!',34:'Ange filändelse!'} 
gerstrings = {0:'Emulatoren',1:'Vollbild Visualisierung',2:'Vollbild Video',3:'Wähle aus',4:'Zurück',5:'Starte Emulator',6:'Starte Rom',7:'Name des Emulators:',8:'Emulator auswählen',9:'Stück',10:'Suche',11:'Emulator hinzufügen',12:'Emulator entfernen',13:'Fehler beim Schreiben des Config-Files',14:'Bestätigen',15:'Soll wirklich entfernt werden?\n',16:'Alle',17:'Welche Emulatoren?',18:'Nach welchem Wort soll gesucht werden?',19:'Die gewählte Funktion ist zur Zeit nicht möglich',20:'Title:',21:'Path (.xbe):',22:'ROMS dir:',23:'Path (icon):',24:'Rom extension:',25:'Accept:',26:'Type...',27:'Browse...',28:'OK',29:'Cancel',30:'Specify an emulator title!',31:'Specify the emulator path!',32:'Specify the roms path!',33:'Specify the system-icon!',34:'Specify the rom extention!'} 
norstrings = {0:'Emulatorer', 1:'Fullskjerm visualisering', 2:'Fullskjerm video', 3:'Velg', 4:'Tilbake', 5:'Start emulator', 6:'Start rom', 7:'Navn på emulator', 8:'Velg en emulator', 9:'Objekter', 10:'Søk', 11:'Legg til emulator', 12:'Fjern emulator', 13:'Problemer med å skrive konfigurasjonsfil', 14:'Bekreft', 15:'Er du sikker på at du vil fjerne:\n', 16: 'Alle', 17: 'Hvilke emulatorer?', 18:'Velg nøkkelord du vil søke etter', 19:'Den valgte funksjonen er foreløpig ikke tilgjengelig.',20:'Tittel',21:'Bane (.xbe)',22:'Rom Mappe',23:'Bane (ikon)',24:'ROM tillegg',25:'Godta',26:'Skriv..',27:'Bla igjennom',28:'OK',29:'Avbryt',30:'Spesifiser en emulator tittel!',31:'Spesifiser emulator banen!',32:'spesifiser rom banen!',33:'Spesifiser system ikonet!',34:'Spesifiser rom tillegget!'} 
spanstrings = {0:'Emuladores',1:'Visualización de Pantalla Completa',2:'Video de Pantalla Completa',3:'Elegir',4:'Regresar',5:'Lanzar Emulador',6:'Lanzar Rom',7:'Nombre del Emulador:',8:'Seleccionar Emulador',9:'Articulos',10:'Buscar',11:'Añadir Emulador',12:'Remover Emulador',13:'Hubo un error escribiendo el archivo de configuración',14:'Confirmar',15:'Estas seguro que deseas remover:\n',16:'Todo',17:'Cuales emulador(es)?',18:'Insertar palabras claves a buscar',19:'Función seleccionada no esta disponible por el momento',20:'Title:',21:'Path (.xbe):',22:'ROMS dir:',23:'Path (icon):',24:'Rom extension:',25:'Accept:',26:'Type...',27:'Browse...',28:'OK',29:'Cancel',30:'Specify an emulator title!',31:'Specify the emulator path!',32:'Specify the roms path!',33:'Specify the system-icon!',34:'Specify the rom extention!'} 
dutchstrings = {0:'Emulatoren',1:'Full Screen Visualisatie',2:'Full Screen Video',3:'Selecteer',4:'Terug',5:'Start Emulator',6:'Start Rom',7:'Emulator naam',8:'Selecteer emulator',9:'Elementen',10:'Zoeken',11:'Voeg emulator toe',12:'Verwijder emulator',13:'Fout bij schrijven configuratie bestand',14:'Bevestig',15:'Akkoord om :\n te verwijderen',16:'Alles',17:'Welke emulator(en)?',18:'Vul zoekwoorden in',19:'Geselecteerde functie momenteel niet beschikbaar',20:'Titel',21:'Locatie (.xbe)',22:'ROMS map',23:'Locatie (icoon)',24:'Rom extentie(s)',25:'Bevestig',26:'Type...',27:'Blader...',28:'Akkoord',29:'Annuleer',30:'Kies een emulator titel!',31:'Kies een emulator locatie!',32:'Kies de roms locatie!',33:'Kies het systeem-icoon!',34:'Kies de rom extentie(s)!'}

LANGUAGE = {'swedish':swestrings,'english':engstrings,'german':gerstrings, 'norwegian':norstrings,'spanish':spanstrings,'dutch':dutchstrings}

## States, used for onaction to know where it was called from
STATE_EMU = int(1)
STATE_ROMS = int(2)
STATE_SEARCH = int(3)

## Button Codes
ACTION_MOVE_LEFT =  1
ACTION_MOVE_RIGHT =  2
ACTION_MOVE_UP  =  3
ACTION_MOVE_DOWN =  4
ACTION_PAGE_UP  =  5
ACTION_PAGE_DOWN =  6
ACTION_SELECT_ITEM =  7
ACTION_HIGHLIGHT_ITEM =  8
ACTION_PARENT_DIR =  9
ACTION_PREVIOUS_MENU = 10
ACTION_SHOW_INFO = 11
ACTION_PAUSE  = 12
ACTION_STOP  = 13
ACTION_NEXT_ITEM = 14
ACTION_PREV_ITEM = 15
ACTION_Y = 34

class AddEmu(xbmcgui.Window):
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)

        self.CanClose = 0
        self.emuname = ""
        self.emupath = ""
        self.rompath = ""
        self.romicon = ""
        self.romext = ""

        if XBMC_SKIN == "project mayhem iii":
            self.addControl(xbmcgui.ControlImage(0,0, 720,576, 'background-apps.png'))
            self.addControl(xbmcgui.ControlLabel(200,63, 200,35, 'xbox media center', font="special12", alignment=1))
            self.addControl(xbmcgui.ControlImage(160,108, 64,468, 'contentpanel_left.png'))
            self.addControl(xbmcgui.ControlImage(224,108, 500,468, 'contentpanel.png'))
            self.addControl(xbmcgui.ControlLabel(207, 63, 200, 35, LANGUAGE[XBMC_LANGUAGE][0], 'special13'))
            self.theList = xbmcgui.ControlList(205, 120, 470, 390, buttonTexture="list-nofocus.png", buttonFocusTexture="list-focus.png")
            self.addControl(xbmcgui.ControlLabel(40,124,200,35,LANGUAGE[XBMC_LANGUAGE][20],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,153,200,35,LANGUAGE[XBMC_LANGUAGE][21],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,182,200,35,LANGUAGE[XBMC_LANGUAGE][22],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,211,200,35,LANGUAGE[XBMC_LANGUAGE][23],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,240,200,35,LANGUAGE[XBMC_LANGUAGE][24],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,269,200,35,LANGUAGE[XBMC_LANGUAGE][25],"font13","0xFFFFFFFF"))
    # skin is MC360
        elif XBMC_SKIN == "mc360":
    # bkg image
            self.addControl(xbmcgui.ControlImage(0,0, 720,576, 'background-green.png'))
            self.addControl(xbmcgui.ControlImage(18,0, 702,576, xbmc.getInfoLabel('Skin.String(Games)')))
            self.addControl(xbmcgui.ControlImage(70,0, 16,64, 'bkgd-whitewash-glass-top-left.png'))
            self.addControl(xbmcgui.ControlImage(86,0, 667,64, 'bkgd-whitewash-glass-top-middle.png'))
            self.addControl(xbmcgui.ControlImage(753,0, 16,64, 'bkgd-whitewash-glass-top-right.png'))
            self.addControl(xbmcgui.ControlImage(86,427, 667,64, 'bkgd-whitewash-glass-bottom-middle.png'))
            self.addControl(xbmcgui.ControlImage(70,427, 16,64, 'bkgd-whitewash-glass-bottom-left.png'))
            self.addControl(xbmcgui.ControlImage(753,427, 667,64, 'bkgd-whitewash-glass-bottom-right.png'))
            self.addControl(xbmcgui.ControlImage(60,0, 32,576, 'background-overlay-whitewash-left.png'))
            self.addControl(xbmcgui.ControlImage(92,0, 628,576, 'background-overlay-whitewash-centertile.png'))
            self.addControl(xbmcgui.ControlImage(-61,0, 128,576, 'blades-runner-left.png'))
            self.addControl(xbmcgui.ControlImage(18,0, 80,576, 'blades-size4-header.png'))
    # add the text Emulators (heading)
            self.addControl(xbmcgui.ControlLabel(102,35, 200,35, LANGUAGE[XBMC_LANGUAGE][0], font="font18"))
    # add buttons, check if media is playing
            self.addControl(xbmcgui.ControlImage(125,505, 21,21, 'button-Y.png'))
            self.addControl(xbmcgui.ControlImage(112,525, 21,21, 'button-X.png'))
            if xbmc.Player().isPlayingAudio():
                self.addControl(xbmcgui.ControlLabel(145,528, 300,35, LANGUAGE[XBMC_LANGUAGE][1],font="font12"))
                self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X.png')
            elif xbmc.Player().isPlayingVideo():
                self.addControl(xbmcgui.ControlLabel(145,528, 300,35, LANGUAGE[XBMC_LANGUAGE][2],font="font12"))
                self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X.png')
            else:
                self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X-turnedoff.png')
                self.addControl(xbmcgui.ControlImage(620,505, 21,21, 'button-B.png'))
                self.addControl(xbmcgui.ControlLabel(610,510, 200,35, LANGUAGE[XBMC_LANGUAGE][4],alignment=1,font="font12"))
            self.addControl(self.x_img)
            self.addControl(xbmcgui.ControlImage(633,525, 21,21, 'button-A.png'))
            self.addControl(xbmcgui.ControlLabel(623,528, 200,35, LANGUAGE[XBMC_LANGUAGE][3],alignment=1,font="font12"))
            self.addControl(xbmcgui.ControlLabel(155,510, 200,35, LANGUAGE[XBMC_LANGUAGE][10],font="font12"))
    # add text to blade
            self.addControl(xbmcgui.ControlLabel(79,155, 200,35, string.lower(LANGUAGE[XBMC_LANGUAGE][0]),angle=270,textColor="0xFF000000",font="font14"))
    # add list for roms and emus
            self.theList = xbmcgui.ControlList(300, 90, 400, 395, "font13","0xFF000000","iconlist-nofocus.png","iconlist-focus.png",itemTextXOffset=4)
            self.addControl(xbmcgui.ControlLabel(100,94,200,35,LANGUAGE[XBMC_LANGUAGE][20],"font13","0xFF000000"))
            self.addControl(xbmcgui.ControlLabel(100,123,200,35,LANGUAGE[XBMC_LANGUAGE][21],"font13","0xFF000000"))
            self.addControl(xbmcgui.ControlLabel(100,152,200,35,LANGUAGE[XBMC_LANGUAGE][22],"font13","0xFF000000"))
            self.addControl(xbmcgui.ControlLabel(100,181,200,35,LANGUAGE[XBMC_LANGUAGE][23],"font13","0xFF000000"))
            self.addControl(xbmcgui.ControlLabel(100,210,200,35,LANGUAGE[XBMC_LANGUAGE][24],"font13","0xFF000000"))
            self.addControl(xbmcgui.ControlLabel(100,239,200,35,LANGUAGE[XBMC_LANGUAGE][25],"font13","0xFF000000"))
    # skin is Blackbolt Classic
        elif XBMC_SKIN == "blackbolt classic":
    # bkg image
            self.addControl(xbmcgui.ControlImage(0,0, 720,576, 'background.png'))
    # master chief image
            self.addControl(xbmcgui.ControlImage(315,30, 410,272, 'master.png'))
    # controller image
            self.addControl(xbmcgui.ControlImage(242,310, 481,220, 'myprogs-bkgd.png'))
    # panel
            self.addControl(xbmcgui.ControlImage(55,115, 150,250, 'panel.png'))
    # xbmc logo
            self.addControl(xbmcgui.ControlImage(70,30, 130,70, 'xbmc.png'))
    # add the text Emulators (heading)
            self.addControl(xbmcgui.ControlLabel(242,70, 200,35, LANGUAGE[XBMC_LANGUAGE][11], font="font14", textColor="0xFFE7FF00"))
    # add list for roms and emus
            self.theList = xbmcgui.ControlList(230, 120, 400, 395, "font13","0xFFFFFFFF","list-nofocus.png","list-focus.png",itemTextXOffset=4)
            self.addControl(xbmcgui.ControlLabel(70,124,200,35,LANGUAGE[XBMC_LANGUAGE][20],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(70,153,200,35,LANGUAGE[XBMC_LANGUAGE][21],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(70,182,200,35,LANGUAGE[XBMC_LANGUAGE][22],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(70,211,200,35,LANGUAGE[XBMC_LANGUAGE][23],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(70,240,200,35,LANGUAGE[XBMC_LANGUAGE][24],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(70,269,200,35,LANGUAGE[XBMC_LANGUAGE][25],"font13","0xFFFFFFFF"))
    # skinsetting unknown
        else:
            if os.path.isfile(HOME_DIR+'images\\bkg-emuLauncher.png'): self.addControl(xbmcgui.ControlImage(0,0, 720,576, HOME_DIR+'images\\background-apps.png'))
            self.addControl(xbmcgui.ControlLabel(200,63, 200,35, 'xbox media center', font="special12", alignment=1))
            self.addControl(xbmcgui.ControlLabel(207, 63, 200, 35, LANGUAGE[XBMC_LANGUAGE][0], 'special13'))
            if os.path.isfile(HOME_DIR+"images\\button-nofocus.png"):
              self.theList = xbmcgui.ControlList(205, 120, 470, 390, buttonTexture=HOME_DIR+"images\\button-nofocus.png", buttonFocusTexture=HOME_DIR+"images\\button-focus.png")
            else:
              self.theList = xbmcgui.ControlList(205, 120, 470, 390)
            self.addControl(xbmcgui.ControlLabel(40,124,200,35,LANGUAGE[XBMC_LANGUAGE][20],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,153,200,35,LANGUAGE[XBMC_LANGUAGE][21],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,182,200,35,LANGUAGE[XBMC_LANGUAGE][22],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,211,200,35,LANGUAGE[XBMC_LANGUAGE][23],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,240,200,35,LANGUAGE[XBMC_LANGUAGE][24],"font13","0xFFFFFFFF"))
            self.addControl(xbmcgui.ControlLabel(40,269,200,35,LANGUAGE[XBMC_LANGUAGE][25],"font13","0xFFFFFFFF"))
    # main window drawn, add common stuff ;)

        self.addControl(self.theList)
        self.theList.addItem(xbmcgui.ListItem(LANGUAGE[XBMC_LANGUAGE][26]))
        self.theList.addItem(xbmcgui.ListItem(LANGUAGE[XBMC_LANGUAGE][27]))
        self.theList.addItem(xbmcgui.ListItem(LANGUAGE[XBMC_LANGUAGE][27]))
        self.theList.addItem(xbmcgui.ListItem(LANGUAGE[XBMC_LANGUAGE][27]))
        self.theList.addItem(xbmcgui.ListItem(LANGUAGE[XBMC_LANGUAGE][26]))
        self.theList.addItem(xbmcgui.ListItem(LANGUAGE[XBMC_LANGUAGE][28]))
        self.theList.addItem(xbmcgui.ListItem(LANGUAGE[XBMC_LANGUAGE][29]))
        self.setFocus(self.theList)
        return
    
    def onControl(self, control):
        if control == self.theList:
            lstPos = self.theList.getSelectedPosition()
            if lstPos == 0:
                keyboard = xbmc.Keyboard(self.emuname, LANGUAGE[XBMC_LANGUAGE][20])
                keyboard.doModal()
                self.emuname = keyboard.getText()
                self.theList.getSelectedItem(lstPos).setLabel(self.emuname)
                del keyboard
                return
            elif lstPos == 1:
                self.emupath = xbmcgui.Dialog().browse(1,LANGUAGE[XBMC_LANGUAGE][21],"files")
                self.theList.getSelectedItem(lstPos).setLabel(self.emupath)
                return
            elif lstPos == 2:
                self.rompath = xbmcgui.Dialog().browse(0,LANGUAGE[XBMC_LANGUAGE][22],"files")
                self.theList.getSelectedItem(lstPos).setLabel(self.rompath)
                return
            elif lstPos == 3:
                self.romicon = xbmcgui.Dialog().browse(1,LANGUAGE[XBMC_LANGUAGE][23],"files")
                self.theList.getSelectedItem(lstPos).setLabel(self.romicon)
                return
            elif lstPos == 4:
                keyboard = xbmc.Keyboard(self.romext, LANGUAGE[XBMC_LANGUAGE][24])
                keyboard.doModal()
                self.romext = keyboard.getText()
                self.theList.getSelectedItem(lstPos).setLabel(self.romext)
                del keyboard
                return
            elif lstPos == 5:
                ## all fields must be filled, else display msg
                error = []
                msg = ""
                if self.emuname == "":
                    error.append(LANGUAGE[XBMC_LANGUAGE][24])
                if self.emupath == "":
                    error.append(LANGUAGE[XBMC_LANGUAGE][24])
                if self.rompath == "":
                    error.append(LANGUAGE[XBMC_LANGUAGE][24])
                if self.romicon == "":
                    error.append(LANGUAGE[XBMC_LANGUAGE][24])
                if self.romext == "":
                    error.append(LANGUAGE[XBMC_LANGUAGE][24])
                if len(error) > 0:
                    for e in error:
                        msg = msg + e + '\n'
                    self.message(msg)
                    self.CanClose = 0
                else:	  
                    self.close()
                    self.CanClose = 1
                return
            elif lstPos == 6:
                ## user canceled clear all values
                self.emuname = ""
                self.emupath = ""
                self.rompath = ""
                self.romicon = ""
                self.romext = ""
                self.CanClose = 0
                self.close()
            return

        return

    def message(self, string):
        dialog = xbmcgui.Dialog()
        dialog.ok(" emuLauncher", string)
        del dialog
        return


class Launcher(xbmcgui.Window):
    def __init__(self):
        self.setCoordinateResolution(6)
        if Emulating: xbmcgui.Window.__init__(self)
        self.ViewState = int(0)
        
        self.ICON_LEFT = int(0)
        self.ICON_TOP = int(0)
        #Initialize lists
        self.emus = []      # Names of systems
        self.emupath = []   # Path of emulator
        self.rompath = []   # Path of roms
        self.romext = []    # File extension of roms
        self.icon = []      # Icons of each system
        self.searchRES = [] # what emu is the search from.
        ## NOTE: It is assumed throughout the program that all the above variables have the same length.
        ##   (maybe in the future turn all these list-variables into one list of tuples)

        self.index = -1
                
# Start building the graphic interface (NOTE v2.0! Assign constants of w/h to the common parts instead and make them later to shorten code)
        if XBMC_SKIN == "project mayhem iii":
            self.addControl(xbmcgui.ControlImage(0,0, 720,576, 'background-apps.png'))
            self.addControl(xbmcgui.ControlLabel(200,63, 200,35, 'xbox media center', font="special12", alignment=1))
            self.addControl(xbmcgui.ControlImage(160,108, 64,468, 'contentpanel_left.png'))
            self.addControl(xbmcgui.ControlImage(224,108, 500,468, 'contentpanel.png'))
            self.addControl(xbmcgui.ControlLabel(207, 63, 200, 35, LANGUAGE[XBMC_LANGUAGE][0], 'special13'))
            self.lblCount = xbmcgui.ControlLabel(545,526, 200,35, '',alignment=1, font="font10")
            self.addControl(self.lblCount)
            self.ICON_LEFT = int(39)
            self.ICON_TOP = int(394)
            self.imgIcon = xbmcgui.ControlImage(self.ICON_LEFT, self.ICON_TOP, 128, 128, "")
            self.lblTitle = xbmcgui.ControlLabel(215, 526, 400, 35, '', 'font10')
            self.lstEmu = xbmcgui.ControlList(205, 120, 470, 390, buttonTexture="list-nofocus.png", buttonFocusTexture="list-focus.png")
            self.lstTools = xbmcgui.ControlList(10, 120, 190, 205, buttonTexture="button-nofocus.png", buttonFocusTexture="button-focus.png")
    # skin is MC360
        elif XBMC_SKIN == "mc360":
    # bkg image
            self.addControl(xbmcgui.ControlImage(0,0, 720,576, 'background-green.png'))
            self.addControl(xbmcgui.ControlImage(18,0, 702,576, xbmc.getInfoLabel('Skin.String(Games)')))
            self.addControl(xbmcgui.ControlImage(70,0, 16,64, 'bkgd-whitewash-glass-top-left.png'))
            self.addControl(xbmcgui.ControlImage(86,0, 667,64, 'bkgd-whitewash-glass-top-middle.png'))
            self.addControl(xbmcgui.ControlImage(753,0, 16,64, 'bkgd-whitewash-glass-top-right.png'))
            self.addControl(xbmcgui.ControlImage(86,427, 667,64, 'bkgd-whitewash-glass-bottom-middle.png'))
            self.addControl(xbmcgui.ControlImage(70,427, 16,64, 'bkgd-whitewash-glass-bottom-left.png'))
            self.addControl(xbmcgui.ControlImage(753,427, 667,64, 'bkgd-whitewash-glass-bottom-right.png'))
            self.addControl(xbmcgui.ControlImage(60,0, 32,576, 'background-overlay-whitewash-left.png'))
            self.addControl(xbmcgui.ControlImage(92,0, 628,576, 'background-overlay-whitewash-centertile.png'))
            self.addControl(xbmcgui.ControlImage(-61,0, 128,576, 'blades-runner-left.png'))
            self.addControl(xbmcgui.ControlImage(18,0, 80,576, 'blades-size4-header.png'))
    # add the text Emulators (heading)
            self.addControl(xbmcgui.ControlLabel(102,35, 200,35, LANGUAGE[XBMC_LANGUAGE][0], font="font18"))
    # add buttons, check if media is playing
            self.addControl(xbmcgui.ControlImage(125,505, 21,21, 'button-Y.png'))
            self.addControl(xbmcgui.ControlImage(112,525, 21,21, 'button-X.png'))
            if xbmc.Player().isPlayingAudio():
                self.addControl(xbmcgui.ControlLabel(145,528, 300,35, LANGUAGE[XBMC_LANGUAGE][1],font="font12"))
                self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X.png')
            elif xbmc.Player().isPlayingVideo():
                self.addControl(xbmcgui.ControlLabel(145,528, 300,35, LANGUAGE[XBMC_LANGUAGE][2],font="font12"))
                self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X.png')
            else:
                self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X-turnedoff.png')
                self.addControl(xbmcgui.ControlImage(620,505, 21,21, 'button-B.png'))
                self.addControl(xbmcgui.ControlLabel(610,510, 200,35, LANGUAGE[XBMC_LANGUAGE][4],alignment=1,font="font12"))
            self.addControl(self.x_img)
            self.addControl(xbmcgui.ControlImage(633,525, 21,21, 'button-A.png'))
            self.addControl(xbmcgui.ControlLabel(623,528, 200,35, LANGUAGE[XBMC_LANGUAGE][3],alignment=1,font="font12"))
            self.addControl(xbmcgui.ControlLabel(155,510, 200,35, LANGUAGE[XBMC_LANGUAGE][10],font="font12"))
    # add text to blade
            self.addControl(xbmcgui.ControlLabel(79,155, 200,35, string.lower(LANGUAGE[XBMC_LANGUAGE][0]),angle=270,textColor="0xFF000000",font="font14"))
    # add list for roms and emus
            self.lblCount = xbmcgui.ControlLabel(100,466, 200,35, '', font="font14", textColor="0xFF000000")
            self.addControl(self.lblCount)
            self.ICON_LEFT = int(539)
            self.ICON_TOP = int(300)
            self.addControl(xbmcgui.ControlImage(self.ICON_LEFT-20, self.ICON_TOP-20, 188, 198, "middle-panel.png"))
            self.imgIcon = xbmcgui.ControlImage(self.ICON_LEFT, self.ICON_TOP, 128, 128, "")
            self.lblTitle = xbmcgui.ControlLabel(100, 443, 400, 35, '', 'font10', textColor="0xFF000000")
            self.lstEmu = xbmcgui.ControlList(100, 90, 400, 395, "font13","0xFF000000","iconlist-nofocus.png","iconlist-focus.png",itemTextXOffset=4)
            self.lstTools = xbmcgui.ControlList(505, 90, 200, 200, "font13","0xFF000000","iconlist-nofocus.png","iconlist-focus.png",itemTextXOffset=4)
    # skin is blackbolt classic
        elif XBMC_SKIN == "blackbolt classic":
    # bkg image
            self.addControl(xbmcgui.ControlImage(0,0, 720,576, 'background.png'))
    # master chief image
            self.addControl(xbmcgui.ControlImage(315,30, 410,272, 'master.png'))
    # controller image
            self.addControl(xbmcgui.ControlImage(242,310, 481,220, 'myprogs-bkgd.png'))
    # panel
            self.addControl(xbmcgui.ControlImage(55,115, 150,250, 'panel.png'))
    # xbmc logol
            self.addControl(xbmcgui.ControlImage(70,30, 130,70, 'xbmc.png'))
    # add the text Emulators (heading)
            self.addControl(xbmcgui.ControlLabel(242,70, 200,35, LANGUAGE[XBMC_LANGUAGE][0], font="font14", textColor="0xFFE7FF00"))
    # add list for roms and emus
            self.lblCount = xbmcgui.ControlLabel(227,523, 200,35, '', font="font13", textColor="0xFFE7FF00")
            self.addControl(self.lblCount)
            self.ICON_LEFT = int(539)
            self.ICON_TOP = int(300)
            self.addControl(xbmcgui.ControlImage(self.ICON_LEFT-20, self.ICON_TOP-20, 188, 198, "middle-panel.png"))
            self.imgIcon = xbmcgui.ControlImage(self.ICON_LEFT, self.ICON_TOP, 128, 128, "")
            self.lblTitle = xbmcgui.ControlLabel(215, 526, 400, 35, '', 'font10', textColor="0x00E7FF00")
            self.lstEmu = xbmcgui.ControlList(230, 120, 400, 395, "font13","0xFFFFFFFF","list-nofocus.png","list-focus.png",itemTextXOffset=4)
            self.lstTools = xbmcgui.ControlList(60, 120, 140, 200, "font13","0xFFFFFFFF","button-nofocus.png","button-focus.png",itemTextXOffset=0)
    # skinsetting unknown
        else:
            if os.path.isfile(HOME_DIR+'images\\background-apps.png'): self.addControl(xbmcgui.ControlImage(0,0, 720,576, HOME_DIR+'images\\background-apps.png'))
            self.addControl(xbmcgui.ControlLabel(200,63, 200,35, 'xbox media center', font="special12", alignment=1))
            if os.path.isfile(HOME_DIR+'images\\contentpanel_left.png'): self.addControl(xbmcgui.ControlImage(160,108, 64,468, HOME_DIR+'images\\contentpanel_left.png'))
            if os.path.isfile(HOME_DIR+'images\\contentpanel.png'): self.addControl(xbmcgui.ControlImage(224,108, 500,468, HOME_DIR+'images\\contentpanel.png'))
            self.addControl(xbmcgui.ControlLabel(207, 63, 200, 35, LANGUAGE[XBMC_LANGUAGE][0], 'special13'))
            self.lblCount = xbmcgui.ControlLabel(545,526, 200,35, '',alignment=1, font="font10")
            self.addControl(self.lblCount)
            self.ICON_LEFT = int(39)
            self.ICON_TOP = int(394)
            self.imgIcon = xbmcgui.ControlImage(self.ICON_LEFT, self.ICON_TOP, 128, 128, "")
            self.lblTitle = xbmcgui.ControlLabel(215, 526, 400, 35, '', 'font10')
            if os.path.isfile(HOME_DIR+"images\\button-nofocus.png"):
              self.lstEmu = xbmcgui.ControlList(205, 120, 470, 390, buttonTexture=HOME_DIR+"images\\button-nofocus.png", buttonFocusTexture=HOME_DIR+"images\\button-focus.png")
              self.lstTools = xbmcgui.ControlList(10, 120, 190, 205, buttonTexture=HOME_DIR+"images\\button-nofocus.png", buttonFocusTexture=HOME_DIR+"images\\button-focus.png")
            else:
              self.lstEmu = xbmcgui.ControlList(205, 120, 470, 390)
              self.lstTools = xbmcgui.ControlList(10, 120, 190, 205)
    # main window drawn, add common stuff ;)
        self.addControl(self.imgIcon)
        self.addControl(self.lblTitle)
        self.addControl(self.lstTools)
        self.addControl(self.lstEmu)
        self.lstTools.addItem(LANGUAGE[XBMC_LANGUAGE][10])
        self.lstTools.addItem(LANGUAGE[XBMC_LANGUAGE][5])
        self.lstTools.addItem(LANGUAGE[XBMC_LANGUAGE][11])
        self.lstTools.addItem(LANGUAGE[XBMC_LANGUAGE][12])
        self.setFocus(self.lstEmu)
        if XBMC_SKIN == "mc360":
          self.lstEmu.controlRight(self.lstTools)
          self.lstTools.controlLeft(self.lstEmu)
        else:
          self.lstEmu.controlLeft(self.lstTools)
          self.lstTools.controlRight(self.lstEmu)

        self.ReadConfig(HOME_DIR + CONFIG_FILE)
        self.ShowEmus()

    def ReadConfig(self, path): # Fills in the lists with information specified by the config file
        self.emus = []      # Names of systems
        self.emupath = []   # Path of emulator
        self.rompath = []   # Path of roms
        self.romext = []    # File extension of roms
        self.icon = []      # Icons of each system
        f=open(path,"r")
        for line in f:
##            if line.lower().strip().count("<emu>") > 0:
##                self.emus.append(line.strip()[5:-6])
##                continue
##            if line.lower().strip().count("<emupath>") > 0:
##                self.emupath.append(line.strip()[9:-10])
##                continue
##            if line.lower().strip().count("<rompath>") > 0:
##                self.rompath.append(line.strip()[9:-10])
##                continue
##            if line.lower().strip().count("<emuext>") > 0:
##                self.emupath.append(line.strip()[8:-9])
##                continue
##            if line.lower().strip().count("<icon>") > 0:
##                self.emupath.append(line.strip()[9:-10])
##                continue
            i = string.find(line, "<emu>")
            if i >= 0:
                j = string.find(line, "</emu>")
                self.emus.append(line[i+5:j])
            i = string.find(line, "<emupath>")
            if i >= 0:
                j = string.find(line, "</emupath>")
                self.emupath.append(line[i+9:j])
            i = string.find(line, "<rompath>")
            if i >= 0:
                j = string.find(line, "</rompath>")
                self.rompath.append(line[i+9:j])
            i = string.find(line, "<romext>")
            if i >= 0:
                j = string.find(line, "</romext>")
                self.romext.append(line[i+8:j])
            i = string.find(line, "<icon>")
            if i >= 0:
                j = string.find(line, "</icon>")
                self.icon.append(line[i+6:j])
        f.close()
        return

    def WriteConfig(self, path): # Writes to config file from lists
        try:
            os.remove(path)
            f=open(path,"wb")
            f.write("<emulators>\n")
            for i in range(len(self.emus)):
                f.write("\t<emu>" + self.emus[i] + "</emu>\n")
                f.write("\t\t<emupath>" + self.emupath[i] + "</emupath>\n")
                f.write("\t\t<rompath>" + self.rompath[i] + "</rompath>\n")
                f.write("\t\t<romext>" + self.romext[i] + "</romext>\n")
                f.write("\t\t<icon>" + self.icon[i] + "</icon>\n")
            f.write("</emulators>\n")
        except: self.message2(LANGUAGE[XBMC_LANGUAGE][13])

        ##For the future:  Add code to write favorites section in config file.
        
        f.close()
        return

    def RemoveEmu(self):
        emulist = []
        for emu in self.emus:
            emulist.append(emu)
        emulist.append("Cancel")
        
        index = xbmcgui.Dialog().select(LANGUAGE[XBMC_LANGUAGE][12], emulist)
        if index == -1 or index == len(self.emus): ## User canceled remove operation
            pass
        else:
            if xbmcgui.Dialog().yesno(LANGUAGE[XBMC_LANGUAGE][14], LANGUAGE[XBMC_LANGUAGE][15] + self.emus[index] ):                
                self.emus.remove(self.emus[index])
                self.emupath.remove(self.emupath[index])
                self.rompath.remove(self.rompath[index])
                self.romext.remove(self.romext[index])
                self.icon.remove(self.icon[index])
                self.WriteConfig(HOME_DIR + CONFIG_FILE)
        self.ReadConfig(HOME_DIR + CONFIG_FILE)
        self.ShowEmus()
        return

    def AddEmu(self):
        ## Create a new window asking for certain information
        ## Will write this as a new class then make an object of that type and doModal() it.
        # Basic steps are as follows:
 
        # Create new addEmu object
        A = AddEmu()
        # Display it
        A.doModal()

        # Extract information out of it
        if A.CanClose > 0:
            self.emus.append(A.emuname)
            self.emupath.append(A.emupath)
            self.rompath.append(A.rompath)
            self.romext.append(A.romext)
            self.icon.append(A.romicon)
            # Write to config file
            self.WriteConfig(HOME_DIR + CONFIG_FILE)

        del A
                        
        self.ReadConfig(HOME_DIR + CONFIG_FILE)
        self.ShowEmus()
        
        return

    def ShowEmus(self):
        self.lstEmu.reset()
        self.imgIcon.setImage(self.icon[0])
# count label in PMIII (shows lstEmu count)
        self.lblCount.setLabel(str(len(self.emus))+' '+LANGUAGE[XBMC_LANGUAGE][9])
        self.ViewState = STATE_EMU
        for emu in self.emus:
            self.lstEmu.addItem(xbmcgui.ListItem(emu, "", "", ""))
        self.setFocus(self.lstEmu)


    def ShowRoms(self, index):
        self.ViewState = STATE_ROMS
        self.index = index
        self.lstEmu.reset()
        self.lblCount.setLabel(str(len(os.listdir(self.rompath[index])))+' '+LANGUAGE[XBMC_LANGUAGE][9])
        for rom in os.listdir(self.rompath[index]):
            if rom.lower().endswith(self.romext[index]):
                self.lstEmu.addItem(xbmcgui.ListItem(rom[0:-4], index, "", ""))

    def LaunchRom(self, title):
        SHORTCUT = HOME_DIR + CUT_FILE
        f=open(SHORTCUT, "wb")
        f.write("<shortcut>\n")
        f.write("    <path>" + self.emupath[self.index] + "</path>\n")
        f.write("    <custom>\n")
        f.write("       <game>" + title + '.' + self.romext[self.index] + "</game>\n")
        f.write("    </custom>\n")
        f.write("</shortcut>\n")
        f.close()
        xbmc.executebuiltin('XBMC.Runxbe(' + SHORTCUT + ')')

    def LaunchEmu(self):
        emulist = []
        for emu in self.emus:
            emulist.append(emu)
        emulist.append("Cancel")
        
        index = xbmcgui.Dialog().select(LANGUAGE[XBMC_LANGUAGE][8], emulist)
        try:
            if index != -1 and index != len(self.emus): xbmc.executebuiltin('XBMC.Runxbe(' + self.emupath[index] + ')')
        except:
            return
        return

    def Search(self):   # Function needs testing
        searchwhat = [LANGUAGE[XBMC_LANGUAGE][16]]
        for emu in self.emus:
            searchwhat.append(emu)
        dialog = xbmcgui.Dialog()
        dialogreturn = xbmcgui.Dialog().select(LANGUAGE[XBMC_LANGUAGE][17], searchwhat)
        if dialogreturn == -1: return
        self.searchRES = []
        dialogreturn = dialogreturn - 1
        self.ViewState = STATE_SEARCH
        if dialogreturn == -1:  # Selected to search all Emulators
            keyboard = xbmc.Keyboard("", LANGUAGE[XBMC_LANGUAGE][18])
            keyboard.doModal()
            if (keyboard.isConfirmed()):
                self.lstEmu.reset()
                results = []
                for path in self.rompath:
                    roms = os.listdir(path)
                    for keyword in string.split(keyboard.getText()):
                        for rom in roms[:]:
                            if string.find(string.lower(str(rom)), string.lower(str(keyword))) == -1:
                                roms.remove(rom)                                
                    # Now the list 'roms' holds all roms that contain ALL keywords
                    for rom in roms:
                        if os.path.isfile(path+"\\"+rom):
                            results.append((str(rom), self.rompath.index(path)))
                results.sort(key=lambda obj:obj[0])
                for result in results:
                    self.lstEmu.addItem(xbmcgui.ListItem(result[0][0:-4],"", "", ""))
                    self.searchRES.append(result[1])
                self.setFocus(self.lstEmu)
                self.lblCount.setLabel(str(len(results))+' '+LANGUAGE[XBMC_LANGUAGE][9])
            return
        elif dialogreturn >= 0:
            keyboard = xbmc.Keyboard("", LANGUAGE[XBMC_LANGUAGE][18])
            keyboard.doModal()
            if (keyboard.isConfirmed()):
                self.lstEmu.reset()
                results = []
                roms = os.listdir(self.rompath[dialogreturn])
                for keyword in string.split(keyboard.getText()):
                    for rom in roms[:]:
                        if string.find(string.lower(str(rom)), string.lower(str(keyword))) == -1:
                            roms.remove(rom)
                # Now the list 'roms' holds all roms that contain ALL keywords
                for rom in roms:
                    if os.path.isfile(self.rompath[dialogreturn]+"\\"+rom):
                        results.append((str(rom), dialogreturn))
                results.sort(key=lambda obj:obj[0])
                for result in results:
                    self.lstEmu.addItem(xbmcgui.ListItem(result[0], "", "", ""))
                    self.searchRES.append(result[1])
                self.setFocus(self.lstEmu)
                self.lblCount.setLabel(str(len(results))+' '+LANGUAGE[XBMC_LANGUAGE][9])
            return
        return

    def onControl(self, control):
        try:
            if control == self.lstEmu:
                if self.ViewState == STATE_EMU:
                    self.index = self.lstEmu.getSelectedPosition()
                    self.ShowRoms(self.lstEmu.getSelectedPosition())
                    return
                elif self.ViewState == STATE_ROMS:
                    self.LaunchRom(self.rompath[self.index] + self.lstEmu.getSelectedItem().getLabel())
                    return
                elif self.ViewState == STATE_SEARCH: ## LaunchRom function wasnt working from search results for some reason...
                    self.index = int(self.searchRES[self.lstEmu.getSelectedPosition()])
                    title = str(self.rompath[self.index]) + str(self.lstEmu.getSelectedItem().getLabel())
                    SHORTCUT = HOME_DIR + CUT_FILE
                    f=open(SHORTCUT, "wb")
                    f.write("<shortcut>\n")
                    f.write("    <path>" + self.emupath[self.index] + "</path>\n")
                    f.write("    <custom>\n")
                    f.write("       <game>" + title + '.' + self.romext[self.index] + "</game>\n")
                    f.write("    </custom>\n")
                    f.write("</shortcut>\n")
                    f.close()
                    xbmc.executebuiltin('XBMC.Runxbe(' + SHORTCUT + ')')
                    return
        except:
            return

        try:
            if control == self.lstTools:
                if self.lstTools.getSelectedPosition() == 0:
                    self.Search()
                elif self.lstTools.getSelectedPosition() == 3:
                    self.RemoveEmu()
                elif self.lstTools.getSelectedPosition() == 2:
                    self.AddEmu()
                elif self.lstTools.getSelectedPosition() == 1:
                    self.LaunchEmu()
                else: self.message2(LANGUAGE[XBMC_LANGUAGE][19])
                return
        except:
            return
        return
                

    def onAction(self, action):
        try:
            if action == ACTION_PREVIOUS_MENU:
                self.close()
                return
            if action == ACTION_PARENT_DIR: # B Button was pressed
                self.ShowEmus()
                return
            if action == ACTION_Y:
##                self.browsetest()
                self.Search()
                return
            if self.ViewState == STATE_ROMS:    # Was showing list of roms
                try:  ## Always add a try, except statement when checking the getFocus()
                    if self.getFocus() == self.lstEmu: ## Update label (not image)
                        self.lblTitle.setLabel(self.lstEmu.getSelectedItem().getLabel())
                        return
                except: pass
            elif self.ViewState == STATE_EMU:
                try:
                    if self.getFocus() == self.lstEmu: ## Updates image and label
                        self.imgIcon.setImage(self.icon[self.lstEmu.getSelectedPosition()])
                        self.lblTitle.setLabel(self.lstEmu.getSelectedItem().getLabel())
                        return
                except: pass
            elif self.ViewState == STATE_SEARCH:
                try:
                    if self.getFocus() == self.lstEmu:  ## Updates image and label
                        self.imgIcon.setImage(self.icon[self.searchRES[self.lstEmu.getSelectedPosition()]])
                        self.lblTitle.setLabel(self.lstEmu.getSelectedItem().getLabel())
                        return
                except: pass
        except: return
        return


    ## Following two functions just used for debugging....
    def message(self):  
        dialog = xbmcgui.Dialog()
        dialog.ok(" My message title", " This is a nice message")
        del dialog
        return

    def message2(self, index):
        dialog = xbmcgui.Dialog()
        dialog.ok(" emuLauncher", str(index))
        del dialog
        return

    def browsetest(self):
        dialog = xbmcgui.Dialog()
        self.message2(dialog.browse(1, "Emulator XBE", "files"))
        del dialog
        return

D = Launcher()
D.doModal()
del D
