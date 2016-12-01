#!/usr/bin/python

import subprocess
import os
import re
import sys

from spelbuild_common import *

revFile = "/home/vkoshura/spelbuildbot.last"
logFile = "/home/vkoshura/spelbuildbot.log"
usrFile = "/home/vkoshura/spelbuildbot.usr"
lockFile = "/home/vkoshura/spelbuildbot.lock"
#buildFile = "/home/vkoshura/spelbuild.sh"
srvPath = "/srv/pose/"

def getLastSavedRev(file):
	if not os.path.exists(file):
		return 0
	f = open(file, 'r')
	rev = f.read()
	f.close()
	return int(rev)

def setLastSavedRev(file, rev):
	f = open(file, 'w')
	f.write(rev)
	f.close()

def parseLastRevision(text):
	exp = re.compile(r"changeset:\s+(\d+):")
	res = exp.search(text)
	return res.groups()[0]

def getCurrentRevision():
	process = subprocess.Popen(["hg", "log", "-l", "1"], stdout=subprocess.PIPE)
	output, err = process.communicate()
	res = parseLastRevision(output);
	return int(res)

def getNewRevisions(last, curr, file):
	range = str(last + 1) + ":" + str(curr)
	process = subprocess.Popen(["hg", "log", "-r", range], stdout=subprocess.PIPE)
	output, err = process.communicate()
	f = open(file, "w")
	f.write("New pushed revisions:\n\n")
	f.write(output)
	f.close()

def sendMail(to, subject, body, files):
	command = "mutt -s" + subject + " " + to + " < " + body
	process = subprocess.Popen(command, shell=True)
	process.communicate()

def sendMails(to, subject, body, files):
	f = open(to, 'r')
	lines = f.readlines()
	for line in lines:
		addr = line.rstrip('\n')
		sendMail(addr, subject, body, files)
	f.close()

def start():
	cwd = os.getcwd()
	os.chdir(srvPath)

	lastSavedRev = getLastSavedRev(revFile)
	currentRev = getCurrentRevision()

	if currentRev <= lastSavedRev:
		os.chdir(cwd)
		return

	getNewRevisions(lastSavedRev, currentRev, logFile)

	#Do main job

	setLastSavedRev(revFile, currentRev)
	
	if os.path.exists(logFile):
		sendMails(usrFile, "SPEL Build Bot Report", logFile, [])
		os.remove(logFile)

	os.chdir(cwd)

def main ():
	res = createLockFile(lockFile)
	if not res:
		sys.exit(1)
	else:
		start()
		deleteLockFile(lockFile)
	return

#main()
start()