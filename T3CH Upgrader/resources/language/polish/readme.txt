Polish ver. Work in progress - polska wersja pliku readme - praca w toku - pomoc mile widziana
T3CH Upgrader - Skrypt do pobierania i instalacji ostatnich najnowszych wydañ grupy T3CH.
-------------------------------------------------------------------------------------------
Ustawienia wstêpne - Jest parê opcji ustawieñ wstêpnych które musisz wprowadziæ zanim zaczniesz u¿ywaæ skryptu:
1) Jaki dysk i jaki katalog ma byæ u¿ywany jako roboczy  ( np. E:\apps ) .Struktura katalogów po wypakowaniu nowych wersji bêdzie wygl±da³a tak ( np.  E:\apps\<t3ch_build_name>\XBMC )
2) Umiejscowienie pliku startowego dasha i jego nazwa, jest to w du¿ej mierze zwi±zane z Twoj± przeróbk± i u¿ywanym biosem ( w Polsce najczê¶ciej jest to plik o nazwie evoxdash.xbe na dysku C konsoli - dla przeróbek z czipkiem lub default.xbe umiejscowiony w katalogu dashboard na dysku E konsoli - dla tzw. bezczipowych). To w tym miejscu bêdzie u¿yty TEAM XBMC Shortcut.xbe i powi±zany z nim plik konfiguracyjny .cfg
   Dysk: np. C:
   Plik startowy dasha:  np. evoxdash (mo¿esz tutaj wprowadziæ ¶cie¿kê np. dashbord\default )
3) Pliki, które zawsze kopiujesz - tutaj prawie wszystko jasne, lista plików i folderów w których co¶ zmienili¶my ¿eby nasz xbmc by³ bardziej naszy taki i chcemy aby tak zosta³o. ( nale¿y pamiêtaæ ¿e skrypt nie nadpisuje folderów a jedynie konkretne pliki.)
4) Pliki, które zawsze usuwasz - opcja ta przydaje siê do usuwania niepotrzebnych scraperów , wersji jêzykowych, d¼wiêków startowych, splashy z pobranej wersji.

To Install a new T3CH Build
---------------------------
Select the Main Menu option "Download: <build_name>"
The following will happen;
1) Downloads T3CH rar
2) Extracts rar to location specified in Settings Menu.
3) Copies old build UserData (if still located within XBMC folder structure).
4) Copies Scripts (if they don't exist in new build) - same for vizualisations, skins etc.
5) Copies additional files/folders as per 'Maintain Copies'.
6) Deletes files/folders as per 'Maintain Deletes'.
7) Prompts to create and install new dash booting shortcuts.
   Backups are always made, named *.xbe_old and *.cfg_old on boot drive.
8) Prompt to Reboot
If all is well after reboot, you will be now running the latest T3CH build!

Local Installation:
-------------------
If you ftp a T3CH build rar to the designed rar download location (eg. E:\apps\) the Main Menu will give you the option to do an installation from that.

Auto startup with XBMC Startup:
-------------------------------
It is possible to have the script start with XBMC by the use of autoexec.py.
It is included, all you need to do is copy it to Q:\scripts
It can startup in three modes:
# SILENT = do whole upgrade without GUI interaction.
# NOTIFY = just inform of new build
# NORMAL = Interactive prompt driven
The required mode needs to be edited into autoexec.py executebuiltin.  The script comes with it set to NOTIFY

Knonw Problems:
---------------
*sometimes* the newly extracted rar folder strcture doesnt appear to exist, and the script won't continue.
This is known problem and the best thing to do is, reboot and try again, your existing XBMC installation has not been touched.
If you're stuck, post in the appropiate forum at http://www.xboxmediacenter.com/forum/

Written By BigBellyBilly
Thanks to others for ideas, testing, graphics ... VERY MUCH APPRECIATED !
bigbellybilly AT gmail DOT com
je¿eli masz jakie¶ pytania po polsku, zapraszam
smuto.promyk AT gmail DOT com