import os, xbmc, time
origver =
origpath = 
newpath =

os.rename(origpath, origpath + "(OLD)_v" + origver)
os.rename(newpath,origpath)
try:
    sys.path.append( os.path.join( origpath, 'src', 'lib' ) )
    from XinBox_Util import UpdateSettings
    UpdateSettings().loadsettings()
    time.sleep(1)
except:pass
xbmc.executescript(origpath + "\\default.py")
