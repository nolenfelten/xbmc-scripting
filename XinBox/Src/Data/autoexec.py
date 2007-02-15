
import xbmc, time
fh = open("Q:\\scripts\\XinBox\\Src\\Data\\auto.dat", "w")
fh.write("Auto")
fh.close()
xbmc.executescript('Q:\\scripts\\XinBox\\default.py')
time.sleep(1)
