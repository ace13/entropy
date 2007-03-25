#!/usr/bin/python
'''
    # DESCRIPTION:
    # generic tools for all the handlers applications

    Copyright (C) 2007 Fabio Erculiani

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''

def initializePortageTree():
    portage.settings.unlock()
    portage.settings['PORTDIR'] = etpConst['portagetreedir']
    portage.settings['PORTDIR_OVERLAY'] = etpConst['overlays']
    portage.settings.lock()
    portage.portdb.__init__(etpConst['portagetreedir'])

# Fix for wrong cache entries - DO NOT REMOVE
import os
from entropyConstants import *
os.environ['PORTDIR'] = etpConst['portagetreedir']
os.environ['PORTDIR_OVERLAY'] = etpConst['overlays']
import portage
import portage_const
from portage_dep import isvalidatom, isspecific, isjustname, dep_getkey, dep_getcpv
from entropyConstants import *
initializePortageTree()

# colours support
import output
from output import bold, colorize, green, darkred, red, yellow, blue, darkblue, nocolor
import re
import sys
import random
import commands

def isRoot():
    import getpass
    if (getpass.getuser() == "root"):
        return True
    return False

def getPortageEnv(var):
    try:
	rc = portage.config(clone=portage.settings).environ()[var]
	return rc
    except KeyError:
	return None

def getRandomNumber():
    return int(str(random.random())[2:7])

def getThirdPartyMirrors(mirrorname):
    return portage.thirdpartymirrors[mirrorname]

# resolve atoms automagically (best, not current!)
# sys-libs/application --> sys-libs/application-1.2.3-r1
def getBestAtom(atom):
    try:
        rc = portage.portdb.xmatch("bestmatch-visible",str(atom))
        return rc
    except ValueError:
	return "!!conflicts"

# I need a valid complete atom...
def calculateFullAtomsDependencies(atoms, deep = False, extraopts = ""):
    # in order... thanks emerge :-)
    deepOpt = ""
    if (deep):
	deepOpt = "-Du"
    deplist = []
    blocklist = []
    
    try:
	useflags = "USE='"+os.environ['USE']+"' "
    except:
	useflags = ""
    cmd = useflags+cdbRunEmerge+" --pretend --color=n --quiet "+deepOpt+" "+extraopts+" "+atoms
    result = commands.getoutput(cmd).split("\n")
    for line in result:
	if line.startswith("[ebuild"):
	    line = line.split("] ")[1].split(" [")[0].split()[0].strip()
	    deplist.append(line)
	if line.startswith("[blocks"):
	    line = line.split("] ")[1].split()[0].strip()
	    blocklist.append(line)

    # filter garbage
    _deplist = []
    for i in deplist:
	if (i != "") and (i != " "):
	    _deplist.append(i)
    deplist = _deplist
    _blocklist = []
    for i in blocklist:
	if (i != "") and (i != " "):
	    _blocklist.append(i)
    blocklist = _blocklist

    if deplist != []:
        return deplist, blocklist
    else:
	rc = os.system(cmd)
	sys.exit(1)

def calculateAtomUSEFlags(atom):
    try:
	useflags = "USE='"+os.environ['USE']+"' "
    except:
	useflags = ""
    cmd = useflags+cdbRunEmerge+" --pretend --color=n --nodeps --quiet --verbose "+atom
    result = commands.getoutput(cmd).split("\n")
    useparm = ""
    for line in result:
	if line.startswith("[ebuild") and (line.find("USE=") != -1):
	    useparm = line.split('USE="')[len(line.split('USE="'))-1].split('"')[0].strip()
    useparm = useparm.split()
    _useparm = []
    for use in useparm:
	# -cups
	if use.startswith("-") and (not use.endswith("*")):
	    use = darkblue(use)
	# -cups*
	elif use.startswith("-") and (use.endswith("*")):
	    use = yellow(use)
	# use flag not available
	elif use.startswith("("):
	    use = blue(use)
	# cups*
	elif use.endswith("*"):
	    use = green(use)
	else:
	    use = darkred(use)
	_useparm.append(use)
    useparm = string.join(_useparm," ")
    return useparm

# should be only used when a pkgcat/pkgname <-- is not specified (example: db, amarok, AND NOT media-sound/amarok)
def getAtomCategory(atom):
    try:
        rc = portage.portdb.xmatch("match-all",str(atom))[0].split("/")[0]
        return rc
    except:
	return None

# This function compare the version number of two atoms
# This function needs a complete atom, pkgcat (not mandatory) - pkgname - pkgver
# if atom1 < atom2 --> returns a NEGATIVE number
# if atom1 > atom2 --> returns a POSITIVE number
# if atom1 == atom2 --> returns 0
def compareAtoms(atom1,atom2):
    # filter pkgver
    x, atom1 = extractPkgNameVer(atom1)
    x, atom2 = extractPkgNameVer(atom2)
    from portage_versions import vercmp
    return vercmp(atom1,atom2)

def countdown(secs=5,what="Counting..."):
    import time
    if secs:
	print what
        for i in range(secs):
            sys.stdout.write(str(i)+" ")
            sys.stdout.flush()
	    time.sleep(1)

def spinner(rotations, interval, message=''):
	for x in xrange(rotations):
		writechar(message + '|/-\\'[x%4] + '\r')
		time.sleep(interval)
	writechar(' ')
	for i in xrange(len(message)): print ' ',
	writechar('\r')

def writechar(char):
	sys.stdout.write(char); sys.stdout.flush()

def getArchFromChost(chost):
	# when we'll add new archs, we'll have to add a testcase here
	if chost.startswith("x86_64"):
	    resultingArch = "amd64"
	elif chost.split("-")[0].startswith("i") and chost.split("-")[0].endswith("86"):
	    resultingArch = "x86"
	else:
	    resultingArch = "ERROR"
	
	return resultingArch

def translateArchFromUname(string):
    import commands
    rc = commands.getoutput("uname -m").split("\n")[0]
    return translateArch(string,rc)

def translateArch(string,chost):
    if string.find(ETP_ARCH_CONST) != -1:
        # substitute %ARCH%
        resultingArch = getArchFromChost(chost)
	return re.subn(ETP_ARCH_CONST,resultingArch, string)[0]
    else:
	return string

# please always force =pkgcat/pkgname-ver if possible
def getInstalledAtom(atom):
    rc = portage.db['/']['vartree'].dep_match(str(atom))
    if (rc != []):
	if (len(rc) == 1):
	    return rc[0]
	else:
            return rc[len(rc)-1]
    else:
        return None

def getPackageSlot(atom):
    if atom.startswith("="):
	atom = atom[1:]
    rc = portage.db['/']['vartree'].getslot(atom)
    if rc != "":
	return rc
    else:
	return None

# you must provide a complete atom
def collectBinaryFilesForInstalledPackage(atom):
    if atom.startswith("="):
	atom = atom[1:]
    pkgcat = atom.split("/")[0]
    pkgnamever = atom.split("/")[1]
    dbentrypath = "/var/db/pkg/"+pkgcat+"/"+pkgnamever+"/CONTENTS"
    binarylibs = []
    if os.path.isfile(dbentrypath):
	f = open(dbentrypath,"r")
	contents = f.readlines()
	f.close()
	for i in contents:
	    file = i.split()[1]
	    if i.startswith("obj") and (file.find("lib") != -1) and (file.find(".so") != -1) and (not file.endswith(".la")):
		# FIXME: rough way
		binarylibs.append(i.split()[1].split("/")[len(i.split()[1].split("/"))-1])
        return binarylibs
    else:
	return binarylibs

def getEbuildDbPath(atom):
    return portage.db['/']['vartree'].getebuildpath(atom)

def getInstalledAtoms(atom):
    rc = portage.db['/']['vartree'].dep_match(str(atom))
    if (rc != []):
        return rc
    else:
        return None

# YOU MUST PROVIDE A COMPLETE ATOM with a pkgcat !
def unmerge(atom):
    if isjustname(atom) or (not isvalidatom(atom)) or (atom.find("/") == -1):
	return 1
    else:
	pkgcat = atom.split("/")[0]
	pkgnamever = atom.split("/")[1]
	portage.settings.unlock()
	rc = portage.unmerge(pkgcat, pkgnamever, ETP_ROOT_DIR, portage.settings, 1)
	portage.settings.lock()
	return rc

# TO THIS FUNCTION:
# must be provided a valid and complete atom
def extractPkgNameVer(atom):
    package = dep_getcpv(atom)
    package = atom.split("/")[len(atom.split("/"))-1]
    package = package.split("-")
    pkgname = ""
    pkglen = len(package)
    if package[pkglen-1].startswith("r"):
        pkgver = package[pkglen-2]+"-"+package[pkglen-1]
	pkglen -= 2
    else:
	pkgver = package[len(package)-1]
	pkglen -= 1
    for i in range(pkglen):
	if i == pkglen-1:
	    pkgname += package[i]
	else:
	    pkgname += package[i]+"-"
    return pkgname,pkgver

def emerge(atom, options, outfile = None, redirect = "&>", simulate = False):
    if (simulate):
	return 0,"" # simulation enabled
    if (outfile is None) and (redirect == "&>"):
	outfile = etpConst['packagestmpdir']+"/.emerge-"+str(getRandomNumber())
    elif (redirect is None):
	outfile = ""
	redirect = ""
    if os.path.isfile(outfile):
	try:
	    os.remove(outfile)
	except:
	    spawnCommand("rm -rf "+outfile)
    
    # elog configuration
    elogopts = dbPORTAGE_ELOG_OPTS+" "
    # clean elog shit
    elogfile = atom.split("=")[len(atom.split("="))-1]
    elogfile = elogfile.split(">")[len(atom.split(">"))-1]
    elogfile = elogfile.split("<")[len(atom.split("<"))-1]
    elogfile = elogfile.split("/")[len(atom.split("/"))-1]
    elogfile = etpConst['logdir']+"/elog/*"+elogfile+"*"
    os.system("rm -rf "+elogfile)
    
    rc = spawnCommand(elogopts+cdbRunEmerge+" "+options+" "+atom, redirect+outfile)
    return rc, outfile

def parseElogFile(atom):
    if atom.startswith("="):
	atom = atom[1:]
    if atom.startswith(">"):
	atom = atom[1:]
    if atom.startswith("<"):
	atom = atom[1:]
    if (atom.find("/") != -1):
	pkgcat = atom.split("/")[0]
	pkgnamever = atom.split("/")[1]+"*.log"
    else:
	pkgcat = "*"
	pkgnamever = atom+"*.log"
    elogfile = pkgcat+":"+pkgnamever
    reallogfile = commands.getoutput("find "+etpConst['logdir']+"/elog/ -name '"+elogfile+"'").split("\n")[0].strip()
    if os.path.isfile(reallogfile):
	# FIXME: improve this part
	logline = False
	logoutput = []
	f = open(reallogfile,"r")
	reallog = f.readlines()
	f.close()
	for line in reallog:
	    if line.startswith("INFO: postinst") or line.startswith("LOG: postinst"):
		logline = True
		continue
		# disable all the others
	    elif line.startswith("INFO:") or line.startswith("LOG:"):
		logline = False
		continue
	    if (logline) and (line.strip() != ""):
		# trap !
		logoutput.append(line.strip())
	return logoutput
    else:
	return []

def compareLibraryLists(pkgBinaryFiles,newPkgBinaryFiles):
    brokenBinariesList = []
    # check if there has been a API breakage
    if pkgBinaryFiles != newPkgBinaryFiles:
	_pkgBinaryFiles = []
	_newPkgBinaryFiles = []
	# extract only similar packages
	for pkg in pkgBinaryFiles:
	    _pkg = pkg.split(".so")[0]
	    for newpkg in newPkgBinaryFiles:
		_newpkg = newpkg.split(".so")[0]
		if (_newpkg == _pkg):
		    _pkgBinaryFiles.append(pkg)
		    _newPkgBinaryFiles.append(newpkg)
	pkgBinaryFiles = _pkgBinaryFiles
	newPkgBinaryFiles = _newPkgBinaryFiles
	
	# check for version bumps
	for pkg in pkgBinaryFiles:
	    _pkgver = pkg.split(".so")[len(pkg.split(".so"))-1]
	    _pkg = pkg.split(".so")[0]
	    for newpkg in newPkgBinaryFiles:
		_newpkgver = newpkg.split(".so")[len(newpkg.split(".so"))-1]
		_newpkg = newpkg.split(".so")[0]
		if (_newpkg == _pkg):
		    # check version
		    if (_pkgver != _newpkgver):
			brokenBinariesList.append([ pkg, newpkg ])
    return brokenBinariesList


# create a .tbz2 file in the specified path
def quickpkg(atom,dirpath):
    # getting package info
    pkgname = atom.split("/")[1]
    pkgcat = atom.split("/")[0]
    pkgfile = pkgname+".tbz2"
    dirpath += "/"+pkgname+".tbz2"
    tmpdirpath = etpConst['packagestmpdir']+"/"+pkgname+".tbz2"+"-tmpdir"
    if os.path.isdir(tmpdirpath): spawnCommand("rm -rf "+tmpdirpath)
    os.makedirs(tmpdirpath)
    dbdir = "/var/db/pkg/"+pkgcat+"/"+pkgname+"/"

    # crate file list
    f = open(dbdir+dbCONTENTS,"r")
    pkgcontent = f.readlines()
    f.close()
    _pkgcontent = []
    for line in pkgcontent:
	line = line.strip().split()[1]
	if not ((os.path.isdir(line)) and (os.path.islink(line))):
	    _pkgcontent.append(line)
    pkgcontent = _pkgcontent
    f = open(tmpdirpath+"/"+dbCONTENTS,"w")
    for i in pkgcontent:
	f.write(i+"\n")
    f.flush()
    f.close()

    # package them into a file
    rc = spawnCommand("tar cjf "+dirpath+" -C / --files-from='"+tmpdirpath+"/"+dbCONTENTS+"' --no-recursion", redirect = "&>/dev/null")
    
    # appending xpak informations
    import xpak
    tbz2 = xpak.tbz2(dirpath)
    tbz2.recompose(dbdir)
    
    # Remove tmp file
    os.system("rm -rf "+tmpdirpath)
    
    if os.path.isfile(dirpath):
	return dirpath
    else:
	return False

def unpackTbz2(tbz2File,tmpdir = None):
    import xpak
    if tmpdir is None:
	tmpdir = etpConst['packagestmpdir']+"/"+tbz2File.split("/")[len(tbz2File.split("/"))-1].split(".tbz2")[0]+"/"
    if (not tmpdir.endswith("/")):
	tmpdir += "/"
    tbz2 = xpak.tbz2(tbz2File)
    if os.path.isdir(tmpdir):
	os.system("rm -rf "+tmpdir+"*")
    tbz2.decompose(tmpdir)
    return tmpdir

# NOTE: atom must be a COMPLETE atom, with version!
def isTbz2PackageAvailable(atom, verbose = False):
    # check if the package have been already merged
    atomName = atom.split("/")[len(atom.split("/"))-1]
    tbz2Available = False
    
    uploadPath = etpConst['packagessuploaddir']+"/"+atomName+".tbz2"
    storePath = etpConst['packagesstoredir']+"/"+atomName+".tbz2"
    packagesPath = etpConst['packagesbindir']+"/"+atomName+".tbz2"
    
    if (verbose): print "testing in directory: "+packagesPath
    if os.path.isfile(packagesPath):
        tbz2Available = packagesPath
    if (verbose): print "testing in directory: "+storePath
    if os.path.isfile(storePath):
        tbz2Available = storePath
    if (verbose): print "testing in directory: "+uploadPath
    if os.path.isfile(uploadPath):
        tbz2Available = uploadPath
    if (verbose): print "found here: "+str(tbz2Available)

    return tbz2Available

def checkAtom(atom):
    bestAtom = getBestAtom(atom)
    if bestAtom == "!!conflicts":
	bestAtom = ""
    if (isvalidatom(atom) == 1) or ( bestAtom != ""):
        return True
    return False

def removeSpaceAtTheEnd(string):
    if string.endswith(" "):
        return string[:len(string)-1]
    else:
	return string

def md5sum(filepath):
    import md5
    m = md5.new()
    readfile = file(filepath)
    block = readfile.read(1024)
    while block:
        m.update(block)
	block = readfile.read(1024)
    return m.hexdigest()

# Tool to run commands
def spawnCommand(command, redirect = None):
    if redirect is not None:
        command += " "+redirect
    rc = os.system(command)
    return rc

def getPackageDependencyList(atom):
    pkgSplittedDeps = []
    tmp = portage.portdb.aux_get(atom, ["DEPEND"])[0].split()
    for i in tmp:
	pkgSplittedDeps.append(i)
    tmp = portage.portdb.aux_get(atom, ["RDEPEND"])[0].split()
    for i in tmp:
	pkgSplittedDeps.append(i)
    tmp = portage.portdb.aux_get(atom, ["PDEPEND"])[0].split()
    for i in tmp:
	pkgSplittedDeps.append(i)
    return pkgSplittedDeps

# parser of the gentoo db "NEEDED" file
# this file is contained in the .tbz2->.xpak file
def getPackageRuntimeDependencies(NEEDED):

    if not os.path.isfile(NEEDED):
	return [],[] # both empty

    f = open(NEEDED,"r")
    includedBins = f.readlines()
    f.close()

    neededLibraries = []
    # filter the first word
    for line in includedBins:
        line = line.strip().split()
	line = line[0]
	depLibs = commands.getoutput("ldd "+line).split("\n")
	for i in depLibs:
	    i = i.strip()
	    if i.find("=>") != -1:
	        i = i.split("=>")[1]
	    # format properly
	    if i.startswith(" "):
	        i = i[1:]
	    if i.startswith("//"):
	        i = i[1:]
	    i = i.split()[0]
	    neededLibraries.append(i)
    neededLibraries = list(set(neededLibraries))

    runtimeNeededPackages = []
    runtimeNeededPackagesXT = []
    for i in neededLibraries:
	if i.startswith("/"): # filter garbage
	    pkgs = commands.getoutput(pFindLibraryXT+i).split("\n")
	    if (pkgs[0] != ""):
	        for y in pkgs:
	            runtimeNeededPackagesXT.append(y)
		    y = dep_getkey(y)
		    runtimeNeededPackages.append(y)

    runtimeNeededPackages = list(set(runtimeNeededPackages))
    runtimeNeededPackagesXT = list(set(runtimeNeededPackagesXT))
    return runtimeNeededPackages, runtimeNeededPackagesXT

def getUSEFlags():
    return getPortageEnv('USE')

# you must provide a complete atom
def getPackageIUSE(atom):
    return getPackageVar(atom,"IUSE")

def getPackageVar(atom,var):
    if atom.startswith("="):
	atom = atom[1:]
    # can't check - return error
    if (atom.find("/") == -1):
	return 1
    return portage.portdb.aux_get(atom,[var])[0]

def synthetizeRoughDependencies(roughDependencies, useflags = None):
    if useflags is None:
        useflags = getUSEFlags()
    # returns dependencies, conflicts

    useMatch = False
    openParenthesis = 0
    openOr = False
    useFlagQuestion = False
    dependencies = ""
    conflicts = ""
    for atom in roughDependencies:

	if atom.endswith("?"):
	    # we need to see if that useflag is enabled
	    useFlag = atom.split("?")[0]
	    useFlagQuestion = True
	    for i in useflags.split():
		if i.startswith("!"):
		    if (i != useFlag):
			useMatch = True
			break
		else:
		    if (i == useFlag):
		        useMatch = True
		        break

        if atom.startswith("("):
	    openParenthesis += 1

        if atom.startswith(")"):
	    if (openOr):
		# remove last "_or_" from dependencies
		openOr = False
		if dependencies.endswith(dbOR):
		    dependencies = dependencies[:len(dependencies)-len(dbOR)]
		    dependencies += " "
	    openParenthesis -= 1
	    if (openParenthesis == 0):
		useFlagQuestion = False
		useMatch = False

        if atom.startswith("||"):
	    openOr = True
	
	if atom.find("/") != -1 and (not atom.startswith("!")) and (not atom.endswith("?")):
	    # it's a package name <pkgcat>/<pkgname>-???
	    if ((useFlagQuestion) and (useMatch)) or ((not useFlagQuestion) and (not useMatch)):
	        # check if there's an OR
		dependencies += atom
		if (openOr):
		    dependencies += dbOR
                else:
		    dependencies += " "

        if atom.startswith("!") and (not atom.endswith("?")):
	    if ((useFlagQuestion) and (useMatch)) or ((not useFlagQuestion) and (not useMatch)):
		conflicts += atom
		if (openOr):
		    conflicts += dbOR
                else:
		    conflicts += " "
		

    # format properly
    tmpConflicts = list(set(conflicts.split()))
    conflicts = ''
    for i in tmpConflicts:
	i = i[1:] # remove "!"
	conflicts += i+" "
    conflicts = removeSpaceAtTheEnd(conflicts)

    tmpDeps = list(set(dependencies.split()))
    dependencies = ''
    for i in tmpDeps:
	dependencies += i+" "
    dependencies = removeSpaceAtTheEnd(dependencies)

    return dependencies, conflicts

# Collect installed packages
def getInstalledPackages():
    import os
    appDbDir = getPortageAppDbPath()
    dbDirs = os.listdir(appDbDir)
    installedAtoms = []
    for pkgsdir in dbDirs:
	pkgdir = os.listdir(appDbDir+pkgsdir)
	for pdir in pkgdir:
	    pkgcat = pkgsdir.split("/")[len(pkgsdir.split("/"))-1]
	    pkgatom = pkgcat+"/"+pdir
	    if pkgatom.find("-MERGING-") == -1:
	        installedAtoms.append(pkgatom)
    return installedAtoms, len(installedAtoms)

def getPortageAppDbPath():
    rc = getPortageEnv("ROOT")+portage_const.VDB_PATH
    if (not rc.endswith("/")):
	return rc+"/"
    return rc

# ------ BEGIN: activator tools ------

class activatorFTP:

    # ftp://linuxsabayon:asdasd@silk.dreamhost.com/sabayon.org
    # this must be run before calling the other functions
    def __init__(self, ftpuri):
	
	from ftplib import FTP
	
	self.ftpuri = ftpuri
	
	self.ftphost = ftpuri.split("ftp://")[len(ftpuri.split("ftp://"))-1]
	self.ftphost = self.ftphost.split("@")[len(self.ftphost.split("@"))-1]
	self.ftphost = self.ftphost.split("/")[0]
	self.ftphost = self.ftphost.split(":")[0]
	
	self.ftpuser = ftpuri.split("ftp://")[len(ftpuri.split("ftp://"))-1].split(":")[0]
	if (self.ftpuser == ""):
	    self.ftpuser = "anonymous@"
	    self.ftppassword = "anonymous"
	else:
	    self.ftppassword = ftpuri.split("@")[:len(ftpuri.split("@"))-1]
	    if len(self.ftppassword) > 1:
		import string
		self.ftppassword = string.join(self.ftppassword,"@")
		self.ftppassword = self.ftppassword.split(":")[len(self.ftppassword.split(":"))-1]
		if (self.ftppassword == ""):
		    self.ftppassword = "anonymous"
	    else:
		self.ftppassword = self.ftppassword[0]
		self.ftppassword = self.ftppassword.split(":")[len(self.ftppassword.split(":"))-1]
		if (self.ftppassword == ""):
		    self.ftppassword = "anonymous"
	
	self.ftpport = ftpuri.split(":")[len(ftpuri.split(":"))-1]
	try:
	    self.ftpport = int(self.ftpport)
	except:
	    self.ftpport = 21
	
	self.ftpdir = ftpuri.split("ftp://")[len(ftpuri.split("ftp://"))-1]
	self.ftpdir = self.ftpdir.split("/")[len(self.ftpdir.split("/"))-1]
	self.ftpdir = self.ftpdir.split(":")[0]
	self.ftpdir = self.ftpdir+translateArchFromUname(etpConst['binaryurirelativepath'])
	if self.ftpdir.endswith("/"):
	    self.ftpdir = self.ftpdir[:len(self.ftpdir)-1]

	print self.ftpdir

	self.ftpconn = FTP(self.ftphost)
	self.ftpconn.login(self.ftpuser,self.ftppassword)
	# change to our dir
	self.ftpconn.cwd(self.ftpdir)

    def getFTPHost(self):
	return self.ftphost

    def getFTPPort(self):
	return self.ftpport

    def getFTPDir(self):
	return self.ftpdir

    def getCWD(self):
	return self.ftpconn.pwd()

    def setCWD(self,dir):
	self.ftpconn.cwd(dir)

    # list files and directory of a FTP
    # @returns a list
    def listFTPdir(self):
	# directory is: self.ftpdir
	try:
	    rc = self.ftpconn.nlst()
	    _rc = []
	    for i in rc:
		_rc.append(i.split("/")[len(i.split("/"))-1])
	    rc = _rc
	except:
	    return []
	return rc

    def deleteFile(self,file):
	try:
	    rc = self.ftpconn.delete(self.ftpdir+"/"+file)
	    if rc.startswith("250"):
		return True
	    else:
		return False
	except:
	    return False

    def uploadFile(self,file,ascii = False):
	if (not ascii):
	    f = open(file)
	    file = file.split("/")[len(file.split("/"))-1]
	    rc = self.ftpconn.storbinary("STOR "+file,f)
	    return rc
	else:
	    f = open(file)
	    file = file.split("/")[len(file.split("/"))-1]
	    rc = self.ftpconn.storlines("STOR "+file,f)
	    return rc

    # also used to move files
    def renameFile(self,fromfile,tofile):
	self.ftpconn.rename(fromfile,tofile)

    def closeFTPConnection(self):
	self.ftpconn.quit()


    # FIXME: add upload/delete/mv commands

# ------ END: activator tools ------

# get a list, returns a sorted list
def alphaSorter(seq):
    def stripter(s, goodchrs):
        badchrs = set(s)
        for c in goodchrs:
            if c in badchrs:
                badchrs.remove(c)
        badchrs = ''.join(badchrs)
        return s.strip(badchrs)
    
    def chr_index(value, sortorder):
        result = []
        for c in stripter(value, order):
            cindex = sortorder.find(c)
            if cindex == -1:
                cindex = len(sortorder)+ord(c)
            result.append(cindex)
        return result
    
    order = ( '0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz' )
    deco = [(chr_index(a, order), a) for a in seq]
    deco.sort()
    return list(x[1] for x in deco)

# Temporary files cleaner
def cleanup(options):

    toCleanDirs = [ etpConst['packagestmpdir'], etpConst['logdir'] ]
    counter = 0

    for dir in toCleanDirs:
        print_info(red(" * ")+"Cleaning "+yellow(dir)+" directory...", back = True)
	dircontent = os.listdir(dir)
	if dircontent != []:
	    for data in dircontent:
		os.system("rm -rf "+dir+"/"+data)
		counter += 1

    print_info(green(" * ")+"Cleaned: "+str(counter)+" files and directories")

def mountProc():
    # check if it's already mounted
    procfiles = os.listdir("/proc")
    if len(procfiles) > 2:
	return True
    else:
	os.system("mount -t proc proc /proc &> /dev/null")
	return True

def umountProc():
    # check if it's already mounted
    procfiles = os.listdir("/proc")
    if len(procfiles) > 2:
	os.system("umount /proc &> /dev/null")
	os.system("umount /proc &> /dev/null")
	os.system("umount /proc &> /dev/null")
	return True
    else:
	return True

def askquestion(prompt):
    responses, colours = ["Yes", "No"], [green, red]
    print green(prompt),
    try:
	while True:
	    response=raw_input("["+"/".join([colours[i](responses[i]) for i in range(len(responses))])+"] ")
	    for key in responses:
		# An empty response will match the first value in responses.
		if response.upper()==key[:len(response)].upper():
		    return key
		    print "I cannot understand '%s'" % response,
    except (EOFError, KeyboardInterrupt):
	print "Interrupted."
	sys.exit(1)

def print_error(msg):
    print red(">>")+" "+msg

def print_info(msg, back = False):
    writechar("\r                                                                                                \r")
    if (back):
	writechar("\r"+green(">>")+" "+msg)
	return
    print green(">>")+" "+msg

def print_warning(msg):
    print yellow(">>")+" "+msg

def print_generic(msg): # here we'll wrap any nice formatting
    print msg