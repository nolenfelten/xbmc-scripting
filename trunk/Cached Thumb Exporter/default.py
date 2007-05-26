import os
import shutil
from pysqlite2 import dbapi2 as sqlite
import xbmcgui
import traceback

def get_browse_dialog( default="", heading="", type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value

def copy_thumbs( paths, base_cache_path, save_as_folder, subfolder ):
    global dialog
    for count, path in enumerate( paths ):
        if ( dialog.iscanceled() ): break
        try:
            percent = int( ( count +1 ) * ( float( 100 ) / len( paths ) ) )
            thumb = xbmc.getCacheThumbName( path[ 0 ].replace( "\r\n", "" ).replace( "\r", "" ).replace( "\n", "" ) )
            if ( subfolder ):
                cached_thumb = os.path.join( base_cache_path, thumb[ 0 ], thumb )
            else:
                cached_thumb = os.path.join( base_cache_path, thumb )
            if ( not save_as_folder ):
                finished_thumb = "%s.tbn" % os.path.join( thumb_folder, path[ 1 ].replace( "\r\n", "" ).replace( "\r", "" ).replace( "\n", "" ) )
            else:
                finished_thumb = os.path.join( thumb_folder, path[ 1 ].replace( "\r\n", "" ).replace( "\r", "" ).replace( "\n", "" ), "folder.jpg" )
            dialog.update( percent, "Current file: %s" % os.path.split( cached_thumb )[ 1 ], "To: %s" % finished_thumb )
            if ( not os.path.isdir( os.path.split( finished_thumb )[ 0 ] ) ):
                #print "FOLDER:", os.path.split( finished_thumb )[ 0 ]
                os.makedirs( os.path.split( finished_thumb )[ 0 ] )
            #print cached_thumb
            #print finished_thumb.encode("ascii","ignore")
            #print path[ 0 ].encode("ascii","ignore")
            shutil.copy( cached_thumb, finished_thumb )
            #print "--------------------------------------"#"***Succeeded***"
            #xbmc.sleep(500)
        except:
            #print "***failed***"
            traceback.print_exc()

def make_fatx_compatible( name, save_as_folder ):
    if ( len( name ) > ( 4 * save_as_folder + 38 ) ):
        name = name[ : ( 4 * save_as_folder + 38 ) ]
    name = name.replace( ",", "_" ).replace( "*", "_" ).replace( "=", "_" ).replace( "\\", "_" ).replace( "|", "_" )
    name = name.replace( "<", "_" ).replace( ">", "_" ).replace( "?", "_" ).replace( ";", "_" ).replace( ":", "_" )
    name = name.replace( '"', "_" ).replace( "+", "_" ).replace( "/", "_" )
    if ( os.path.supports_unicode_filenames ):
        name = unicode( name, "utf-8", "ignore" )
    return name

def read_path_file( file_path, save_as_folder ):
    global dialog
    dialog.update( -1, "Selecting records.." )
    try:
        paths = ()
        base_cache_path = ""
        if ( "videos" in file_path.lower() ):
            sql = "SELECT path.strpath, files.strfilename FROM files, path WHERE files.idpath=path.idpath ORDER BY files.strfilename;"
            base_cache_path = "q:\\UserData\\Thumbnails\\Video"
        elif ( "music" in file_path.lower() ):
            #        "select distinct a.strpath, c.stralbum, d.strartist from path a,song b,album c,artist d where a.idpath = b.idpath and b.idalbum = c.idalbum and c.idartist = d.idartist"
            sql = "SELECT DISTINCT path.strpath, album.stralbum, artist.strartist FROM path, album, artist, song WHERE artist.idartist=album.idartist AND album.idalbum=song.idalbum AND song.idpath=path.idpath ORDER BY artist.strartist;"
            base_cache_path = "q:\\UserData\\Thumbnails\\Music"
        else:
            raise
        if ( file_path.endswith( ".txt" ) ):
            file_object = open( os.path.join( file_path ), "r" )
            paths = file_object.readlines()
            file_object.close()
        else:
            db = sqlite.connect( file_path )
            cursor = db.cursor()
            cursor.execute( sql )
            tmp_paths = cursor.fetchall()
            db.close()
            if ( tmp_paths ):
                if ( "videos" in file_path.lower() ):
                    for path in tmp_paths:
                        paths += ( ( os.path.join( path[ 0 ], path[ 1 ] ), make_fatx_compatible( path[ 1 ], save_as_folder ), ), )
                elif ( "music" in file_path.lower() ):
                    for path in tmp_paths:
                        try:
                            artist = u"unknown"#unicode( "unknown", "utf-8" )
                            album = u"unknown"#unicode( "unknown", "utf-8" )
                            if ( path[ 1 ] and path[ 2 ] ):
                                album = path[ 1 ]
                                artist = path[ 2 ]
                            elif ( path[ 1 ] ):
                                album = path[ 1 ]
                            elif ( path[ 2 ] ):
                                album = path[ 2 ]
                            paths += ( ( album + artist, make_fatx_compatible( artist, True ) + u"\\" + make_fatx_compatible( album, save_as_folder ), ), )
                        except: 
                            traceback.print_exc()
                            pass
    except:
        traceback.print_exc()

    return paths, base_cache_path


if ( __name__ == "__main__" ):
    file_path = get_browse_dialog( "q:\\UserData\\Database", "database or text file", 1, "files", ".db|.txt" )
    if ( file_path.endswith( ".txt" ) or file_path.endswith( ".db" ) ):
        thumb_folder = get_browse_dialog( "f:\\", "export folder", 3, "files" )
        save_as_folder = xbmcgui.Dialog().yesno( "Save method", "Save the thumbs as folder.jpg?", "", "", "name.tbn", "folder.jpg" )
        dialog = xbmcgui.DialogProgress()
        dialog.create( "Exporting cached thumbs" )
        paths, base_cache_path = read_path_file( file_path, save_as_folder )
        if ( paths ):
            copy_thumbs( paths, base_cache_path, save_as_folder, "music" in file_path.lower() )
        dialog.close()