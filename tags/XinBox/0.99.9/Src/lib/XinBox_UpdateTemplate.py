import xbmc, xbmcgui, sys, os
origpath =
newpath =

class UpdateSettings:
    def loadsettings(self):
        dialog = xbmcgui.DialogProgress()
        dialog.create("Importing New Settings","Please Wait...")
        self.settings = Settings("XinBox_Settings.xml","XinBox","")
        self.editallaccounts()
        self.settings.saveXMLfromArray()
        time.sleep(1)
        dialog.close()

    def editallaccounts(self):
        for item in self.settings.getSetting("Accounts")[1]:
                self.accountSettings = self.settings.getSettingInListbyname("Accounts",item[0])
                if self.accountSettings.getSetting("Mini Mode SFX",None) == None:
                    self.accountSettings.addSetting("Mini Mode SFX","True","boolean")
                if self.accountSettings.getSetting("XinBox Promote",None) == None:
                    self.accountSettings.addSetting("XinBox Promote","True","boolean")
                for item2 in self.accountSettings.getSetting("Inboxes")[1]:
                    self.inboxSettings = self.accountSettings.getSettingInListbyname("Inboxes",item2[0])
                    if self.inboxSettings.getSetting("SMTP Auth",None) == None:
                        self.inboxSettings.addSetting("SMTP Auth","True","boolean")


for root, dirs, files in os.walk(origpath, topdown=False):
    for name in files:
        os.remove(os.path.join(root, name))
    for name in dirs:
        os.rmdir(os.path.join(root, name))
os.rmdir(origpath)
os.rename(newpath,origpath)
sys.path.append( os.path.join( origpath, 'src', 'lib' ) )
from XinBox_Settings import Settings
UpdateSettings().loadsettings()
xbmc.executescript(origpath + "\\default.py")
