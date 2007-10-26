import os, xbmc, time
origver =
origpath = 
newpath =

os.rename(origpath, origpath + "(OLD)_v" + origver)
os.rename(newpath,origpath)
xbmc.executescript(origpath + "\\default.py")
