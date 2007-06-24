"""
This script will create a playlist by recursively searching MUSIC_PATH and adding songs.
"""
import os
import xbmc

# add all music paths here, no subdirectories needed
MUSIC_PATH = ( "E:\\Music", "F:\\Music", )
# add all music extensions wanted in lowercase
MUSIC_EXT = ".nsv|.m4a|.flac|.aac|.strm|.pls|.rm|.mpa|.wav|.wma|.ogg|.mp3|.mp2|.m3u|.mod|.amf|.669|.dmf|.dsm|.far|.gdm|.imf|.it|.m15|.med|.okt|.s3m|.stm|.sfx|.ult|.uni|.xm|.sid|.ac3|.dts|.cue|.aif|.aiff|.wpl|.ape|.mac|.mpc|.mp+|.mpp|.shn|.zip|.rar|.wv|.nsf|.spc|.gym|.adplug|.adx|.dsp|.adp|.ymf|.ast|.afc|.hps|.xsp|.xwav|.waa|.wvs|.wam|.gcm|.idsp|.mpdsp|.mss|.spt|.rsd"
# set to True to shuffle the playlist
SHUFFLE = True

def create_playlist( base_path=MUSIC_PATH, shuffle=SHUFFLE ):
    playlist = xbmc.PlayList( 0 )
    playlist.clear()
    for path in base_path:
        os.path.walk( path, add_music, playlist )
    if ( shuffle ): playlist.shuffle()
    return playlist

def add_music( playlist, path, files ):    
    for file in files:
        ext = os.path.splitext( file )[ 1 ].lower()
        if ( ext and ext in MUSIC_EXT ):
            playlist.add( os.path.join( path, file ) )

if ( __name__ == "__main__" ):
    playlist = create_playlist()
    xbmc.Player().play( playlist )
