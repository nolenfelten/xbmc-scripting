"""

	urlCookieLib.py - Collection of url based functions.

    ChangeLog:
    23/10/06 - Created.
    27/10/06 - Added urlCookieRequestRetrieve()
    06/07/07 - Modified to prefix with http

"""

import sys,os.path
import xbmc

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__title__ = "urlCookieLib"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '20-12-2007'
xbmc.output("Imported From: " + __scriptname__ + " title: " + __title__ + " Date: " + __date__)

DIR_HOME = sys.modules[ "__main__" ].DIR_HOME
DIR_RESOURCES_LIB = sys.modules[ "__main__" ].DIR_RESOURCES_LIB

sys.path.insert(0, os.path.join( DIR_RESOURCES_LIB, 'ClientCookie.zip'))
import ClientCookie
from bbbLib import debug, messageOK, fileExist, deleteFile, handleException, HTTPErrorCode

#################################################################################################################
# ClientCookie url retrieve
#################################################################################################################
def urlCookieRetrieve(url, file, deleteIfExist=True, ignore404=False):
	debug("> urlCookieRetrieve() url: " + url)
	success = False

	if deleteIfExist and fileExist(file):
		deleteFile(file)

	try:
		if not url.startswith('http://'):
			url = 'http://' + url
		ClientCookie.urlretrieve(url, file)
		success = fileExist(file)
	except IOError, errobj:
		handleIOError(errobj, ignore404)
	except:
		handleException()

	debug("< urlCookieRetrieve() success = " + str(success))
	return success

#################################################################################################################
# ClientCookie url read
#################################################################################################################
def urlCookieRead(url, ignore404=False):
	debug("> urlCookieRead() url: " + url)
	doc = None

	try:
		if not url.startswith('http://'):
			url = 'http://' + url
		fp = ClientCookie.urlopen(url)
		doc = fp.read()
		fp.close()
	except IOError, errobj:
		handleIOError(errobj, ignore404)
	except:
		handleException()

	debug("< urlCookieRead()")
	return doc

#################################################################################################################
# Request & Retrieve . Does a request first which allow subsequent retrieve to use any cookies set
#################################################################################################################
def urlCookieRequestRetrieve(url, file, deleteIfExist=True, ignore404=False):
	debug("> urlCookieRequestRetrieve()")
	success = False

	response = urlCookieRequest(url, ignore404)
	if response:
		success = urlCookieRetrieve(url, file, deleteIfExist, ignore404)

	debug("< urlCookieRequestRetrieve() success=" + str(success))
	return success

#################################################################################################################
# Request & Read. Does a request first which allow subsequent read to use any cookies set
#################################################################################################################
def urlCookieRequestRead(url, ignore404=False):
	debug("> urlCookieRequestRead() url: " + url)
	doc = None

	response = urlCookieRequest(url, ignore404)
	if response:
		try:
			doc = response.read()
		except:
			handleException()

	debug("< urlCookieRequestRead()")
	return doc

#################################################################################################################
# HANDLES ANY COOKIES THAT NEED SETTING
#################################################################################################################
def urlCookieRequest(url, ignore404=False):
	debug("> urlCookieRequest()")
	try:
		if not url.startswith('http://'):
			url = 'http://' + url
		request = ClientCookie.Request(url)
		response = ClientCookie.urlopen(request)
		print "response=", response.info()
	except IOError, errobj:
		handleIOError(errobj, ignore404)
		response = None
	except:
		handleException()
		response = None

	debug("< urlCookieRequest() success")
	return response


#################################################################################################################
def handleIOError(errObj, ignore404=False):
	try:
		code = errobj[1]
	except:
		code = 0
	if not (ignore404 and code == 404):
		title, txt = HTTPErrorCode(code)
		messageOK(title, txt)
