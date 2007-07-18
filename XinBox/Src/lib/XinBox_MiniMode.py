import time, sys

class Minimode:
    def init(self):
        print "accountname = " + str(sys.argv[1:][0])

Minimode().init()
