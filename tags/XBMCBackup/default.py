##XBMCBackup by Stanley87##

import xbmc, xbmcgui
from os.path import getsize, join, exists
from os import stat, mkdir, rmdir
import os
import shutil


CopiedFiles = 0
CopiedSize = 0
CreatedDirs = 0
DeletedDirs = 0
DeletedFiles = 0
DeletedSize = 0

def getsizelabel (size):
    if size >= 1024:
        size = size/1024.0
        sizeext = "KB"
        if size >= 1024:
            size = size/1024.0
            sizeext = "MB"
    else:sizeext = "bytes"
    return "%.1f %s" % (size,  sizeext)


print "Starting"
dialog = xbmcgui.Dialog()
fn = dialog.browse(0, 'Browse for Original/XBMC Dir', 'files', '', False, False, '')
InputDir = fn
fn = dialog.browse(0, 'Browse for Backup Dir', 'files', '', False, False, '')
OutputDir = fn
for root, dirs, files in os.walk(OutputDir, topdown=False):
    newroot = InputDir + root.replace(OutputDir,"")
    for name in dirs:
        if not exists(join(newroot, name)):
            rmdir(join(root, name))
            DeletedDirs += 1
    for name in files:
        newpath = join(root, name)
        origpath = join(newroot,name)
        if not exists (origpath):
            DeletedSize += stat(newpath).st_size
            os.remove(newpath)
            DeletedFiles += 1

print "Total Dirs Deleted = " + str(DeletedDirs)
print "Total files Deleted = " + str(DeletedFiles)
print "Total Size Deleted = " + getsizelabel(DeletedSize)
           
for root, dirs, files in os.walk(InputDir, topdown=True):
    newroot = OutputDir + root.replace(InputDir,"")
    for name in dirs:
        if not exists(join(newroot, name)):
            CreatedDirs += 1
            mkdir(join(newroot, name))
    for name in files:
        origpath = join(root, name)
        newpath = join(newroot,name)
        if exists (newpath):
            origstat = stat(origpath)
            newstat = stat(newpath)
            if origstat.st_size  != newstat.st_size or int(origstat.st_mtime)  != int(newstat.st_mtime) :
                shutil.copy2(origpath,newpath)
                CopiedFiles += 1
                CopiedSize += newstat.st_size
        else:
            shutil.copy2(origpath,newpath)
            CopiedFiles += 1
            CopiedSize += stat(newpath).st_size
            
print "Total Dirs Created = " + str(CreatedDirs)
print "Total files copied = " + str(CopiedFiles)
print "Total Size copied = " + getsizelabel(CopiedSize)
print "Finished"
