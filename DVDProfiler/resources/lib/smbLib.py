"""
    smbLib.py - Functions to help with SMB connection and files fetching etc.

    ChangeLog:
    22/10/06 - Created.
    12/01/07 - Updated, smbConnect(), parseSMBPath()
    10/12/07 - Added parseSMBBasePath()
"""

import sys, os.path
import xbmc, xbmcgui
import smb, nmb
import re

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__title__ = "smbLib"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '19-12-2007'
xbmc.output("Imported From: " + __scriptname__ + " title: " + __title__ + " Date: " + __date__)

from bbbLib import debug, messageOK, fileExist, deleteFile, handleException, DEBUG

try: Emulating = xbmcgui.Emulating
except: Emulating = False

dialog = xbmcgui.DialogProgress()

###################################################################################################
def smbConnect(hostIP, smbPath):
	debug("> smbConnect() hostIP="+hostIP+"  smbPath="+smbPath)
	success = False
	remote = None
	remoteInfo = None

	dialog.create("Connecting to SMB","Please wait ...")
	remoteInfo = parseSMBPath(smbPath)
	if DEBUG: print remoteInfo
	if not remoteInfo:
		messageOK("SMB Parse Error","Invalid SMB path:",smbPath)
	else:
		domain,user,password,pcname,service,dirPath,fileName = remoteInfo
		try:
			remote = smb.SMB(pcname, hostIP)
			debug("SMB connection established")
		except:
			messageOK("SMB Connection Failed", "Check PCName & Share are correct.", "PCName: "+pcname, "IP: "+hostIP)
		else:
			useLogin = remote.is_login_required()
			debug("is_login_required = " + str(useLogin))
			if useLogin:
				if not user or not password:
					messageOK("SMB Login Failed","User & Password required.")
				else:
					try:
						remote.login(user, password, domain)
					except smb.SessionError, ex:
						handleExceptionSMB(ex,"SMB Login")
					except:
						handleException("SMB Login Failed","UnHandled Exception")
					else:
						debug("SMB login OK")
						success = True
			else:
				success = True

	if not success:
		remote = None
		remoteInfo = None
	dialog.close()
	debug("< smbConnect() success="+str(success))
	return remote, remoteInfo

###################################################################################################
def getSMBFileSize(remote, remoteInfo, remoteFile):
    debug("> getSMBFileSize() remoteFile: " + remoteFile)
    fileSize = -1
    connected = False
    if not remoteFile:
        messageOK("SMB Setup Incomplete","Remote filename is missing.")
    elif not remote or not remoteInfo:
        messageOK("SMB Fetch Error","No remote connection.")
    else:
        if DEBUG: print remoteInfo
        domain,user,password,pcname,service,dirPath,filename = remoteInfo
        remotePath = "%s%s" % (dirPath,remoteFile)
        try:
            fileSize = remote.list_path(service, remotePath)[0].get_filesize()
        except:
            debug("remote file not found")

    debug("< getSMBFileSize() fileSize: " + str(fileSize))
    return fileSize


###################################################################################################
def smbFetchFile(smbPath, localPath, remote=None, hostIP='', silent=True):
	debug("> smbFetchFile()\nsmbPath="+smbPath+"\nlocalPath="+localPath)
	success = False

	smbPath = "smb://" + smbPath.replace('smb://','').replace('//','/').replace('\\','/')
	debug( "new smbPath=" + smbPath )

	# if no remote connection supplied, establish one now
	if not remote:
		remote, remoteInfo = smbConnect(hostIP, smbPath)

	if not remote:
		messageOK("SMB Copy Error","No remote connection.")
	else:
		remoteInfo = parseSMBPath(smbPath)
		if DEBUG: print remoteInfo
		if not remoteInfo:
			messageOK("SMB Setup Incomplete","Invalid SMB path:",smbPath)
		else:
			domain,user,password,pcname,service,dirPath,fileName = remoteInfo
			remotePath = "%s%s" % (dirPath, fileName)
			debug("remotePath="+remotePath)
			if not silent:
				dialog.create("SMB Fetch File",remotePath, localPath)

			try:
				f = open(localPath, "wb")
				remote.retr_file( service, remotePath, f.write)
				f.close()
			except smb.SessionError, ex:
				if not (ex[1] == 1 and ex[2] == 2):			# file not found
					handleExceptionSMB(ex, "SMB Fetch Error")
				else:
					debug("Remote file not found")
			except:
				messageOK("smbFetchFile()",remotePath, localPath)
				handleException()
			else:
				success = fileExist(localPath)

			if not success:
				try:
					f.close()
				except: pass
				deleteFile(localPath)

			if not silent:
				dialog.close()

	debug("< smbFetchFile() success="+str(success))
	return success

###################################################################################################
def smbSendFile(remote, share, localFile, remoteFile, silent=False):
	debug("> smbSendFile()\remoteFile="+remoteFile+"\localFile="+localFile)
	success = False

	if not remote:
		messageOK("SMB Send Error","No remote connection.  Unable to send file.")
	else:
		if not silent:
			dialog.create("SMB Send File","From: " + localFile,"To: " + remoteFile)

		try:
			debug("opening local file")
			f = open(localFile, "rb")
			debug("sending file to share")
			remote.stor_file(share, remoteFile, f.read)
			f.close()
			success = True
		except smb.SessionError, ex:
			handleExceptionSMB(ex, "SMB Send Error")
		except:
			messageOK("SMB Fetch Unknown Exception","From: " + remotePath, "To: " + localPath)
			handleException()

		if not silent:
			dialog.close()

	debug("< smbSendFile() success="+str(success))
	return success

#################################################################################################################
def parseSMBPath(path):

	# smb://domain;user:pass@pcname/share/folder/filename
	m = re.match('^smb://(\w+);(\w+):([^@]+)@([^/]+)/([^/]+)(/?.*?)([^/]*)$', path)
	if m:
		xbmc.output("matches smb://domain;user:pass@pcname/share/folder/filename")
		return m.groups()

	# smb://user:pass@pcname/share/folder/filename
	m = re.match('^smb://(\w+):([^@]+)@([^/]+)/([^/]+)(/?.*?)([^/]*)$', path)
	if m:
		xbmc.output("matches smb://user:pass@pcname/share/folder/filename")
		return '', m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)

	# smb://user:pass@pcname/share/folder/
	m = re.match('^smb://(\w+):([^@]+)@([^/]+)/([^/]+)(/?.*?)$', path)
	if m:
		xbmc.output("matches smb://user:pass@pcname/share/folder/")
		return '', m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), ''

	# smb://pcname/share/folder/filename
	m = re.match('^smb://([^/]+)/([^/]+)(/?.*?)([^/]*)$', path)
	if m:
		xbmc.output("matches smb://pcname/share/folder/filename")
		return '', '', '', m.group(1), m.group(2), m.group(3), m.group(4)

	# smb://pcname/share/folder/
	m = re.match('^smb://([^/]+)/([^/]+)(/?.*?)$', path)
	if m:
		xbmc.output("matches smb://pcname/share/folder/")
		return '', '', '', m.group(1), m.group(2), m.group(3), ''

	xbmc.output("no smb path matches")
	return None

#################################################################################################################
def parseSMBBasePath(path):
	# smb://user:pass@pcname
	m = re.match('^smb://(\w+):([^@]+)@([^/]+)$', path)
	if m:
		xbmc.output("matches smb://user:pass@pcname")
		return ('', m.group(1), m.group(2), m.group(3), '', '', '')

	# smb://pcname
	m = re.match('^smb://([^/]+)$', path)
	if m:
		xbmc.output("matches smb://pcname")
		return ('', '', '', m.group(1), '', '', '')

	return None

	
#################################################################################################################
def getIPFromName(pcname):
	debug("> getIPFromName() pcname=" + pcname)
	ip = ''
	dialog.create("SMB Discover IP","Using PCName: " + pcname, "Please wait ...")
	try:
		ip = nmb.NetBIOS().gethostbyname(pcname)[0].get_ip()
		if not xbmcgui.Dialog().yesno("Correct IP for PC Name: " + pcname + ' ?', \
								"IP: " + ip,"YES to use this IP.\nNO to enter manually."):
			ip = ''
	except:
		messageOK("SMB Discover IP Failed", \
				"Unable to discover IP from PCName: "+pcname,"Please enter IP manually.")
		ip=''
	dialog.close()

	debug("< getIPFromName() ip="+ip)
	return ip

#################################################################################################################
def isIP(host):
	result = re.match('^\d+\.\d+\.\d+\.\d+$', host)
	debug("isIP: " + host + " = " + str(result))
	return result

#################################################################################################################
def getSMBPathIP(smbPath, isSMBBasePathOnly=False):
	debug("> getSMBPathIP() " + smbPath)
	success = False
	ip = ""
	if smbPath.endswith('/'): smbPath = smbPath[:-1]
	if not isSMBBasePathOnly:
		remoteInfo = parseSMBPath(smbPath)
	else:
		remoteInfo = parseSMBBasePath(smbPath)
	if DEBUG: print remoteInfo

	if remoteInfo and smbPath:
#		if smbPath[-1] not in ["\\","/"]: smbPath += '/'
		
		domain,user,password,pcname,share,dirPath,fileName = remoteInfo
		if not isIP(pcname):											# is a PCNAME
			ip = getIPFromName(pcname)								# discover IP
		else:
			messageOK("Invalid SMB Path","Use PCNAME not IP in path.","EG: OFFICE")
	else:
		messageOK("Invalid SMB Path","Invalid path format")
		smbPath = ""

	debug("< getSMBPathIP()")
	return smbPath, ip

###############################################################################################################
# fetch a file from SMB if the remote file is newer than the local file
###############################################################################################################
def isNewSMBFile(smbPath, localPath, remote=None, hostIP='', silent=False):
	debug("> isNewSMBFile()\nsmbPath="+smbPath+"\nlocalPath="+localPath)
	remoteFileSecs = 0
	localFileSecs = 0

	smbPath = "smb://" + smbPath.replace('smb://','').replace('//','/').replace('\\','/')
	debug( "new smbPath=" + smbPath )

	# if no remote connection supplied, establish one now
	if not remote:
		remote, remoteInfo = smbConnect(hostIP, smbPath)

	if not remote:
		messageOK("SMB File Update Failed","No remote connection.")
	else:
		remoteInfo = parseSMBPath(smbPath)
		if DEBUG: print remoteInfo
		if not remoteInfo:
			messageOK("SMB Setup Incomplete","Invalid SMB path:",smbPath)
		else:
			domain,user,password,pcname,service,dirPath,fileName = remoteInfo
			remotePath = "%s%s" % (dirPath,fileName)
			debug("remotePath="+remotePath)
			if not silent:
				dialog.create("Checking for updated file ...", remotePath)

			try:
				localFileSecs = os.path.getmtime(localPath)
			except: pass

			# list files on SMB of remote filename, check modified timestamp
			try:
				remoteFileSecs = remote.list_path(service, remotePath)[0].get_mtime_epoch()
			except:
				debug("remote file not found")

			if not silent:
				dialog.close()

	debug("local timestamp: " + str(localFileSecs) + " Remote timestamp: " + str(remoteFileSecs))
	# check secs since epoch of files.
	newFileFound = (remoteFileSecs > localFileSecs) # greater secs means newer
	debug("< isNewSMBFile() newFileFound: "+str(newFileFound))
	return newFileFound

###############################################################################################################
def handleExceptionSMB(ex, title):
	errCodeStr = "Err Codes: " + str(ex[1]) + ", " + str(ex[2])
	if ex[1] == 1 and ex[2] == 2:			# file not found
		messageOK(title,errCodeStr,"Remote file not found.")
	elif ex[1] == 1 and ex[2] == 3:
		messageOK(title,errCodeStr,"Directory invalid","Please correct SMB Path")
	elif ex[1] == 1 and ex[2] == 5:			# Access denied
		messageOK(title,errCodeStr,"Remote file Access Denied.","Check remote Permissions/User/Password are correct.")
	elif ex[1] == 1 and ex[2] == 15:
		messageOK(title,errCodeStr,"Invalid drive specified.","Please correct SMB Path.")
	elif ex[1] == 1 and ex[2] == 32:
		messageOK(title,errCodeStr,"Share mode can't be granted.","Please check remote share.")
	elif ex[1] == 1 and ex[2] == 67:
		messageOK(title,errCodeStr,"Invalid Share Name.","Please correct SMB Path.")
	else:									# trap other SMB err
		messageOK(title,errCodeStr, "UnTrapped error codes, Check smb.h for definition.")
