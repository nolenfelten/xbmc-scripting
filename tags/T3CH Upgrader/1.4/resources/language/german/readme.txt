T3CH Aktualisierer - Skript zum downloaden, installieren und umstellen auf das letzte T3CH Build.

Installation:
 Kopiere nach \scripts\T3CH Upgrader (Unterordnerstruktur beibehalten!)


Gebrauch: 
 default.py ausführen

Beim Starten wird erkannt ob ein neues T3CH Build verfügbar ist.

Vor-Installation-Einstellungen:
-----------------------------

Man kann verschiedene Aspekte der Installation in den Einstellungen verändern:

1) Welches Laufwerk & Pfad der Installation:

   z.B. E:\apps

   Dann wird das Build entpackt nach:
         E:\apps\<t3ch_build_name>\XBMC

2) Den Pfad der Xbox Verknüpfung, die das XBMC als Dashboard lädt; und somit auch den Namen der Verknüpfung, den dein Modchip lädt.
   Es ist der Pfad, der auch in eine neue Verknüpfung geschrieben wird, damit das neu installierte T3CH XBMC Build geladen werden kann.
   Es wird die TEAM XBMC Shortcut.xbe verwendet. Diese benötigt eine .cfg Datei, in der der Pfad gespeichert wird.


   Laufwerk: z.B. C:

   DashName:  z.B. xbmc
   Man kann auch Unterordner im DashNamen angeben:
   
   z.B. dashboard\xbmc

3) Kopierliste:  
   Dies ist eine Liste mit Ordnern und Dateien, die vom aktuellen Build mit in das neue Build kopiert werden sollen.

4) Löschliste:   
   Dies ist eine Liste mit Ordnern und Dateien, die aus dem neuen Build gelöscht werden sollen.


Installation eines neuen T3CH Build
----------------------------------

Wähle im Hauptmenü die Option "Download: <build_name>"

Folgendes wird passieren:

1) Download der aktuellsten T3CH .rar
2) Entpackt die .rar in den gewählten Pfad.
3) Kopiert alte Userdata (falls in XBMC Ordnerstruktur vorhanden).
4) Kopiert Skripts (wenn nicht im neuen Build bereits vorhanden) - das Gleiche gilt für Visualisierungen, Skins etc.
5) Kopiert zusätzliche Dateien/Ordner aus der 'Kopierliste'.
6) Löscht Dateien/Ordner aus der 'Löschliste'.
7) Aufforderung zum erstellen und installieren einer neuen Dashverknüpfung.
   Backups werden immer gemacht, sie werden in *.xbe_old und *.cfg_old umbenannt.
8) Aufforderung zum Neustart.

Wenn nach dem Neustart alles in Ordnung ist, sollte nun das aktuellste T3CH Build laufen!

Lokale Installation:
------------------
Wenn man ein T3CH Build .rar per FTP in den angegebenen .rar Downloadpfad (z.B. E:\apps\) kopiert, wird im Hauptmenü eine Option zum installieren der .rar angezeigt.


Auto Start mit XBMC Start:
--------------------------
Es ist möglich das Skript mit Start des XBMC zu starten. Dazu verwendet man die autoexec.py.
Diese ist mitinbegriffen, man muss sie nur noch nach 'Q:\scripts' kopieren.

Das Skript kann in 3 Modi gestartet werden:
# SILENT = macht den ganzen Aktualisierungsvorgang ohne GUI.
# NOTIFY = informiert nur über ein neues Build.
# NORMAL = mit GUI und Aufforderungen usw.

Der gewünschte Mode muss in der autoexec.py angegeben werden.  Das Skript hat standardmäßig den 'NOTIFY' Mode angegeben.


Bekannte Probleme:
-------------------
*manchmal* wird der neu erstellte rar Ordner nicht erkannt, somit macht das Skript nicht weiter.
Dies ist ein bekanntes Problem und man kann nur eines probieren: neustarten und nochmal versuchen. Die bestehende XBMC Installation wird dabei nicht verändert.

Wenn du nicht mehr weiterkommst, melde dich im dafür vorgesehenen Forum: http://www.xboxmediacenter.com/forum/


Skript geschrieben von BigBellyBilly

Thanks to others for ideas, testing, graphics ... VERY MUCH APPRECIATED !

bigbellybilly AT gmail DOT com


Deutsche Übersetzung (Strings und Readme) von bootsy

bootsy82 AT gmail DOT com