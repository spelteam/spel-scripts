#!/usr/bin/python

import os
import re
import sys

from spelbuild_common import *

revFile = "/home/vkoshura/spelbuildbot.last"
logFile = "/home/vkoshura/spelbuildbot.log"
buildLogFile = "/home/vkoshura/spelbuild.log"
testsFile="/home/vkoshura/spelbuildtests.log"
usrFile = "/home/vkoshura/spelbuildbot.usr"
dbPwd = "/home/vkoshura/spelbuildbot.dbpwd"
lockFile = "/home/vkoshura/spelbuildbot.lock"
srvPath = "/srv/pose/"
srcPath = "/home/vkoshura/pose/"
logs = "/home/vkoshura/linuxlogs.7z"

def getLastSavedRev(file):
	if not os.path.exists(file):
		return 0
	f = open(file, 'r')
	rev = f.read()
	f.close()
	return int(rev)

def setLastSavedRev(file, rev):
	f = open(file, 'w')
	f.write(str(rev))
	f.close()

def parseLastRevision(text):
	exp = re.compile(r"changeset:\s+(\d+):")
	res = exp.search(text)
	if res is not None:
		return res.groups()[0]
	return 0

def getCurrentRevision():
	retcode, output, err = runProcess(["hg", "log", "-l", "1"])
	res = parseLastRevision(output);
	return int(res)

def getNewRevisions(last, curr, file):
	range = str(last + 1) + ":" + str(curr)
	retcode, output, err = runProcess(["hg", "log", "-r", range])
	writeLog("New pushed revisions:\n", file, True)
	writeLog(output, file)

def updateRepo():
	retcode, output, err = runProcess(["hg", "pull"])
	writeLog(output, buildLogFile)
	if retcode != 0:
		return 1
	retcode, output, err = runProcess(["hg", "up"])
	writeLog(output, buildLogFile)
	if retcode != 0:
		return 1
	return 0

def build():
	os.chdir(srcPath)
	writeLog("Start build:\n", buildLogFile, True)
	retcode = updateRepo()
	if retcode != 0:
		return retcode
	os.chdir("build")
	retcode, output, err = runProcess(["make", "clean"])
	writeLog(output, buildLogFile)
	if retcode != 0:
		return 2
	retcode, output, err = runProcess(["cmake", "../src/"])
	writeLog(output, buildLogFile)
	if retcode != 0:
		return 3
	retcode, output, err = runProcess(["make", "-j2"])
	writeLog(output, buildLogFile)
	if retcode != 0:
		return 4
	return 0

def runTest(test):
	insertTestIntoDb(test, dbPwd)
	retcode, output, err = runProcess(["./speltests", "--gtest_filter=" + test])
	writeLog(output, testsFile)
	status = parseTestResults(output, logFile)
	updateTestInDb(test, "linux", status, dbPwd)
	return status

def packLogs(archive, logs):
	files = []
	for log in logs:
		if os.path.exists(log):
			files.append(log)
	if len(files) > 0:
		runProcess(["7z", "a", archive] + files)
	return

def run():
	os.chdir("tests")
	retcode, output, err = runProcess(["./speltests", "--gtest_list_tests"])
	tests = getTestList(output)
	writeLog("\nTests Summary:\n", logFile)
	writeLog("", testsFile)
	failedList = []
	failed = 0;
	success = 0;
	for test in tests:
		if test.find("DISABLED_") == -1:
			if runTest(test) == 1:
				success = success + 1
			else:
				failed = failed + 1
				failedList.append(test)
	writeLog("\nFailed Tests:\n", logFile)
	failedList.sort()
	for test in failedList:
		writeLog(test, logFile)
	writeLog("\nOK: " + str(success), logFile)
	writeLog("Failed: " + str(failed), logFile)
	writeLog("Total: " + str(success + failed), logFile)
	return

def buildAndRun():
	retcode = build()
	if retcode == 0:
		run()
	packLogs(logs, [buildLogFile, testsFile])
	status = "SPEL Build Bot: Build Report: "
	if retcode == 0:
		status = status + "SUCCESSFULL"
	elif retcode == 1:
		status = status + "FAILED: Repository update failed"
	elif retcode == 2:
		status = status + "FAILED: Clean failed"
	elif retcode == 3:
		status = status + "FAILED: CMake rebuild failed"
	elif retcode == 4:
		status = status + "FAILED: SPEL rebuild failed"
	else:
	  status = status + "FAILED: Unknown reason"
	if os.path.exists(logs):
		sendMails(usrFile, status, logFile, logs)
	return retcode

def clean():
	if os.path.exists(logFile):
		os.remove(logFile)
	if os.path.exists(buildLogFile):
		os.remove(buildLogFile)
	if os.path.exists(testsFile):
		os.remove(testsFile)
	if os.path.exists(logs):
		os.remove(logs)
	return

def start():
	cwd = os.getcwd()
	os.chdir(srvPath)

	lastSavedRev = getLastSavedRev(revFile)
	currentRev = getCurrentRevision()
	if currentRev <= lastSavedRev:
		os.chdir(cwd)
		return

	getNewRevisions(lastSavedRev, currentRev, logFile)
	buildAndRun()
	clean()
	setLastSavedRev(revFile, currentRev)

	os.chdir(cwd)

def main ():
	res = createLockFile(lockFile)
	if not res:
		sys.exit(1)
	else:
		start()
		deleteLockFile(lockFile)
	return

main()
