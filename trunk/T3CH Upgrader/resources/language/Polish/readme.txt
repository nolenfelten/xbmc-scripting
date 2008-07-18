T3CH Upgrader - Skrypt do zarz±dzania, pobierania i instalacji wydañ XBMC grupy T3CH.

Ustawienia wstêpne "Opcje ustawieñ"
- Jest parê opcji ustawieñ wstêpnych, które musisz wprowadziæ zanim zaczniesz u¿ywaæ skryptu:

1) "Dysk z plikiem startowym dasha" i "Nazwa pliku startowego dasha"
Umiejscowienie pliku startowego dasha i jego nazwa, s± zwi±zane z Twoj± przeróbk± i u¿ywanym biosem ( w Polsce najczê¶ciej jest to plik o nazwie evoxdash.xbe na dysku C konsoli - dla przeróbek z czipkiem lub default.xbe umiejscowiony w katalogu dashboard na dysku E konsoli - dla tzw. bezczipowych).
To na bazie tych ustawieñ bêdziesz mia³ mo¿liwo¶æ ustawienia xbmc jako dashboardu i swobodnego prze³±czania siê pomiêdzy wersjami XBMC ( w tym miejscu bêdzie u¿yty TEAM XBMC Shortcut.xbe jako skrót i powi±zany z nim plik konfiguracyjny .cfg )
Nazwa pliku startowego dasha ( np. evoxdash lub mo¿esz tutaj wprowadziæ ¶cie¿kê np. dashbord\default )

2) "¦cie¿ka instalacji"
Jaki dysk i jaki katalog ma byæ u¿ywany jako roboczy  ( np. E:\MY_BUILDS ) .To do tego katalogu skrypt bêdzie pobiera³ archiwa z wersjami XBMC i do niego bêdzie je wypakowywa³. Tak¿e do tego katalogu wgrywasz archiwum, je¿eli nie masz po³±czenia z Internetem i chcesz zainstalowaæ now± wersjê z dysku.
Struktura katalogów po wypakowaniu bêdzie wygl±da³a na przyk³ad tak ( np.  E:\MY_BUILDS\T3CH_2008-01-27\XBMC\ )

3) "Powiadamiaj, gdy nie ma nowej wersji T3CH"
Do skryptu jest do³±czony autoexec.py, gdy przekopiujesz go do Q:\scripts bêdziesz otrzymywa³ na starcie powiadomienia czy jest nowa wersja czy jej nie ma. Dla wiêkszo¶ci z nas wiedza, ¿e nie ma nowej wersji jest niepotrzebna.

4) "Sprawdzaj aktualizacje skryptu na starcie"
Nic dodaæ nic uj±æ - nowsza wersja prawie zawsze lepsza

5) "Kopiuj UserData do nowej wersji T3CH"
Podstawowa zaleta skryptu - nie tracimy swoich ustawieñ, zapisanych ok³adek, miniaturek zdjêæ, informacji o mediach... itd.
S± tylko dwie znane mi sytuacje, gdzie by¶my nie chcieli kopiowaæ zawarto¶ci UserData:
 - chcemy nieæ ca³kowicie czyst± wersjê i zacz±æ wszystko od zera
 - mamy ustawion± w pliku profiles.xml w³asn± ¶cie¿kê do katalogu UserData ( na zewn±trz dysku Q ), nie potrzebujemy kopiowaæ czego¶, co nie jest nam potrzebne.
 
6) "Zawsze pytaj zanim usuniesz archiwum"
Jak kto¶ lubi jak go pytaj± to zostawi sobie t± opcje - tak naprawdê XBMC ma problemy z wypakowaniem du¿ych archiwów i jest niezrêcznie, gdy wypakowanie siê nie uda³o a skrypt usun±³ paczkê i trzeba zacz±æ pobieranie od nowa.

7) "Wyczy¶æ ustawienia"
Czasami stare ustawienia przeszkadzaj± - warto wyczy¶ciæ i wprowadziæ na nowo, gdy co¶ nie dzia³a a powinno.

=======================================================================================================
Ekran g³ówny "Menu"
- W nag³ówku ekranu g³ównego mamy podane informacje o wersji skryptu i aktualnie u¿ywanej wersji XBMC ( dobrze jest byæ doinformowanym nawet jak nie jest to potrzebne)

1) "Pobierz: <nazwa_wersji>
Wybieramy i skrypt zainstaluje najnowsz± wersjê, ale zanim to zrobimy warto dopasowaæ j± do naszych potrzeb ( personalizacja XBMC to podstawa, co cz³owiek to inne wymagania ). S³u¿± to tego dwie pozycje menu, umiejscowione zaraz poni¿ej i o nich teraz bêdzie mowa (pozycje te niczego nie usuwaj± ani niczego nie kopiuj± tworz± tylko listê, wed³ug której pliki bêd± kasowane z nowo pobranej wersji lub kopiowane z naszej aktualnej wersji do nowo pobranej podczas procesu instalacji - raz zestawiona listy mo¿e s³u¿yæ nam latami)

2) "Pliki, które zawsze kopiujesz"
Tutaj prawie wszystko jasne - lista plików i folderów, w których co¶ zmienili¶my ¿eby nasz xbmc by³ bardziej nasz taki i chcemy, aby tak zosta³o. ( nale¿y pamiêtaæ, ¿e skrypt nie nadpisuje folderów a jedynie konkretne pliki.)

3) "Pliki, które zawsze usuwasz"
Pozycja ta przydaje siê do usuwania niepotrzebnych scraperów, wersji jêzykowych, d¼wiêków startowych, splashy z pobranej wersji.

4) "Wybierz inn± wersjê T3CH"
Z czasem w katalogu roboczym bêdziemy mieli parê wersji XBMC, najnowsza nie znaczy najlepsza. Dziêki tej pozycji mo¿emy swobodnie prze³±czaæ siê pomiêdzy wersjami zapisanymi na dysku, a tak¿e pobieraæ i zainstalowaæ dowoln± archiwaln± wersjê XBMC kompilowan± przez T3CH.

5) "Usuñ niepotrzebn± wersjê T3CH"
Dysk nie jest z gumy, w koñcu skoñczy siê na nim miejsce. Jak ju¿ nazbieramy parê wersji to warto siê zdecydowaæ na usuniêcie niektórych z nich. Skrypt robi to znacznie szybciej ni¿ eksplorator w XBMC.

6) "Aktualizuj skrypt"
Aktualizacjê skryptu mo¿na aktywowaæ rêcznie i takie ustawienia s± domy¶lne. Osobi¶cie polecam w³±czenie opcji automatycznej aktualizacji, trzeba tylko pamiêtaæ, ¿e skrypt bêdzie siê za ka¿dym razem (na starcie) ³±czy³ i sprawdza³ dostêpno¶æ.

========================================================================================================
Jak dzia³a skrypt i jak zachowywaæ siê podczas instalacji
---------------------------
Aby siê wszystko zaczê³o wybierz z menu pozycjê "Pobierz: <nazwa_wersji>"
Co siê dzieje podczas instalowania nowej wersji;
1) Pobierane jest archiwum zawieraj±ce XBMC grupy T3CH
2) Paczka jest wypakowywana do katalogu roboczego ustawionego w "opcjach ustawieñ".
3) Zostaniesz zapytany czy kopiowaæ z aktualnej wersji wszystko, co jest tam dlatego, ¿e jest to twój XBMC.
3) Kopiowana jest zawarto¶æ twojego UserData ( chyba, ¿e ¶wiadomie z tego zrezygnowa³e¶).
4) Kopiowane s± skrypty, (je¿eli takie same nie istniej± ju¿ w pobranej wersji) - to samo dzieje siê z wizualizacjami, skórami itp.
5) Kopiowane s± pliki i katalogi z w³asnej listy "Pliki, które zawsze kopiujesz".
6) Usuwane s± pliki i katalogi z w³asnej listy "Pliki, które zawsze usuwasz".
7) Zostaniesz zapytany czy chcesz siê prze³±czyæ na now± wersjê. Kopie bezpieczeñstwa s± zawsze wykonywane poprzez dodanie do nazwy plików dodatków _new i _old.
8) Zostaniesz zapytany czy uruchomiæ ponownie konsole.
Jest bardzo du¿a szansa, ¿e po restarcie twoim oczom uka¿e siê nowa wersja XBMC i w dodatku kompilowana przez T3CH!

Opcje dodatkowe;
"Instaluj z zapisanego na dysku":
Je¿eli wgrasz do katalogu roboczego paczkê z archiwum od T3CH to w menu g³ównym pojawi ci siê pozycja, dziêki której bêdziesz móg³ przeprowadziæ ca³± instalacjê bez po³±czenia z Internetem. Prawie niemo¿liwe, ¿e s± jeszcze takie sytuacje, ale jakby co to w trybie offline te¿ da siê u¿ywaæ skryptu T3CH Upgrader.

Zawansowane tryby pracy i instalacja automatyczna;
Skrypt mo¿e pracowaæ w trzech trybach:
# SILENT = ca³a instalacja w tle,
# NOTIFY = proste informowanie o dostêpnej wersji,
# NORMAL = normalna wspó³praca z u¿ytkownikiem, pyta siê prawie o wszystko,

Tak jest mo¿liwe, aby skrypt instalowa³ nowe wersje bez ¿adnego pytania nas o zgodê - tzn. bez przesady na koñcu zapyta siê czy ma wykonaæ restart. S± dwie opcje takiej zaawansowanej pracy i obie wymagaj± dodatkowej edycji plików np. przy u¿yciu notepada:

1) po przekopiowaniu do³±czonego autoexec.py do Q:\scripts\
edycja pliku Q:\scripts\autoexec.py
wymieniamy argument NOTIFY na SILENT - skrypt zamiast nas powiadamiaæ o dostêpnej nowej wersji to j± instaluje na starcie konsoli
------------------------------------------------------------------------------------------------------
xbmc.executebuiltin("XBMC.RunScript(Q:\\scripts\\T3CH Upgrader\\default.py, SILENT)")
------------------------------------------------------------------------------------------------------

2) po dodaniu skryptu do ulubionych
edycja pliku \UserData\favourites.xml dodajemy argument SILENT i mamy mo¿liwo¶æ odpalenia trybu w tle wtedy, gdy chcemy.
------------------------------------------------------------------------------------------------------
<favourite name="T3CH Upgrader" thumb="c:\xbmc\userdata\Thumbnails\Programs\e4649b7c.tbn">
RunScript(Q:\scripts\T3CH Upgrader\default.py, SILENT)</favourite>
------------------------------------------------------------------------------------------------------

Znane problemy:
---------------
*czasami* wypakowane archiwum nie zawiera wszystkich folderów lub plików - skrypt wtedy nie kontynuuje instalacji. Najlepszym lekarstwem na to jest restart konsoli i rozpoczêcie od nowa. Problem jest znany, ale co najwa¿niejsze nic siê nie dzieje z twoj± aktualnie u¿ywan± wersj±.
Jakiekolwiek inne problemy, zapraszam na forum http://www.xboxmediacenter.com/forum/

Skrypt napisany przez BigBellyBilly
bigbellybilly AT gmail DOT com
je¿eli masz jakie¶ pytania po polsku, zapraszam
smuto.promyk AT gmail DOT com
=======================================================================================================
Oryginalny plik readme.txt
T3CH Upgrader - Script to download, install and migrate to latest T3CH builds.

SETUP:
 Install to \scripts\T3CH Upgrader (keep sub folder structure intact)


USAGE: 
 run default.py

At startup Main Menu will indicate the availability of a new T3CH build.

Pre Installation Settings:
--------------------------

You can setup several aspects of the installation using the Settings Menu:

1) Which drive & location to install to

   eg. E:\apps

   Will then result in build being unpacked to;
   eg.  E:\apps\<t3ch_build_name>\XBMC

2) The location of your xbox shortcut that boots to the XBMC as a dashboard, and the name of the shortcut that your mod chip boot too
   It is this location that a new shortcut will be wrutten too inorder to boot to the newly installed T3CH build XBMC.
   It uses the TEAM XBMC Shortcut.xbe  and associated .cfg inorder to achieve this.


   Drive: eg. C:

   DashName:  eg. xbmc
   You can also use a subfolder in the dashname;
   
   eg. dashboard\xbmc

3) Maintain Copies;  
   This is a list of Folders and Files that you want to the post installation to be forced to COPY to new build.

4) Maintain Deletes;  
   This is a list of Folders and Files that you want to the post installation to be forced to DELETE from new build.


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
If you ftp a T3CH build archive (RAR or ZIP) to the designed rar download location (eg. E:\apps\) the Main Menu will show an option to install from that.


Switch To Another Build
-----------------------
The Menu option 'Switch to Another T3CH Build' will allow to either;
1) Switch to an existing local T3CH installation.
or
2) Select from the web archive of old T3CH builds, download, then install.

NB. Although the presented lists of available builds should have had the current build date removed, take caution not to overwrite current build!


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