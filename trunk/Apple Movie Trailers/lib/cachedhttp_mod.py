"""
    This is a simple script that lets me keep track of which version of 
    cachedhttp I'm using.
"""
CACHEDHTTP_DIR = 'cachedhttp-v13a'

import sys, os
path = os.path.join( os.path.dirname( sys.modules['cachedhttp_mod'].__file__ ), CACHEDHTTP_DIR )
sys.path.insert( 0, path )
from cachedhttp import *
