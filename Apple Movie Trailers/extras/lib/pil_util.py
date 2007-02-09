import sys, os
sys.path.append( os.path.join( os.path.dirname( sys.modules['pil_util'].__file__ ), '_PIL.zip' ) )
from PIL import Image, ImageEnhance
    
def makeThumbnails( poster ):
    try:
        size = ( 26, 38 )
        thumbnail = '%s.png' % ( os.path.splitext( poster )[0], )
        watched_thumbnail = '%s-w.png' % ( os.path.splitext( poster )[0], )
        im = Image.open( poster )
        im.thumbnail(size, Image.ANTIALIAS)
        im = im.convert('RGBA')
        im.save(thumbnail, 'PNG')
        alpha = im.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.2)
        im.putalpha(alpha)
        im.save(watched_thumbnail, 'PNG')
        return True
    except:
        return False
