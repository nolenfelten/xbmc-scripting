import xbmc, xbmcgui, sys, os
origpath =
newpath =

for root, dirs, files in os.walk(origpath, topdown=False):
    for name in files:
        os.remove(os.path.join(root, name))
    for name in dirs:
        os.rmdir(os.path.join(root, name))
os.rmdir(origpath)
os.rename(newpath,origpath)
try:
    sys.path.append( os.path.join( origpath, 'src', 'lib' ) )
    from XinBox_Util import UpdateSettings
    UpdateSettings().loadsettings()
except:pass
xbmc.executescript(origpath + "\\default.py")
