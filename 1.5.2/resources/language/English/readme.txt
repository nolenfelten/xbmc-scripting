COMICS

Python XBMC script to view comics from RSS Feeds and/or HTML pages.

 The feeds come from three locations;

  1) Online: tapestrycomics.com using RSS feeds
  2) Online: Comics.com using HTML scrapping
  3) File: MyComics.xml (optional) using combination of RSS feeds and/or HTML scrapping

 SETUP:
 1) Unpack all files to Q:\scripts\Comics
 2) (optional) Add additional RSS feeds and/or HTML pages to MyComics.xml 
       - I've preloaded some as examples.


 USAGE: 
   1) On startup select Comic data source
   2) Select Feed from left list - this will fetch all comics and show a 2nd list of 'Comic Editions'
   3) Select 'Comic Edition' - Will either display an image or a 3rd list of available images for selection.

   To view image fullscreen press X.
     Once in fullscreen view:
         Left Thumb Stick                 = Move image.
         Right Thumb Stick or Triggers    = Zoom image.
         Click Left Thumb Stick           = Reset image.
         X, B or BACK to return from fullscreen view

   Select a different DataSource: Y Button

   View Main Menu: White Buttton

   Exit script:  BACK Button


Notes:
  Script checks for an update on startup follow onscreen instructions if new release found.

Contact me if you wish to provide additional Language translations or new Skin.

Written By BigBellyBilly	 - Thanks to others if I've used code from your scripts.
bigbellybilly AT gmail DOT com - bugs, comments, ideas ...


Additional RSS feeds can be placed into MyComics.xml

EXAMPLES:
The first two feeds are RSS the third is a HTML page containing more page links, which hold images.

<MyComics>
	<feed>
		<title>Extra Life</title>
		<link>http://atheos.de/funnies/extralife.rdf</link>
		<description>By Scott Johnson</description>
	</feed>
	<feed>
		<title>This Modern World</title>
		<link>http://www.jwz.org/cheesegrater/RSS/thismodernworld.rss</link>
		<description>by Tom Tomorrow</description>
	</feed>
	<feed>
		<title>Ctrl+Alt+Del (RSS)</title>
		<link>http://www.cad-comic.com/rss/rss-comics.xml</link>
		<description>Tragically l337</description>
		<reImage><![CDATA[<img src="(/comics/.+?\.jpg)"]]></reImage>
	</feed>
	<feed>
		<title>Ctrl+Alt+Del</title>
		<link>http://www.ctrlaltdel-online.com/index.php?t=archives</link>
		<description>Tragically l337</description>
		<reItem><![CDATA[<option value="([^"\'<>]+)">([^<>]+)<]]></reItem>
		<reImage><![CDATA[<img src="([^"\'<>]+)(?<=(\.gif|\.jpg|\.bmp))" STYLE="border:2px]]></reImage>
	</feed>
</MyComics>


EXTRA NOTES on MyComics.XML:

HTML page link:
	The page can contains either an image or links to other HTML pages that contain images.

	1) If you wish to supply a HTML page that contains links to further HTML pages, which inturn contain the image;
		You need to provide Regular Expressions for BOTH 'reItem' (webpages links) and 'reImage' (comic image)
		EG:	<reItem><![CDATA[<option value="([^"\'<>]+)">([^<>]+)<]]></reItem>
			<reImage><![CDATA[<img src="([^"\'<>]+)(?<=(\.gif|\.jpg|\.bmp))" STYLE="border:2px]]></reImage>

		2) If you wish to supply a HTML page that contains the comic image;
		You need to provide a single Regular expression 'reImage'.
			<reImage><![CDATA[<img src="(/comics/.+?\.jpg)"]]></reImage>

RSS Feeds:
	Minumim requirment is are  <Title> and <link> elements.


Special thanks to smuto for providing some skins.
Thanks to all others who've contributed language translations.
Thanks to those who've help beta test.

Much appreciated!
BBB