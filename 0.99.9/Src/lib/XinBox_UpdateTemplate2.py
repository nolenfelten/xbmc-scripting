import os, xbmc
origver =
origpath = 
newpath =

os.rename(origpath, origpath + "(OLD)_v" + origver)
os.rename(newpath,origpath)
try:
    sys.path.append( os.path.join( origpath, 'src', 'lib' ) )
    from XinBox_Util import UpdateSettings
    UpdateSettings().loadsettings()
except:pass
xbmc.executescript(origpath + "\\default.py")
