"""
 SFV checksum checker.
 Reads a SFV containing one or more crc
 Compare an entry from SFV with an archive crc
""" 

import sys,os.path
import zlib, md5, struct, binascii, os
import traceback

__title__ = 'SFVCheck'
__date__ = '19-05-2008'

class SFVCheck:
	""" Contruct with SFV filename or SFV doc, then check(entry name, rar filename)"""
	def __init__(self, sfvFilename="", sfvDoc=""):

		# load in all files from sfv file
		self.files= {}
		if sfvFilename:
			self.parseSFVFiles(sfvFilename)
		elif sfvDoc:
			self.parseSFVDoc(sfvDoc)

	def check(self, entry, archiveFilename):
		"""  Given sfv entry name , compare crc with archive """
		ok = None		# entry not found
		fcrc = 0
		crc = self.getCRC(entry)
		if crc:
			ok, fcrc = compareOne(archiveFilename, crc)
		print "check() %s crc=%s fcrc=%s" % (ok, crc, fcrc)
		return ok

	def getCRC(self, entry):
		""" Get crc for given entry """
		try:
			crc = self.files[entry]
		except:
			crc = 0
		print "getCRC() %s crc= %s" % (entry, crc)
		return crc

	def parseSFVFiles(self, filename):
		""" Get dict of entry = crc for all in sfv filename """
		self.files = {}
		for line in file(filename).readlines():
			if line and line[0] != ';':
				try:
					self.files[line[:-9].strip()] = line[-9:].strip()
				except:
					traceback.print_exc()
		print "parseSfvFiles() ", self.files
		return self.files

	def parseSFVDoc(self, doc):
		""" Get dict of entry = crc for all in sfv doc """
		self.files = {}
		for line in doc.split('\n'):
			if line and line[0] != ';':
				try:
					self.files[line[:-9].strip()] = line[-9:].strip()
				except:
					traceback.print_exc()
		print "parseSFVDoc() ", self.files
		return self.files

class CRC32:
    def __init__(self, s=''):
        self.value = zlib.crc32(s)
        
    def update(self, s):
        self.value = zlib.crc32(s, self.value)
        
    def digest(self):
        return struct.pack('>I',self.value)


class CheckSum:
	def __init__(self, archiveFilename):
		self.filename = archiveFilename

	def _getCheckSum(self, filename, checksumtype):
		print "_getCheckSum() %s " % filename
		try:
			f = file(filename, 'rb')
			while True:
				x = f.read(65536)
				if not x:
					f.close()
					return checksumtype.digest()
				checksumtype.update(x)
		except (IOError, OSError):
			print "No such file"
			return "No such file"

	def getfilemd5(self):
		return binascii.hexlify(self._getCheckSum(self.filename, md5.new()))

	def getfilecrc(self):
		return binascii.hexlify(self._getCheckSum(self.filename, CRC32()))


def compareOne(archiveFilename, crc, filetype='sfv'):
    checksum = CheckSum(archiveFilename)
    if filetype == 'sfv':
        filecrc = checksum.getfilecrc()
    else:
        filecrc = checksum.getfilemd5()

    print "compareOne() filecrc=%s" % filecrc
    if filecrc.lower() == crc.lower():
        return True, filecrc
    elif filecrc == "4e6f20737563682066696c65": #"No such file" after it has been hexlifyed from Checksums
        return False, None
    return False, filecrc
    

#if __name__ == "__main__":
#    app = SFVCheck("E:\\apps\\XBMC-SVN_2008-01-27_rev11426-T3CH.sfv")
#    print app.check("XBMC-SVN_2008-01-27_rev11426-T3CH.rar", "E:\\apps\\XBMC-SVN_2008-01-27_rev11426-T3CH.rar", )
